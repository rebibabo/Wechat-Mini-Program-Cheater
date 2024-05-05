import numpy as np
import copy

class Table:
    def __init__(self, str):
        self.table = []
        self.row_state = [0] * 9
        self.col_state = [0] * 9
        self.cell_state = [0] * 9
        self.grade = 0
        for line in str.split('\n'):
            if not line:
                continue
            line = list(map(int, line.strip().split(' ')))
            self.table.append(line)
        for i in range(9):
            for j in range(9):
                if self.table[i][j] != 0:
                    self.set_state(i, j, self.table[i][j])
        self.table = np.array(self.table)

    def set_state(self, i, j, num):
        self.grade += 1
        self.table[i][j] = num
        self.row_state[i] |= 1 << num
        self.col_state[j] |= 1 << num
        self.cell_state[i//3*3+j//3] |= 1 << num

    def get_state(self, i, j):
        state = []
        for num in range(1, 10):
            if self.row_state[i] & 1 << num == 0 and self.col_state[j] & 1 << num == 0 and self.cell_state[i//3*3+j//3] & 1 << num == 0:
                state.append(num)
        return state

    # def step(self):
    #     for i in range(9):
    #         for j in range(9):
    #             if len(self.get_state(i, j)) == 1 and self.table[i][j] == 0:
    #                 num = self.get_state(i, j)[0]
    #                 self.set_state(i, j, num)
    #                 return False 
    #     return True

    def __str__(self):
        str = ''
        for i in range(9):
            for j in range(9):
                if self.table[i][j] == 0:
                    str += '  '
                else:
                    str += f'{self.table[i][j]:2}'
                if j in [2, 5]:
                    str += ' |'
            if i in [2, 5]:
                str += '\n-------+-------+-------'
            str += '\n'
        return str


if __name__ == '__main__':
    str = '''
9 0 0 0 0 0 0 0 0 
8 0 0 0 0 4 7 0 0 
4 0 3 0 6 5 0 0 1
0 0 0 0 0 0 0 5 0
0 0 2 9 0 0 0 8 0
0 0 8 0 7 0 0 0 3
6 0 0 0 0 0 4 7 0 
0 3 0 0 0 0 0 0 2
0 1 0 0 0 6 0 0 0 
'''
    table = Table(str)
    queue = [table]
    while queue:
        table = queue.pop(0)
        # print(table)
        # input(table.grade)
        if table.grade == 81:
            print(table)
            break
        only = False
        states = {}
        for i in range(9):
            for j in range(9):
                state = table.get_state(i, j)
                if table.table[i][j] == 0:
                    if state:
                        states[(i, j)] = state
                    if len(state) == 1:
                        num = table.get_state(i, j)[0]
                        table.set_state(i, j, num)
                        queue.append(table)
                        only = True
        if not only:
            for (i, j), state in states.items():
                if len(state) == 2:
                    for num in state:
                        new_table = copy.deepcopy(table)
                        new_table.set_state(i, j, num)
                        queue.append(new_table)
