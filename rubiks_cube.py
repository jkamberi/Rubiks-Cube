import random
from random import shuffle
from enum import Enum
from copy import deepcopy
from typing import List, Tuple, Union
from space_search import State


class Color(Enum):
    RED: int = 1
    WHITE: int = 2
    GREEN: int = 3
    BLUE: int = 4
    YELLOW: int = 5
    ORANGE: int = 6


class ColorShape(Enum):
    RED = '🟥'
    WHITE = '⬜'
    GREEN = '🟩'
    BLUE = '🟦'
    YELLOW = '🟨'
    ORANGE = '🟧'


FRONT_FACE: int = 0
BACK_FACE: int = 1
RIGHT_FACE: int = 2
LEFT_FACE: int = 3
UPPER_FACE: int = 4
DOWN_FACE: int = 5

SOLVED_CUBE = [[[1, 1, 1], [1, 1, 1], [1, 1, 1]], [[2, 2, 2], [2, 2, 2], [2, 2, 2]],
               [[3, 3, 3], [3, 3, 3], [3, 3, 3]], [[4, 4, 4], [4, 4, 4], [4, 4, 4]],
               [[5, 5, 5], [5, 5, 5], [5, 5, 5]], [[6, 6, 6], [6, 6, 6], [6, 6, 6]]]

all_cube_operations = ['up_clockwise', 'up_counterclockwise', 'down_clockwise',
                       'down_counterclockwise', 'back_clockwise', 'back_counterclockwise',
                       'front_clockwise', 'front_counterclockwise', 'left_clockwise',
                       'left_counterclockwise', 'right_clockwise', 'right_counterclockwise']

# These 2 sets have faces that are completely opposite to each other.
first_set = {'up', 'left', 'front'}
second_set = {'down', 'right', 'back'}


class CubeState(State):

    def __init__(self, cube: List):
        self._cube = CubeState._get_cube_state(cube)
        self._cube_list = cube
        self._g_score = 0
        self._h_score = 0
        self._parent = None  # Parent state
        self._parent_operation = None  # Operation that was applied to parent and led to current state
        self._prohibit_operation = None

    def __hash__(self) -> int:
        return hash(self._cube)

    def __eq__(self, other: 'CubeState') -> bool:
        return self._cube == other._cube

    def __lt__(self, other: 'CubeState'):
        return self._h_score + self._g_score < other._h_score + other._g_score

    def get_children(self) -> List['CubeState']:
        return self._get_children_states()

    def get_g_score(self) -> Union[float, int]:
        return self._g_score

    def get_h_score(self) -> Union[float, int]:
        return self._h_score

    def set_g_score(self, score: Union[float, int]) -> None:
        self._g_score = score

    def set_h_score(self, score: Union[float, int]) -> None:
        self._h_score = score

    def get_parent(self) -> 'CubeState':
        return self._parent

    def set_parent(self, state: 'CubeState') -> None:
        self._parent = state

    def get_cube(self):
        return self._cube_list

    def get_parent_operation(self):
        return self._parent_operation

    @staticmethod
    def _get_cube_state(cube: List) -> Tuple:
        """
        :return: a tuple of the actual values (current state of the cube)
        """
        return tuple([cube[i][j][k] for k in range(3) for j in range(3) for i in range(6)])

    @staticmethod
    def _are_operations_opposite(o1: str, o2: str) -> bool:
        s = {o1, o2}
        if 'up_clockwise' in s and 'up_counterclockwise' in s:
            return True
        elif 'down_clockwise' in s and 'down_counterclockwise' in s:
            return True
        elif 'back_clockwise' in s and 'back_counterclockwise' in s:
            return True
        elif 'front_clockwise' in s and 'front_counterclockwise' in s:
            return True
        elif 'left_clockwise' in s and 'left_counterclockwise' in s:
            return True
        elif 'right_clockwise' in s and 'right_counterclockwise' in s:
            return True

        return False

    @staticmethod
    def _are_faces_opposite(f1: str, f2: str):
        s = {f1, f2}
        if 'up' in s and 'down' in s:
            return True
        if 'left' in s and 'right' in s:
            return True
        if 'front' in s and 'back' in s:
            return True

        return False

    def _get_children_states(self):

        children = []
        for operation in all_cube_operations:

            if self._parent_operation is not None:
                # Check if we do an operation that leads us to our parent state.
                if CubeState._are_operations_opposite(self._parent_operation, operation):
                    continue

                # Let's say we make 2 opposite side rotations, for example U and D. We end up in the exact same state if
                # we first did D and then U. That's why we need to prune one of these branches.
                parent_op_face = self._parent_operation.split('_')[0]
                if parent_op_face in second_set:
                    op_face = operation.split('_')[0]
                    if CubeState._are_faces_opposite(op_face, parent_op_face):
                        continue

            # If we try to perform the same operation for the 3rd time
            if self._prohibit_operation is not None and self._prohibit_operation == operation:
                continue

            cube_copy = deepcopy(self._cube_list)
            try:
                op = getattr(RubiksCube, operation)
                op(cube_copy)

                new_state = CubeState(cube_copy)

                # If we have already done the same operation twice, we need to prohibit the child from doing it again.
                if self._parent_operation is not None and self._parent_operation == operation:
                    new_state._prohibit_operation = operation

                new_state._parent_operation = operation
                children.append(new_state)

            except AttributeError:
                print(f"Attribute not found for operation {operation}")

        return children


