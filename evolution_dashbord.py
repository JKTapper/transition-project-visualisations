"""Streamlit code for the dashboard"""
import streamlit as st
from population_evolver import Population

st.title("General's Game Simulation")

with st.expander("See explanations"):
    with st.expander("Explanation of game:"):
        st.write('''
            The General's game is a 2 player simultaneous reveal game, like rock, paper, scissors.
            In this game there are a number of 'locations' worth different amounts of points, from 1 to n.
            Each player has a certain number of 'soldiers' that they can distribute as they see fit amongst the locations.
            Each location is won by the side that sent more soldiers to it. The side with the most points at the end wins.
        ''')
    with st.expander("Explanation of project:"):
        st.write('''
            In game theory, a nash equilibrium is reached when all players of a game are employing strategies
            that do not permit coutnerplay i.e there is no strategy an opponent could employ to gain advantage
            over them. For instance, in rock, paper, scissors, the nash equilibrium is reach when both players
            randomly choose to throw one of the three gestures with no bias. If one player tend to do one gesture
            more than the others then their opponent could exploit that to gain the upper hand.
            
            All versions of the General's game will also have some strategy that forms the nash equilibrium when
            employed by both sides. This project is an attempt to roughly approximate these equilibriums using
            an evolutionary simulation.
        ''')
    with st.expander("Explanation of simulation:"):
        st.write('''
            This simulation starts with a population of strategies. At each step two are chosen randomly and made
            to compete with each other. The loser is removed from the population and the winner gets to produce
            an child to take its place. The child will be a clone of the parent unless a mutation occurs, in which
            case it will be slightly different. There is also a corrective factor to discourage deviations from
            average trends. This is necessary to prevent strong strategies being driven to extiction by temporary
            circumstances.
        ''')

num_locations = st.number_input(
    "How many locations are the two sides fighting to control?", value=4)
num_forces = st.number_input(
    "How many soldiers does each side have to allocate?", value=2)
pop = Population(1000, num_locations, num_forces, 0.01)
pop.run_simulation_dashboard(25000, 0.01)
