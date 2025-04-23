import io
import re
import time
import traceback
from collections import defaultdict
from itertools import permutations

import tkinter as tk
from tkinter import ttk

import requests
from PIL import Image, ImageOps
from tkinter import filedialog, messagebox, simpledialog

from path_finding import dijkstra

def get_floor_name():
    """Prompt the user to enter the floor name and return it."""
    floor_name = simpledialog.askstring("Floor Selection", "Enter the floor number:")
    if not floor_name:
        print("No floor selected.")
        return None
    return floor_name

def undo(canvas):
    """Undo the last action."""
    if canvas.history:
        action, item = canvas.history.pop()
        if action == 'create':
            canvas.canvas.delete(item)
            canvas.future.append((action, item))

def redo(canvas):
    """Redo the last undone action."""
    if canvas.future:
        action, item = canvas.future.pop()
        if action == 'create':
            canvas.canvas.create_line(canvas.canvas.coords(item))

def clear_canvas(canvas):
    """Clear the canvas."""
    canvas.canvas.delete('all')
    canvas.history.clear()
    canvas.future.clear()

def save_canvas(canvas):
    """Save the entire canvas as an image, including the parts not currently visible."""
    landmarks = fetch_landmark_names()
    selected_landmark = prompt_landmark_selection(landmarks)
    if not selected_landmark:
        return  # Exit if no landmark is selected

    floor_name = get_floor_name()
    if not floor_name:
        return  # Exit if no floor name is provided

    save_path = filedialog.asksaveasfilename(defaultextension=".png", initialfile=f"mapbase-{floor_name}.png", filetypes=[("PNG files", "*.png")])
    if save_path:
        # Save the current scroll position
        x_scroll = canvas.canvas.xview()
        y_scroll = canvas.canvas.yview()

        # Scroll to the top-left corner
        canvas.canvas.xview_moveto(0)
        canvas.canvas.yview_moveto(0)

        # Get the full canvas size
        canvas.canvas.update_idletasks()
        bbox = canvas.canvas.bbox('all')
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        # Generate PostScript file from the full canvas
        ps = canvas.canvas.postscript(colormode='color', x=bbox[0], y=bbox[1], width=width, height=height)
        
        # Convert PostScript to Image
        img = Image.open(io.BytesIO(ps.encode('utf-8')))
        img = img.convert('RGB')
        img = ImageOps.fit(img, (width, height), Image.LANCZOS)
        img.save(save_path)
        time.sleep(2)
        upload_file_to_flask(save_path, selected_landmark)

        # Restore the scroll position
        canvas.canvas.xview_moveto(x_scroll[0])
        canvas.canvas.yview_moveto(y_scroll[0])

        messagebox.showinfo("Saved", f"Your canvas has been saved as {save_path}")

def choose_brush_size(canvas):
    """Choose a brush size."""
    return simpledialog.askinteger("Brush size", "Enter brush size:", minvalue=1, maxvalue=100)

def save_path(canvas):
    """Save the generated paths to a file and print the output in the terminal."""
    floor_name = get_floor_name()
    if not floor_name:
        return  # Exit if no floor name is provided

    save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"model-{floor_name}.txt", filetypes=[("Text files", "*.txt")])
    if save_path:
        if not canvas.generated_paths:
            print("No paths to save.")
            messagebox.showwarning("No Paths", "There are no generated paths to save.")
            return
        
        with open(save_path, 'w') as file:
            for path, _ in canvas.generated_paths:
                if path:
                    path_coords = [(node.x, node.y) for node in path]
                    file.write(f"{path_coords}\n")
                    print(f"Saved path: {path_coords}")  # Confirm each path in the terminal
                else:
                    print("Encountered an empty path, skipping.")
                    
        upload_file_to_flask(save_path)
                    
        messagebox.showinfo("Saved", f"Paths have been saved to {save_path}")
    else:
        print("Save operation was cancelled.")
        
