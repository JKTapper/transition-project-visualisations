from unittest.mock import patch
import pytest
from population_evolver import get_random_strategy, get_point_advantage, Population, mutate, get_child, decide_game


def player_chooses(choices: list, monkeypatch) -> None:
    """
    Take a list of choices and uses them to feed into the game to test with
    Monkeypatch is used to fake (or 'mock') the input from the user
    """
    answers = iter(choices)
    monkeypatch.setattr('builtins.input', lambda name: next(answers))


def test_get_random_strategy():
    strategy_1 = get_random_strategy(10, 50)
    strategy_2 = get_random_strategy(10, 50)
    assert sum(strategy_1) == 50
    assert sum(strategy_2) == 50
    assert strategy_1 != strategy_2


def test_mutate():
    strategy = get_random_strategy(10, 50)
    mutant = mutate(strategy)
    assert len(mutant) == 10
    assert sum(mutant) == 50
    assert strategy != mutant


def test_get_child_no_mutation():
    with patch("population_evolver.random.uniform") as mock_random_uniform:
        mock_random_uniform.return_value = 0.75
        strategy = get_random_strategy(10, 50)
        child = get_child(strategy, 0.5)
        assert sum(child) == 50
        assert strategy == child


def test_get_child_mutation():
    with patch("population_evolver.random.uniform") as mock_random_uniform:
        mock_random_uniform.return_value = 0.25
        strategy = get_random_strategy(10, 50)
        child = get_child(strategy, 0.5)
        assert sum(child) == 50
        assert strategy != child


point_advantage_test_data = [
    ([1, 0], [0, 1], -1),
    ([1, 0], [1, 0], 0),
    ([0, 1], [1, 0], 1),
    ([0, 2, 1, 7], [0, 0, 5, 5], 3),
    ([0, 2, 1, 7], [1, 2, 3, 4], 0),
    ([0, 2, 1, 7], [0, 0, 2, 8], -5)
]


@pytest.mark.parametrize('strat_1,strat_2,result', point_advantage_test_data)
def test_get_point_advantage(strat_1: list, strat_2: list, result: int):
    assert get_point_advantage(strat_1, strat_2) == result


def test_population_init():
    population = Population(100, 4, 10, 0.1)
    assert sum(population.strategies.values()) == 100
    strategy = set(population.strategies.keys()).pop()
    assert len(strategy) == 4
    assert sum(strategy) == 10


def test_simulation_step_simple_win():
    population = Population(2, 2, 1, -1)
    strat_1 = (0, 1)
    strat_2 = (1, 0)
    population.strategies = {strat_1: 1, strat_2: 1}
    with patch("population_evolver.get_child") as child_mock:
        child_mock.return_value = 'child'
        population.run_simulation_step(1)
    assert population.strategies in ({strat_1: 1, strat_2: 0, 'child': 1}, {
                                     strat_1: 0, strat_2: 1, 'child': 1})


def test_simulation_step_draw():
    population = Population(2, 3, 2, -1)
    strat_1 = (0, 0, 2)
    strat_2 = (1, 1, 0)
    population.strategies = {strat_1: 1, strat_2: 1}
    population.run_simulation_step(1)
    assert population.strategies in (
        {strat_1: 2, strat_2: 0}, {strat_1: 1, strat_2: 1}, {strat_1: 0, strat_2: 2})


# def test_run_simulation_big_step(monkeypatch):
#     player_chooses(['', "stop"], monkeypatch)
#     population = Population(5, 2, 3, 0.01)
#     population.run_simulation_console(1000)
#     assert population.strategies == {
#         (3, 0): 0, (2, 1): 0, (1, 2): 0, (0, 3): 5}


# def test_run_simulation_small_step(monkeypatch):
#     player_chooses(['']*1000 + ["stop"], monkeypatch)
#     population = Population(5, 2, 3, 0.01)
#     population.run_simulation_console(1)
#     assert population.strategies == {
#         (3, 0): 0, (2, 1): 0, (1, 2): 0, (0, 3): 5}