class RubiksCube:

    @staticmethod
    def give_me_cube(random_rotations=10) -> List:
        new_cube = list(SOLVED_CUBE)
        RubiksCube.shuffle_cube(new_cube, random_rotations)
        return new_cube

    @staticmethod
    def shuffle_cube(cube, number_of_rotations=50) -> None:
        functions_on_cube = [RubiksCube.up_clockwise, RubiksCube.up_counterclockwise, RubiksCube.down_clockwise,
                             RubiksCube.down_counterclockwise, RubiksCube.back_clockwise,
                             RubiksCube.back_counterclockwise,
                             RubiksCube.front_clockwise, RubiksCube.front_counterclockwise, RubiksCube.left_clockwise,
                             RubiksCube.left_counterclockwise, RubiksCube.right_clockwise,
                             RubiksCube.right_counterclockwise]

        l = len(functions_on_cube)

        for i in range(number_of_rotations):
            functions_on_cube[random.randint(0, l - 1)](cube)

    @staticmethod
    def count_solved_faces(cube: List) -> int:
        """
        Iterates over the cube and calculates the number of faces that have already been solved.
        :return: Number of solved cube faces.
        """
        count = 0
        for i in range(6):
            flag = True
            for j in range(3):
                for k in range(3):
                    if cube[i][j][k] != cube[i][0][0]:
                        flag = False
            if flag:
                count += 1

        return count

    @staticmethod
    def heuristic3(current: List) -> float:
        cost = 0

        for i in range(3):
            for j in range(3):
                if current[BACK_FACE][i][j] == 1:
                    cost += 2

                if current[LEFT_FACE][i][j] == 1:
                    if i == 0 or i == 2:
                        cost += 1
                    else:
                        cost += 2

                if current[RIGHT_FACE][i][j] == 1:
                    if i == 0 or i == 2:
                        cost += 1
                    else:
                        cost += 2

                if current[DOWN_FACE][i][j] == 1:
                    if j == 0 or j == 2:
                        cost += 1
                    else:
                        cost += 2

                if current[UPPER_FACE][i][j] == 1:
                    if j == 0 or j == 2:
                        cost += 1
                    else:
                        cost += 2

        return cost / 8

    @staticmethod
    def heuristic2(current: List) -> float:
        total = 0
        for i in range(3):
            for j in range(3):
                if i != 1 and j != 1:
                    if current[FRONT_FACE][i][j] == 2:
                        total += 2
                    elif current[FRONT_FACE][i][j] != 2:
                        total += 1

                    if current[BACK_FACE][i][j] == 1:
                        total += 2
                    elif current[BACK_FACE][i][j] != 1:
                        total += 1

                    if current[RIGHT_FACE][i][j] == 4:
                        total += 2
                    elif current[RIGHT_FACE][i][j] != 4:
                        total += 1

                    if current[LEFT_FACE][i][j] == 3:
                        total += 2
                    elif current[LEFT_FACE][i][j] != 3:
                        total += 1

                    if current[UPPER_FACE][i][j] == 6:
                        total += 2
                    elif current[UPPER_FACE][i][j] != 6:
                        total += 1

                    if current[DOWN_FACE][i][j] == 5:
                        total += 2
                    elif current[DOWN_FACE][i][j] != 5:
                        total += 1

        return total / 8

    @staticmethod
    def heuristic(current: List) -> float:
        def is_edge(row, col):
            return (row == 1 and col == 0) or (row == 0 and col == 1) or (row == 1 and col == 2) or (
                    row == 2 and col == 1)

        def left_and_right(face, opposite_face_number, i, j):
            s = 0
            if current[face][i][j] == opposite_face_number:
                s += 2
            else:
                if i == 0 or i == 2:
                    if current[face][i][j] in [1, 2]:
                        s += 1
                    elif current[face][i][j] in [5, 6]:
                        s += 2
                else:
                    if current[face][i][j] in [1, 2]:
                        s += 2
                    elif current[face][i][j] in [5, 6]:
                        s += 1

            return s

        def up_and_down(face, opposite_face_number, i, j):
            s = 0
            if current[face][i][j] == opposite_face_number:
                s += 2
            else:
                if i == 0 or i == 2:
                    if current[face][i][j] in [3, 4]:
                        s += 1
                    elif current[face][i][j] in [1, 2]:
                        s += 2
                else:
                    if current[face][i][j] in [3, 4]:
                        s += 2
                    elif current[face][i][j] in [1, 2]:
                        s += 1

            return s

        def front_and_back(face, opposite_face_number, i, j):
            s = 0
            if current[face][i][j] == opposite_face_number:
                s += 2
            else:
                if i == 0 or i == 2:
                    if current[face][i][j] in [3, 4]:
                        s += 1
                    elif current[face][i][j] in [5, 6]:
                        s += 2
                else:
                    if current[face][i][j] in [3, 4]:
                        s += 2
                    elif current[face][i][j] in [5, 6]:
                        s += 1

            return s

        total = 0
        for i in range(3):
            for j in range(3):
                if is_edge(i, j):
                    total += left_and_right(LEFT_FACE, 3, i, j)
                    total += left_and_right(RIGHT_FACE, 4, i, j)
                    total += up_and_down(UPPER_FACE, 6, i, j)
                    total += up_and_down(DOWN_FACE, 5, i, j)
                    total += front_and_back(FRONT_FACE, 2, i, j)
                    total += front_and_back(BACK_FACE, 1, i, j)

        return total / 4

    @staticmethod
    def _print_face(cube: List, face: int, message: str) -> None:
        if message:
            print(message)

        if face > 5 or face < 0:
            raise Exception("Invalid face")

        for row in cube[face]:

            for i in row:
                print(ColorShape[Color(i).name].value, end=" ")

            print("")

    @staticmethod
    def print_cube(cube: List) -> None:

        RubiksCube._print_face(cube, UPPER_FACE, "Upper Face")
        RubiksCube._print_face(cube, LEFT_FACE, "Left Face")
        RubiksCube._print_face(cube, FRONT_FACE, "Front Face")
        RubiksCube._print_face(cube, RIGHT_FACE, "Right Face")
        RubiksCube._print_face(cube, BACK_FACE, "Back Face")
        RubiksCube._print_face(cube, DOWN_FACE, "Down Face")

    @staticmethod
    def up_clockwise(cube: List) -> None:
        RubiksCube.rotate_row_faces_clockwise(cube, row=0)
        RubiksCube.rotate_face_clockwise(cube, UPPER_FACE)

    @staticmethod
    def up_counterclockwise(cube: List) -> None:
        RubiksCube.rotate_row_faces_counter_clockwise(cube, row=0)
        RubiksCube.rotate_face_counter_clockwise(cube, UPPER_FACE)

    @staticmethod
    def right_clockwise(cube: List) -> None:
        RubiksCube.rotate_column_clockwise_yaxis(cube, 2)
        RubiksCube.rotate_face_clockwise(cube, RIGHT_FACE)

    @staticmethod
    def right_counterclockwise(cube: List) -> None:
        RubiksCube.rotate_column_counter_clockwise_yaxis(cube, 2)
        RubiksCube.rotate_face_counter_clockwise(cube, RIGHT_FACE)

    @staticmethod
    def left_clockwise(cube: List) -> None:
        RubiksCube.rotate_column_counter_clockwise_yaxis(cube, 0)
        RubiksCube.rotate_face_clockwise(cube, LEFT_FACE)

    @staticmethod
    def left_counterclockwise(cube: List) -> None:
        RubiksCube.rotate_column_clockwise_yaxis(cube, 0)
        RubiksCube.rotate_face_counter_clockwise(cube, LEFT_FACE)

    @staticmethod
    def front_clockwise(cube: List) -> None:
        RubiksCube.rotate_column_clockwise_xaxis(cube, 0)
        RubiksCube.rotate_face_clockwise(cube, FRONT_FACE)

    @staticmethod
    def front_counterclockwise(cube: List) -> None:
        RubiksCube.rotate_column_counter_clockwise_xaxis(cube, 0)
        RubiksCube.rotate_face_counter_clockwise(cube, FRONT_FACE)

    @staticmethod
    def back_clockwise(cube: List) -> None:
        RubiksCube.rotate_column_counter_clockwise_xaxis(cube, 2)
        RubiksCube.rotate_face_clockwise(cube, BACK_FACE)

    @staticmethod
    def back_counterclockwise(cube: List) -> None:
        RubiksCube.rotate_column_clockwise_xaxis(cube, 2)
        RubiksCube.rotate_face_counter_clockwise(cube, BACK_FACE)

    @staticmethod
    def down_clockwise(cube: List) -> None:
        RubiksCube.rotate_row_faces_counter_clockwise(cube, row=2)
        RubiksCube.rotate_face_clockwise(cube, DOWN_FACE)

    @staticmethod
    def down_counterclockwise(cube: List) -> None:
        RubiksCube.rotate_row_faces_clockwise(cube, row=2)
        RubiksCube.rotate_face_counter_clockwise(cube, DOWN_FACE)

    @staticmethod
    def rotate_column_clockwise_xaxis(cube: List, column: int) -> None:
        if column > 2 or column < 0:
            raise Exception("Invalid column number")

        cube[RIGHT_FACE][0][column], \
        cube[UPPER_FACE][2 - column][0], \
        cube[LEFT_FACE][2][2 - column], \
        cube[DOWN_FACE][column][2] = \
            cube[UPPER_FACE][2 - column][0], \
            cube[LEFT_FACE][2][2 - column], \
            cube[DOWN_FACE][column][2], \
            cube[RIGHT_FACE][0][column]

        cube[RIGHT_FACE][1][column], \
        cube[UPPER_FACE][2 - column][1], \
        cube[LEFT_FACE][1][2 - column], \
        cube[DOWN_FACE][column][1] = \
            cube[UPPER_FACE][2 - column][1], \
            cube[LEFT_FACE][1][2 - column], \
            cube[DOWN_FACE][column][1], \
            cube[RIGHT_FACE][1][column]

        cube[RIGHT_FACE][2][column], \
        cube[UPPER_FACE][2 - column][2], \
        cube[LEFT_FACE][0][2 - column], \
        cube[DOWN_FACE][column][0] = \
            cube[UPPER_FACE][2 - column][2], \
            cube[LEFT_FACE][0][2 - column], \
            cube[DOWN_FACE][column][0], \
            cube[RIGHT_FACE][2][column]

    @staticmethod
    def rotate_column_counter_clockwise_xaxis(cube: List, column: int) -> None:

        if column > 2 or column < 0:
            raise Exception("Invalid column number")

        cube[RIGHT_FACE][0][column], \
        cube[UPPER_FACE][2 - column][0], \
        cube[LEFT_FACE][2][2 - column], \
        cube[DOWN_FACE][column][2] = \
            cube[DOWN_FACE][column][2], \
            cube[RIGHT_FACE][0][column], \
            cube[UPPER_FACE][2 - column][0], \
            cube[LEFT_FACE][2][2 - column]

        cube[RIGHT_FACE][1][column], \
        cube[UPPER_FACE][2 - column][1], \
        cube[LEFT_FACE][1][2 - column], \
        cube[DOWN_FACE][column][1] = \
            cube[DOWN_FACE][column][1], \
            cube[RIGHT_FACE][1][column], \
            cube[UPPER_FACE][2 - column][1], \
            cube[LEFT_FACE][1][2 - column]

        cube[RIGHT_FACE][2][column], \
        cube[UPPER_FACE][2 - column][2], \
        cube[LEFT_FACE][0][2 - column], \
        cube[DOWN_FACE][column][0] = \
            cube[DOWN_FACE][column][0], \
            cube[RIGHT_FACE][2][column], \
            cube[UPPER_FACE][2 - column][2], \
            cube[LEFT_FACE][0][2 - column]

    @staticmethod
    def rotate_column_clockwise_yaxis(cube: List, column: int) -> None:
        if column > 2 or column < 0:
            raise Exception("Invalid column number")

        cube[UPPER_FACE][0][column], \
        cube[BACK_FACE][0][column], \
        cube[DOWN_FACE][0][column], \
        cube[FRONT_FACE][0][column], = \
            cube[FRONT_FACE][0][column], \
            cube[UPPER_FACE][0][column], \
            cube[BACK_FACE][0][column], \
            cube[DOWN_FACE][0][column]

        cube[UPPER_FACE][1][column], \
        cube[BACK_FACE][1][column], \
        cube[DOWN_FACE][1][column], \
        cube[FRONT_FACE][1][column], = \
            cube[FRONT_FACE][1][column], \
            cube[UPPER_FACE][1][column], \
            cube[BACK_FACE][1][column], \
            cube[DOWN_FACE][1][column]

        cube[UPPER_FACE][2][column], \
        cube[BACK_FACE][2][column], \
        cube[DOWN_FACE][2][column], \
        cube[FRONT_FACE][2][column], = \
            cube[FRONT_FACE][2][column], \
            cube[UPPER_FACE][2][column], \
            cube[BACK_FACE][2][column], \
            cube[DOWN_FACE][2][column]

    @staticmethod
    def rotate_column_counter_clockwise_yaxis(cube: List, column: int) -> None:
        if column > 2 or column < 0:
            raise Exception("Invalid column number")

        cube[UPPER_FACE][0][column], \
        cube[BACK_FACE][0][column], \
        cube[DOWN_FACE][0][column], \
        cube[FRONT_FACE][0][column], = \
            cube[BACK_FACE][0][column], \
            cube[DOWN_FACE][0][column], \
            cube[FRONT_FACE][0][column], \
            cube[UPPER_FACE][0][column]

        cube[UPPER_FACE][1][column], \
        cube[BACK_FACE][1][column], \
        cube[DOWN_FACE][1][column], \
        cube[FRONT_FACE][1][column], = \
            cube[BACK_FACE][1][column], \
            cube[DOWN_FACE][1][column], \
            cube[FRONT_FACE][1][column], \
            cube[UPPER_FACE][1][column]

        cube[UPPER_FACE][2][column], \
        cube[BACK_FACE][2][column], \
        cube[DOWN_FACE][2][column], \
        cube[FRONT_FACE][2][column], = \
            cube[BACK_FACE][2][column], \
            cube[DOWN_FACE][2][column], \
            cube[FRONT_FACE][2][column], \
            cube[UPPER_FACE][2][column]

    @staticmethod
    def rotate_row_faces_clockwise(cube: List, row: int) -> None:
        if row > 2 or row < 0:
            raise Exception("Invalid column number")
        cube[LEFT_FACE][row][0], \
        cube[BACK_FACE][row][0], \
        cube[RIGHT_FACE][row][0], \
        cube[FRONT_FACE][row][0] = \
            cube[FRONT_FACE][row][0], \
            cube[LEFT_FACE][row][0], \
            cube[BACK_FACE][row][0], \
            cube[RIGHT_FACE][row][0]

        cube[LEFT_FACE][row][1], \
        cube[BACK_FACE][row][1], \
        cube[RIGHT_FACE][row][1], \
        cube[FRONT_FACE][row][1] = \
            cube[FRONT_FACE][row][1], \
            cube[LEFT_FACE][row][1], \
            cube[BACK_FACE][row][1], \
            cube[RIGHT_FACE][row][1]

        cube[LEFT_FACE][row][2], \
        cube[BACK_FACE][row][2], \
        cube[RIGHT_FACE][row][2], \
        cube[FRONT_FACE][row][2] = \
            cube[FRONT_FACE][row][2], \
            cube[LEFT_FACE][row][2], \
            cube[BACK_FACE][row][2], \
            cube[RIGHT_FACE][row][2]

    @staticmethod
    def rotate_row_faces_counter_clockwise(cube: List, row: int) -> None:
        if row > 2 or row < 0:
            raise Exception("Invalid column number")
        cube[LEFT_FACE][row][0], \
        cube[BACK_FACE][row][0], \
        cube[RIGHT_FACE][row][0], \
        cube[FRONT_FACE][row][0] = \
            cube[BACK_FACE][row][0], \
            cube[RIGHT_FACE][row][0], \
            cube[FRONT_FACE][row][0], \
            cube[LEFT_FACE][row][0]

        cube[LEFT_FACE][row][1], \
        cube[BACK_FACE][row][1], \
        cube[RIGHT_FACE][row][1], \
        cube[FRONT_FACE][row][1] = \
            cube[BACK_FACE][row][1], \
            cube[RIGHT_FACE][row][1], \
            cube[FRONT_FACE][row][1], \
            cube[LEFT_FACE][row][1]

        cube[LEFT_FACE][row][2], \
        cube[BACK_FACE][row][2], \
        cube[RIGHT_FACE][row][2], \
        cube[FRONT_FACE][row][2] = \
            cube[BACK_FACE][row][2], \
            cube[RIGHT_FACE][row][2], \
            cube[FRONT_FACE][row][2], \
            cube[LEFT_FACE][row][2]

    @staticmethod
    def rotate_face_clockwise(cube: List, face: int) -> None:
        if face > 5 or face < 0:
            raise Exception("Invalid face")
        cube[face][2][2], \
        cube[face][2][0], \
        cube[face][0][0], \
        cube[face][0][2] = \
            cube[face][0][2], \
            cube[face][2][2], \
            cube[face][2][0], \
            cube[face][0][0]

        cube[face][2][1], \
        cube[face][1][0], \
        cube[face][0][1], \
        cube[face][1][2] = \
            cube[face][1][2], \
            cube[face][2][1], \
            cube[face][1][0], \
            cube[face][0][1]

    @staticmethod
    def rotate_face_counter_clockwise(cube: List, face: int) -> None:
        if face > 5 or face < 0:
            raise Exception("Invalid face")

        cube[face][2][2], \
        cube[face][2][0], \
        cube[face][0][0], \
        cube[face][0][2] = \
            cube[face][2][0], \
            cube[face][0][0], \
            cube[face][0][2], \
            cube[face][2][2]

        cube[face][2][1], \
        cube[face][1][0], \
        cube[face][0][1], \
        cube[face][1][2] = \
            cube[face][1][0], \
            cube[face][0][1], \
            cube[face][1][2], \
            cube[face][2][1]
