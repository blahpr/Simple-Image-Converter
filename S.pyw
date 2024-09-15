import os
import sys
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, PhotoImage, BooleanVar, Toplevel

def resource_path(relative_path):
    try:
        base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, 'images', relative_path)

def convert_image(input_image_path, output_image_path, format, size=None, transparency=False):
    try:
        img = Image.open(input_image_path)

        if format.upper() == 'JPG':
            img = img.convert('RGB')
        else:
            img = img.convert('RGBA') if img.mode != 'RGBA' else img
        
        if size:
            img = img.resize(size, Image.LANCZOS)

        save_params = {}
        if format.upper() == 'JPG':
            save_params = {'format': 'JPEG', 'quality': 100}
        elif format.upper() == 'PNG':
            save_params = {'format': 'PNG', 'optimize': True}
        elif format.upper() == 'BMP':
            save_params = {'format': 'BMP'}
        elif format.upper() == 'ICO':
            save_params = {
                'format': 'ICO', 
                'sizes': [(size[0], size[1])],
            }
            if transparency:
                img = img.convert("RGBA")     
        img.save(output_image_path, **save_params)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to convert image: {e}")

def browse_file():
    file_paths = filedialog.askopenfilenames(
        title="Select Image Files  (By: BLAHPR 2024)",
        filetypes=(("Image Files", "*.bmp;*.png;*.jpg;*.jpeg;*.ico"), ("All Files", "*.*"))
    )
    if not file_paths:
        messagebox.showwarning("No files selected", "Please select at least one image file.")
        return None
    return list(file_paths)

def get_output_image_path(input_image_path, size, format):
    base_name, ext = os.path.splitext(os.path.basename(input_image_path))
    dir_name = os.path.dirname(input_image_path)
    size_str = f"{size[0]}x{size[1]}"
    new_path = os.path.join(dir_name, f"{base_name}_{size_str}.{format.lower()}")
    count = 1
    while os.path.exists(new_path):
        new_path = os.path.join(dir_name, f"{base_name}_{size_str}_{count}.{format.lower()}")
        count += 1
    return new_path


def load_image(image_path):
    load_window = Toplevel(root)
    load_window.title("Image Preview")

    # Set default size for the preview window
    load_window.geometry("900x500")

    # Create a Canvas widget for displaying and interacting with the image
    canvas = tk.Canvas(load_window, bg="white", bd=0, highlightthickness=0)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add vertical and horizontal scrollbars
    h_scroll = tk.Scrollbar(load_window, orient="horizontal", command=canvas.xview)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    v_scroll = tk.Scrollbar(load_window, orient="vertical", command=canvas.yview)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

    # Load and display the image
    img = Image.open(image_path)
    img_preview = ImageTk.PhotoImage(img)

    # Create a Frame to hold the image on the Canvas
    img_frame = tk.Frame(canvas)
    img_frame_id = canvas.create_window((0, 0), window=img_frame, anchor="nw")

    img_label = tk.Label(img_frame, image=img_preview)
    img_label.image = img_preview
    img_label.pack()

    # Variables for dragging
    drag_start_x = None
    drag_start_y = None

    def on_drag_start(event):
        nonlocal drag_start_x, drag_start_y
        drag_start_x = event.x
        drag_start_y = event.y

    def on_drag_motion(event):
        nonlocal drag_start_x, drag_start_y
        if drag_start_x is not None and drag_start_y is not None:
            # Calculate how much the mouse has moved
            dx = event.x - drag_start_x
            dy = event.y - drag_start_y
            # Move the image on the canvas
            canvas.move(img_frame_id, dx, dy)
            # Update the starting position
            drag_start_x = event.x
            drag_start_y = event.y
            # Update the canvas scroll region dynamically
            bbox = canvas.bbox("all")
            canvas.config(scrollregion=bbox)

    def adjust_size():
        try:
            new_width = int(width_entry.get())
            new_height = int(height_entry.get())
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            resized_preview = ImageTk.PhotoImage(resized_img)

            img_label.config(image=resized_preview)
            img_label.image = resized_preview

            # Adjust the canvas scroll region to match the resized image
            canvas.config(scrollregion=canvas.bbox("all"))
        except ValueError:
            messagebox.showerror("Invalid Size", "Please enter valid dimensions.")

    def zoom(event):
        scale = 1.1 if event.delta > 0 else 0.9
        width = int(img_label.winfo_width() * scale)
        height = int(img_label.winfo_height() * scale)
        resized_img = img.resize((width, height), Image.LANCZOS)
        resized_preview = ImageTk.PhotoImage(resized_img)

        img_label.config(image=resized_preview)
        img_label.image = resized_preview

        # Adjust the canvas scroll region to match the zoomed image
        canvas.config(scrollregion=canvas.bbox("all"))

    def on_window_resize(event):
        canvas.config(scrollregion=canvas.bbox("all"))

    # Bind mouse events for dragging the image
    img_label.bind("<Button-1>", on_drag_start)
    img_label.bind("<B1-Motion>", on_drag_motion)

    # Bind mouse wheel for zooming
    load_window.bind_all("<MouseWheel>", zoom)

    # Bind window resize event
    load_window.bind("<Configure>", on_window_resize)

    # Create frame for size adjustment controls
    size_frame = tk.Frame(load_window)
    size_frame.pack(fill=tk.X)

    # Width entry
    tk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
    width_entry = tk.Entry(size_frame)
    width_entry.grid(row=0, column=1, padx=5, pady=5)

    # Height entry
    tk.Label(size_frame, text="Height:").grid(row=1, column=0, padx=5, pady=5)
    height_entry = tk.Entry(size_frame)
    height_entry.grid(row=1, column=1, padx=5, pady=5)

    # Apply size button
    apply_button = tk.Button(size_frame, text="Apply Size", command=adjust_size)
    apply_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Bind the Enter key to the adjust_size function for both width and height entries
    width_entry.bind('<Return>', lambda event: adjust_size())
    height_entry.bind('<Return>', lambda event: adjust_size())

    # Initial canvas configuration
    canvas.config(scrollregion=canvas.bbox("all"))

    # Prevent flickering by using after_idle
    def update_scrollregion():
        canvas.config(scrollregion=canvas.bbox("all"))

    canvas.after_idle(update_scrollregion)

