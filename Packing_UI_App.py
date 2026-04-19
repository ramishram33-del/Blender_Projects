import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox

class RectangleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rectangle Drawer")

        # ---- Input Fields ----
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

     
        # Canvas size inputs
        tk.Label(input_frame, text="Canvas Width").grid(row=0, column=0)
        self.canvas_width_entry = tk.Entry(input_frame)
        self.canvas_width_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="Canvas Height").grid(row=0, column=2)
        self.canvas_height_entry = tk.Entry(input_frame)
        self.canvas_height_entry.grid(row=0, column=3)

        # Rectangle size inputs
        tk.Label(input_frame, text="Rect Width").grid(row=1, column=0)
        self.rect_width_entry = tk.Entry(input_frame)
        self.rect_width_entry.grid(row=1, column=1)

        tk.Label(input_frame, text="Rect Height").grid(row=1, column=2)
        self.rect_height_entry = tk.Entry(input_frame)
        self.rect_height_entry.grid(row=1, column=3)

        # ---- Buttons ----
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.selected_color = "skyblue"  # default color
        tk.Button(button_frame, text="Choose Color", command=self.choose_color).grid(row=0, column=3, padx=5)


        tk.Button(button_frame, text="Add Rectangle", command=self.add_rectangle).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Remove Rectangle", command=self.remove_rectangle).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Reset Canvas", command=self.reset_canvas).grid(row=0, column=2, padx=5)

        # ---- Canvas ----
        self.canvas = tk.Canvas(root, bg="white", width=400, height=300)
        self.canvas.pack(pady=10)

        # Store rectangles
        self.rectangles = []
        self.current_x = 10
        self.current_y = 10


    def choose_color(self):
        color = colorchooser.askcolor(title="Pick a color")
        if color[1]:  # color[1] is hex value like '#ff0000'
            self.selected_color = color[1]

    # ---- Draw Rectangle Function ----
    def draw_rectangle(self, width, height):
        x1 = self.current_x
        y1 = self.current_y
        x2 = x1 + width
        y2 = y1 + height

        rect = self.canvas.create_rectangle(x1, y1, x2, y2,  fill=self.selected_color)
        self.rectangles.append(rect)

        # Move next rectangle position
        self.current_y += height + 10

    # ---- Add Rectangle ----
    def add_rectangle(self):
        try:
            width = int(self.rect_width_entry.get())
            height = int(self.rect_height_entry.get())
            self.draw_rectangle(width, height)
        except ValueError:
            messagebox.showerror("Error", "Enter valid rectangle dimensions")

    # ---- Remove Rectangle ----
    def remove_rectangle(self):
        if self.rectangles:
            rect = self.rectangles.pop()
            self.canvas.delete(rect)
            self.current_y -= 50  # Adjust spacing (simple logic)
        else:
            messagebox.showinfo("Info", "No rectangles to remove")

    # ---- Reset Canvas ----
    def reset_canvas(self):
        try:
            width = int(self.canvas_width_entry.get())
            height = int(self.canvas_height_entry.get())

            self.canvas.config(width=width, height=height)
            self.canvas.delete("all")

            self.rectangles.clear()
            self.current_x = 10
            self.current_y = 10

        except ValueError:
            messagebox.showerror("Error", "Enter valid canvas dimensions")


# ---- Run App ----
if __name__ == "__main__":
    root = tk.Tk()
    app = RectangleApp(root)
    root.mainloop()