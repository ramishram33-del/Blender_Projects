import tkinter as tk
from tkinter import colorchooser
from tkinter import messagebox
from tkinter import ttk

class RectangleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rectangle Drawer")
        self.room_types = {"Washroom": "WC", "Bedroom": "BR", "Toilet": "TO", "Kitchen": "KT", "Living Room": "LR", "Dining Room": "DR", "Balcony": "BL", "Sitout": "ST"}
        self.room_types_counter = {key: 0 for key in self.room_types.keys()}
        self.room_colors = {"Washroom": "lightblue", "Bedroom": "lightgreen", "Toilet": "lightyellow", "Kitchen": "lightcoral", "Living Room": "lightcyan", "Dining Room": "lightpink", "Balcony": "lightgray", "Sitout": "lightgoldenrod"}
        self.selected_color = self.room_colors["Washroom"]  # Default color
        self.selected_room_type = "Washroom"  # Default room type
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

        # ---- Combobox ----
        tk.Label(input_frame, text="Select Layout Type").grid(row=2, column=0)
        combo = ttk.Combobox(input_frame, values=list(self.room_types.keys()))
        combo.current(0)  # set default
        combo.grid(row=2, column=1, pady=10)
        combo.bind("<<ComboboxSelected>>", self.update_room_type)

        # ---- Buttons ----
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Add Rectangle", command=self.add_rectangle).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Remove Rectangle", command=self.remove_rectangle).grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Reset Canvas", command=self.reset_canvas).grid(row=0, column=2, padx=5)

        # ---- Canvas Main ----
        self.canvas = tk.Canvas(root, bg="white", width=400, height=300)
        self.canvas.pack(pady=10, side=tk.LEFT)

        self.canvas_sub = tk.Canvas(root, bg="white", width=100, height=300)
        self.canvas_sub.pack(pady=10, side=tk.LEFT)

        # Store rectangles
        self.layouts = []
        self.current_y = 5  # Initialize current y position

    # ---- Draw Rectangle Function ----
    def draw_rectangle(self, width, height):
        w = 20
        h = 20
        rect = self.canvas_sub.create_rectangle(5, self.current_y, 5+ w, self.current_y + h,  fill=self.selected_color)
        text = self.canvas_sub.create_text(2 * w + 10, self.current_y + h/2, text=self.room_types[self.selected_room_type] + str(self.room_types_counter[self.selected_room_type] + 1), font=("Arial", 10))
        self.layouts.append({"rect": rect, "text": text, "type": self.selected_room_type})
        self.room_types_counter[self.selected_room_type] += 1  # Increment room type counter
        # Move next rectangle position
        self.current_y += h + 5


        # ---- Update Room Type ----
        # This function updates the selected color based on the room type chosen in the combobox
    def update_room_type(self, event):    
        selected_room = event.widget.get()
        self.selected_color = self.room_colors[selected_room]
        self.selected_room_type = selected_room

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
        if self.layouts:
            item = self.layouts.pop()
            self.canvas_sub.delete(item["rect"])
            self.canvas_sub.delete(item["text"])
            self.current_y -= 25  # Adjust spacing (simple logic)
            self.room_types_counter[item["type"]] -= 1
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