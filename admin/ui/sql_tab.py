import tkinter as tk
from tkinter import ttk, messagebox
import requests

class SQLTab:
    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.setup_ui()
        
    def setup_ui(self):
        input_frame = ttk.Frame(self.parent, padding=10)
        input_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        ttk.Label(input_frame, text="Enter SQL Command:").pack(anchor="w")
        self.sql_text = tk.Text(input_frame, height=10)
        self.sql_text.pack(fill=tk.BOTH, expand=True)
        
        execute_btn = ttk.Button(input_frame, text="Execute", command=self.execute_sql)
        execute_btn.pack(pady=5)
        
        output_frame = ttk.Frame(self.parent, padding=10)
        output_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        ttk.Label(output_frame, text="Output:").pack(anchor="w")
        self.output_text = tk.Text(output_frame, height=10, bg="black", fg="white")
        self.output_text.pack(fill=tk.BOTH, expand=True)
        self.output_text.configure(state="disabled")
    
    def execute_sql(self):
        command = self.sql_text.get("1.0", tk.END).strip()
        if not command:
            messagebox.showwarning("Warning", "Please enter a SQL command.")
            return
        
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        
        # Using the Flask endpoint:
        try:
            response = requests.post("https://navcampus-e0cw.onrender.com/api/execute_sql", json={"command": command})
            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    for row in data["result"]:
                        self.output_text.insert(tk.END, str(row) + "\n")
                else:
                    self.output_text.insert(tk.END, data.get("message", "Command executed successfully.") + "\n")
            else:
                error = response.json().get("error", "Unknown error")
                self.output_text.insert(tk.END, f"Error: {error}\n")
        except Exception as e:
            self.output_text.insert(tk.END, f"Exception: {str(e)}\n")
        finally:
            self.output_text.configure(state="disabled")