def save_full_model(canvas):
    """Saves the start and goal nodes, along with the generated paths, without the base map array."""
    landmarks = fetch_landmark_names()
    selected_landmark = prompt_landmark_selection(landmarks)
    if not selected_landmark:
        return  # Exit if no landmark is selected

    floor_name = get_floor_name()
    if not floor_name:
        return  # Exit if no floor name is provided

    save_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"model-{floor_name}.txt", filetypes=[("Text files", "*.txt")])
    if save_path:
        with open(save_path, 'w') as file:
            # Saves designated names and locations of start and goal nodes
            file.write("Start and Goal Nodes:\n")
            for cell, name in canvas.selected_cells:
                file.write(f"Node: {name}, Location: {cell}\n")

            # Saves the generated paths as sequences of coordinates
            file.write("\nGenerated Paths:\n")
            for path, _ in canvas.generated_paths:
                if path:
                    path_coords = [(node.x, node.y) for node in path]
                    file.write(f"Path: {path_coords}\n")
        
        upload_file_to_flask(save_path, selected_landmark)

        messagebox.showinfo("Saved", f"Full model has been saved to {save_path}")

def load_model(canvas):
    """Load a saved model file that contains only start/goal nodes and generated paths without clearing the base map."""
    load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not load_path:
        print("Load operation was cancelled.")
        return

    try:
        # Clear only selected nodes and generated paths
        canvas.selected_cells.clear()
        canvas.generated_paths.clear()
        canvas.path_graph = defaultdict(list)  # Create an adjacency list to represent the paths

        with open(load_path, 'r') as file:
            lines = file.readlines()

        # Initialize section state
        section = None

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Identify sections based on header lines
            if line == "Start and Goal Nodes:":
                section = "nodes"
                continue
            elif line == "Generated Paths:":
                section = "paths"
                continue

            # Process sections
            if section == "nodes":
                match = re.match(r"Node: (.*), Location: \((\d+), (\d+)\)", line)
                if match:
                    name = match.group(1)
                    x, y = int(match.group(2)), int(match.group(3))
                    location = (x, y)
                    canvas.selected_cells.add((location, name))

                    # Visualize node on canvas
                    x_pixel, y_pixel = location[0] * canvas.grid_size, location[1] * canvas.grid_size
                    canvas.canvas.create_rectangle(x_pixel, y_pixel, x_pixel + canvas.grid_size, y_pixel + canvas.grid_size, outline="gray", fill='yellow')

            elif section == "paths":
                path_coords = eval(line.split(": ")[1])
                for i in range(len(path_coords) - 1):
                    start = path_coords[i]
                    end = path_coords[i + 1]
                    canvas.path_graph[start].append((end, 1))  # Distance of 1 between connected nodes
                    canvas.path_graph[end].append((start, 1))  # Undirected graph

                # Visualize path on canvas
                for i in range(len(path_coords) - 1):
                    x1, y1 = path_coords[i][0] * canvas.grid_size + canvas.grid_size // 2, path_coords[i][1] * canvas.grid_size + canvas.grid_size // 2
                    x2, y2 = path_coords[i + 1][0] * canvas.grid_size + canvas.grid_size // 2, path_coords[i + 1][1] * canvas.grid_size + canvas.grid_size // 2
                    canvas.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        messagebox.showinfo("Loaded", f"Model loaded from {load_path}")

    except Exception as e:
        print("An error occurred while loading the model.")
        traceback.print_exc()
        messagebox.showerror("Load Error", "The file could not be loaded due to an unexpected format or content error.")
        
def load_nodes(canvas):
    load_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if not load_path:
        print("Load operation was cancelled.")
        return
    
    try:
        # Clear only selected nodes and generated paths
        canvas.selected_cells.clear()
        canvas.generated_paths.clear()
        canvas.path_graph = defaultdict(list)  # Create an adjacency list to represent the paths

        with open(load_path, 'r') as file:
            lines = file.readlines()

        # Initialize section state
        section = None

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Identify sections based on header lines
            if line == "Start and Goal Nodes:":
                section = "nodes"
                continue
            elif line == "Generated Paths:":
                section = "paths"
                continue

            # Process sections
            if section == "nodes":
                match = re.match(r"Node: (.*), Location: \((\d+), (\d+)\)", line)
                if match:
                    name = match.group(1)
                    x, y = int(match.group(2)), int(match.group(3))
                    location = (x, y)
                    canvas.selected_cells.add((location, name))

                    # Visualize node on canvas
                    x_pixel, y_pixel = location[0] * canvas.grid_size, location[1] * canvas.grid_size
                    canvas.canvas.create_rectangle(x_pixel, y_pixel, x_pixel + canvas.grid_size, y_pixel + canvas.grid_size, outline="gray", fill='yellow')

        messagebox.showinfo("Loaded", f"Nodes loaded from {load_path}")

    except Exception as e:
        print("An error occurred while loading the model.")
        traceback.print_exc()
        messagebox.showerror("Load Error", "The file could not be loaded due to an unexpected format or content error.")

