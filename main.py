import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
from numpy import ndarray
import json

config = json.load(open("config.json"))

class MineSweeper:
    """
    dimension:
    easy -> 8x10, 10 mines
    medium -> 14 x 18, 40 mines
    hard -> 20 x 24, 99 mines
    """
    #(width, height, mines)
    DIMENSION_EASY: tuple[int,int] = (
        config["dimension"]["easy"]["width"], config["dimension"]["easy"]["height"], config["dimension"]["easy"]["bombs"])
    DIMENSION_MEDIUM: tuple[int,int] = (
        config["dimension"]["medium"]["width"], config["dimension"]["medium"]["height"], config["dimension"]["medium"]["bombs"])
    DIMENSION_HARD: tuple[int,int] = (
        config["dimension"]["hard"]["width"], config["dimension"]["hard"]["height"], config["dimension"]["hard"]["bombs"])
    current_dimension = DIMENSION_MEDIUM

    DEFFICULTY_OPTION = ['easy', 'medium', 'hard']
    current_difficulty = DEFFICULTY_OPTION[1]
    TILE_SIZE: int = config["tile-size"]

    TILE_1 = Image.open(config["image-path"]["tile-1"])
    TILE_2 = Image.open(config["image-path"]["tile-2"])
    TILE_3 = Image.open(config["image-path"]["tile-3"])
    TILE_4 = Image.open(config["image-path"]["tile-4"])
    TILE_5 = Image.open(config["image-path"]["tile-5"])
    TILE_6 = Image.open(config["image-path"]["tile-6"])
    TILE_COVERED = Image.open(config["image-path"]["tile-covered"])
    TILE_BLANK = Image.open(config["image-path"]["tile-blank"])
    TILE_FLAG = Image.open(config["image-path"]["tile-flag"])
    TILE_BOMB_REVEAL = Image.open(config["image-path"]["tile-bomb-reveal"])
    TILE_BOMB_EXPLODE = Image.open(config["image-path"]["tile-bomb-explode"])
    SMILE_ICON = Image.open(config["image-path"]["smile-icon"])
    SAD_ICON = Image.open(config["image-path"]["sad-icon"])

    def __init__(self) -> None:

        self.game_start = False
        self.time_elapsed: int = 0
        self.time_id = None

        self.safe_tile_count = self.current_dimension[0] * self.current_dimension[1] - self.current_dimension[2]

        self.window = tk.Tk()
        self.window.title(config["title"])
        self.window.geometry(f'+{config["window"]["main"]["position"][0]}+{config["window"]["main"]["position"][1]}')
        self.window.resizable(0,0)

        self.info_frame = tk.Frame(
            self.window, width= self.current_dimension[0]*self.TILE_SIZE, height= 40)
        self.game_frame = tk.Frame(
            self.window, width= self.current_dimension[0]*self.TILE_SIZE, height= self.current_dimension[1]*self.TILE_SIZE)
        
        self.opt_var = tk.StringVar()
        self.difficulty_opt = ttk.Combobox(
            self.info_frame, values= self.DEFFICULTY_OPTION, textvariable= self.opt_var, width= 10, state= 'readonly')
        self.difficulty_opt.grid(row = 0, column= 0, padx= (0,5))
        self.difficulty_opt.current(self.DEFFICULTY_OPTION.index(self.current_difficulty))
        self.difficulty_opt.bind('<<ComboboxSelected>>', self.change_difficulty)

        self.new_game_btn = tk.Button(self.info_frame, text= 'New Game', width= 10, command= self.new_game)
        self.new_game_btn.grid(row= 0, column= 1, padx= 5, pady= 2)

        self.time_lbl = tk.Label(self.info_frame, height= 1, width= 10, text= str(self.time_elapsed).zfill(3), borderwidth=2, relief="ridge")
        self.time_lbl.grid(row= 0, column= 2, padx= (5,0))

        self.info_frame.grid(row= 0, sticky= '')
        self.game_frame.grid(row= 1, sticky= "wesn")
        self.game_frame.grid_propagate(0)

        self.list_of_box = np.empty((self.current_dimension[1],self.current_dimension[0]), dtype= object)

        self.tile_1 = ImageTk.PhotoImage(self.TILE_1, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_1')
        self.tile_2 = ImageTk.PhotoImage(self.TILE_2, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_2')
        self.tile_3 = ImageTk.PhotoImage(self.TILE_3, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_3')
        self.tile_4 = ImageTk.PhotoImage(self.TILE_4, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_4')
        self.tile_5 = ImageTk.PhotoImage(self.TILE_5, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_5')
        self.tile_6 = ImageTk.PhotoImage(self.TILE_6, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_6')
        self.tile_covered = ImageTk.PhotoImage(self.TILE_COVERED, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_covered')
        self.tile_blank = ImageTk.PhotoImage(self.TILE_BLANK, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_blank')
        self.tile_flag = ImageTk.PhotoImage(self.TILE_FLAG, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'tile_flag')
        self.smile_icon = ImageTk.PhotoImage(self.SMILE_ICON, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'smile_icon')
        self.sad_icon = ImageTk.PhotoImage(self.SAD_ICON, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'sad_icon')
        self.bomb_explode = ImageTk.PhotoImage(self.TILE_BOMB_EXPLODE, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'bomb_explode')
        self.bomb_reveal = ImageTk.PhotoImage(self.TILE_BOMB_REVEAL, height= self.TILE_SIZE, width= self.TILE_SIZE, name= 'bomb_reveal')

        self.number_tile = [self.tile_blank,self.tile_1, self.tile_2, self.tile_3, self.tile_4, self.tile_5, self.tile_6]

        for row in range(self.current_dimension[1]):
            for col in range(self.current_dimension[0]):
                box = tk.Label(
                    self.game_frame, image= self.tile_covered,width= self.TILE_SIZE, height= self.TILE_SIZE, borderwidth= 0)
                box.grid(row= row, column= col)
                box.bind("<Button-1>", self.left_click)
                box.bind("<Button-3>", self.right_click)

                self.list_of_box[row, col] = box

        self.window.mainloop()

    def left_click(self,event):
        box: tk.Label = event.widget
        position = np.argwhere(self.list_of_box == box)[0]
        position = (position[0], position[1])

        if not self.game_start:
            self.map, self.bomb_coor = generate_map(position, self.current_dimension)
            self.game_start = True
            self.reveal_map(position)
            self.time_id = self.window.after(1000,self.change_time)
        else:
            if box["image"] == 'tile_covered':
                self.reveal_map(position)

        if self.safe_tile_count == 0:
            self.game_end()
        
    def right_click(self,event):
        box: tk.Label = event.widget
        if box["image"] == 'tile_covered':
            box["image"] = self.tile_flag
        elif box["image"] == 'tile_flag':
            box["image"] = self.tile_covered

    def reveal_map(self, position):
        row, col = position
        if self.list_of_box[position]["image"] == 'tile_covered':
            num = self.map[position]
            if num == -1:
                self.list_of_box[position]["image"] = self.bomb_explode
                self.game_end()
            elif num == 0:
                self.list_of_box[position]["image"] = self.number_tile[num]
                self.safe_tile_count -= 1    
                for current_row in range(
                    row - 1 if row != 0 else 0, 
                    row + 2 if row != self.current_dimension[1] - 1 else self.current_dimension[1]):

                    for current_col in range(
                        col - 1 if col != 0 else 0, 
                        col + 2 if col != self.current_dimension[0] - 1 else self.current_dimension[0]):

                        current_idx = (current_row, current_col)
                        if self.map[current_idx] == 0:
                            self.reveal_map(current_idx)
                        if self.list_of_box[current_idx]["image"] == 'tile_covered':
                            self.safe_tile_count -= 1

                        self.list_of_box[current_idx]["image"] = self.number_tile[self.map[current_idx]]

            else:
                self.list_of_box[position]["image"] = self.number_tile[num]
                self.safe_tile_count -= 1

    def change_difficulty(self, event):
        if self.time_id:
            self.window.after_cancel(self.time_id)
        if self.difficulty_opt.get() != self.current_difficulty:
            opt = self.difficulty_opt.get()
            if opt == 'easy':
                self.current_dimension = self.DIMENSION_EASY
                self.current_difficulty = 'easy'
            if opt == 'medium':
                self.current_dimension = self.DIMENSION_MEDIUM
                self.current_difficulty = 'medium'
            if opt == 'hard':
                self.current_dimension = self.DIMENSION_HARD
                self.current_difficulty = 'hard'

        self.refresh_window()

    def game_end(self):
        self.window.after_cancel(self.time_id)
        for box_row in self.list_of_box:
            for box in box_row:
                box.unbind("<Button-1>")
                box.unbind("<Button-3>")

        if self.safe_tile_count == 0:
            self.game_win()
        else:
            for row, col in np.nditer(self.bomb_coor, flags=['external_loop'], order='C'):
                box = self.list_of_box[row, col]
                if box["image"] != 'bomb_explode':
                    box["image"] = self.bomb_reveal
            self.game_lose()

    def game_win(self):
        message = config["messages"]["win-message"].format(self.time_elapsed)

        self.display_message(self.smile_icon, message= message)

    def game_lose(self):
        message = config["messages"]["lose-message"]

        self.display_message(self.sad_icon, message= message)


    def new_game(self):
        if self.time_id:
            self.window.after_cancel(self.time_id)
        
        self.refresh_window()

    def refresh_window(self):
        self.window.destroy()
        self.__init__()

    def change_time(self):
        self.time_elapsed += 1
        self.time_lbl['text'] = str(self.time_elapsed).zfill(3)
        self.time_id = self.window.after(1000, self.change_time)

    def display_message(self, icon: ImageTk, message: str) -> None:
        msg_window = tk.Toplevel()
        msg_window.geometry(f'+{config["window"]["message"]["position"][0]}+{config["window"]["message"]["position"][1]}')
        msg_window.resizable(0, 0)
        
        msg_frame = tk.Frame(msg_window)
        msg_frame.pack()

        icon_lbl = tk.Label(msg_frame, image= icon, width= 32, height= 32, anchor= "center")
        msg_lbl = tk.Label(msg_frame, text= message, width= 20, anchor= "center")

        icon_lbl.grid(row= 0, column= 0, padx= 5, pady= 5)
        msg_lbl.grid(row=0, column= 1)

        msg_window.mainloop()


def generate_map(position, dimension = (18,14,40)) -> ndarray:
    rows = dimension[1]
    cols = dimension[0]
    num_of_mines = dimension[2]

    border = (
        (position[0] - 1) if (position[0] - 1 >= 0) else 0,
        (position[1] - 1) if (position[1] - 1 >= 0) else 0,
        (position[1] + 1) if (position[1] + 1 < cols) else (cols - 1),
        (position[0] + 1) if (position[0] + 1 < rows) else (rows - 1)) #top, left, right bottom

    size_of_start = (border[3] + 1 - border[0]) * (border[2] + 1 - border[1])

    mines = np.full(num_of_mines, -1, dtype= int)
    blank = np.zeros(rows * cols - num_of_mines - size_of_start, dtype= int)

    map = np.concatenate((mines, blank))
    np.random.default_rng().shuffle(map)

    full_map = np.full((rows, cols), 0, dtype= int)
    
    """
    divide the whole map into 4 region with the origin at the middle
    a: the rows at the top of the origin
    b: the columns at the left of the origin bounded by a and d
    c: the columns at the righ of the origin bounded by a and d
    d: the rows at the bottom of the origin

                a
    -------------------------
        b   |   ori |   c
    -------------------------
                d
    """
    count = 0
    region_a_size = border[0]*cols
    if region_a_size != 0:
        submap_a = map[count:count + region_a_size]
        count += region_a_size
        submap_a.resize((border[0], cols))
        full_map[ : border[0], : ] = submap_a

    region_b_size = (border[3] + 1 - border[0]) * border[1]
    if region_b_size != 0:
        submap_b = map[count: count + region_b_size]
        count += region_b_size
        submap_b.resize((border[3] + 1 - border[0],border[1]))
        full_map[border[0] : border[3] + 1, : border[1]] = submap_b

    region_c_size = (border[3] + 1 - border[0]) * (cols - border[2] - 1)
    if region_c_size != 0:
        submap_c = map[count : count + region_c_size]
        count += region_c_size
        submap_c.resize((border[3] + 1 - border[0],cols - border[2] - 1))
        full_map[border[0] : border[3] + 1 ,border[2] + 1 : ] = submap_c

    region_d_size = (rows - border[3] - 1) * (cols)
    if region_d_size != 0:
        submap_d = map[count : count + region_d_size]
        count += region_d_size
        submap_d.resize((rows - border[3] - 1,cols))
        full_map[border[3] + 1 : , : ] = submap_d

    coor = np.argwhere(full_map == -1)

    for row, col in coor:
        start_row = row - 1
        end_row = row + 2
        start_col = col - 1
        end_col = col + 2
        if row == 0:
            start_row = 0
        if row == rows - 1:
            end_row = rows
        if col == 0:
            start_col = 0
        if col == cols - 1:
            end_col = cols

        full_map[start_row: end_row, start_col: end_col] += 1

    for row, col in np.nditer(coor, flags=['external_loop'], order='C'):
        full_map[row][col] = -1

    if not is_map_solvable(full_map, position):
        full_map, coor = generate_map(position, dimension= dimension)

    if np.argwhere(full_map == 7).size > 0 or np.argwhere(full_map == 8).size > 0:
        full_map, coor = generate_map(position, dimension= dimension)

    return full_map, coor

def is_map_solvable(plane: ndarray, position: tuple[int,int]) -> bool:
    """
    from the centre position, go to the top of the blank area
    check anticlockwise if the blank area is a rectangle -> return false
    also check for diagonal if there is any blank tile -> true
    """

    current_position = [position[0], position[1]] #[row, col]

    #move to the top
    while plane[current_position[0] - 1, current_position[1]] == 0:
        current_position[0] -= 1
    top_idx = current_position[0]

    #move to the left, check if the above tile is blank
    while plane[current_position[0], current_position[1] - 1] == 0:
        current_position[1] -= 1
        if plane[current_position[0] - 1, current_position[1]] == 0:
            return True
        
    if plane[current_position[0] - 1, current_position[1] - 1] == 0:
        return True
    
    #move to the bottom, check if the leftside tile is blank
    while plane[current_position[0] + 1, current_position[1]] == 0:
        current_position[0] += 1
        if plane[current_position[0], current_position[1] - 1] == 0:
            return True

    if plane[current_position[0] + 1, current_position[1] - 1] == 0:
        return True
    
    #move to the right, check if the bottom tile is blank
    while plane[current_position[0], current_position[1] + 1] == 0:
        current_position[1] += 1
        if plane[current_position[0] + 1, current_position[1]] == 0:
            return True

    if plane[current_position[0] + 1, current_position[1] + 1] == 0:
        return True
            
    #move to the top, check if the rightside tile is blank
    while plane[current_position[0] - 1, current_position[1]] == 0:
        current_position[0] -= 1
        if plane[current_position[0], current_position[1] + 1] == 0:
            return True

    if plane[current_position[0] - 1, current_position[1] + 1] == 0:
        return True
            
    #move to the left, check if the above tile is blank
    while plane[current_position[0], current_position[1] - 1] == 0:
        current_position[1] -= 1
        if plane[current_position[0] - 1, current_position[1]] == 0:
            return True
    
    if current_position[0] != top_idx:
        return True

    return False

MineSweeper()
