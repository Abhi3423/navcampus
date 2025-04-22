from tkinter import filedialog, simpledialog, messagebox
from PIL import Image
from utilities import upload_file_to_flask

# def get_floor_name():
#     """Prompt the user to enter the floor name and return it."""
#     floor_name = simpledialog.askstring("Floor Selection", "Enter the floor number:")
#     if not floor_name:
#         print("No floor selected.")
#         return None
#     return floor_name

def load_image(canvas):
    """Load an image onto the canvas and save it with the mapbase file naming convention."""
    # floor_name = get_floor_name()
    # if not floor_name:
    #     messagebox.showerror("Error", "Floor name is required to load the image.")
    #     return  # Exit if no floor name is provided

    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp *.gif")])
    if file_path:
        # Define the save path with the correct naming convention
       # save_path = f"mapbase-{floor_name}.png"
        process_image(file_path, canvas)
       # upload_file_to_flask(save_path)

def process_image(file_path, canvas):
    """Process and load the image onto the canvas and save it to disk."""
    bg_image = Image.open(file_path).convert('L').resize((1600, 900))
    width, height = bg_image.size

    # Loop through image and create blocks based on brightness
    for x in range(0, width, canvas.map_brush_size):
        for y in range(0, height, canvas.map_brush_size):
            block = bg_image.crop((x, y, x + canvas.map_brush_size, y + canvas.map_brush_size))
            avg_pixel = sum(block.getdata()) // (canvas.map_brush_size ** 2)

            if avg_pixel < 128:  # Darker blocks
                canvas.canvas.create_rectangle(x, y, x + canvas.map_brush_size, y + canvas.map_brush_size, fill='black', outline='black')

    # Save the processed image with the specified floor naming convention
    # bg_image.save(save_path)
    # print(f"Image saved as '{save_path}'.")
