from tkinter import Tk, BOTH, Canvas, Button

class Window:
  
    def __init__(self, width, height):
        self.__root = Tk()
        self.__root.title("Loner is fat")
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.__canvas = Canvas(self.__root, width=width, height=height)
        self.__canvas.pack(fill=BOTH, expand=True)
        self.__running = False


        self.__button_clear = Button(self.__root, text="Clear", command=self.clear_canvas)
        self.__button_clear.pack()

        self.__canvas.bind("<Button-1>", self.start_draw)
        self.__canvas.bind("<B1-Motion>", self.draw)
        self.__canvas.bind("<ButtonRelease-1>", self.stop_draw)

        self.__drawing = False
        self.__is_drag = False

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def clear_canvas(self):
        self.__canvas.delete("all")

    def start_draw(self, event):
        self.__drawing = True
        self.__last_x = event.x
        self.__last_y = event.y
        self.__is_drag = False

    def draw(self, event):
        if self.__drawing:
            self.__is_drag = True
            x, y = event.x, event.y
            self.__canvas.create_line(self.__last_x, self.__last_y, x , y, fill="blue", width=2)
            self.__last_x, self.__last_y = x, y

    def stop_draw(self, event):
        if not self.__is_drag:
            self.__canvas.create_oval(event.x -2, event.y -2, event.x + 2, event.y + 2, fill="blue")
        self.__drawing = False
        self.__is_drag = False