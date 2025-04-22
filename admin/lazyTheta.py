import random
from tkinter import messagebox, simpledialog
from tqdm import tqdm
from itertools import permutations
import heapq
import time
import math

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.g = float('inf')  # Cost from start to this node
        self.rhs = float('inf')  # Right Hand Side (used in Lazy Theta*)
    
    def __repr__(self):
        return f"Node(x={self.x}, y={self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __lt__(self, other):
        # Define how to compare two nodes when their priorities are equal
        return (self.x, self.y) < (other.x, other.y)

def heuristic(node1, node2):
    """Calculate the Euclidean distance between two nodes."""
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

def line_of_sight(canvas, node1, node2):
    """Check if there is a direct line of sight between two nodes using Bresenham's algorithm."""
    x0, y0 = node1.x, node1.y
    x1, y1 = node2.x, node2.y
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while x0 != x1 or y0 != y1:
        if not is_free_space(canvas, Node(x0, y0)):
            return False
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return True

def is_free_space(canvas, node):
    """Check if the node is in free space using pixel-based collision detection."""
    x_pixel = node.x * canvas.grid_size
    y_pixel = node.y * canvas.grid_size
    overlapping_items = canvas.canvas.find_overlapping(x_pixel, y_pixel, x_pixel + 1, y_pixel + 1)
    free = len(overlapping_items) == 0
    return free

def get_neighbors(canvas, node):
    """Get valid neighboring nodes for a given node."""
    neighbors = []
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4-connected grid
        x = node.x + dx
        y = node.y + dy
        if 0 <= x < canvas.size_col and 0 <= y < canvas.size_row:
            neighbor = Node(x, y)
            if is_free_space(canvas, neighbor):
                neighbors.append(neighbor)
    return neighbors

def lazy_theta_star(canvas, start, goal, timeout=60, max_iterations=80000):
    """Implement the Lazy Theta* algorithm with timeout and iteration limit."""
    start_time = time.time()
    open_set = []
    heapq.heappush(open_set, (start.g + heuristic(start, goal), start))
    came_from = {}
    start.g = 0
    start.rhs = 0
    iterations = 0

    while open_set:
        if time.time() - start_time > timeout:
            print("Timeout: Pathfinding took too long.")
            return None
        if iterations > max_iterations:
            print("Max iterations reached.")
            return None

        _, current = heapq.heappop(open_set)
        iterations += 1

        if iterations % 1000 == 0:
            print(f"Iteration {iterations}: Current node = {current}")

        if current == goal:
            print(f"Path found in {iterations} iterations.")
            return reconstruct_path(came_from, current)

        for neighbor in get_neighbors(canvas, current):
            if line_of_sight(canvas, current.parent if current.parent else current, neighbor):
                # Path 2: Direct path from parent of current to neighbor
                new_g = (current.parent.g if current.parent else 0) + heuristic(current.parent if current.parent else current, neighbor)
                if new_g < neighbor.g:
                    neighbor.g = new_g
                    neighbor.parent = current.parent if current.parent else current
                    heapq.heappush(open_set, (neighbor.g + heuristic(neighbor, goal), neighbor))
            else:
                # Path 1: Path through current node
                new_g = current.g + heuristic(current, neighbor)
                if new_g < neighbor.g:
                    neighbor.g = new_g
                    neighbor.parent = current
                    heapq.heappush(open_set, (neighbor.g + heuristic(neighbor, goal), neighbor))

    return None  # No path found

def reconstruct_path(came_from, current):
    """Reconstruct the path from the goal to the start."""
    path = []
    while current:
        path.append(current)
        current = came_from.get(current, None)
    path.reverse()
    return path

def draw_path(canvas, path):
    """Draw the path on the canvas."""
    for i in range(len(path) - 1):
        x1 = path[i].x * canvas.grid_size + canvas.grid_size // 2
        y1 = path[i].y * canvas.grid_size + canvas.grid_size // 2
        x2 = path[i + 1].x * canvas.grid_size + canvas.grid_size // 2
        y2 = path[i + 1].y * canvas.grid_size + canvas.grid_size // 2
        canvas.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)
        canvas.canvas.update()

def generate_paths(canvas):
    """Generate paths between all pairs of selected grid points using Lazy Theta*."""
    if len(canvas.selected_cells) < 2:
        messagebox.showwarning("Warning", "You need at least two selected grid points to generate paths.")
        return

    print("Generating paths for all pairs of selected points...")
    points = list(canvas.selected_cells)

    # Metrics initialization
    total_time_taken = 0
    total_nodes_explored = 0

    # Start timing
    start_time = time.time()

    for start_point, goal_point in permutations(points, 2):
        start_cell, start_name = start_point
        goal_cell, goal_name = goal_point

        print(f"Attempting path generation from {start_name} to {goal_name}")
        start_node = Node(start_cell[0], start_cell[1])
        goal_node = Node(goal_cell[0], goal_cell[1])

        path = lazy_theta_star(canvas, start_node, goal_node, timeout=60, max_iterations=80000)
        
        if path:
            draw_path(canvas, path)
            # Append path to generated_paths
            canvas.generated_paths.append((path, []))  # [] is for line_ids if used in drawing
            print(f"Path successfully generated from {start_name} to {goal_name}")
        else:
            print(f"No path found from {start_name} to {goal_name}")

    # End timing
    total_time_taken = time.time() - start_time

    # Calculate operation speed
    total_nodes_explored = sum(len(path) for path, _ in canvas.generated_paths if path)
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
