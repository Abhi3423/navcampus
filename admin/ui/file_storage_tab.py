import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import io
import os
import re
from PIL import Image, ImageTk
from ui.model_file_viewer import open_model_file_viewer


class FileStorageTab:
    def __init__(self, parent, root, landmarks_tab):
        self.parent = parent
        self.root = root
        self.landmarks_tab = landmarks_tab  # Reference to obtain landmark names
        self.files_data = []
        self.view_mode = tk.StringVar(value="Default")
        self.setup_ui()
        self.refresh_files()
    
    def setup_ui(self):
        # Search bar for files
        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, pady=5)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_files).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Clear", command=self.clear_search_files).pack(side=tk.LEFT, padx=(5,0))
        
        # View Mode selector
        view_mode_frame = ttk.Frame(self.parent)
        view_mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(view_mode_frame, text="View Mode:").pack(side=tk.LEFT, padx=5)
        view_mode_combo = ttk.Combobox(view_mode_frame, textvariable=self.view_mode,
                                       values=["Default", "Hierarchical"], state="readonly", width=15)
        view_mode_combo.pack(side=tk.LEFT)
        view_mode_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_files())
        
        # Frame to hold the tree widget
        self.tree_frame = ttk.Frame(self.parent)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # CRUD and View Button Frame
        btn_frame = ttk.Frame(self.parent)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Add File", command=self.add_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit File", command=self.edit_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete File", command=self.delete_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View", command=self.view_file).pack(side=tk.LEFT, padx=5)
    
    def create_tree_widget(self):
        """Create a new tree widget inside self.tree_frame based on the view mode."""
        # Destroy previous tree widget if it exists
        if hasattr(self, "tree"):
            self.tree.destroy()
        # Clear any children in tree_frame
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        
        if self.view_mode.get() == "Default":
            # Flat view: Treeview with columns and headings.
            self.tree = ttk.Treeview(self.tree_frame,
                                     columns=("ID", "Filename", "Type", "Timestamp", "Landmark"),
                                     show="headings")
            for col in ("ID", "Filename", "Type", "Timestamp", "Landmark"):
                self.tree.heading(col, text=col)
                if col in ("ID", "Type"):
                    self.tree.column(col, width=60, anchor="center")
                elif col == "Timestamp":
                    self.tree.column(col, width=160, anchor="center")
                else:
                    self.tree.column(col, width=150, anchor="center")
        else:
            # Hierarchical view: Treeview without preset columns.
            self.tree = ttk.Treeview(self.tree_frame, show="tree")
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
        self.tree.bind("<Double-1>", lambda e: self.view_file())
    
    def build_tree_default(self, file_records):
        """Build a flat table view for file records."""
        self.tree.delete(*self.tree.get_children())
        for f in file_records:
            self.tree.insert("", "end", iid=str(f["id"]),
                             values=(f["id"], f["filename"], f["file_type"],
                                     f["timestamp"], f["landmark"]))
    
    def build_tree_hierarchical(self, file_records):
        """Build a hierarchical tree view grouping files by landmark, floor, and file type.
        All nodes are collapsed by default."""
        self.tree.delete(*self.tree.get_children())
        grouping = {}
        for f in file_records:
            landmark = f.get("landmark") or "Unknown"
            filename = f.get("filename", "")
            base, ext = os.path.splitext(filename)
            ext = ext.lstrip('.').lower()
            m = re.search(r'-(\d+)$', base)
            if m:
                floor = m.group(1)
                floor_group = f"Floor {floor}"
            else:
                floor_group = base
            grouping.setdefault(landmark, {}).setdefault(floor_group, {}).setdefault(ext, []).append(f)
        
        for landmark in sorted(grouping.keys()):
            landmark_node = self.tree.insert("", "end", text=landmark, open=False)
            for floor_group in sorted(grouping[landmark].keys()):
                floor_node = self.tree.insert(landmark_node, "end", text=floor_group, open=False)
                for ext in sorted(grouping[landmark][floor_group].keys()):
                    ext_node = self.tree.insert(floor_node, "end", text=ext, open=False)
                    for file_rec in grouping[landmark][floor_group][ext]:
                        display_text = f"{file_rec.get('filename', '')} ({file_rec.get('timestamp', '')})"
                        self.tree.insert(ext_node, "end", text=display_text, values=(file_rec.get("id"),))
    
    def refresh_files(self):
        try:
            resp = requests.get("https://navcampus-e0cw.onrender.com/api/file_storage")
            resp.raise_for_status()
            data = resp.json()  # List of file records
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch file records: {e}")
            return
        self.files_data = data
        
        # Recreate the tree widget according to the selected view mode.
        self.create_tree_widget()
        
        if self.view_mode.get() == "Default":
            self.build_tree_default(self.files_data)
        else:
            self.build_tree_hierarchical(self.files_data)
    
    def search_files(self):
        query = self.search_var.get().strip().lower()
        if query == "":
            self.refresh_files()
            return
        
        filtered = []
        for f in self.files_data:
            filename = f.get("filename", "").lower()
            landmark = f.get("landmark", "").lower()
            _, ext = os.path.splitext(filename)
            ext = ext.lstrip('.').lower()
            if query in filename or query in landmark or query in ext:
                filtered.append(f)
        self.create_tree_widget()
        if self.view_mode.get() == "Default":
            self.build_tree_default(filtered)
        else:
            self.build_tree_hierarchical(filtered)
    
    def clear_search_files(self):
        self.search_var.set("")
        self.refresh_files()
    
    def add_file(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add File")
        dialog.grab_set()
        
        new_file_path = {"path": None}
        ttk.Label(dialog, text="File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        file_label = ttk.Label(dialog, text="No file selected")
        file_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        def choose_file():
            path = filedialog.askopenfilename()
            if path:
                new_file_path["path"] = path
                file_label.config(text=os.path.basename(path))
        ttk.Button(dialog, text="Browse...", command=choose_file).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(dialog, text="Landmark:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        landmark_names = [lm["landmark_name"] for lm in self.landmarks_tab.landmarks_data]
        landmark_combo = ttk.Combobox(dialog, values=landmark_names, state="readonly")
        landmark_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        if landmark_names:
            landmark_combo.current(0)
        
        def submit_upload():
            if not new_file_path["path"]:
                messagebox.showerror("Error", "Please select a file to upload.")
                return
            sel_landmark = landmark_combo.get().strip()
            if not sel_landmark:
                messagebox.showerror("Error", "Please select a landmark.")
                return
            try:
                files = {'file': open(new_file_path["path"], 'rb')}
                data = {'landmark': sel_landmark}
                resp = requests.post("https://navcampus-e0cw.onrender.com/api/file_storage", files=files, data=data)
                if resp.status_code not in (200, 201):
                    raise Exception(f"Error {resp.status_code}: {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to upload file: {e}")
                return
            dialog.destroy()
            self.refresh_files()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=2, column=0, padx=5, pady=15)
        ttk.Button(dialog, text="Upload", command=submit_upload).grid(row=2, column=1, padx=5, pady=15)
    
    def get_selected_file_id(self):
        """Return the file ID for the selected leaf node (if any)."""
        selected = self.tree.focus()
        if not selected:
            return None
        values = self.tree.item(selected, "values")
        if values:
            return values[0]
        return None
    
    def edit_file(self):
        file_id = self.get_selected_file_id()
        if not file_id:
            messagebox.showwarning("No Selection", "Please select a file record to edit (leaf node).")
            return
        file_rec = next((f for f in self.files_data if str(f.get("id")) == str(file_id)), None)
        if file_rec is None:
            messagebox.showerror("Error", "Could not find the selected file record.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit File Record")
        dialog.grab_set()
        
        ttk.Label(dialog, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(dialog, text=str(file_rec.get("id"))).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(dialog, text="Filename:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        filename_label = ttk.Label(dialog, text=file_rec.get("filename", ""))
        filename_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        new_file_path = {"path": None}
        def choose_new_file():
            path = filedialog.askopenfilename()
            if path:
                new_file_path["path"] = path
                filename_label.config(text=os.path.basename(path))
        ttk.Button(dialog, text="Replace File...", command=choose_new_file).grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Label(dialog, text="Landmark:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        landmark_names = [lm["landmark_name"] for lm in self.landmarks_tab.landmarks_data]
        landmark_combo = ttk.Combobox(dialog, values=landmark_names, state="readonly")
        landmark_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        if file_rec.get("landmark") in landmark_names:
            landmark_combo.set(file_rec.get("landmark"))
        elif landmark_names:
            landmark_combo.current(0)
        
        def submit_edit_file():
            sel_landmark = landmark_combo.get().strip()
            try:
                if new_file_path["path"]:
                    files = {'file': open(new_file_path["path"], 'rb')}
                    data = {'landmark': sel_landmark}
                    resp = requests.put(f"https://navcampus-e0cw.onrender.com/api/file_storage/{file_rec.get('id')}", files=files, data=data)
                else:
                    data = {'landmark': sel_landmark}
                    resp = requests.put(f"https://navcampus-e0cw.onrender.com/api/file_storage/{file_rec.get('id')}", data=data)
                if resp.status_code != 200:
                    raise Exception(f"Error {resp.status_code}: {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update file record: {e}")
                return
            dialog.destroy()
            self.refresh_files()
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=3, column=0, padx=5, pady=15)
        ttk.Button(dialog, text="Save", command=submit_edit_file).grid(row=3, column=1, padx=5, pady=15)
    
    def delete_file(self):
        file_id = self.get_selected_file_id()
        if not file_id:
            messagebox.showwarning("No Selection", "Please select a file record to delete (leaf node).")
            return
        fname = ""
        file_rec = next((f for f in self.files_data if str(f.get("id")) == str(file_id)), None)
        if file_rec:
            fname = file_rec.get("filename", "")
        if not messagebox.askyesno("Confirm Delete", f"Delete file '{fname}'?"):
            return
        try:
            resp = requests.delete(f"https://navcampus-e0cw.onrender.com/api/file_storage/{file_id}")
            if resp.status_code != 200:
                raise Exception(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file record: {e}")
            return
        self.refresh_files()
    
    def view_file(self):
        file_id = self.get_selected_file_id()
        if not file_id:
            return
        try:
            resp = requests.get(f"https://navcampus-e0cw.onrender.com/api/file/{file_id}")
            if resp.status_code != 200:
                raise Exception(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve file: {e}")
            return
        file_rec = next((f for f in self.files_data if str(f.get("id")) == str(file_id)), None)
        file_type = file_rec.get("file_type") if file_rec else None
        filename = file_rec.get("filename", "File") if file_rec else "File"
        if file_type == "image":
            try:
                image = Image.open(io.BytesIO(resp.content))
            except Exception:
                messagebox.showerror("Error", "Unable to open image data.")
                return
            img_window = tk.Toplevel(self.root)
            img_window.title(filename)
            img = ImageTk.PhotoImage(image)
            lbl = ttk.Label(img_window, image=img)
            lbl.image = img  # Keep a reference
            lbl.pack()
        elif file_type == "text":
            text_data = resp.content.decode('utf-8', errors='ignore')
            # Check if this is a model file (with nodes and generated paths)
            if "Start and Goal Nodes:" in text_data and "Generated Paths:" in text_data:
                file_id = file_rec.get("id")
                from ui.model_file_viewer import open_model_file_viewer
                open_model_file_viewer(self.root, file_id, filename, text_data)
            else:
                text_window = tk.Toplevel(self.root)
                text_window.title(filename)
                text_area = tk.Text(text_window, wrap="word")
                text_area.insert("1.0", text_data)
                text_area.configure(state="disabled")
                text_area.pack(fill=tk.BOTH, expand=True)

        else:
            save_path = filedialog.asksaveasfilename(
                title="Save File As", initialfile=filename)
            if save_path:
                try:
                    with open(save_path, 'wb') as f:
                        f.write(resp.content)
                    messagebox.showinfo("Saved", f"File saved to {save_path}")
                except Exception as ex:
                    messagebox.showerror("Error", f"Failed to save file: {ex}")