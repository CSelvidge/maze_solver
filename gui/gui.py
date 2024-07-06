from tkinter import Tk, BOTH, Canvas, Button, Frame, simpledialog
import random

class Window:
    def __init__(self, width, height, cell_size = None):
        self.__root = Tk()
        self.__root.title("Maze Solver V 0.1")
        self.__canvas = Canvas(self.__root, width=width, height=height)
        self.__canvas.pack(fill=BOTH, expand=True)
        self.__running = False
        self.cell_size = cell_size
        self.cells = []
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

        self.create_buttons()

    def create_buttons(self) -> None:
        button_frame = Frame(self.__root)
        button_frame.pack(pady=10)

        populate_button = Button(button_frame, text="Populate Canvas", command= self.populate_canvas)
        populate_button.pack(padx=5)

        clear_button = Button(button_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_button.pack(padx=5)

    def calculate_grid_size(self) -> None:
        if self.cell_size is None:
            raise ValueError("Cell size is not defined")
        
        canvas_width = self.__canvas.winfo_width()
        canvas_height = self.__canvas.winfo_height()

        num_cols = canvas_width // self.cell_size
        num_rows = canvas_height // self.cell_size

        return num_rows, num_cols
    
    def clear_canvas(self) -> None:
        self.__canvas.delete("all")
        self.cells = []

    def set_cell_size(self, cell_size) -> None:
        self.cell_size = cell_size

    def populate_canvas(self) -> None:
        self.clear_canvas()
        if self.cell_size is None or self.cell_size < 1:
            self.set_cell_size(simpledialog.askinteger("Input", "Enter cell size(in pixels):", minvalue=1))
        self.cell_geometry = self.calculate_grid_size()
        self.cells = self.populate_cells(self.cell_geometry[0], self.cell_geometry[1])
        

    def populate_cells(self, num_rows, num_cols) -> None:
        self.cells = [
            [
                self.create_randomized_cell(col, row)
                for col in range(num_cols)
            ]
            for row in range(num_rows)
        ]

    def create_randomized_cell(self, col, row) -> 'Cell':
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        cell = Cell(x1, y1, x2, y2, self)

        cell.walls = {
            'top': random.choice([True,False]),
            'right': random.choice([True,False]),
            'bottom': random.choice([True,False]),
            'left': random.choice([True,False])
        }
        cell.draw_walls()
        return cell

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False

    def draw_line(self, line, fill_color):
        line.draw(self.__canvas, fill_color)

class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class Line:
    def __init__(self, point1, point2) -> None:
        self.x1 = point1.x
        self.x2 = point2.x
        self.y1 = point1.y
        self.y2 = point2.y

    def draw(self, canvas, fill_color):
        canvas.create_line(self.x1, self.y1, self.x2, self.y2, fill=fill_color, width=2)


class Cell:
    def __init__(self, x1, y1, x2, y2, win) -> None:
        self.walls = {
            'top': True,
            'right': True,
            'bottom': True,
            'left': True
        }

        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2

        self._win = win

    def draw_walls(self) -> None:

        walls = { #I love dictionaries
            "left": Line(Point(self._x1, self._y1), Point(self._x1, self._y2)),
            "right": Line(Point(self._x2, self._y2), Point(self._x2, self._y1)),
            "top": Line(Point(self._x1, self._y1), Point(self._x2, self._y1)),
            "bottom": Line(Point(self._x1, self._y2), Point(self._x2, self._y2))
        }

        for wall, is_present in self.walls.items():
            if is_present:
                self._win.draw_line(walls[wall], "black")

    def draw_move(self, cell, undo = False) -> None:
        if undo:
            self._draw_color = "gray"
        else:
            self._draw_color = "red"

        self._center = Point(((self._x1 + self._x2) / 2), (self._y1 + self._y2) / 2)
        _cell_center = Point(((cell._x1 + cell._x2) / 2), (cell._y1 + cell._y2) / 2)
        line = Line(self._center, _cell_center)
        self._win.draw_line(line, self._draw_color)       