def main():
    def on_convert():
        file_paths = browse_file()
        if file_paths:
            format = format_var.get().upper()
            size = select_size()
            if not size:
                return
            for input_image_path in file_paths:
                output_image_path = get_output_image_path(input_image_path, size, format)
                convert_image(input_image_path, output_image_path, format, size=size, transparency=transparency_var.get())
            message = (
                f"Saved to Same Folder"
                f"\n\n\n-By: BLAHPR 2024-"
            )
            messagebox.showinfo("DONE!", message)

    def select_size():
        selected_option = size_option_var.get()
        selected_size = size_var.get().strip()

        try:
            if 'x' in selected_size:
                width, height = map(int, selected_size.lower().split('x'))
            else:
                messagebox.showerror("Invalid Size", "Please enter a valid size in the format 'widthxheight'.")
                return None

            format = format_var.get().upper()
            if format == 'ICO' and (width < 16 or width > 256 or height < 16 or height > 256):
                messagebox.showerror("Invalid Size", "ICO Size Limit 16-256.")
                return None

            return width, height
        except ValueError:
            messagebox.showerror("Invalid Size", "Please enter a valid size in the format 'widthxheight'.")
            return None

    global root
    root = tk.Tk()
    root.title("Simple Image Converter v1.2")
    root.size_selection = None

    icon_path = resource_path('s.ico')
    root.iconbitmap(icon_path)
    icon_path = resource_path('s.png')
    icon = PhotoImage(file=icon_path)
    root.iconphoto(True, icon)

    format_var = tk.StringVar(value='ico')
    transparency_var = BooleanVar(value=True)
    size_option_var = StringVar(value="common")
    size_var = StringVar(value="64x64")

    format_frame = tk.Frame(root)
    format_frame.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

    size_frame = tk.Frame(root)
    size_frame.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

    convert_frame = tk.Frame(root)
    convert_frame.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

    tk.Label(format_frame, text="Select Output Format:").grid(row=0, column=0, sticky=tk.W)
    formats = ['ico', 'png', 'bmp', 'jpg']
    for i, format in enumerate(formats):
        tk.Radiobutton(format_frame, text=format.upper(), variable=format_var, value=format).grid(row=0, column=i+1, sticky=tk.W)

    tk.Label(size_frame, text="Select Size:").grid(row=0, column=0, sticky=tk.W)
    sizes = ["16x16", "32x32", "48x48", "64x64", "128x128", "256x256", "512x512", "800x800", "1024x1024", "2048x2048", "4096x4096"]
    size_dropdown = tk.OptionMenu(size_frame, size_var, *sizes)
    size_dropdown.grid(row=0, column=1, sticky=tk.W)

    tk.Radiobutton(size_frame, text="Default Sizes", variable=size_option_var, value="common").grid(row=1, column=0, sticky=tk.W)
    tk.Radiobutton(size_frame, text="Custom Size", variable=size_option_var, value="custom").grid(row=1, column=1, sticky=tk.W)

    custom_size_label = tk.Label(size_frame, text="Custom Size (WxH):")
    custom_size_label.grid(row=2, column=0, sticky=tk.W)
    custom_size_entry = tk.Entry(size_frame, textvariable=size_var)
    custom_size_entry.grid(row=2, column=1, sticky=tk.W)

    def update_size_input():
        if size_option_var.get() == "custom":
            size_dropdown.grid_remove()
            custom_size_label.grid()
            custom_size_entry.grid()
        else:
            size_dropdown.grid()
            custom_size_label.grid_remove()
            custom_size_entry.grid_remove()

    size_option_var.trace_add("write", lambda *args: update_size_input())

    tk.Button(convert_frame, text="Convert Image", command=on_convert).pack(pady=10)

    load_button = tk.Button(root, text="Preview Image", command=lambda: load_image(browse_file()[0]))
    load_button.grid(row=2, column=0, pady=10)

    update_size_input()
    root.mainloop()

if __name__ == "__main__":
    main()
