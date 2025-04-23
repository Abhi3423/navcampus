import tkinter as tk
from tkinter import ttk, messagebox
import requests

class LandmarksTab:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.landmarks_data = []
        self.setup_ui()
        self.refresh_landmarks()
    
    def setup_ui(self):
        # Search bar
        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self.parent)
        search_frame.pack(fill=tk.X, pady=5)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Search", command=self.search_landmarks).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="Clear", command=self.clear_search_landmarks).pack(side=tk.LEFT, padx=(5,0))
        
        # Treeview for landmarks
        cols = ("ID", "Name", "Latitude", "Longitude")
        self.tree = ttk.Treeview(self.parent, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col=="ID" else 150, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars for Treeview
        scroll_y = ttk.Scrollbar(self.parent, orient="vertical", command=self.tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(self.parent, orient="horizontal", command=self.tree.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
        
        # CRUD Button Frame
        btn_frame = ttk.Frame(self.parent)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Add", command=self.add_landmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.edit_landmark).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_landmark).pack(side=tk.LEFT, padx=5)
    
    def refresh_landmarks(self):
        try:
            resp = requests.get("https://navcampus-e0cw.onrender.com/api/landmarks")
            resp.raise_for_status()
            data = resp.json()  # List of landmarks
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch landmarks: {e}")
            return
        self.landmarks_data = data
        self.tree.delete(*self.tree.get_children())
        for lm in self.landmarks_data:
            self.tree.insert("", "end", iid=lm["id"],
                             values=(lm["id"], lm["landmark_name"], lm["latitude"], lm["longitude"]))
    
    def clear_search_landmarks(self):
        self.search_var.set("")
        self.refresh_landmarks()
    
    def search_landmarks(self):
        query = self.search_var.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        results = self.landmarks_data if query == "" else [
            lm for lm in self.landmarks_data
            if query in str(lm["id"]).lower() or query in lm["landmark_name"].lower()
        ]
        for lm in results:
            self.tree.insert("", "end", iid=lm["id"],
                             values=(lm["id"], lm["landmark_name"], lm["latitude"], lm["longitude"]))
    
    def add_landmark(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Landmark")
        dialog.grab_set()

        ttk.Label(dialog, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        id_entry = ttk.Entry(dialog)
        id_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        name_entry = ttk.Entry(dialog)
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Latitude:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        lat_entry = ttk.Entry(dialog)
        lat_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Longitude:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        lon_entry = ttk.Entry(dialog)
        lon_entry.grid(row=3, column=1, padx=5, pady=5)

        def submit_new():
            lid = id_entry.get().strip()
            lname = name_entry.get().strip()
            lat_str = lat_entry.get().strip()
            lon_str = lon_entry.get().strip()
            if not lid or not lname or not lat_str or not lon_str:
                messagebox.showerror("Validation Error", "All fields are required.")
                return
            try:
                lat_val = float(lat_str)
                lon_val = float(lon_str)
            except ValueError:
                messagebox.showerror("Validation Error", "Latitude and Longitude must be numeric.")
                return
            try:
                resp = requests.post("https://navcampus-e0cw.onrender.com/api/landmarks", json={
                    "id": lid, "landmark_name": lname, "latitude": lat_val, "longitude": lon_val
                })
                if resp.status_code not in (200, 201):
                    raise Exception(f"Error {resp.status_code}: {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add landmark: {e}")
                return
            dialog.destroy()
            self.refresh_landmarks()

        def cancel():
            dialog.destroy()

        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=4, column=0, padx=5, pady=15)
        ttk.Button(dialog, text="Add", command=submit_new).grid(row=4, column=1, padx=5, pady=15)
    
    def edit_landmark(self):
        selected_id = self.tree.focus()
        if not selected_id:
            messagebox.showwarning("No Selection", "Please select a landmark to edit.")
            return
        lm = next((item for item in self.landmarks_data if str(item["id"]) == str(selected_id)), None)
        if lm is None:
            messagebox.showerror("Error", "Could not find the selected landmark data.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Landmark")
        dialog.grab_set()

        ttk.Label(dialog, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(dialog, text=str(lm["id"])).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(dialog, text="Name:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, lm["landmark_name"])
        name_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Latitude:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        lat_entry = ttk.Entry(dialog)
        lat_entry.insert(0, str(lm["latitude"]))
        lat_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(dialog, text="Longitude:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        lon_entry = ttk.Entry(dialog)
        lon_entry.insert(0, str(lm["longitude"]))
        lon_entry.grid(row=3, column=1, padx=5, pady=5)

        def submit_edit():
            lname = name_entry.get().strip()
            lat_str = lat_entry.get().strip()
            lon_str = lon_entry.get().strip()
            if not lname or not lat_str or not lon_str:
                messagebox.showerror("Validation Error", "Name, Latitude, and Longitude are required.")
                return
            try:
                lat_val = float(lat_str)
                lon_val = float(lon_str)
            except ValueError:
                messagebox.showerror("Validation Error", "Latitude and Longitude must be numeric.")
                return
            try:
                resp = requests.put(f"https://navcampus-e0cw.onrender.com/api/landmarks/{lm['id']}", json={
                    "landmark_name": lname, "latitude": lat_val, "longitude": lon_val
                })
                if resp.status_code != 200:
                    raise Exception(f"Error {resp.status_code}: {resp.text}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update landmark: {e}")
                return
            dialog.destroy()
            self.refresh_landmarks()

        def cancel():
            dialog.destroy()

        ttk.Button(dialog, text="Cancel", command=cancel).grid(row=4, column=0, padx=5, pady=15)
        ttk.Button(dialog, text="Save", command=submit_edit).grid(row=4, column=1, padx=5, pady=15)
    
    def delete_landmark(self):
        selected_id = self.tree.focus()
        if not selected_id:
            messagebox.showwarning("No Selection", "Please select a landmark to delete.")
            return
        name = self.tree.item(selected_id, 'values')[1]
        if not messagebox.askyesno("Confirm Delete", f"Delete landmark '{name}'?"):
            return
        try:
            resp = requests.delete(f"https://navcampus-e0cw.onrender.com/api/landmarks/{selected_id}")
            if resp.status_code != 200:
                raise Exception(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete landmark: {e}")
            return
        self.refresh_landmarks()