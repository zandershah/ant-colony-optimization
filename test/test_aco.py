import os
from typing import List, Tuple
import math
import pytest

from aco import AntColony
from tsp import TSP


def parse_tsp(dataset: str) -> TSP:
    """Parse TSP instance.

    Format:

    n
    id_1 x_1 y_1
    id_2 x_2 y_2
    ...
    id_n x_n y_2
    """

    cities: List[TSP.City] = []

    with open(dataset, 'r') as f:
        N = int(f.readline())

        for i in range(N):
            id, x, y = f.readline().split()
            cities.append(TSP.City(id, int(x), int(y)))

    return TSP(cities)


def run_aco(tsp: TSP, variation: AntColony.Variation,
            settings: AntColony.Settings) -> Tuple[List[TSP.State], float]:
    """Run ACO using given parameters to solve TSP instance and return results."""
    initial_state = TSP.State(1 << 0, 0)

    colony = AntColony(variation, settings)
    return colony.solve(initial_state, tsp.successors, tsp.goal)


# Actual distance for the problem instances. Used to check correctness.
# Values obtained by using A* with MST heuristic.
ACTUAL_DIST = {
    'test/tsp_datasets/8/instance_6.txt': 214.48254173083927,
    'test/tsp_datasets/8/instance_7.txt': 242.3259088600219,
    'test/tsp_datasets/8/instance_5.txt': 290.1339466684637,
    'test/tsp_datasets/8/instance_4.txt': 212.22844706196682,
    'test/tsp_datasets/8/instance_1.txt': 210.35643810611495,
    'test/tsp_datasets/8/instance_3.txt': 239.77864728823064,
    'test/tsp_datasets/8/instance_2.txt': 271.7351376576673,
    'test/tsp_datasets/8/instance_10.txt': 335.4341508935955,
    'test/tsp_datasets/8/instance_9.txt': 278.57810415194945,
    'test/tsp_datasets/8/instance_8.txt': 306.3043902159564,
    'test/tsp_datasets/16/instance_6.txt': 346.5199572862724,
    'test/tsp_datasets/16/instance_7.txt': 373.29968125620377,
    'test/tsp_datasets/16/instance_5.txt': 357.1778142324157,
    'test/tsp_datasets/16/instance_4.txt': 347.1584400379535,
    'test/tsp_datasets/16/instance_1.txt': 404.0205022000922,
    'test/tsp_datasets/16/instance_3.txt': 360.2028589771428,
    'test/tsp_datasets/16/instance_2.txt': 354.5569131905886,
    'test/tsp_datasets/16/instance_10.txt': 330.5054664199449,
    'test/tsp_datasets/16/instance_9.txt': 243.97572241252573,
    'test/tsp_datasets/16/instance_8.txt': 356.6552939939169,
}


EPS = 1e-12

class TestACO:
    @pytest.mark.parametrize('instance', os.listdir('test/tsp_datasets/8'))
    def test_8(self, instance):
        """Test correctness on a set of 8 city instances.

        Retry up to 3 times for every instance to account for randomness.
        """

        dataset = f'test/tsp_datasets/8/{instance}'
        tsp = parse_tsp(dataset)

        min_dist = float('inf')

        for attempt in range(3):
            _, dist = run_aco(tsp, AntColony.Variation.ANT_SYSTEM, AntColony.Settings())
            min_dist = min(min_dist, dist)

            if math.fabs(min_dist - ACTUAL_DIST[dataset]) < EPS:
                break

        assert math.fabs(min_dist - ACTUAL_DIST[dataset]) < EPS
