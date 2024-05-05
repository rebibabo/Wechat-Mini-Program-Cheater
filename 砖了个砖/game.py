import random
import numpy as np
from cv_digit import recognize_digit2
import os
import copy
from PIL import Image

def set_seed(seed):
    random.seed(seed)

class Table:
    def __init__(self, table):
        self.width = 10
        self.height = 14
        # self.table = np.array([[random.randint(1, 16) for _ in range(self.width)] for _ in range(self.height)])
        self.table = table
        self.grade = 0
        self.operations = []
        self.max_grade = np.sum(self.table != 0) // 2

    def load_table(self, str):
        for i, row in enumerate(str.split('\n')[2:]):
            for j in range(5, len(row), 3):
                if row[j:j+2] == '  ':
                    self.table[i][(j-5)//3] = 0
                else:
                    self.table[i][(j-5)//3] = int(row[j:j+2])
        # print(self.show())

    def show(self, merge=None, direction=None, choice=None):
        str = '       0  1  2  3  4  5  6  7  8  9\n     _______________________________\n'
        str_table = [['' for _ in range(self.width)] for _ in range(self.height)]
        for i, row in enumerate(self.table):
            for j, cell in enumerate(row):
                if cell == 0:
                    cell = '  '
                else:
                    cell = f'{cell:2}'
                str_table[i][j] = cell
        if merge:
            x_1, y_1, x_2, y_2 = merge
            if direction == 0:
                for i in range(x_2+2, x_1):
                    str_table[i][y_1] = '| '
                str_table[x_2+1][y_1] = '↑ '
            elif direction == 1:
                for i in range(x_1+1, x_2-1):
                    str_table[i][y_1] = '| '
                str_table[x_2-1][y_1] = '↓ '
            elif direction == 2:
                for j in range(y_2+2, y_1):
                    str_table[x_1][j] = '--'
                str_table[x_1][y_2+1] = '←-'
            elif direction == 3:
                for j in range(y_1+1, y_2-1):
                    str_table[x_1][j] = '--'
                str_table[x_1][y_2-1] = '-→'
            if x_1 == x_2:
                for i in range(min(x_2, choice[0])+1, max(x_2, choice[0])):
                    str_table[i][y_2] = '：'
            if y_1 == y_2:
                for i in range(min(y_2, choice[1])+1, max(y_2, choice[1])):
                    str_table[x_2][i] = '··'
            str_table[x_1][y_1] = '▢ '
            str_table[x_2][y_2] = '▢ '
            str_table[choice[0]][choice[1]] = '▢ '
        for i, row in enumerate(self.table):
            str += f'{i:<4}｜'
            for j, cell in enumerate(row):
                str += f'{str_table[i][j]} '
            str = str[:-1] + '｜\n'
        str += '     ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾'
        return str

    def find_adj(self, x, y, direction):
        if direction == 0:
            for i in range(x-1, -1, -1):
                if self.table[i][y] != 0 or i == 0:
                    return i, y
        elif direction == 1:
            for i in range(x+1, self.height):
                if self.table[i][y] != 0 or i == self.height- 1:
                    return i, y
        elif direction == 2:
            for j in range(y-1, -1, -1):
                if self.table[x][j] != 0 or j == 0:
                    return x, j
        elif direction == 3:
            for j in range(y+1, self.width):
                if self.table[x][j] != 0 or j == self.width - 1:
                    return x, j
        return x, y

    def find_margin(self, x, y, direction):
        if direction == 0:
            for i in range(x, -1, -1):
                if i == 0 or self.table[i-1][y] == 0:
                    return i, y
        elif direction == 1:
            for i in range(x, self.height):
                if i == self.height- 1 or self.table[i+1][y] == 0:
                    return i, y
        elif direction == 2:
            for j in range(y, -1, -1):
                if j == 0 or self.table[x][j-1] == 0:
                    return x, j
        elif direction == 3:
            for j in range(y, self.width):
                if j == self.width - 1 or self.table[x][j+1] == 0:
                    return x, j

    def equal(self, coord1, coord2):
        return coord1 != coord2 and self.table[coord1[0]][coord1[1]] == self.table[coord2[0]][coord2[1]]

    def move(self, x_1, x_2, y_1, y_2, direction):
        if direction == -1:
            return
        margin = self.find_margin(x_1, y_1, direction)
        if direction == 0:
            self.table[x_2-x_1+margin[0]:x_2+1, y_1] = self.table[margin[0]:x_1+1, y_1]
            self.table[max(margin[0], x_2+1):x_1+1, y_1] = 0
        elif direction == 1:
            self.table[x_2:x_2+margin[0]-x_1+1, y_1] = self.table[x_1:margin[0]+1, y_1]
            self.table[x_1:min(x_2, margin[0]+1), y_1] = 0
        elif direction == 2:
            self.table[x_1, y_2-y_1+margin[1]:y_2+1] = self.table[x_1, margin[1]:y_1+1]
            self.table[x_1, max(margin[1], y_2+1):y_1+1] = 0
        elif direction == 3:
            self.table[x_1, y_2:y_2+margin[1]-y_1+1] = self.table[x_1, y_1:margin[1]+1]
            self.table[x_1, y_1:min(y_2, margin[1]+1)] = 0

    def show_pic(self, i):
        image = Image.open(f'image/{i}.jpg')
        image.show()

    def merge(self, x_1, y_1, x_2, y_2, stop=False):
        '''↑:0 ↓:1 ←:2 →:3'''
        if self.table[x_1, y_1] == 0:
            return
        if x_1 == x_2 and y_1 == y_2:
            direction = -1
        elif x_1 == x_2:
            direction = 2 + int(y_1 < y_2)
        elif y_1 == y_2:
            direction = int(x_1 < x_2)
        else:
            return
        if direction in [0, 1]:
            margin = self.find_margin(x_1, y_1, direction)
            adjac = self.find_adj(margin[0], margin[1], direction)
            length = abs(margin[0] - adjac[0])
            if abs(x_2 - x_1) >= length:
                return
        elif direction in [2, 3]:
            margin = self.find_margin(x_1, y_1, direction)
            adjac = self.find_adj(margin[0], margin[1], direction)
            length = abs(margin[1] - adjac[1])
            if abs(y_2 - y_1) >= length:
                return
        table = copy.deepcopy(self.table)
        self.move(x_1, x_2, y_1, y_2, direction)
        left = self.find_adj(x_2, y_2, 2)
        right = self.find_adj(x_2, y_2, 3)
        up = self.find_adj(x_2, y_2, 0)
        down = self.find_adj(x_2, y_2, 1)
        choices = []
        if self.equal(up, (x_2, y_2)) and direction in [-1, 2, 3]:
            choices.append(up)
        if self.equal(down, (x_2, y_2)) and direction in [-1, 2, 3]:
            choices.append(down)
        if self.equal(left, (x_2, y_2)) and direction in [-1, 0, 1]:
            choices.append(left)
        if self.equal(right, (x_2, y_2)) and direction in [-1, 0, 1]:
            choices.append(right)
        if len(choices) == 0:
            self.table = table
            return
        choice = random.choice(choices)
        self.operations.append((x_1, y_1, x_2, y_2))
        self.grade += 1
        self.table[x_2, y_2] = 0
        self.table[choice[0], choice[1]] = 0
        if stop:
            direction_dict = {-1: '.', 0: '↑', 1: '↓', 2: '←', 3: '→'}
            print(f'current grade: {self.grade}, step: {(x_1, y_1, x_2, y_2)}, direction: {direction_dict[direction]}')
            # self.show_pic(idx)
            input(self.show((x_1, y_1, x_2, y_2), direction, choice))
            
def run(t, stop=False):
    table = Table(t)
    # print(table.show())
    for _ in range(300000):
        x_1 = random.randint(0, table.height- 1)
        y_1 = random.randint(0, table.width - 1)
        x_2 = random.randint(0, table.height- 1)
        y_2 = random.randint(0, table.width - 1)
        table.merge(x_1, y_1, x_2, y_2, stop)
    # print(table.show())
    return table

if __name__ == '__main__':
    max_grade = 0
    best_seed = 0
    for file in os.listdir('.'):
        if file.endswith('.jpg'):
            t = np.array(recognize_digit2(file))
            break
    for i in range(151, 200):
        set_seed(i)
        table = run(t)
        print(f'seed: {i}, grade: {table.grade}, best seed: {best_seed}, max grade: {max_grade}, therotic max grade: {table.max_grade}')
        if table.grade > max_grade:
            max_grade = table.grade
            best_seed = i
            if table.grade >= table.max_grade - 1:
                break

    set_seed(best_seed)
    run(t, stop=True)