import sys
import cv2
import numpy as np
import trimesh
from shapely.geometry import Polygon, MultiPolygon, Point
import shapely.ops
from PIL import Image, ImageDraw
import trimesh.transformations
import trimesh.creation
import trimesh.visual.material
from matplotlib.textpath import TextPath
from config import SessionLocal
from services.models import FileStorage

# --- Global Constants (used for scaling and offset) ---
GRID_SIZE = 10      # Each cell is 10x10 pixels
CANVAS_WIDTH = 1600
CANVAS_HEIGHT = 900
Y_OFFSET = -10
X_OFFSET = -27

# --------------------------------------------------------------------
# 1. Helper functions for building geometry from the floorplan image
# --------------------------------------------------------------------

def build_black_geometry(contours, hierarchy):
    """
    Build a Shapely MultiPolygon from black wall contours using the even-odd fill rule.
    """
    geometry = MultiPolygon()

    def traverse_contour(idx, depth, geom):
        poly = Polygon(contours[idx][:, 0, :])
        if not poly.is_valid or poly.area < 1.0:
            return geom  # Skip invalid or tiny polygons
        if depth % 2 == 0:
            geom = geom.union(poly)
        else:
            geom = geom.difference(poly)
        child_idx = hierarchy[0][idx][2]
        while child_idx != -1:
            geom = traverse_contour(child_idx, depth + 1, geom)
            child_idx = hierarchy[0][child_idx][0]
        return geom

    for i in range(len(contours)):
        if hierarchy[0][i][3] == -1:  # top-level contour
            geometry = traverse_contour(i, 0, geometry)
    return geometry

def create_reverse_teardrop_polygon(circle_radius, tip_offset):
    """
    Create a 2D polygon that approximates a reverse teardrop shape.
    This is used for creating markers (for connected yellow points).
    """
    num_points = 50
    angles = np.linspace(0, np.pi, num_points)
    top_arc = [(circle_radius * np.cos(a), circle_radius * np.sin(a)) for a in angles]
    tip = (0, -tip_offset)
    polygon_points = top_arc + [tip]
    return Polygon(polygon_points)

# --------------------------------------------------------------------
# 2. Updated function to create a text mesh that preserves holes correctly
# --------------------------------------------------------------------

def create_text_mesh(text, font="DejaVu Sans", size=16, depth=1.0, scale=1.0):
    """
    Create a 3D mesh from text by:
      1. Using matplotlib's TextPath to create a 2D outline.
      2. Converting the outline to shapely polygons while preserving holes.
      3. Extruding the polygon(s) into 3D with the given depth.
      4. Scaling the result.
    """
    try:
        text_path = TextPath((0, 0), text, size=size, prop=dict(family=font))
    except Exception as e:
        print(f"Error generating TextPath for '{text}': {e}")
        return None

    raw_polys = text_path.to_polygons()
    if not raw_polys:
        print(f"No polygons generated for text '{text}'")
        return None

    # Partition raw polygons into outer rings and inner rings using signed area.
    outer_polys = []
    inner_polys = []
    for poly in raw_polys:
        poly = np.array(poly)
        # Ensure the polygon is 2D with shape (n,2)
        if poly.ndim != 2 or poly.shape[1] != 2:
            continue
        # Ensure the polygon is closed.
        if not np.allclose(poly[0], poly[-1]):
            poly = np.vstack([poly, poly[0]])
        # Compute the signed area using the shoelace formula.
        area = 0.5 * np.sum(poly[:-1, 0]*poly[1:, 1] - poly[1:, 0]*poly[:-1, 1])
        # Swap the condition: now if area < 0, treat as outer; else as inner.
        if area < 0:
            outer_polys.append(poly)
        else:
            inner_polys.append(poly)

    # Assign inner rings (holes) to the appropriate outer ring.
    polys_with_holes = []
    for outer in outer_polys:
        poly_obj = Polygon(outer)
        holes = []
        for inner in inner_polys:
            inner_obj = Polygon(inner)
            if poly_obj.contains(inner_obj):
                holes.append(inner.tolist())
        polys_with_holes.append(Polygon(outer.tolist(), holes))

    combined = shapely.ops.unary_union(polys_with_holes)

    try:
        if combined.geom_type == 'MultiPolygon':
            meshes = []
            for poly in combined.geoms:
                try:
                    m = trimesh.creation.extrude_polygon(poly, height=depth)
                    meshes.append(m)
                except Exception as e:
                    print(f"Error extruding polygon for text '{text}': {e}")
            if not meshes:
                return None
            mesh = trimesh.util.concatenate(meshes)
        else:
            mesh = trimesh.creation.extrude_polygon(combined, height=depth)
    except Exception as e:
        print(f"Error extruding polygon for text '{text}': {e}")
        return None

    mesh.apply_scale(scale)
    return mesh

