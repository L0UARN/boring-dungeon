"""
Classes:
    - Mobile
"""

from source.core.tools import Position, Direction


class Mobile:
    """
    A mobile entity is an entity which can move inside a graph.
    """
    def __init__(self, position: Position, direction: Direction, graph: dict[Position, [Position]]) -> None:
        """
        :param position: The initial position of the entity inside of the graph.
        :param direction: The initial orientation of the entity.
        :param graph: The graph in which the entity will move.
        """
        self.position = position
        self.direction = direction
        self.graph = graph

    def step_in_direction(self, direction: Direction = None) -> bool:
        """ Moves 1 step in the specified direction. The entity's direction will be changed to match the direction of
        the latest step taken.

        :param direction: The direction in which the entity has to step.
        :return: True if the entity could step, False if not.
        """
        if direction is None:
            direction = self.direction
        else:
            self.direction = direction

        if self.position.next_in_direction(direction) in self.graph[self.position]:
            self.position = self.position.next_in_direction(direction)
            return True
        return False

    def move_towards(self, position: Position, teleport: bool = False) -> bool:
        """ Calculates a path to the specified position, then moves the entity 1 step towards the position if a valid
        path is found, or teleports the entity to the desired location if teleport is specified and the position is in
        the graph. The entity's direction will be changed to match the direction of the latest step taken.

        :param position: The position towards which the entity should step.
        :param teleport: Whether or not the entity should instantly be placed on the position, or should make 1 step.
        :return: True if the entity could step or teleport, False if not.
        """
        if teleport:
            if position in self.graph:
                self.direction = position.direction(self.position)
                self.position = position
                return True
            else:
                return False

        parents = {self.position: None}
        opened = [self.position]
        closed = []

        while opened:
            temp = opened.pop(0)
            if temp not in closed:
                closed.append(temp)

            for neighbor in self.graph[temp]:
                if neighbor not in opened and neighbor not in closed:
                    opened.append(neighbor)
                    parents[neighbor] = temp

        path = []
        point = position
        while parents[point] is not None:
            path = [point] + path
            point = parents[point]

        if path:
            self.direction = path[0].direction(self.position)
            self.position = path[0]
            return True
        return False