def run_dijkstras_on_all_pairs(canvas):
    """Run Dijkstra's algorithm on all permutations of nodes using only the loaded paths."""
    if len(canvas.selected_cells) < 2:
        messagebox.showwarning("Warning", "At least two nodes are required to run Dijkstra's algorithm.")
        return

    shortest_paths = {}
    nodes = list(canvas.selected_cells)
    for (start_cell, start_name), (goal_cell, goal_name) in permutations(nodes, 2):
        start_node = (start_cell[0], start_cell[1])
        goal_node = (goal_cell[0], goal_cell[1])

        path = dijkstra(canvas, start_node, goal_node)
        if path:
            path_length = len(path)
            # Store only the shortest path for each start-goal pair
            if (start_node, goal_node) not in shortest_paths or path_length < len(shortest_paths[(start_node, goal_node)]):
                shortest_paths[(start_node, goal_node)] = path

    # Clear existing paths on canvas and draw only the shortest paths
    canvas.generated_paths.clear()
    canvas.canvas.delete('path_line')
    for path in shortest_paths.values():
        for i in range(len(path) - 1):
            x1, y1 = path[i][0] * canvas.grid_size + canvas.grid_size // 2, path[i][1] * canvas.grid_size + canvas.grid_size // 2
            x2, y2 = path[i + 1][0] * canvas.grid_size + canvas.grid_size // 2, path[i + 1][1] * canvas.grid_size + canvas.grid_size // 2
            line_id = canvas.canvas.create_line(x1, y1, x2, y2, fill="green", width=2, tags="path_line")
        canvas.generated_paths.append((path, []))

    messagebox.showinfo("Dijkstra's Complete", "Dijkstra's algorithm completed for all node pairs.")
    
def upload_file_to_flask(file_path, landmark, url="https://navcampus-e0cw.onrender.com/api/update_file"):
    """Uploads a file to the Flask backend."""
    try:
        with open(file_path, 'rb') as file:
            response = requests.post(url, files={'file': file}, data={'landmark': landmark})
            if response.status_code == 200:
                print(f"File '{file_path}' uploaded successfully to Flask.")
            else:
                print(f"Failed to upload '{file_path}':", response.json())
    except Exception as e:
        print("Error uploading file:", e)
        
def fetch_landmark_names():
    """Fetch landmark names from the server."""
    try:
        response = requests.get("https://navcampus-e0cw.onrender.com/api/get_landmarks")
        if response.status_code == 200:
            return response.json().get("landmarks", [])
        else:
            print("Failed to fetch landmarks:", response.json())
            return []
    except Exception as e:
        print("Error fetching landmarks:", e)
        return []
    
def prompt_landmark_selection(landmarks):
    """Prompt the user to select a landmark using a dropdown menu."""
    if not landmarks:
        messagebox.showwarning("No Landmarks", "No landmarks available to select.")
        return None

    # Create a new top-level window
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Create a new window for the selection
    selection_window = tk.Toplevel(root)
    selection_window.title("Select Landmark")

    # Label for the combobox
    label = tk.Label(selection_window, text="Select a landmark:")
    label.pack(pady=10)

    # Create a combobox with the list of landmarks
    combobox = ttk.Combobox(selection_window, values=landmarks, state="readonly")
    combobox.pack(pady=10)
    combobox.set(landmarks[0])  # Set the default selection to the first landmark

    # Variable to store the selected landmark
    selected_landmark = tk.StringVar()

    def on_select():
        """Callback function when a selection is made."""
        selected_landmark.set(combobox.get())
        selection_window.destroy()  # Close the selection window

    # Button to confirm the selection
    select_button = tk.Button(selection_window, text="Select", command=on_select)
    select_button.pack(pady=10)

    # Wait for the window to close
    selection_window.wait_window()

    # Return the selected landmark
    return selected_landmark.get() if selected_landmark.get() else None

