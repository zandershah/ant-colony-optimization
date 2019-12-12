from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, List, Tuple, NamedTuple
from collections import defaultdict
import numpy as np # type: ignore

class AntColony:
    class Variation(Enum):
        ANT_SYSTEM = auto()
        ANT_COLONY_SYSTEM = auto()
        ELITIST_ANT_SYSTEM = auto()
        MAXMIN_ANT_SYSTEM = auto()
        RANKBASED_ANT_SYSTEM = auto()


    @dataclass
    class Settings:
        alpha: float = 0.5 # Control the influence of pheremone.
        beta: float = 1.2 # Control the influence of a priori knowledge (inverse distance).
        rho: float = 0.4 # Pheremone evaporation constant.
        Q: float = 500 # Pheremone deposited on a path.
        ants: int = 50 # Number of ants.
        iterations: int = 100


    class Trail(NamedTuple):
        path: List[Any]
        distance: float


    def __init__(self, variation: Variation = Variation.ANT_SYSTEM,
                 settings: Settings = Settings()):
        self.variation = variation
        self.settings = settings

        # Map from edges to amount of pheremone. Edges are given as state tuples.
        self.pheremones: Dict[Any, float] = defaultdict(lambda: settings.Q)

    def _generate_solution(self, initial_state, successors_fn, goal_fn) -> Trail:
        """Walk an ant through the graph, returning the path and the distance."""
        path = [initial_state]
        distance = 0.0

        while not goal_fn(path[-1]):
            successors: List[Tuple[Any, float]] = successors_fn(path[-1])

            desirability = [
                pow(self.pheremones[(path[-1], next_state)],
                    self.settings.alpha) *
                pow(1 / dist, self.settings.beta)
                for next_state, dist in successors]

            # Normalize desirability.
            total = sum(desirability)
            desirability = [d / total for d in desirability]

            successor = np.random.choice(range(len(successors)), p=desirability)
            next_state, dist = successors[successor]

            path.append(next_state)
            distance += dist

        return AntColony.Trail(path, distance)

    def _daemon_actions(self, trails: List[Trail]) -> None:
        pass 

    def _update_pheremones(self, trails: List[Trail]) -> None:
        """Update pheremones based on trails.

        Pheremones evaporate based on the given constant rho.
        For every trail, pheremones are deposited along the edges, weighted by
        the inverse length of the path.
        """
        for edge in self.pheremones:
            self.pheremones[edge] *= (1 - self.settings.rho)

        for path, distance in trails:
            for i in range(len(path) - 1):
                self.pheremones[(path[i], path[i + 1])] += self.settings.Q / distance

    def solve(self, initial_state: Any, successors_fn, goal_fn):
        self.best_solution = AntColony.Trail([], float('inf'))

        for _ in range(self.settings.iterations):
            trails: List[AntColony.Trail] = []

            # TODO: Parallelize.
            for ant in range(self.settings.ants):
                trail = self._generate_solution(initial_state, successors_fn, goal_fn)
                trails.append(trail)

                if trail.distance < self.best_solution.distance:
                    self.best_solution = trail

            self._daemon_actions(trails)
            self._update_pheremones(trails)

        return self.best_solution
