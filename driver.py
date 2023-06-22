import sys
from rubiks_cube import RubiksCube, CubeState
from space_search import solve

if __name__ == '__main__':

    # Driver Code

    if len(sys.argv) != 2:
        raise Exception(f"Number of arguments expected is: 2. Got {len(sys.argv)}.")

    k = 1
    try:
        k = int(sys.argv[1])
    except ValueError:
        print("An integer was expected as an argument.")

    cube1 = CubeState(RubiksCube.give_me_cube(18))


    def is_solved(cube_state: CubeState) -> bool:
        return RubiksCube.count_solved_faces(cube_state.get_cube()) >= k


    def heuristic(cube_state: CubeState) -> float:
        return RubiksCube.heuristic(cube_state.get_cube())


    def d(parent, child):
        return 1


    solution = solve(cube1, is_solved, heuristic, d)

    for state in solution:
        print("=================")
        RubiksCube.print_cube(state.get_cube())

    print("=================")
    print(f"Sequence of rotations to solve {k} faces of the cube:")
    for i in range(1, len(solution)):
        print(solution[i].get_parent_operation(), end=". ")

    print("\n=================")
