import tkinter as tk
from tkinter import colorchooser
from utilities import undo, redo, choose_brush_size, save_canvas

class MapCanvas:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600, scrollregion=(0, 0, 1600, 900))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_x = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(side="bottom", fill="x")
        self.scroll_y = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side="right", fill="y")
        self.canvas.config(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # Initialize drawing settings
        self.tool = 'pen'
        self.selected_color = 'black'
        self.brush_size = 10
        self.map_brush_size = 7  # Set default brush size for map processing
        self.grid_size = 10  # Default grid size
        self.history = []
        self.future = []
        self.selected_cells = set()
        self.grid_items = []

        # Map grid
        self.size_row = 90  # Example size: 900px canvas / 10px grid size
        self.size_col = 160  # Example size: 1600px canvas / 10px grid size
        self.map_array = [[1 for _ in range(self.size_col)] for _ in range(self.size_row)]  # 1 = free space, 0 = obstacle

        # Bind drawing events
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.drawing)
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
        
        self.generated_paths = []

        # Note: Grid is not created automatically here anymore
        # You can call self.create_grid() manually later if needed

    def start_draw(self, event):
        """Start drawing with the selected tool."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # Tool logic
        if self.tool == 'pen':
            self.current_item = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill=self.selected_color, width=self.brush_size)
            self.update_map(self.start_x, self.start_y, value=1)  # Update map array with free space
        elif self.tool == 'line':
            self.current_item = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill=self.selected_color, width=self.brush_size)
        elif self.tool == 'rectangle':
            self.current_item = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=self.selected_color, width=self.brush_size)
        elif self.tool == 'eraser':
            self.current_item = self.canvas.create_line(self.start_x, self.start_y, self.start_x, self.start_y, fill="white", width=self.brush_size)
            self.update_map(self.start_x, self.start_y, value=0)  # Update map array with obstacle

        self.history.append(('create', self.current_item))

    def drawing(self, event):
        """Handle drawing motion."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        if self.tool == 'pen':  # Freehand drawing
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.selected_color, width=self.brush_size)
            self.update_map(x, y, value=1)  # Update map array with free space
            self.start_x = x
            self.start_y = y
        elif self.tool == 'line':  # Update the line coordinates
            self.canvas.coords(self.current_item, self.start_x, self.start_y, x, y)
        elif self.tool == 'rectangle':
            self.canvas.coords(self.current_item, self.start_x, self.start_y, x, y)
        elif self.tool == 'eraser':
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill="white", width=self.brush_size)
            self.update_map(x, y, value=0)  # Update map array with obstacle
            self.start_x = x
            self.start_y = y

    def stop_draw(self, event):
        """Finish drawing."""
        self.future.clear()  # Clear redo history on new action

    def set_tool(self, tool):
        """Set the active drawing tool."""
        self.tool = tool

    def choose_color(self):
        """Choose a color for drawing."""
        self.selected_color = colorchooser.askcolor(color=self.selected_color)[1]

    def choose_brush_size(self):
        """Choose brush size for drawing tools."""
        self.brush_size = choose_brush_size(self)

    def undo(self):
        """Undo the last action."""
        undo(self)

    def redo(self):
        """Redo the last undone action."""
        redo(self)

    def create_grid(self):
        """Create a grid on the canvas when called manually."""
        for x in range(0, 1600, self.grid_size):
            for y in range(0, 900, self.grid_size):
                rect_id = self.canvas.create_rectangle(x, y, x + self.grid_size, y + self.grid_size, outline="gray")
                self.grid_items.append(rect_id)
                self.canvas.tag_bind(rect_id, '<Button-1>', lambda event, x=x, y=y: self.select_cell(x, y))

    def select_cell(self, x, y):
        """Select or deselect a cell in the grid."""
        cell = (x // self.grid_size, y // self.grid_size)
        if cell in self.selected_cells:
            self.selected_cells.remove(cell)
            self.canvas.create_rectangle(x, y, x + self.grid_size, y + self.grid_size, outline="gray", fill='white')
        else:
            self.selected_cells.add(cell)
            self.canvas.create_rectangle(x, y, x + self.grid_size, y + self.grid_size, outline="gray", fill='yellow')

    def update_map(self, x, y, value):
        """Update the map array based on brush actions."""
        row = int(y // self.grid_size)
        col = int(x // self.grid_size)
        if 0 <= row < self.size_row and 0 <= col < self.size_col:
            self.map_array[row][col] = value  # 1 = free space, 0 = obstacle

    def disable_grid_mode(self):
        """Disable grid selection."""
        for grid_item in self.grid_items:
            self.canvas.delete(grid_item)
        self.grid_items.clear()
        messagebox.showinfo("Grid Mode", "Grid selection completed and saved.")