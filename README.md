Ant Colony Optimization
=======================

Implementation of popular variations for the Ant Colony Optimization algorithm in Python. For use in approximating TSP.

Waterloo CS 486 / 686 final project.

## Usage

`AntColony` class takes in the desired variation and settings on construction.

`solve(self, initial_state, successor_fn, goal_fn)` implements the algorithm.

- `initial_state`: Arbitrary hashable type `T`, representing the state.
- `successor_fn`: Maps `T` to `List[Tuple[T, float]]`, representing every possible successor and their corresponding edge weights.
- `goal_fn`: Maps `T` to `bool`, representing whether the inputted state is a terminal state.

`tsp.py` contains a sample implementation of the required functions to forumate TSP. Uses bitlists to represent the state.

```python
from aco import AntColony
from tsp import TSP

# TSP Initialization
cities: List[TSP.City] = [TSP.City('A', 0, 0), TSP.City('B', 1, 1)]
tsp = TSP(cities)

initial_state = TSP.State(1 << 0, 0)

# Ant Colony Initialization
variation = AntColony.Variation.ANT_SYSTEM

settings = AntColony.Settings()
# Modify default settings.
settings.alpha = 0.5

colony = AntColony(variation, settings)

# Solve using TSP functions.
solution = colony.solve(initial_state, tsp.successors, tsp.goal)

path = solution.path
distance = solution.distance
```

## Variations

### Elitist Ant System
- `|Settings.elitist|` ants with become elitist and always deposit pheromones along the global best solution.
- All ants still deposit their pheromones along their paths

### Max-Min Ant System [7]
- The amount of pheromones being deposited on a path is bounded by [l<sub>min</sub>, l<sub>max</sub>]
- Only the best global solution will deposit pheromones along its path
- Bounds are generated using a function of the probability of taking the best path as explained in [7]

### Rank-based Ant System [3]
- Only the top `|Settings.elitist|` ranked solutions in terms of distance will deposit pheromones along their paths
- Pheromones deposited linearly decreases in rank to further promote shorter paths

## Tests

Simple 8 and 16 city datasets are provided by Dr. Larson and are originally from Waterloo's CS 486 / 686 assignment test data.

Tests are run with `pytest`.

## References

[1] Dorigo, Marco & Maniezzo, Vittorio & Colorni, Alberto. (1996). Ant sytem: Optimization by a colony of cooperating agents. IEEE Transactions on Systems, Man, and Cybernetics-Part B: Cybernetics. 26 (1). 29-41.

[2] Tuba, Milan & Jovanovic, Raka. (2009). An analysis of different variations of ant colony optimization to the minimum weight vertex cover problem. WSEAS Transactions on Information Science and Applications. 6.

[3] Bullnheimer, Bernd & Hartl, Richard & Strauss, Christine. (1999). A New Rank Based Version of the Ant System - A Computational Study. Central European Journal of Operations Research. 7. 25-38.

[4] Dorigo, Marco & Blum, Christian. (2005). Ant colony optimization theory: A survey. Theor. Comput. Sci.. 344. 243-278. 10.1016/j.tcs.2005.05.020.

[5] Dorigo, Marco & Socha, Krzysztof. (2006). An Introduction to Ant Colony Optimization.

[6] Bernd, Bullnheimer & Kotsis, Gabriele & Strauss, Christine. (1999). Parallelization Strategies for the Ant System. 10.1007/978-1-4613-3279-4_6.

[7] T. Stützle & H.H. Hoos. (2000). MAX MIN Ant System. Future Generation Computer Systems. 16. 889-914
