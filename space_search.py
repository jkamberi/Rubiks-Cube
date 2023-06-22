from abc import abstractmethod, ABC
from typing import List, Union, Callable
from queue import PriorityQueue


class State(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """
        Useful when we want to place objects of this class inside a set.
        :return: A unique hash value.
        """
        pass

    @abstractmethod
    def __eq__(self, other: 'State') -> bool:
        """
        If two objects represent the same state this method returns True.
        :param other:
        :return: boolean
        """
        pass

    @abstractmethod
    def __lt__(self, other: 'State') -> bool:
        """
        Compares two State objects in terms of their f-score. F-score calculation depends on classes derived from State.
        Useful for priority queue used by A* algorithm.
        :param other:
        :return: boolean value.
        """
        pass

    @abstractmethod
    def get_children(self) -> List['State']:
        """
        :return: A list of objects of type State. These objects come directly from a parent state.
        """
        pass

    @abstractmethod
    def get_g_score(self) -> Union[float, int]:
        pass

    @abstractmethod
    def get_h_score(self) -> Union[float, int]:
        pass

    @abstractmethod
    def set_g_score(self, score: Union[float, int]) -> None:
        pass

    @abstractmethod
    def set_h_score(self, score: Union[float, int]) -> None:
        pass

    @abstractmethod
    def get_parent(self) -> 'State':
        pass

    @abstractmethod
    def set_parent(self, state: 'State') -> None:
        pass


# A* Algorithm
def solve(start: State, is_goal: Callable, h: Callable, d: Callable) -> List[State]:
    """
    Function that uses A* Algorithm to find the best path to a solution.
    :param start: Object of type State.
    :param is_goal: Callable. A function that returns whether the current state is a final state or not.
    :param h: Callable. A heuristic function that estimates the cost between current state and final state.
    :param d: Callable. A function that returns the cost of the distance between parent and child states.
    :return:
    """
    if not isinstance(start, State):
        raise Exception("'start' must inherit from State class.")

    if not isinstance(is_goal, Callable):
        raise Exception("'is_goal' must be callable.")

    if not isinstance(h, Callable):
        raise Exception("'h' must be callable.")

    if not isinstance(d, Callable):
        raise Exception("'d' must be callable.")

    # Open set and q include states who have not been explored completely (Frontier). We use a combination of set and
    # priority queue to achieve access to minimum value in O(logn) time while adding and searching for an item in O(1)
    # time.
    open_set = set()
    q = PriorityQueue()

    # Closed set includes states whose all children have been explored.
    closed_set = set()

    start.set_g_score(0)
    start.set_h_score(h(start))

    open_set.add(start)
    q.put(start)

    print("Solving...")
    while open_set:

        # Find the state with the lowest f score in the open set (and priority queue)
        current_state = None
        if not q.empty():
            current_state = q.get()

        # If the current state is a goal, reconstruct the path and return
        if is_goal(current_state):
            reconstruct_path = []
            while current_state.get_parent() is not None:
                reconstruct_path.append(current_state)
                current_state = current_state.get_parent()

            reconstruct_path.append(current_state)
            reconstruct_path.reverse()
            return reconstruct_path

        open_set.remove(current_state)
        closed_set.add(current_state)

        # Iterate over current state's children
        for child in current_state.get_children():
            if child in closed_set:
                continue

            if child in open_set:
                # The cost between parent and child is the current cost from the root plus the cost between parent
                # and child.
                tentative_g_score = current_state.get_g_score() + d(current_state, child)
                if tentative_g_score < child.get_g_score():
                    # We found a better path. Update the parent.
                    child.set_g_score(tentative_g_score)
                    child.set_parent(current_state)
            else:
                child.set_g_score(current_state.get_g_score() + d(current_state, child))
                child.set_h_score(h(child))
                child.set_parent(current_state)
                open_set.add(child)
                q.put(child)

    raise Exception("Algorithm failed to find a solution.")
