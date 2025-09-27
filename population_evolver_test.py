"""Tests for the evolutionary simulation"""
import os
from unittest.mock import patch
import pytest
import pandas as pd
from population_evolver import get_random_strategy, get_point_advantage, encode_tuple_tuple
from population_evolver import Population, mutate, get_child, decide_game, decode_tuple_tuple


def player_chooses(choices: list, monkeypatch) -> None:
    """
    Take a list of choices and uses them to feed into the game to test with
    Monkeypatch is used to fake (or 'mock') the input from the user
    """
    answers = iter(choices)
    monkeypatch.setattr('builtins.input', lambda name: next(answers))


def test_get_random_strategy():
    """Tests that get random strategy correctly produces a random strategy"""
    strategy_1 = get_random_strategy(10, 50)
    strategy_2 = get_random_strategy(10, 50)
    assert sum(strategy_1) == 50
    assert sum(strategy_2) == 50
    assert strategy_1 != strategy_2


def test_mutate():
    """Tests that mutate correctly mutates a strategy"""
    strategy = get_random_strategy(10, 50)
    mutant = mutate(strategy)
    assert len(mutant) == 10
    assert sum(mutant) == 50
    assert strategy != mutant


def test_get_child_no_mutation():
    """Tests that get_child produces a clone when no mutation occurs"""
    with patch("population_evolver.random.uniform") as mock_random_uniform:
        mock_random_uniform.return_value = 0.75
        strategy = get_random_strategy(10, 50)
        child = get_child(strategy, 0.5)
        assert sum(child) == 50
        assert strategy == child


def test_get_child_mutation():
    """Tests that get_child doesn ot produce a clone hwen a mutation occurs"""
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
    """Tests that get_point_advantage calculates correctly"""
    assert get_point_advantage(strat_1, strat_2) == result


decide_game_test_data = [
    ((1, 0), (0, 1), ((0, 1), (1, 0))),
    ((1, 0), (1, 0), ((1, 0), (1, 0))),
    ((0, 1), (1, 0), ((0, 1), (1, 0))),
    ((0, 2, 1, 7), (0, 0, 5, 5), ((0, 2, 1, 7), (0, 0, 5, 5))),
    ((0, 2, 1, 7), (1, 2, 3, 4), ((0, 2, 1, 7), (1, 2, 3, 4))),
    ((0, 2, 1, 7), (0, 0, 2, 8), ((0, 0, 2, 8), (0, 2, 1, 7)))
]


@pytest.mark.parametrize('strat_1,strat_2,result', decide_game_test_data)
def test_decide_game(strat_1: list, strat_2: list, result: int):
    """Tests that decide_game produces the correct outcome"""
    assert decide_game(strat_1, strat_2) == result


def test_population_init():
    """Tests that populations get initialised correctly"""
    population = Population(
        strategies=[1],
        cumulative_strategies=2,
        solved_games=3,
        history=4
    )
    assert population.strategies == [1]
    assert population.cumulative_strategies == 2
    assert population.solved_games == 3
    assert population.history == 4
    assert population.size == 1


def test_population_create():
    """Tests that new populations get created correctly"""
    population = Population.create(100, 4, 10, 0.1)
    assert sum(population.strategies.values()) == 100
    strategy = set(population.strategies.keys()).pop()
    assert len(strategy) == 4
    assert sum(strategy) == 10


def test_simulation_step_simple_win():
    """Tests that a simulation step replaces a strategy with a child"""
    population = Population.create(2, 2, 1)
    strat_1 = (0, 1)
    strat_2 = (1, 0)
    population.strategies = {strat_1: 1, strat_2: 1}
    with patch("population_evolver.get_child") as child_mock:
        child_mock.return_value = 'child'
        population.run_simulation_step(1, -1)
    assert population.strategies in ({strat_1: 1, strat_2: 0, 'child': 1}, {
                                     strat_1: 0, strat_2: 1, 'child': 1})


def test_simulation_step_draw():
    """Tests that simulation steps only change populations in limited ways"""
    population = Population.create(2, 3, 2)
    strat_1 = (0, 0, 2)
    strat_2 = (1, 1, 0)
    population.strategies = {strat_1: 1, strat_2: 1}
    population.run_simulation_step(1, -1)
    assert population.strategies in (
        {strat_1: 2, strat_2: 0}, {strat_1: 1, strat_2: 1}, {strat_1: 0, strat_2: 2})


def test_run_simulation_big_step(monkeypatch):
    """Tests that leaving a simulation to run for many steps produces expected outcome"""
    player_chooses(['', "stop"], monkeypatch)
    population = Population.create(5, 2, 3)
    population.run_simulation(0.1, steps_between_saves=1000, terminal=True)
    assert max(population.strategies.values()) == population.strategies[(0, 3)]


def test_run_simulation_small_step(monkeypatch):
    """Tests that telling a simulation to run for many steps produces expected outcome"""
    player_chooses(['']*1000 + ["stop"], monkeypatch)
    population = Population.create(5, 2, 3)
    population.run_simulation(0.1, steps_between_saves=1, terminal=True)
    assert max(population.strategies.values()) == population.strategies[(0, 3)]


def test_population_saving_and_loading():
    population = Population(
        {(1, 0): 1},
        {(1, 0): 1},
        {},
        pd.Dataframe({'step': [0], 'strat': [(1, 0)], 'count': 1})
    )
    population.save_name = 'test'
    population.save()
    copy = Population.load('test')
    assert population.history.equals(copy.history)
    assert population.strategies == copy.strategies
    assert population.cumulative_strategies == copy.cumulative_strategies
    assert population.solved_games == copy.solved_games


def test_tuple_tuple_encoding():
    assert encode_tuple_tuple(
        ((1, 2, 3), (4, 5, 6), (7, 8, 9))) == '1,2,3 4,5,6 7,8,9'


def test_tuple_tuple_decoding():
    assert decode_tuple_tuple('1,2,3 4,5,6 7,8,9') == (
        (1, 2, 3), (4, 5, 6), (7, 8, 9))
