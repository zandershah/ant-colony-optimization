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

## References

[1] Dorigo, Marco & Maniezzo, Vittorio & Colorni, Alberto. (1996). Ant sytem: Optimization by a colony of cooperating agents. IEEE Transactions on Systems, Man, and Cybernetics-Part B: Cybernetics. 26 (1). 29-41.

[2] Tuba, Milan & Jovanovic, Raka. (2009). An analysis of different variations of ant colony optimization to the minimum weight vertex cover problem. WSEAS Transactions on Information Science and Applications. 6.

[3] Bullnheimer, Bernd & Hartl, Richard & Strauss, Christine. (1999). A New Rank Based Version of the Ant System - A Computational Study. Central European Journal of Operations Research. 7. 25-38.

[4] Dorigo, Marco & Blum, Christian. (2005). Ant colony optimization theory: A survey. Theor. Comput. Sci.. 344. 243-278. 10.1016/j.tcs.2005.05.020.

[5] Dorigo, Marco & Socha, Krzysztof. (2006). An Introduction to Ant Colony Optimization.

[6] Bernd, Bullnheimer & Kotsis, Gabriele & Strauss, Christine. (1999). Parallelization Strategies for the Ant System. 10.1007/978-1-4613-3279-4_6.