def create_text_label_final(text, node_location, scale=1.0, height_offset=10.0):
    """
    Create a 3D text label for a node.
    
    The node_location comes from the model file as (x, y) and is first scaled and offset:
      final_x = (node_x * GRID_SIZE) + X_OFFSET
      final_z = (node_y * GRID_SIZE) + Y_OFFSET
      
    The label is then placed at vertical height (final_y = height_offset) in the final coordinate system.
    (No additional rotation is applied.)
    """
    text_mesh = create_text_mesh(text, size=16, depth=2.0, scale=1.0)
    if text_mesh is None:
        print(f"Error creating text mesh for '{text}'")
        return None

    # Adjust the text mesh so its bottom center is at the origin.
    bounds = text_mesh.bounds
    center_x = (bounds[0][0] + bounds[1][0]) / 2.0
    min_y = bounds[0][1]
    text_mesh.apply_translation(-np.array([center_x, min_y, 0]))

    # Apply the desired scaling.
    text_mesh.apply_scale(scale)

    # Compute final position using grid scaling and offsets.
    final_x = (node_location[0] * GRID_SIZE) + X_OFFSET
    final_y = height_offset
    final_z = (node_location[1] * GRID_SIZE) + Y_OFFSET
    text_mesh.apply_translation(np.array([final_x, final_y, final_z]))
    
    # Set the text color to white (RGBA)
    text_mesh.visual.face_colors = [114, 0, 196, 255]
    
    return text_mesh


# --------------------------------------------------------------------
# 3. Parsing node data from model file content (text file)
# --------------------------------------------------------------------

def load_nodes_from_content(content):
    """
    Parse nodes from the model file content.
    Expected format:
       Start and Goal Nodes:
       Node: <name>, Location: (<x>, <y>)
       ...
       Generated Paths:
       ...
    Returns a dictionary mapping node names to coordinate tuples.
    """
    if isinstance(content, bytes):
        lines = content.decode("utf-8").splitlines()
    else:
        lines = content.splitlines()
    nodes = {}
    section = None
    for line in lines:
        line = line.strip()
        if "Start and Goal Nodes" in line:
            section = "nodes"
            continue
        elif "Generated Paths" in line:
            section = "paths"
            continue
        if section == "nodes" and line:
            parts = line.split(", Location: ")
            if len(parts) < 2:
                continue
            node_part = parts[0]
            node_name = node_part.split("Node: ")[1].strip()
            location_str = parts[1].strip("()")
            coords = tuple(map(int, location_str.split(", ")))
            nodes[node_name] = coords
    return nodes, None

# --------------------------------------------------------------------
# 4. Main function to generate a 3D model (GLB bytes) from image bytes and DB model file
# --------------------------------------------------------------------

