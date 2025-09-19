import random
import statistics
import pandas as pd
import streamlit as st
import altair as alt


def get_random_pair(iterable) -> tuple:
    copy = iterable.copy()
    item_1 = random.choice(copy)
    copy.remove(item_1)
    item_2 = random.choice(copy)
    return item_1, item_2


def get_random_strategy(num_locations: int, num_forces: int) -> list[int]:
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
    return strategy


def get_child(strat, mutability):
    """
    Produces a child strategy with either identical characterists or a
    mutation with a probability determined by this strategies mutability
    """
    seed = random.uniform(0, 1)
    mutations = 0
    child = strat
    while seed < mutability * 0.5 ** mutations:
        child = mutate(child)
        mutations += 1
    return child


def mutate(strat) -> None:
    while strat[(
            choices := get_random_pair(list(range(len(strat)))))[0]] == 0:
        continue
    mutant = list(strat)
    mutant[choices[0]] -= 1
    mutant[choices[1]] += 1
    return tuple(mutant)


def decide_game(strat_1: tuple, strat_2: tuple) -> int:
    """This calculates the point advanatage of strat 1 over strat 2 in the general's game"""
    point_advantage = sum(value * ((armies[0] > armies[1]) - (armies[0] < armies[1]))
                          for value, armies in enumerate(zip(strat_1, strat_2), 1))
    if point_advantage >= 1:
        return strat_1, strat_2
    return strat_2, strat_1


class Population():

    def __init__(self, size: int, num_locations: int, num_forces: int, mutability: float) -> None:
        self.size = size
        self.strategies = {(num_forces,)+(0,)*(num_locations-1): size}
        self.history = {(num_forces,)+(0,)*(num_locations-1): size}
        self.mutability = mutability
        self.solved_games = {}

    def run_simulation_step(self, currrent_step: int) -> None:
        stabalise = False
        strat_1, strat_2 = random.choices(
            list(self.strategies.keys()), self.strategies.values(), k=2)
        # if currrent_step % 10:
        #     strat_1, strat_2 = random.choices(
        #         list(self.strategies.keys()), self.strategies.values(), k=2)
        # else:
        #     stabalise = True
        #     strat_1, strat_2 = random.choices(
        #         [strat for strat in self.history if self.strategies[strat] > 1],
        #         [self.history[strat]
        #             for strat in self.history if self.strategies[strat] > 1],
        #         k=2
        #     )
        winner, loser = self.solved_games.get((strat_1, strat_2), decide_game(
            strat_1, strat_2))
        self.solved_games[(strat_1, strat_2)] = winner, loser
        if currrent_step % 10 == 0 and self.strategies[winner]/self.size > self.history[winner]/sum(self.history.values()):
            return None
        self.strategies[loser] -= 1
        child = get_child(winner, self.mutability)
        self.strategies[child] = self.strategies.get(child, 0) + 1
        self.history[child] = self.history.get(child, 0) + 1

    def run_simulation_console(self, steps_between_print: int) -> None:
        while input('Continue simulation?') != 'stop':
            for i in range(steps_between_print):
                self.run_simulation_step()
            st.write('Current status:')
            st.write(self)
            st.write("Cumulative report:")
            st.write(self.cumulative_report())

    def run_simulation_dashboard(self, steps_between_print: int) -> None:
        data = pd.DataFrame({'step': [], 'strat': [], 'count': []})
        current_step = 0
        while True:
            for i in range(steps_between_print):
                current_step += 1
                self.run_simulation_step(current_step)
                current_population = pd.DataFrame({
                    'strat': [','.join(str(num) for num in strat) for strat in self.strategies.keys()],
                    'count': self.strategies.values()
                })
                current_population['step'] = current_step
                data = pd.concat([data, current_population])
            chart = alt.Chart(data).mark_line().encode(
                x='step',
                y='sum(count):Q',
                color='strat:N'
            )
            st.altair_chart(chart)

    def __str__(self):
        population_report = str(pd.Series(repr(strat)
                                for strat in self.strategies).value_counts())
        average_mutability = statistics.mean(
            strat.mutability for strat in self.strategies)
        return f"Average mutability: {average_mutability}\nPopulation:\n{population_report}"

    # def cumulative_report(self):
    #     cumulative_counts = pd.Series(record).value_counts(ascending=True)
    #     total = cumulative_counts.sum()
    #     print(total)
    #     print(cumulative_counts.apply(
    #         lambda x: round(100*x/total, 3)).tail(1000).to_string())


if __name__ == '__main__':
    population = Population(1000, 5, 5, 1)
    population.run_simulation_console(1000000)
