from flask import Blueprint, jsonify, request
import base64
from config import SessionLocal
from services.models import FileStorage
from services.utils import run_dijkstra, generate_path_image_from_db, load_model_from_db, load_nodes_from_content, find_nearest_lift
from services.model_generation import generate_3d_model_from_bytes

internal_map_bp = Blueprint('internal_map_routes', __name__)

@internal_map_bp.route('/nodes', methods=['GET'])
def get_nodes():
    """API to return all nodes from all floors for a specific landmark."""
    db = SessionLocal()
    landmark_name = request.args.get('landmark')
    if not landmark_name:
        db.close()
        return jsonify({"error": "Landmark name is required"}), 400

    # Query all model files for the specified landmark ordered by timestamp descending.
    model_files = db.query(FileStorage).filter(
        FileStorage.filename.like("model-%.txt"),
        FileStorage.landmark == landmark_name
    ).order_by(FileStorage.timestamp.desc()).all()

    if not model_files:
        db.close()
        return jsonify({"error": "No data found for the specified landmark"}), 404

    all_nodes = {}

    # For each model file, use only the latest file for each floor.
    for model_file in model_files:
        floor_name = model_file.filename.split('-')[1].split('.')[0]
        if floor_name in all_nodes:
            continue  # Skip older files for this floor
        nodes, _ = load_nodes_from_content(model_file.content)
        all_nodes[floor_name] = nodes

    db.close()
    return jsonify(all_nodes)
    
@internal_map_bp.route('/path', methods=['POST'])
def get_path():
    """
    API to get the Dijkstra path between start and end nodes (with multi-floor support).
    If the optional "get3d" parameter is true, the generated 2D path image is used to
    also generate a 3D model (with text labels) in memory, and both the 2D image and the
    base64-encoded 3D model are returned.
    """
    data = request.get_json()
    start_node = data['start']
    end_node = data['end']
    start_floor = data['start_floor']
    end_floor = data['end_floor']
    landmark_name = data.get('landmark')
    get3d = data.get('get3d', False)

    if not landmark_name:
        return jsonify({"error": "Landmark name is required"}), 400

    print(f"Pathfinding request from '{start_node}' on floor '{start_floor}' to '{end_node}' on floor '{end_floor}' for landmark '{landmark_name}'. get3d={get3d}")
    response_data = {}

    if start_floor == end_floor:
        floor_data = load_model_from_db(start_floor, landmark_name)
        if not floor_data:
            return jsonify({"error": "No data found for the specified landmark"}), 404

        nodes, paths = floor_data[start_floor]["nodes"], floor_data[start_floor]["paths"]
        path = run_dijkstra(start_node, end_node, nodes, paths)
        if not path:
            path = run_dijkstra(end_node, start_node, nodes, paths)
            if path:
                path = path[::-1]
        if path:
            img_base64 = generate_path_image_from_db(path, nodes, start_floor, landmark_name)
            response_data["start_end_floor"] = {"image": img_base64, "floor": start_floor, "node": nodes}
            if get3d:
                # Decode the 2D image from base64 into bytes and generate the 3D model in memory
                image_bytes = base64.b64decode(img_base64)
                glb_bytes = generate_3d_model_from_bytes(image_bytes, start_floor, landmark_name)
                response_data["start_end_floor"]["modelData"] = base64.b64encode(glb_bytes).decode("utf-8")
        else:
            return jsonify({"error": "Path does not exist"}), 404
    else:
        floor_data_start = load_model_from_db(start_floor, landmark_name)
        floor_data_end = load_model_from_db(end_floor, landmark_name)
        if not floor_data_start or not floor_data_end:
            return jsonify({"error": "No data found for the specified landmark"}), 404

        nodes_start, paths_start = floor_data_start[start_floor]["nodes"], floor_data_start[start_floor]["paths"]
        nodes_end, paths_end = floor_data_end[end_floor]["nodes"], floor_data_end[end_floor]["paths"]

        nearest_lift_start = find_nearest_lift(start_node, nodes_start)
        nearest_lift_end = nearest_lift_start  # Assuming same lift serves both floors

        path_to_lift = run_dijkstra(start_node, nearest_lift_start, nodes_start, paths_start)
        if not path_to_lift:
            path_to_lift = run_dijkstra(nearest_lift_start, start_node, nodes_start, paths_start)
            if path_to_lift:
                path_to_lift = path_to_lift[::-1]
        path_from_lift = run_dijkstra(nearest_lift_end, end_node, nodes_end, paths_end)
        if not path_from_lift:
            path_from_lift = run_dijkstra(end_node, nearest_lift_end, nodes_end, paths_end)
            if path_from_lift:
                path_from_lift = path_from_lift[::-1]

        if path_to_lift and path_from_lift:
            img_base64_start = generate_path_image_from_db(path_to_lift, nodes_start, start_floor, landmark_name)
            img_base64_end = generate_path_image_from_db(path_from_lift, nodes_end, end_floor, landmark_name)
            response_data["start_floor"] = {"image": img_base64_start, "floor": start_floor, "node": nodes_start}
            response_data["end_floor"] = {"image": img_base64_end, "floor": end_floor, "node": nodes_end}
            
            if get3d:
                image_bytes_start = base64.b64decode(img_base64_start)
                glb_bytes_start = generate_3d_model_from_bytes(image_bytes_start, start_floor, landmark_name)
                response_data["start_floor"]["modelData"] = base64.b64encode(glb_bytes_start).decode("utf-8")
                image_bytes_end = base64.b64decode(img_base64_end)
                glb_bytes_end = generate_3d_model_from_bytes(image_bytes_end, end_floor, landmark_name)
                response_data["end_floor"]["modelData"] = base64.b64encode(glb_bytes_end).decode("utf-8")
        else:
            return jsonify({"error": "Path does not exist"}), 404

    return jsonify(response_data)