def generate_3d_model_from_bytes(image_bytes, floor_name, landmark_name):
    """
    Given image data (as bytes, e.g., the generated 2D path image), the floor name, 
    and landmark identifier, generate a 3D model (as GLB bytes) that includes walls, 
    paths, markers, a floor, and 3D text labels.
    
    The function fetches the latest text model file for the specified floor and landmark
    from the database.
    """
    # Decode the image from bytes
    image_data = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Could not decode image from bytes.")

    # -------------------------
    # 1. Build wall geometry
    # -------------------------
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, wall_mask = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((3, 3), np.uint8)
    wall_mask = cv2.morphologyEx(wall_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    contours, hierarchy = cv2.findContours(wall_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:
        raise RuntimeError("No contours found for walls. Check threshold or image content.")
    black_geometry = build_black_geometry(contours, hierarchy)
    if black_geometry.is_empty:
        raise RuntimeError("Black geometry is empty; check your threshold or image content.")
    
    # -------------------------
    # 2. Detect yellow points (room dots)
    # -------------------------
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    mask_yellow = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    room_contours, _ = cv2.findContours(mask_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    yellow_points = []
    for cnt in room_contours:
        if cv2.contourArea(cnt) < 2:
            continue
        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue
        cx = M["m10"] / M["m00"]
        cy = M["m01"] / M["m00"]
        yellow_points.append((cx, cy))

    # -------------------------
    # 3. Detect blue path (rope polygons)
    # -------------------------
    lower_blue = np.array([100, 80, 50])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    mask_blue = cv2.dilate(mask_blue, np.ones((3, 3), np.uint8), iterations=1)
    path_contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    path_polygons = []
    for cnt in path_contours:
        if cv2.contourArea(cnt) < 5:
            continue
        poly = Polygon(cnt[:, 0, :])
        if poly.is_valid and poly.area > 1:
            path_polygons.append(poly)

    # -------------------------
    # 4. Separate yellow points into connected and regular
    # -------------------------
    threshold_distance = 5.0  # adjust based on image scale
    connected_yellow = []
    regular_yellow = []
    for pt in yellow_points:
        p = Point(pt[0], pt[1])
        if any(path_poly.distance(p) < threshold_distance for path_poly in path_polygons):
            connected_yellow.append(pt)
        else:
            regular_yellow.append(pt)

    expand_distance = 2.0  
    for path_poly in path_polygons:
        expanded_poly = path_poly.buffer(expand_distance)
        black_geometry = black_geometry.difference(expanded_poly)
        
    corner_radius = 9.0
    black_geometry = black_geometry.buffer(corner_radius, join_style=1).buffer(-corner_radius, join_style=1)
    
    # -------------------------
    # 5. Extrude walls, paths, and markers
    # -------------------------
    wall_height = 40.0
    wall_meshes = []
    if black_geometry.geom_type == "Polygon":
        wall_meshes.append(trimesh.creation.extrude_polygon(black_geometry, height=wall_height))
    elif black_geometry.geom_type == "MultiPolygon":
        for poly in black_geometry.geoms:
            wall_meshes.append(trimesh.creation.extrude_polygon(poly, height=wall_height))
    
    wall_material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[1.0, 1.0, 1.0, 0.8]
    )
    for mesh in wall_meshes:
        mesh.visual.material = wall_material

    path_meshes = []
    rope_height = 2.0
    for path_poly in path_polygons:
        rope_mesh = trimesh.creation.extrude_polygon(path_poly, height=rope_height)
        rope_mesh.visual.face_colors = [0, 0, 255, 255]
        rope_mesh.apply_translation((0, 0, 0.1))
        path_meshes.append(rope_mesh)

    room_markers = []
    sphere_radius = 4.0
    for pt in regular_yellow:
        sphere_mesh = trimesh.creation.icosphere(subdivisions=2, radius=sphere_radius)
        sphere_mesh.apply_translation((pt[0], pt[1], sphere_radius))
        sphere_mesh.visual.face_colors = [255, 255, 0, 255]
        room_markers.append(sphere_mesh)
    
    circle_radius = 8.0
    tip_offset = 12.0
    for pt in connected_yellow:
        marker_polygon = create_reverse_teardrop_polygon(circle_radius, tip_offset)
        marker_mesh = trimesh.creation.extrude_polygon(marker_polygon, height=10.0)
        pivot = np.array([0, -tip_offset, 0])
        T1 = trimesh.transformations.translation_matrix(-pivot)
        R = trimesh.transformations.rotation_matrix(np.radians(90), [1, 0, 0])
        T2 = trimesh.transformations.translation_matrix(pivot)
        marker_mesh.apply_transform(T2.dot(R).dot(T1))
        scale_factor = 1.5
        marker_mesh.apply_scale(scale_factor)
        translation_vector = (pt[0], pt[1] + tip_offset, 0)
        marker_mesh.apply_translation(translation_vector)
        marker_mesh.visual.face_colors = [255, 0, 0, 255]
        room_markers.append(marker_mesh)
    
    
    # -------------------------
    # 6. Assemble scene and apply transforms
    # -------------------------
    scene = trimesh.Scene()
    for m in wall_meshes:
        scene.add_geometry(m)
    for m in room_markers:
        scene.add_geometry(m)
    for m in path_meshes:
        scene.add_geometry(m)
        


    # Swap Y and Z axes: (X remains, original Z becomes Y, original Y becomes Z)
    swap_yz = np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ])
    scene.apply_transform(swap_yz)
    
    bounds_scene = scene.bounds
    min_y_scene = bounds_scene[0][1]
    if abs(min_y_scene) > 1e-3:
        translate = trimesh.transformations.translation_matrix((0, -min_y_scene, 0))
        scene.apply_transform(translate)
       
    # -------------------------
    # 6. Build floor mesh
    # -------------------------
    min_x, min_y, max_x, max_y = black_geometry.bounds
    floor_width = max_x - min_x
    floor_depth = max_y - min_y
    floor_thickness = 1.0  # Adjust as needed.
    floor_mesh = trimesh.creation.box(extents=[floor_width, floor_thickness, floor_depth])
    center_x = (min_x + max_x) / 2.0
    center_z = (min_y + max_y) / 2.0
    floor_mesh.apply_translation([center_x, -floor_thickness/2, center_z])
    floor_material = trimesh.visual.material.PBRMaterial(
        baseColorFactor=[200/255, 200/255, 200/255, 0.3],
        alphaMode='BLEND'
    )
    floor_mesh.visual.material = floor_material
    scene.add_geometry(floor_mesh)

    # -------------------------
    # 8. Retrieve text model file from DB and add text labels
    # -------------------------
    db = SessionLocal()
    model_filename = f"model-{floor_name}.txt"
    model_file = db.query(FileStorage).filter(
        FileStorage.filename == model_filename,
        FileStorage.landmark == landmark_name
    ).order_by(FileStorage.timestamp.desc()).first()
    if model_file:
        nodes, _ = load_nodes_from_content(model_file.content)
        for node_name, location in nodes.items():
            text_mesh = create_text_label_final(node_name, location, scale=1.0, height_offset=10.0)
            if text_mesh is not None:
                scene.add_geometry(text_mesh)
    db.close()
    
    
    # -------------------------
    # 8. Add Floor Name Label
    # -------------------------
    if not black_geometry.is_empty:
        floorName = "Floor " + floor_name
        # Create a floor name label at the right front corner
        floor_label = create_text_label_final(floorName, (20, 0), scale=5.0, height_offset=30.0)
        if floor_label:
            scene.add_geometry(floor_label)  # Add label to the scene
            
            
    # -------------------------
    # 9. Export scene as GLB bytes and return them
    # -------------------------
    glb_bytes = scene.export(file_type='glb')
    return glb_bytes
