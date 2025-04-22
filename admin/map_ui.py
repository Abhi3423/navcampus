import tkinter as tk
from tkinter import ttk
from image_processor import load_image
from utilities import clear_canvas, save_canvas, save_path, save_full_model, load_model, run_dijkstras_on_all_pairs, load_nodes  # Import save_path function
from canvas_tools import MapCanvas
from path_finding import create_grid, generate_paths, validate_paths, disable_grid_mode

def setup_ui(root):
    root.title("Map Maker with Editable Background")
    root.geometry("1600x900")
    
    # Create the canvas and associated functionality
    map_canvas = MapCanvas(root)
    
    def toggle_menu():
        if control_frame.winfo_ismapped():
            control_frame.pack_forget()
        else:
            control_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
    
    menu_button = ttk.Button(root, text="☰", command=toggle_menu, width=3)
    menu_button.pack(side=tk.TOP, anchor="ne", padx=10, pady=5)

    control_frame = ttk.Frame(root, padding=10)
    
    def create_section(title):
        label = ttk.Label(control_frame, text=title, font=("Arial", 10, "bold"), anchor="w")
        label.pack(fill=tk.X, pady=(6, 5))
    
    def create_button(text, command, icon=None):
        frame = ttk.Frame(control_frame)
        frame.pack(fill=tk.X, pady=2)
        button_text = f"{icon} {text}" if icon else text
        button = ttk.Button(frame, text=button_text, command=command)
        button.pack(fill=tk.X)

    # Load Section
    create_section("Load Section")
    create_button("Load Map Model (1)", lambda: load_image(map_canvas), "📂")
    create_button("Load Model", lambda: load_model(map_canvas), "📄")
    create_button("Load Nodes", lambda: load_nodes(map_canvas), "🔗")
    
    # Tools Section
    create_section("Tools Section (2)")
    create_button("Pen", lambda: map_canvas.set_tool('pen'), "✏️")
    create_button("Line", lambda: map_canvas.set_tool('line'), "📏")
    create_button("Rectangle", lambda: map_canvas.set_tool('rectangle'), "⬛")
    create_button("Eraser", lambda: map_canvas.set_tool('eraser'), "🧽")
    create_button("Choose Color", lambda: map_canvas.choose_color(), "🎨")
    create_button("Brush Size", lambda: map_canvas.choose_brush_size(), "🖌️")
    create_button("Undo", lambda: map_canvas.undo(), "↩️")
    create_button("Redo", lambda: map_canvas.redo(), "↪️")
    create_button("Clear", lambda: clear_canvas(map_canvas), "🗑️")
    
    create_section("Mapbase Section")
    create_button("Save Mapbase (3)", lambda: save_canvas(map_canvas), "💾")
    
    # Create Section
    create_section("Create Section")
    create_button("Create Grid (4)", lambda: create_grid(map_canvas), "🗺️")
    create_button("Finish Grid Selection (5)", lambda: disable_grid_mode(map_canvas), "✅")
    create_button("RRT Generate Path (6)", lambda: generate_paths(map_canvas), "🚀")
    create_button("Save Full Model (7)", lambda: save_full_model(map_canvas), "📦")
    
    # Redundant Section
    create_section("Redundant Section")
    create_button("Run Dijkstra's", lambda: run_dijkstras_on_all_pairs(map_canvas), "🔍")
    create_button("Save Path", lambda: save_path(map_canvas), "💾")
    create_button("Validate Path", lambda: validate_paths(map_canvas), "✔️")