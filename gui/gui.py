from tkinter import LEFT,Tk, BOTH, Canvas, Button, Frame, simpledialog, Label
import random
import cProfile
import pstats
import time

class Window:
    def __init__(self, width, height, cell_size = None, batch_size = 100):
        self.__root = Tk()
        self.__root.title("Maze Solver V 0.3")
        self.__canvas = Canvas(self.__root, width=width, height=height)
        self.__canvas.pack(fill=BOTH, expand=True)
        self.__running = False
        self.cell_size = cell_size
        self.cell_count = 0
        self.batch_size = batch_size #Only useful when trying batched optimization, otherwise unused
        self.cells = []
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

        self.create_buttons()
        self.create_labels()

    def create_buttons(self) -> None:
        button_frame = Frame(self.__root)
        button_frame.pack(pady=10)

        Button(button_frame, text="Populate Canvas", command=self.profiling_tests).pack(side=LEFT, padx=5)
        Button(button_frame, text="Clear Canvas", command=self.clear_canvas).pack(side=LEFT, padx=5)
        Button(button_frame, text="Cell Size", command=self.user_cell_size).pack(side=LEFT, padx=5)

    def create_labels(self) -> None:
        self.count_label = Label(self.__root, text="Cell count: N/A")
        self.count_label.pack(side=LEFT, padx=5)

        self.cell_size_label = Label(self.__root, text="Cell Size: N/A")
        self.cell_size_label.pack(side=LEFT, padx=5)

        self.timing_label = Label(self.__root, text="Time to Populate: N/A")
        self.timing_label.pack(side=LEFT, padx=5)

    def update_count_label(self) -> None:
        self.count_label.config(text=f"Cell Count: {self.cell_count}")

    def update_cell_size_label(self) -> None:
        self.cell_size_label.config(text=f"Cell Size: {self.cell_size}")

    def update_timing_label(self) -> None:
        self.timing_label.config(text=f"Time to Populate: {self.duration}")

    def calculate_grid_size(self) -> tuple:
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

    def user_cell_size(self) -> None:
        self.set_cell_size(simpledialog.askinteger("Input", "Enter new cell size(in pixels):", minvalue = 1))

    def set_cell_size(self, cell_size) -> None:
        self.cell_size = cell_size
        self.update_cell_size_label()

    def user_batch_size(self) -> None:
        self.set_batch_size(simpledialog.askinteger("Input", "Enter batch size(in pixels):", minvalue=10))

    def set_batch_size(self, batch_size) -> None:
        self.batch_size = batch_size

    def populate_canvas(self) -> None:
        start_time = time.time()
        self.clear_canvas()
        if self.cell_size is None or self.cell_size < 1:
            self.set_cell_size(simpledialog.askinteger("Input", "Enter cell size(in pixels):", minvalue = 1))
        self.cell_geometry = self.calculate_grid_size()
        self.cells = self.populate_cells(self.cell_geometry[0], self.cell_geometry[1])

        end_time = time.time()
        self.duration = end_time - start_time
        self.update_timing_label()

    def profiling_tests(self) -> None:
        #cProfile.runctx('self.populate_canvas()', globals(), locals(), filename='db.prof') #No longer saving directly to file, switching to displaying results after each run to console

        pr = cProfile.Profile()
        pr.enable()

        self.populate_canvas()

        pr.disable()

        stats = pstats.Stats(pr)

        stats.sort_stats(pstats.SortKey.TIME).print_stats(25)

    def populate_cells(self, num_rows, num_cols) -> list:
        self.cells = [
            [
                self.create_randomized_cell(col, row)
                for col in range(num_cols)
            ]
           for row in range(num_rows)
        ]
        self.cell_count = num_rows * num_cols
        self.update_count_label()

        self.draw_all_walls()


        return self.cells

    def create_randomized_cell(self, col, row) -> 'Cell':
        x1 = col * self.cell_size
        y1 = row * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        cell = Cell(x1, y1, x2, y2, self)


        walls_state = random.getrandbits(4)

        cell.walls = {
            'top': bool(walls_state & 1),
            'right': bool(walls_state & 2),
            'bottom': bool(walls_state & 4),
            'left': bool(walls_state & 8)
        }

        return cell
    
    def draw_all_walls(self) -> None:
        drawn_walls = set()
        line_segments =[]

        for row in self.cells:
            for cell in row:
                lines_to_draw = cell.draw_walls(drawn_walls)
                line_segments.extend(lines_to_draw)
                
                
        for start, end in line_segments:
            self.__canvas.create_line(start.x, start.y, end.x, end.y, fill="black", width=2)

        self.__root.update_idletasks()
        self.__root.update()

    def redraw(self) -> None:
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self)-> None:
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self) -> None:
        self.__running = False
        self.__root.destroy()

    def draw_line(self, line, fill_color) -> 'Line':
        line.draw(self.__canvas, fill_color)
        return line

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
    def __init__(self, x1, y1, x2, y2, win):
        self.walls = {}
        
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        self._win = win

    def draw_walls(self, drawn_walls) -> list:
        lines_to_draw = []

        walls = {
            "top": (Point(self._x1, self._y1), Point(self._x2, self._y1)),
            "right": (Point(self._x2, self._y1), Point(self._x2, self._y2)),
            "bottom": (Point(self._x1, self._y2), Point(self._x2, self._y2)),
            "left": (Point(self._x1, self._y1), Point(self._x1, self._y2)),
        }        

        for direction, wall_coords in walls.items():
            if self.walls[direction] and wall_coords not in drawn_walls:
                drawn_walls.add(wall_coords)
                lines_to_draw.append(wall_coords)
        
        return lines_to_draw

    def draw_move(self, to_cell, undo=False) -> None:
        draw_color = "gray" if undo else "red"

        self_center = Point((self._x1 + self._x2) / 2, (self._y1 + self._y2) / 2)
        cell_center = Point((to_cell._x1 + to_cell._x2) / 2, (to_cell._y1 + to_cell._y2) / 2)
        line = Line(self_center, cell_center)
        self._win.draw_line(line, draw_color)