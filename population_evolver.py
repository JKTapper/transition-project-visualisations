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


class Strategy():

    def __init__(self, strategy: list[int], mutability: float) -> None:
        self.commands = strategy
        self.mutability = mutability
        self.num_locations = len(strategy)

    def get_child(self):
        """
        Produces a child strategy with either identical characterists or a
        mutation with a probability determined by this strategies mutability
        """
        seed = random.uniform(0, 1)
        child = Strategy(self.commands.copy(), self.mutability)
        mutations = 0
        while seed < self.mutability * 0.5 ** mutations:
            child.mutate()
            mutations += 1
        return child

    def mutate(self) -> None:
        while self.commands[(
                choices := get_random_pair(list(range(self.num_locations))))[0]] == 0:
            continue
        self.mutability = self.mutability * random.uniform(0.75, 1.25)
        self.commands[choices[0]] -= 1
        self.commands[choices[1]] += 1

    def __repr__(self) -> str:
        return f"[{','.join(str(num) for num in self.commands)}]"


def get_point_advantage(strat_1: Strategy, strat_2: Strategy) -> int:
    """This calculates the point advanatage of strat 1 over strat 2 in the general's game"""
    return sum(value * ((armies[0] > armies[1]) - (armies[0] < armies[1])) for value, armies in enumerate(zip(strat_1, strat_2), 1))


class Population():

    def __init__(self, size: int, num_locations: int, num_forces: int, default_mutability: float) -> None:
        # self.strategies = [Strategy(get_random_strategy(
        #     num_locations, num_forces), default_mutability) for i in range(size)]
        self.strategies = [Strategy(
            [num_forces] + [0]*(num_locations - 1), default_mutability) for i in range(size)]

    def run_simulation_step(self) -> None:
        strat_1, strat_2 = get_random_pair(self.strategies)
        point_advantage = get_point_advantage(
            strat_1.commands, strat_2.commands)
        if point_advantage >= 1:
            self.strategies.remove(strat_2)
            del strat_2
            self.strategies.append(strat_1.get_child())
            # record.append(repr(strat_1))
        else:
            self.strategies.remove(strat_1)
            del strat_1
            self.strategies.append(strat_2.get_child())
            # record.append(repr(strat_2))

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
                self.run_simulation_step()
                current_population = pd.Series(
                    [repr(strat) for strat in self.strategies]).value_counts().to_frame()
                current_population['strat'] = current_population.index
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
