from gui.gui import *

def main():
    win = Window(800, 600)

    cell1 = Cell(50, 50, 100, 100, win)
    cell2 = Cell(110, 50, 160, 100, win)

    cell1.draw_walls()
    cell2.draw_walls()

    cell1.draw_move(cell2, True)



    win.wait_for_close()



if __name__ == "__main__":
    main()