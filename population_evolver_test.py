from unittest.mock import patch
import pytest
from population_evolver import Strategy, get_random_strategy, get_point_advantage, Population


def player_chooses(choices: list, monkeypatch) -> None:
    """
    Take a list of choices and uses them to feed into the game to test with
    Monkeypatch is used to fake (or 'mock') the input from the user
    """
    answers = iter(choices)
    monkeypatch.setattr('builtins.input', lambda name: next(answers))


def test_strategy_init():
    strategy_1 = Strategy(get_random_strategy(10, 50), 0.1)
    strategy_2 = Strategy(get_random_strategy(10, 50), 0.1)
    assert sum(strategy_1.commands) == 50
    assert sum(strategy_2.commands) == 50
    assert strategy_1.mutability == 0.1
    assert strategy_2.mutability == 0.1
    assert strategy_1.commands != strategy_2.commands


def test_safe_mutation():
    strat = Strategy(get_random_strategy(10, 50), 0)
    before = strat.commands.copy()
    strat.mutate()
    assert len(strat.commands) == 10
    assert sum(strat.commands) == 50
    assert strat.mutability == 0
    assert strat.commands != before


def test_get_child_no_mutation():
    with patch("population_evolver.random.uniform") as mock_random_uniform:
        mock_random_uniform.return_value = 0.75
        strategy = Strategy(get_random_strategy(10, 50), 0.5)
        child = strategy.get_child()
        assert sum(child.commands) == 50
        assert child.mutability == 0.5
        assert strategy.commands == child.commands


def test_get_child_mutation():
    with patch("population_evolver.random.uniform") as mock_random_uniform:
        mock_random_uniform.return_value = 0.25
        strategy = Strategy(get_random_strategy(10, 50), 0.5)
        child = strategy.get_child()
        assert sum(child.commands) == 50
        assert child.mutability == 0.5
        assert strategy.commands != child.commands


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
    assert len(population.strategies) == 100
    strategy = population.strategies.pop()
    assert len(strategy.commands) == 4
    assert sum(strategy.commands) == 10
    assert strategy.mutability == 0.1


def test_simulation_step_simple_win():
    population = Population(0, 2, 1, -1)
    strat_1 = Strategy([0, 1], -1)
    strat_2 = Strategy([1, 0], -1)
    population.strategies = [strat_1, strat_2]
    with patch("population_evolver.Strategy.get_child") as child_mock:
        child_mock.return_value = 'child'
        population.run_simulation_step()
    assert population.strategies == [strat_1, 'child']


def test_simulation_step_draw():
    population = Population(0, 3, 2, -1)
    strat_1 = Strategy([0, 0, 2], -1)
    strat_2 = Strategy([1, 1, 0], -1)
    population.strategies = [strat_1, strat_2]
    population.run_simulation_step()
    assert population.strategies == [strat_1, strat_2]


def test_run_simulation_big_step(monkeypatch):
    player_chooses(['', "stop"], monkeypatch)
    population = Population(5, 2, 3, 0.1)
    population.run_simulation(200)
    assert [strategy.commands for strategy in population.strategies] == [[0, 3]]*5


def test_run_simulation_small_step(monkeypatch):
    player_chooses(['']*200 + ["stop"], monkeypatch)
    population = Population(5, 2, 3, 0.1)
    population.run_simulation(1)
    assert [strategy.commands for strategy in population.strategies] == [[0, 3]]*5
