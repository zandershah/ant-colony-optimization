from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Any, List, Tuple, NamedTuple, Optional
from collections import defaultdict
from operator import attrgetter
import numpy as np # type: ignore
import multiprocessing
from multiprocessing.pool import ThreadPool
import itertools

class AntColony:
    class Variation(Enum):
        ANT_SYSTEM = auto()
        ELITIST_ANT_SYSTEM = auto()
        MAXMIN_ANT_SYSTEM = auto()
        RANKBASED_ANT_SYSTEM = auto()


    @dataclass
    class Settings:
        alpha: float = 0.5 # Control the influence of pheromone.
        beta: float = 1.2 # Control the influence of a priori knowledge (inverse distance).
        rho: float = 0.4 # Pheromone evaporation constant.
        Q: float = 1 # Pheromone deposited on a path.
        elitist: int = 3 # Number of elitist ants for elitist and rank-based ant systems.
        ants: int = 50 # Number of ants.
        iterations: int = 100
        infinity: float = 1e9 # Initial value pheromone value for max min ant system.
        p_best: float = 0.05 # Probability of the best solution being taken at convergence for max min ant system.


    class Trail(NamedTuple):
        path: List[Any]
        distance: float


    def __init__(self, variation: Variation = Variation.ANT_SYSTEM,
                 settings: Settings = Settings()):
        self.variation = variation
        self.settings = settings

        # Pheromone limits for max min ant system.
        self.min_pheromones = 0.0
        self.max_pheromones = self.settings.infinity

        initial_pheromones = self.settings.Q
        if self.variation == AntColony.Variation.MAXMIN_ANT_SYSTEM:
            initial_pheromones = self.max_pheromones

        # Map from edges to amount of pheromone. Edges are given as state tuples.
        self.pheromones: Dict[Any, float] = defaultdict(lambda: initial_pheromones)

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

    def _deposit_pheromones(self, trail, is_elitist: bool = False,
                            rank: Optional[int] = None) -> None:
        """Deposit pheromones along the path. """
        path, distance = trail

        amount = self.settings.Q

        if self.variation == AntColony.Variation.ELITIST_ANT_SYSTEM and is_elitist:
            amount += self.settings.elitist
        if self.variation == AntColony.Variation.RANKBASED_ANT_SYSTEM and rank is not None:
            amount *= self.settings.elitist - rank

        for i in range(len(path) - 1):
            edge = (path[i], path[i + 1])
            self.pheromones[edge] += amount / distance

            if self.variation == AntColony.Variation.MAXMIN_ANT_SYSTEM:
                self.pheromones[edge] = np.clip(self.pheromones[edge], self.min_pheromones, self.max_pheromones)

    def _update_pheromones(self, trails: List[Trail]) -> None:
        """Update pheromones based on trails.

        pheromones evaporate based on the given constant rho.
        For every trail, pheromones are deposited along the edges, weighted by
        the inverse length of the path.
        """
        # Pheromones evaporates at the rate of rho per iteration
        for edge in self.pheromones:
            self.pheromones[edge] *= (1 - self.settings.rho)

            if self.variation == AntColony.Variation.MAXMIN_ANT_SYSTEM:
                self.pheromones[edge] = np.clip(self.pheromones[edge], self.min_pheromones, self.max_pheromones)

        # Pheromones deposit.
        if self.variation == self.Variation.ANT_SYSTEM:
            # Every ant's phermones is deposited.
            for t in trails:
                self._deposit_pheromones(t)

        elif self.variation == self.Variation.ELITIST_ANT_SYSTEM:
            # Every ant's pheromones is deposited.
            # Best solution deposits every iteration |self.settings.elitist| times.
            self._deposit_pheromones(self.best_solution, is_elitist=True)
            for t in trails:
                self._deposit_pheromones(t)

        elif self.variation == self.Variation.MAXMIN_ANT_SYSTEM:
            # Only the best ant is allowed to deposit pheromones. The amount of
            # pheromones on a path is limited to [min_pheromones, max_pheromones].
            self._deposit_pheromones(self.best_solution)

        elif self.variation == self.Variation.RANKBASED_ANT_SYSTEM:
            # Only top |self.settings.elitist| ranking solutions are allowed to
            # deposit pheromones. Deposit a linearly decreasing amount.
            sorted_trails = sorted(trails, key=attrgetter('distance'))
            for r in range(self.settings.elitist):
                self._deposit_pheromones(sorted_trails[r], rank=r)

    def solve(self, initial_state: Any, successors_fn, goal_fn) -> Trail:
        self.best_solution = AntColony.Trail([], float('inf'))

        for i in range(self.settings.iterations):
            pool = ThreadPool(multiprocessing.cpu_count())
            trails = pool.starmap(self._generate_solution, zip([initial_state] * self.Settings.ants,
                                                               itertools.repeat(successors_fn),
                                                               itertools.repeat(goal_fn)))

            for trail in trails:
                if trail.distance < self.best_solution.distance:
                    self.best_solution = trail

                    # Update bounds for max min ant system.
                    n_root = pow(self.settings.p_best, 1 / len(trail.path))
                    avg = len(trail.path) / 2

                    self.max_pheromones = 1 / (1 - self.settings.rho) * self.settings.Q / trail.distance
                    self.min_pheromones = self.max_pheromones * (1 - n_root) / (avg - 1) / n_root

                    # print(self.best_solution.distance, ' ', i, '/', self.settings.iterations)

            self._update_pheromones(trails)

        return self.best_solution
