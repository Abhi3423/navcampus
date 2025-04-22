import random
from tkinter import messagebox, simpledialog
from tqdm import tqdm
from itertools import permutations
import heapq
import time

class RRTNode:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None

    def __repr__(self):
        return f"RRTNode(x={self.x}, y={self.y})"

def distance(node1, node2):
    """Calculate the Manhattan distance between two nodes in grid space."""
    dist = abs(node1.x - node2.x) + abs(node1.y - node2.y)
    # print(f"Distance between {node1} and {node2} is {dist}")
    return dist

def random_node(width, height):
    """Generate a random node within the grid's cell space."""
    node = RRTNode(random.randint(0, width - 1), random.randint(0, height - 1))
    # print(f"Generated random node: {node}")
    return node

def nearest_node(tree, node):
    """Find the nearest node in the tree to the random node."""
    nearest = min(tree, key=lambda n: distance(n, node))
    # print(f"Nearest node to {node} is {nearest}")
    return nearest

def steer(from_node, to_node, max_step=1):
    """
    Steer from one node towards another by a maximum step distance of 2 grid cells.
    The movement is restricted to four directions: up, down, left, and right.
    """
    dx = to_node.x - from_node.x
    dy = to_node.y - from_node.y

    if abs(dx) > abs(dy):
        dx = min(max_step, dx) if dx > 0 else max(-max_step, dx)
        dy = 0
    else:
        dy = min(max_step, dy) if dy > 0 else max(-max_step, dy)
        dx = 0

    new_node = RRTNode(from_node.x + dx, from_node.y + dy)
    # print(f"Steered from {from_node} towards {to_node} with max_step={max_step}: New node is {new_node}")
    return new_node

def is_free_space(canvas, node):
    """Check if the node is in free space using pixel-based collision detection."""
    x_pixel = node.x * canvas.grid_size
    y_pixel = node.y * canvas.grid_size
    overlapping_items = canvas.canvas.find_overlapping(x_pixel, y_pixel, x_pixel + 1, y_pixel + 1)
    free = len(overlapping_items) == 0
    # print(f"Node {node} is {'free' if free else 'not free'}")
    return free

def extend(tree, canvas, target_node, max_step=2):
    """Extend the tree towards the target node and draw the path in real-time."""
    nearest = nearest_node(tree, target_node)
    new_node = steer(nearest, target_node, max_step)

    if is_free_space(canvas, new_node):
        new_node.parent = nearest
        tree.append(new_node)
        # print(f"Extended tree with new node {new_node} connected to {nearest}")

        x1 = nearest.x * canvas.grid_size + canvas.grid_size // 2
        y1 = nearest.y * canvas.grid_size + canvas.grid_size // 2
        x2 = new_node.x * canvas.grid_size + canvas.grid_size // 2
        y2 = new_node.y * canvas.grid_size + canvas.grid_size // 2

        canvas.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
        canvas.canvas.update()
        return new_node
    else:
        # print(f"Failed to extend tree from {nearest} to {target_node} due to obstacle.")
        return None

def build_rrt_connect(canvas, start, goal, max_iters=1000, connect_radius=2):
    """Build an RRT-Connect path between start and goal using grid cells."""
    start_tree = [start]
    goal_tree = [goal]
    width, height = canvas.size_col, canvas.size_row

    # print("Starting RRT-Connect...")
    # for i in tqdm(range(max_iters), desc="Building RRT-Connect Path"):
    for i in range(max_iters):
        random_point = random_node(width, height)

        new_start_node = extend(start_tree, canvas, random_point, max_step=1)
        if new_start_node:
            new_goal_node = extend(goal_tree, canvas, new_start_node, max_step=1)
            if new_goal_node and distance(new_start_node, new_goal_node) <= connect_radius:
                #print(f"Path found: Connecting {new_start_node} to {new_goal_node}")
                path = []
                current_node = new_start_node
                while current_node:
                    path.append(current_node)
                    current_node = current_node.parent
                path.reverse()

                current_node = new_goal_node
                while current_node:
                    path.append(current_node)
                    current_node = current_node.parent

                # print(f"Final path: {path}")
                return path
        start_tree, goal_tree = goal_tree, start_tree

    # print("No path found within maximum iterations.")
    return None

def draw_rrt_connect_path(canvas, connect_start, connect_goal):
    """Draw the RRT-Connect path on the canvas in real-time."""
    # print("Drawing RRT-Connect path...")
    current_node = connect_start
    while current_node.parent is not None:
        canvas.canvas.create_line(current_node.x * canvas.grid_size + canvas.grid_size // 2, 
                                  current_node.y * canvas.grid_size + canvas.grid_size // 2,
                                  current_node.parent.x * canvas.grid_size + canvas.grid_size // 2, 
                                  current_node.parent.y * canvas.grid_size + canvas.grid_size // 2, 
                                  fill="blue", width=2)
        canvas.canvas.update()
        current_node = current_node.parent

    current_node = connect_goal
    while current_node.parent is not None:
        canvas.canvas.create_line(current_node.x * canvas.grid_size + canvas.grid_size // 2, 
                                  current_node.y * canvas.grid_size + canvas.grid_size // 2,
                                  current_node.parent.x * canvas.grid_size + canvas.grid_size // 2, 
                                  current_node.parent.y * canvas.grid_size + canvas.grid_size // 2, 
                                  fill="blue", width=2)
        canvas.canvas.update()
        current_node = current_node.parent

    # print("Path drawing completed.")

