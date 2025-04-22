import tkinter as tk
from tkinter import ttk
from ui.landmarks_tab import LandmarksTab
from ui.file_storage_tab import FileStorageTab
from ui.sql_tab import SQLTab   # Import your new SQL tab module

def setup_admin_ui(root):
    root.title("Database Manager")
    root.geometry("1600x900")

    # Create a Notebook for tabbed interface
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Create tabs for Landmarks, File Storage, and SQL
    landmarks_frame = ttk.Frame(notebook, padding=10)
    files_frame = ttk.Frame(notebook, padding=10)
    sql_frame = ttk.Frame(notebook, padding=10)
    
    notebook.add(landmarks_frame, text="Landmarks")
    notebook.add(files_frame, text="File Storage")
    notebook.add(sql_frame, text="SQL")
    
    # Initialize each tab
    landmarks_tab = LandmarksTab(landmarks_frame, root)
    FileStorageTab(files_frame, root, landmarks_tab)
    SQLTab(sql_frame, root)
