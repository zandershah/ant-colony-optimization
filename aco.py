from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, List, Tuple, NamedTuple
from collections import defaultdict
from operator import attrgetter
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
        elitist: float = 2.0 # Pheromone deposited by elitist on a path
        rho: float = 0.4 # Pheremone evaporation constant.
        Q: float = 500 # Pheremone deposited on a path.
        max_limit: float = float('inf') # Maximum amount of pheromone on a path
        min_limit: float = 0 # Minimum amount of pheromone on a path
        rank_cutoff: int = 3 # Rank cut off for rank-based ant system
        ants: int = 50 # Number of ants
        iterations: int = 100


    class Trail(NamedTuple):
        path: List[Any]
        distance: float


    def __init__(self, variation: Variation = Variation.ANT_SYSTEM,
                 settings: Settings = Settings()):
        self.variation = variation
        self.settings = settings

        # Map from edges to amount of pheromone. Edges are given as state tuples.
        self.pheromones: Dict[Any, float] = defaultdict(lambda: settings.max_limit if variation == self.Variation.MAXMIN_ANT_SYSTEM else settings.Q)

    def _generate_solution(self, initial_state, successors_fn, goal_fn) -> Trail:
        """Walk an ant through the graph, returning the path and the distance."""
        path = [initial_state]
        distance = 0.0

        while not goal_fn(path[-1]):
            successors: List[Tuple[Any, float]] = successors_fn(path[-1])

            desirability = [
                pow(self.pheromones[(path[-1], next_state)],
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

    def _deposit_pheromones(self, trail, is_elitist = False, is_max_min = False) -> None:
        path, distance = trail
        amount = self.settings.elitist if is_elitist else self.settings.Q
        for i in range(len(path) - 1):
            if is_max_min:
                self.pheromones[(path[i], path[i + 1])] += max(self.settings.min_limit, min(self.settings.max_limit, amount / distance))
            else:
                self.pheromones[(path[i], path[i + 1])] += amount / distance

    def _update_pheromones(self, trails: List[Trail]) -> None:
        """Update pheromones based on trails.

        pheromones evaporate based on the given constant rho.
        For every trail, pheromones are deposited along the edges, weighted by
        the inverse length of the path.
        """
        # Pheromones evaporates at the rate of rho per iteration
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.settings.rho)

        # Pheromones deposit
        if self.variation == self.Variation.ANT_SYSTEM:
            # Every ant's phermones is deposited
            for t in trails:
                self._deposit_pheromones(t)

        elif self.variation == self.Variation.ANT_COLONY_SYSTEM:
            # Only the best ant is allowed to deposit pheromones
            self._deposit_pheromones(self.best_solution)

        elif self.variation == self.Variation.ELITIST_ANT_SYSTEM:
            # Every ant's pheromones is deposited
            # Best solution has greater influence so can deposit a greater amount
            self._deposit_pheromones(self.best_solution, is_elitist = True)
            for t in trails:
                if t.distance == self.best_solution.distance:
                    continue
                self._deposit_pheromones(t)

        elif self.variation == self.Variation.MAXMIN_ANT_SYSTEM:
            # Only the best ant is allowed to deposit pheromones
            # The amount of pheromones on a path is limited to [max_limit, min_limit]
            self._deposit_pheromones(self.best_solution, is_max_min = True)

        elif self.variation == self.Variation.RANKBASED_ANT_SYSTEM:
            # Only top ranking solutions are allowed to deposit pheromones
            sorted_trails = sorted(trails, key=attrgetter('distance'))
            for r in range(self.settings.rank_cutoff):
                self._deposit_pheromones(sorted_trails[r])

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
            self._update_pheromones(trails)

        return self.best_solution