def generate_paths(canvas):
    """Generate paths between all pairs of selected grid points using RRT-Connect."""
    if len(canvas.selected_cells) < 2:
        messagebox.showwarning("Warning", "You need at least two selected grid points to generate paths.")
        return

    print("Generating paths for all pairs of selected points...")
    points = list(canvas.selected_cells)
    
    n = len(points)
    total = n * (n - 1)

    # Metrics initialization
    total_time_taken = 0
    total_nodes_explored = 0

    # Start timing
    start_time = time.time()

    for start_point, goal_point in tqdm(permutations(points, 2), total=total, desc="Generating Paths"):
        start_cell, start_name = start_point
        goal_cell, goal_name = goal_point

        # print(f"Attempting path generation from {start_name} to {goal_name}")
        start_node = RRTNode(start_cell[0], start_cell[1])
        goal_node = RRTNode(goal_cell[0], goal_cell[1])

        path = build_rrt_connect(canvas, start_node, goal_node, max_iters=1000, connect_radius=2)
        
        if path:
            draw_rrt_connect_path(canvas, start_node, goal_node)
            # Append path to generated_paths
            canvas.generated_paths.append((path, []))  # [] is for line_ids if used in drawing
            
            # print(f"Path successfully generated from {start_name} to {goal_name}")
        # else:
            # print(f"No path found from {start_name} to {goal_name}")

        # Count nodes explored in this iteration
        # print("inside for:", total_nodes_explored)
    
    
    total_nodes_explored = sum(len(path) for path, _ in canvas.generated_paths if path)
    print(f"Total nodes explored: {total_nodes_explored}")
    # End timing
    total_time_taken = time.time() - start_time

    # Calculate operation speed
    operation_speed = total_nodes_explored / total_time_taken if total_time_taken > 0 else 0

    # Print or return metrics
    print(f"Total time taken: {total_time_taken:.2f} seconds")
    print(f"Total nodes explored: {total_nodes_explored}")
    print(f"Operation speed: {operation_speed:.2f} nodes/second")

def validate_paths(canvas):
    """Validate all generated paths and remove only the invalid ones from the canvas."""
    print("Validating all paths...")
    valid_paths = []
    for path, line_ids in canvas.generated_paths:
        start_node = path[0]
        goal_node = path[-1]
        current_node = goal_node
        valid = True

        reverse_path = []
        while current_node is not None:
            reverse_path.append((current_node.x, current_node.y))
            current_node = current_node.parent

        if reverse_path[-1] != (start_node.x, start_node.y):
            valid = False
            print(f"Invalid path from {start_node} to {goal_node}, removing it.")

        if valid:
            valid_paths.append((path, line_ids))
        else:
            for line_id in line_ids:
                canvas.canvas.delete(line_id)

    canvas.generated_paths = valid_paths
    print("Path validation completed.")

def create_grid(canvas):
    """Create a 10x10 grid on the canvas."""
    grid_size = canvas.grid_size
    width, height = 1600, 900

    for x in range(0, width, grid_size):
        for y in range(0, height, grid_size):
            rect_id = canvas.canvas.create_rectangle(x, y, x + grid_size, y + grid_size, outline="gray")
            canvas.grid_items.append(rect_id)
            canvas.canvas.tag_bind(rect_id, '<Button-1>', lambda event, x=x, y=y: select_cell(canvas, x, y))

def select_cell(canvas, x, y):
    """Highlight a cell when selected and prompt for a name."""
    cell = (x // canvas.grid_size, y // canvas.grid_size)
    if cell in canvas.selected_cells:
        canvas.selected_cells.remove(cell)
        print(f"Deselected cell at {cell}")
        canvas.canvas.create_rectangle(x, y, x + canvas.grid_size, y + canvas.grid_size, outline="gray", fill='white')
    else:
        point_name = simpledialog.askstring("Point Name", "Enter a name for this point:")
        if point_name:
            canvas.selected_cells.add((cell, point_name))
            print(f"Selected cell at {cell} with name '{point_name}'")
            canvas.canvas.create_rectangle(x, y, x + canvas.grid_size, y + canvas.grid_size, outline="gray", fill='yellow')
        else:
            messagebox.showwarning("Warning", "A name is required for each selected point.")

def disable_grid_mode(canvas):
    """Disable grid selection."""
    canvas.grid_mode = False
    for grid_item in canvas.grid_items:
        canvas.canvas.delete(grid_item)
    canvas.grid_items.clear()
        
    # Print the selected cells
    print("Selected cells:")
    for cell, name in canvas.selected_cells:
        print(f"Cell: {cell}, Name: {name}")
        
    messagebox.showinfo("Grid Mode", "Grid selection completed and saved.")

def dijkstra(canvas, start, goal):
    """Run Dijkstra's algorithm on the graph of loaded paths to find the shortest path."""
    distances = {start: 0}
    previous_nodes = {}
    queue = [(0, start)]
    visited = set()

    while queue:
        current_distance, current_node = heapq.heappop(queue)
        if current_node in visited:
            continue
        visited.add(current_node)

        # If goal is reached, reconstruct the path
        if current_node == goal:
            path = []
            while current_node in previous_nodes:
                path.append(current_node)
                current_node = previous_nodes[current_node]
            path.append(start)
            path.reverse()
            return path

        # Explore neighbors in the path graph
        for neighbor, weight in canvas.path_graph.get(current_node, []):
            if neighbor not in visited:
                distance = current_distance + weight
                if neighbor not in distances or distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(queue, (distance, neighbor))

    return None  # No path found
