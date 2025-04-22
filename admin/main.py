import tkinter as tk
from tkinter import ttk
from map_ui import setup_ui               # Existing map canvas UI setup
from admin_ui import setup_admin_ui   # New admin GUI setup

def main():
    # Initialize main application window
    root = tk.Tk()
    root.title("Choose Mode")
    root.geometry("300x150")

    # Create a simple selection UI on the root window
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill=tk.BOTH, expand=True)

    label = ttk.Label(frame, text="Select Mode:", font=("Arial", 12))
    label.pack(pady=10)

    def start_map_mode():
        """Switch to Map Canvas mode."""
        frame.destroy()              # Remove mode selection UI
        setup_ui(root)               # Launch the existing map canvas interface

    def start_db_mode():
        """Switch to Database Manager mode."""
        frame.destroy()
        setup_admin_ui(root)         # Launch the new admin database manager interface

    # Two buttons for selecting the mode
    map_btn = ttk.Button(frame, text="Map Canvas", command=start_map_mode)
    db_btn = ttk.Button(frame, text="Database Manager", command=start_db_mode)
    map_btn.pack(pady=5)
    db_btn.pack(pady=5)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()
