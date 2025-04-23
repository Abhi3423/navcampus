import tkinter as tk
from tkinter import ttk, messagebox
import re
import requests

class ModelFileViewer:
    def __init__(self, root, file_id, filename, content):
        self.root = root
        self.file_id = file_id  # The file record ID (used for updating the file)
        self.filename = filename
        self.content = content
        # Parse the file into nodes and paths
        self.nodes, self.paths = self.parse_model_file(content)
        self.create_window()

    def parse_model_file(self, content):
        """
        Parse the model file content into a list of nodes and a list of paths.
        Expected format:
            Start and Goal Nodes:
            Node: <name>, Location: (<x>, <y>)
            ...
            Generated Paths:
            Path: [ ... ]
            ...
        """
        nodes_section = ""
        paths_section = ""
        if "Generated Paths:" in content:
            parts = content.split("Generated Paths:")
            nodes_section = parts[0].replace("Start and Goal Nodes:", "").strip()
            paths_section = parts[1].strip()
        else:
            nodes_section = content.strip()
        nodes = []
        for line in nodes_section.splitlines():
            line = line.strip()
            if line.startswith("Node:"):
                try:
                    parts = line.split(", Location:")
                    node_name = parts[0].replace("Node:", "").strip()
                    location = parts[1].strip() if len(parts) > 1 else ""
                    # Validate that location is in the form (x, y)
                    if not (location.startswith("(") and location.endswith(")")):
                        raise ValueError("Invalid location format")
                    nodes.append((node_name, location))
                except Exception:
                    continue
        paths = []
        for line in paths_section.splitlines():
            line = line.strip()
            if line.startswith("Path:"):
                path_text = line.replace("Path:", "").strip()
                paths.append(path_text)
        return nodes, paths

    def create_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title(self.filename)
        
        # Create two frames: one for nodes and one for paths.
        nodes_frame = ttk.Frame(self.window, padding=10)
        nodes_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        paths_frame = ttk.Frame(self.window, padding=10)
        paths_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # --- Nodes Section ---
        ttk.Label(nodes_frame, text="Nodes:").pack(anchor="w")
        self.nodes_tree = ttk.Treeview(nodes_frame, columns=("Node", "Location"),
                                       show="headings", height=8)
        self.nodes_tree.heading("Node", text="Node")
        self.nodes_tree.heading("Location", text="Location")
        self.nodes_tree.column("Node", width=150)
        self.nodes_tree.column("Location", width=150)
        self.nodes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(nodes_frame, orient="vertical", command=self.nodes_tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.nodes_tree.configure(yscroll=scrollbar.set)
        self.refresh_nodes()

        # Buttons for node operations: Add, Edit, Delete.
        btn_frame = ttk.Frame(nodes_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add Node", command=self.add_node).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit Node", command=self.edit_node).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete Node", command=self.delete_node).pack(side=tk.LEFT, padx=5)
        
        # --- Paths Section ---
        ttk.Label(paths_frame, text="Generated Paths:").pack(anchor="w")
        self.paths_text = tk.Text(paths_frame, height=10)
        self.paths_text.pack(fill=tk.BOTH, expand=True)
        for path in self.paths:
            self.paths_text.insert("end", path + "\n")
        self.paths_text.configure(state="disabled")
        
        # Save Changes Button (to update the model file in the database)
        save_btn = ttk.Button(self.window, text="Save Changes", command=self.save_changes)
        save_btn.pack(pady=5)

    def refresh_nodes(self):
        """Clear and reload the nodes into the treeview."""
        for child in self.nodes_tree.get_children():
            self.nodes_tree.delete(child)
        for node, loc in self.nodes:
            self.nodes_tree.insert("", "end", values=(node, loc))

    def add_node(self):
        """Open a dialog to add a new node."""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Node")
        dialog.grab_set()

        ttk.Label(dialog, text="Node:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        node_entry = ttk.Entry(dialog)
        node_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(dialog, text="Location:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        loc_entry = ttk.Entry(dialog)
        loc_entry.grid(row=1, column=1, padx=5, pady=5)

        def submit():
            new_node = node_entry.get().strip()
            new_loc = loc_entry.get().strip()
            if not new_node:
                messagebox.showerror("Validation Error", "Node name cannot be empty.")
                return
            if not re.match(r'^\(\s*\d+\s*,\s*\d+\s*\)$', new_loc):
                messagebox.showerror("Validation Error",
                                     "Location must be in the format (x, y) with numbers.")
                return
            self.nodes.append((new_node, new_loc))
            self.refresh_nodes()
            dialog.destroy()

        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=2, column=0, padx=5, pady=15)
        ttk.Button(dialog, text="Add", command=submit).grid(row=2, column=1, padx=5, pady=15)

    def edit_node(self):
        """Edit the selected node."""
        selected = self.nodes_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a node to edit.")
            return
        current_values = self.nodes_tree.item(selected, "values")
        if not current_values:
            return
        dialog = tk.Toplevel(self.window)
        dialog.title("Edit Node")
        dialog.grab_set()

        ttk.Label(dialog, text="Node:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        node_entry = ttk.Entry(dialog)
        node_entry.grid(row=0, column=1, padx=5, pady=5)
        node_entry.insert(0, current_values[0])

        ttk.Label(dialog, text="Location:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        loc_entry = ttk.Entry(dialog)
        loc_entry.grid(row=1, column=1, padx=5, pady=5)
        loc_entry.insert(0, current_values[1])

        def submit():
            new_node = node_entry.get().strip()
            new_loc = loc_entry.get().strip()
            if not new_node:
                messagebox.showerror("Validation Error", "Node name cannot be empty.")
                return
            if not re.match(r'^\(\s*\d+\s*,\s*\d+\s*\)$', new_loc):
                messagebox.showerror("Validation Error",
                                     "Location must be in the format (x, y) with numbers.")
                return
            # Find index of selected node in the tree and update the corresponding element in self.nodes.
            index = self.nodes_tree.index(selected)
            self.nodes[index] = (new_node, new_loc)
            self.refresh_nodes()
            dialog.destroy()

        ttk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=2, column=0, padx=5, pady=15)
        ttk.Button(dialog, text="Save", command=submit).grid(row=2, column=1, padx=5, pady=15)

    def delete_node(self):
        """Delete the selected node."""
        selected = self.nodes_tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a node to delete.")
            return
        index = self.nodes_tree.index(selected)
        del self.nodes[index]
        self.refresh_nodes()

    def save_changes(self):
        """Ask for confirmation, compile new file content, and update the file record in the database."""
        if not messagebox.askyesno("Confirm Save", "Do you want to save the changes?"):
            return
        
        # Rebuild the content string with updated nodes and the original paths.
        new_content = "Start and Goal Nodes:\n"
        for node, loc in self.nodes:
            new_content += f"Node: {node}, Location: {loc}\n"
        new_content += "\nGenerated Paths:\n"
        for path in self.paths:
            new_content += f"Path: {path}\n"
        
        # Send a PUT request to update the file in the database.
        try:
            data = {"content": new_content}
            url = f"https://navcampus-e0cw.onrender.com/api/file_storage/{self.file_id}"
            resp = requests.put(url, data=data)
            if resp.status_code != 200:
                raise Exception(f"Error {resp.status_code}: {resp.text}")
            messagebox.showinfo("Success", "Changes saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")

def open_model_file_viewer(root, file_id, filename, content):
    ModelFileViewer(root, file_id, filename, content)