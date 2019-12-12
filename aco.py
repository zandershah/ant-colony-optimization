from enum import Enum, auto

class AntColony:
    class Variation(Enum):
        ANT_SYSTEM = auto()
        ANT_COLONY_SYSTEM = auto()
        ELITIST_ANT_SYSTEM = auto()
        MAXMIN_ANT_SYSTEM = auto()
        RANKBASED_ANT_SYSTEM = auto()

    def __init__(self, variation: Variation):
        self.variation = variation
        self.terminate = False

    def _generate_solutions(self) -> None:
        pass

    def _daemon_actions(self) -> None:
        pass

    def _update_pheremones(self) -> None:
        pass

    def solve(self):
        while not self.terminate: # TODO: Replace with termination criteria.
            self._generate_solutions()
            self._daemon_actions()
            self._update_pheremones()

        return self.best_solution
