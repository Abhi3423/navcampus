import io
from PIL import Image, ImageDraw
import base64
from math import sqrt
from config import SessionLocal  # Import SessionLocal from config
from services.models import FileStorage  # Import model for potential future use

GRID_SIZE = 10      # Each cell is 10x10 pixels
CANVAS_WIDTH = 1600
CANVAS_HEIGHT = 900
Y_OFFSET = -10
X_OFFSET = -27

def load_model(file_path="the-model.txt"):
    """
    Load nodes and paths from a specified model file.
    """
    nodes = {}
    paths = []
    section = None

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if "Start and Goal Nodes" in line:
                section = "nodes"
                continue
            elif "Generated Paths" in line:
                section = "paths"
                continue

            if section == "nodes" and line:
                node_info = line.split(", Location: ")
                node_name = node_info[0].split(": ")[1]
                location = tuple(map(int, node_info[1].strip("()").split(", ")))
                nodes[node_name] = location

            elif section == "paths" and line:
                path_coords = eval(line.split(": ")[1])
                paths.append(path_coords)

    return nodes, paths

def run_dijkstra(start_node, end_node, nodes, paths):
    """
    Find the path between nodes using a simple Dijkstra-like check.
    (This implementation assumes that the paths list contains precomputed paths.)
    """
    for path in paths:
        if path[0] == nodes[start_node] and path[-1] == nodes[end_node]:
            return path
    return None

def generate_path_image(path, nodes):
    """
    Generate a base64-encoded image of the path using a static background image.
    """
    with Image.open("new frame.png") as base_map:
        base_map = base_map.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
        draw = ImageDraw.Draw(base_map)

        # Draw nodes
        for node_name, location in nodes.items():
            x, y = location[0] * GRID_SIZE, location[1] * GRID_SIZE
            radius = 5
            draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill="yellow", outline="black")

        # Draw the path in blue
        for i in range(len(path) - 1):
            start = (path[i][0] * GRID_SIZE, path[i][1] * GRID_SIZE)
            end = (path[i+1][0] * GRID_SIZE, path[i+1][1] * GRID_SIZE)
            draw.line([start, end], fill="blue", width=3)

        img_io = io.BytesIO()
        base_map.save(img_io, 'PNG')
        img_io.seek(0)
        return base64.b64encode(img_io.read()).decode('utf-8')

def load_model_from_db(floor_name, landmark_name):
    """
    Fetch nodes and paths from the latest version of the model file
    for the specified floor and landmark.
    """
    db = SessionLocal()
    model_filename = f"model-{floor_name}.txt"
    model_file = db.query(FileStorage).filter(
        FileStorage.filename == model_filename,
        FileStorage.landmark == landmark_name
    ).order_by(FileStorage.timestamp.desc()).first()

    if not model_file:
        db.close()
        return None

    nodes = {}
    paths = []
    
    if isinstance(model_file.content, bytes):
       lines = model_file.content.decode("utf-8").splitlines()
    else:
       lines = model_file.content.splitlines()

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
            node_info = line.split(", Location: ")
            node_name = node_info[0].split(": ")[1]
            location = tuple(map(int, node_info[1].strip("()").split(", ")))
            nodes[node_name] = location

        elif section == "paths" and line:
            path_coords = eval(line.split(": ")[1])
            paths.append(path_coords)

    db.close()
    return {floor_name: {"nodes": nodes, "paths": paths}}

def generate_path_image_from_db(path, nodes, floor_name, landmark):
    """
    Generate a base64 image of the path using the latest base map image for the specified floor and landmark.
    """
    db = SessionLocal()
    frame_filename = f"mapbase-{floor_name}.png"
    frame_file = db.query(FileStorage).filter(
        FileStorage.filename == frame_filename,
        FileStorage.landmark == landmark
    ).order_by(FileStorage.timestamp.desc()).first()

    if not frame_file:
        db.close()
        raise FileNotFoundError(f"Base map image '{frame_filename}' for landmark '{landmark}' not found in the database.")

    # Load the image from the database
    base_map = Image.open(io.BytesIO(frame_file.content))
    base_map = base_map.resize((CANVAS_WIDTH, CANVAS_HEIGHT))
    draw = ImageDraw.Draw(base_map)

    # Draw nodes as yellow circles with offsets
    for node_name, location in nodes.items():
        x, y = (location[0] * GRID_SIZE) + X_OFFSET, (location[1] * GRID_SIZE) + Y_OFFSET
        radius = 5
        draw.ellipse([(x - radius, y - radius), (x + radius, y + radius)], fill="yellow", outline="black")

    # Draw the path in blue with offsets
    for i in range(len(path) - 1):
        start = ((path[i][0] * GRID_SIZE) + X_OFFSET, (path[i][1] * GRID_SIZE) + Y_OFFSET)
        end = ((path[i+1][0] * GRID_SIZE) + X_OFFSET, (path[i+1][1] * GRID_SIZE) + Y_OFFSET)
        draw.line([start, end], fill="blue", width=3)

    img_io = io.BytesIO()
    base_map.save(img_io, 'PNG')
    img_io.seek(0)
    db.close()
    return base64.b64encode(img_io.read()).decode('utf-8')

def load_nodes_from_content(content):
    """
    Parse nodes (and optionally paths) from the model content.
    Only nodes are returned in this implementation.
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
            node_info = line.split(", Location: ")
            node_name = node_info[0].split(": ")[1]
            location = tuple(map(int, node_info[1].strip("()").split(", ")))
            nodes[node_name] = location

    return nodes, None  # Only return nodes

def find_nearest_lift(start_node, nodes):
    """
    Find the nearest lift to the given start node.
    Assumes that lift nodes contain the word "Lift" in their name.
    """
    lifts = {node: loc for node, loc in nodes.items() if "Lift" in node}
    nearest_lift = min(lifts, key=lambda lift: euclidean_distance(nodes[start_node], nodes[lift]))
    return nearest_lift

def euclidean_distance(p1, p2):
    """Calculate the Euclidean distance between two points."""
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)