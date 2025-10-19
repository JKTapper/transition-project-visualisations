"""The simulation for the evolutionary simulation"""
import random
import json
import pandas as pd
import streamlit as st
import altair as alt


def get_random_pair(iterable) -> tuple:
    """Returns a random pair of elements from an iterable"""
    copy = iterable.copy()
    item_1 = random.choice(copy)
    copy.remove(item_1)
    item_2 = random.choice(copy)
    return item_1, item_2


def get_random_strategy(num_locations: int, num_forces: int) -> tuple[int]:
    """Produces a random strategy for the given version of the general's game"""
    strategy = []
    marks = random.choices(
        range(num_forces),
        k=num_locations - 1
    )
    marks.sort()
    last_mark = 0
    for mark in marks:
        strategy.append(mark - last_mark)
        last_mark = mark
    strategy.append(num_forces - last_mark)
    return tuple(strategy)


def get_child(strat, mutability):
    """
    Produces a child strategy with either identical characterists or a
    mutation with a given probability
    """
    seed = random.uniform(0, 1)
    mutations = 0
    child = strat
    while seed < mutability * 0.5 ** mutations:
        child = mutate(child)
        mutations += 1
    return child


def mutate(strat) -> None:
    """Returns a copy of the strategy that is slightly mutated"""
    while strat[(
            choices := get_random_pair(list(range(len(strat)))))[0]] == 0:
        continue
    mutant = list(strat)
    mutant[choices[0]] -= 1
    mutant[choices[1]] += 1
    return tuple(mutant)


def get_point_advantage(strat_1: tuple, strat_2: tuple) -> int:
    """This calculates the point advanatage of strat 1 over strat 2 in the general's game"""
    return sum(value * ((armies[0] > armies[1]) - (armies[0] < armies[1]))
               for value, armies in enumerate(zip(strat_1, strat_2), 1))


def decide_game(strat_1: tuple, strat_2: tuple) -> int:
    """This returns the winner and loser of a game between two strategies"""
    point_advantage = get_point_advantage(strat_1, strat_2)
    if point_advantage >= 0:
        return strat_1, strat_2
    return strat_2, strat_1


def encode_tuple(tuple: tuple[int]) -> str:
    return ','.join(str(i) for i in tuple)


def decode_tuple(tuple_str: str) -> tuple[int]:
    return tuple(int(num) for num in tuple_str.split(','))


def encode_tuple_tuple(tuple_tuple: tuple[tuple[int]]) -> str:
    return ' '.join(encode_tuple(tuple) for tuple in tuple_tuple)


def decode_tuple_tuple(tuple_tuple_str: str) -> tuple[tuple[int]]:
    return tuple(decode_tuple(tuple_str) for tuple_str in tuple_tuple_str.split())


