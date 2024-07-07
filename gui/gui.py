from tkinter import LEFT,Tk, BOTH, Canvas, Button, Frame, simpledialog, Label
import random
import cProfile
import pstats
import time

class Window:
    def __init__(self, width, height, cell_size = None, batch_size = 100):
        self.__root = Tk()
        self.__root.title("Maze Solver V 0.2")
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

        populate_button = Button(button_frame, text="Populate Canvas", command= self.profiling_tests)
        populate_button.pack(side = LEFT, padx=5)

        clear_button = Button(button_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_button.pack(side=LEFT, padx=5)

        cell_size_button = Button(button_frame, text="Cell Size", command=self.user_cell_size)
        cell_size_button.pack(side=LEFT, padx=5)

        batch_size_button = Button(button_frame, text="Set Batch Size", command=self.user_batch_size)
        batch_size_button.pack(side=LEFT, padx=5)

    def create_labels(self) -> None:
        self.count_label = Label(self.__root, text="Cell count:")
        self.count_label.pack(side=LEFT, padx=5)

        self.cell_size_label = Label(self.__root, text="Cell Size:")
        self.cell_size_label.pack(side=LEFT, padx=5)

        self.timing_label = Label(self.__root, text="Time to Populate:")
        self.timing_label.pack(side=LEFT, padx=5)

    def update_count_label(self) -> None:
        self.count_label.config(text=f"Cell Count: {self.cell_count}")

    def update_cell_size_label(self) -> None:
        self.cell_size_label.config(text=f"Cell Size: {self.cell_size}")

    def update_timing_label(self) -> None:
        self.timing_label.config(text=f"Time to Populate: {self.duration}")

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

        stats.sort_stats(pstats.SortKey.TIME).print_stats(10)

    def populate_cells(self, num_rows, num_cols) -> None:
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

        self.__root.update_idletasks()
        self.__root.update() 

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

        return cell
    
    def draw_all_walls(self) -> None:
        drawn_walls = set()
        lines_to_draw = []

        for row in self.cells:
            for cell in row:
                lines_to_draw.extend(cell.draw_walls(drawn_walls))
        
        self.draw_lines(lines_to_draw)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()

    def close(self):
        self.__running = False
        self.__root.destroy()

    def draw_lines(self, lines:list) -> None:
        for start, end in lines:
            self.draw_line(Line(start, end), "black")

    def draw_line(self, line, fill_color):
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

        self.cached_wall_coords = self._cache_wall_coordinates()

    def _cache_wall_coordinates(self) -> None:
        return {
            'top': (self._x1, self._y1, self._x2, self._y1),
            'right': (self._x2, self._y1, self._x2, self._y2),
            'bottom': (self._x1, self._y2, self._x2, self._y2),
            'left': (self._x1, self._y1, self._x1, self._y2)
        }

    def draw_walls(self, drawn_walls) -> list:
        walls_to_draw = []

        top_wall = ((self._x1, self._y1), (self._x2, self._y1))
        right_wall = ((self._x2, self._y1), (self._x2, self._y2))
        bottom_wall = ((self._x1, self._y2), (self._x1, self._y2))
        left_wall = ((self._x1, self._y1), (self._x1, self._y2))


        if self.walls['top']:
            top_wall = self.cached_wall_coords['top']
            if top_wall not in drawn_walls:
                walls_to_draw.append((Point(*top_wall[:2]), Point(*top_wall[2:])))
                drawn_walls.add(top_wall)
        if self.walls['right']:
            right_wall = self.cached_wall_coords['right']
            if right_wall not in drawn_walls:
                walls_to_draw.append((Point(*right_wall[:2]), Point(*right_wall[2:])))
                drawn_walls.add(right_wall)
        if self.walls['bottom']:
            bottom_wall = self.cached_wall_coords['bottom']
            if bottom_wall not in drawn_walls:
                walls_to_draw.append((Point(*bottom_wall[:2]), Point(*bottom_wall[2:])))
                drawn_walls.add(bottom_wall)
        if self.walls['left']:
            left_wall = self.cached_wall_coords['left']
            if left_wall not in drawn_walls:
                walls_to_draw.append((Point(*left_wall[:2]), Point(*left_wall[2:])))
                drawn_walls.add(left_wall)



        #Non Cached version

#        if self.walls.get('top') and top_wall not in drawn_walls:
#            walls_to_draw.append((Point(self._x1, self._y1), Point(self._x2, self._y1)))
#            drawn_walls.add(top_wall)
#        if self.walls.get('right') and right_wall not in drawn_walls:
#            walls_to_draw.append((Point(self._x2, self._y1), Point(self._x2, self._y2)))
#            drawn_walls.add(right_wall)
#        if self.walls.get('bottom') and bottom_wall not in drawn_walls:
#            walls_to_draw.append((Point(self._x1, self._y2), Point(self._x2, self._y2)))
#            drawn_walls.add(bottom_wall)
#        if self.walls.get('left') and left_wall not in drawn_walls:
#            walls_to_draw.append((Point(self._x1, self._y1), Point(self._x1, self._y2)))
#            drawn_walls.add(left_wall)

        return walls_to_draw

    def draw_move(self, cell, undo: bool = False) -> None:
        if undo:
            self._draw_color = "gray"
        else:
            self._draw_color = "red"

        self._center = Point(((self._x1 + self._x2) / 2), (self._y1 + self._y2) / 2)
        _cell_center = Point(((cell._x1 + cell._x2) / 2), (cell._y1 + cell._y2) / 2)
        line = Line(self._center, _cell_center)
        self._win.draw_line(line, self.__draw_color)       