class Population():
    """A class for the population of strategies being simulated"""

    @classmethod
    def create(cls,
               size: int,
               num_locations: int,
               num_forces: int,
               random_pop: bool = False
               ) -> None:
        """
        Creates a new object of the population class, with
        either a random or uniformly weak population
        """
        if random_pop:
            strategies = {}
            for _ in range(size):
                random_strat = get_random_strategy(num_locations, num_forces)
                strategies[random_strat] = strategies.get(
                    random_strat, 0) + 1
        else:
            strategies = {(num_forces,)+(0,)*(num_locations-1): size}
        cumulative_strategies = strategies.copy()
        solved_games = {}
        history = pd.DataFrame(
            {'step': 0, 'strat': encode_tuple(strat), 'count': count} for strat, count in strategies.items())
        return Population(
            strategies,
            cumulative_strategies,
            solved_games,
            history
        )

    @classmethod
    def load(cls, file: str):
        """Initialises a saved instance of the population class using a file"""
        with open(f'{file}.json', 'r') as f:
            info = json.load(f)
        history = pd.read_csv(f'{file}.csv')
        return Population(
            {decode_tuple(strat): count for strat,
             count in info['strategies'].items()},
            {decode_tuple(strat): count for strat,
             count in info['cumulative_strategies'].items()},
            {decode_tuple_tuple(pair): decode_tuple_tuple(result)
             for pair, result in info['solved_games'].items()},
            history
        )

    def __init__(
        self,
            strategies: dict[tuple[int]:int],
            cumulative_strategies: dict[tuple[int]:int],
            solved_games: dict[tuple[tuple[int]]:tuple],
            history: pd.DataFrame
    ):
        """Initalises a population according to given specifications"""
        self.strategies = strategies
        self.cumulative_strategies = cumulative_strategies
        self.solved_games = solved_games
        self.history = history
        self.size = sum(self.strategies.values())
        strat = list(self.strategies.keys())[0]
        self.num_locations, self.num_forces = len(strat), sum(strat)
        self.save_name = f'l{self.num_locations}f{self.num_forces}s{self.size}'
        self.current_step = max(history['step'])

    def run_simulation_step(self, mutability: float) -> None:
        """Runs a single step of the evolutionary simulation"""
        strat_1, strat_2 = random.choices(
            list(self.strategies.keys()), self.strategies.values(), k=2)
        winner, loser = self.solved_games.get((strat_1, strat_2), decide_game(
            strat_1, strat_2))
        self.solved_games[(strat_1, strat_2)] = winner, loser
        if self.current_step % 10 == 0:
            current_prevelance = self.strategies[winner]/self.size
            historic_prevelance = self.cumulative_strategies[winner] / \
                sum(self.cumulative_strategies.values())
            if current_prevelance > historic_prevelance:
                return None
        self.strategies[loser] -= 1
        child = get_child(winner, mutability)
        self.strategies[child] = self.strategies.get(child, 0) + 1
        self.cumulative_strategies[child] = self.cumulative_strategies.get(
            child, 0) + 1
        return None

    def run_simulation(self, mutability: float,
                       steps_between_saves: int = -1,
                       step_limit: int = 0,
                       terminal: bool = False) -> None:
        """Used to run the simulation."""
        steps_between_saves = steps_between_saves or -1
        steps_in_this_run = 0
        while True:
            steps_after_last_save = 0
            while steps_after_last_save != steps_between_saves:
                self.current_step += 1
                steps_in_this_run += 1
                steps_after_last_save += 1
                self.run_simulation_step(mutability)
                self.history = pd.concat([
                    self.history,
                    pd.DataFrame([{
                        'strat': encode_tuple(strat),
                        'count': count,
                        'step': self.current_step
                    } for strat, count in self.strategies.items()])
                ])
            self.save()
            if terminal:
                print('Current status:')
                print(self)
                if input('Continue simulation?') == 'stop':
                    break
            else:
                st.write(steps_in_this_run, step_limit)
                if steps_in_this_run >= step_limit and step_limit:
                    break

    def __str__(self):
        population_report = str(pd.DataFrame(
            {'strat': strat, 'count': count} for strat, count in sorted(self.strategies.items(), key=lambda x: x[1])))
        return f"Population:\n{population_report}"

    def save(self):
        with open(f'{self.save_name}.csv', 'w') as f:
            self.history.to_csv(f, index=False)
        info = {
            'strategies': {encode_tuple(strat): count for strat, count in self.strategies.items()},
            'cumulative_strategies': {encode_tuple(strat): count for strat, count in self.cumulative_strategies.items()},
            'solved_games': {encode_tuple_tuple(pair): (encode_tuple_tuple(result)) for pair, result in self.solved_games.items()},
        }
        with open(f'{self.save_name}.json', 'w') as f:
            json.dump(info, f)


if __name__ == '__main__':
    population = Population.create(10000, 5, 5)
    population.run_simulation_console(10000, 0.01)
    input('load?')
    population = Population.load('l5f5')
    print(population)
