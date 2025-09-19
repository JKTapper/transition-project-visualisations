import streamlit as st
from population_evolver import Population

st.title("General's game simulation")

with st.expander("Explanation of game:"):
    st.write('''
        The General's game is a 2 player simultaneous reveal game, like rock, paper, scissors.
        In this game there are a number of 'locations' worth different amounts of points, from 1 to n.
        Each player has a certain number of 'soldiers' that they can distribute as they see fit amongst the locations.
        Each location is won by the side that sent more soldiers to it. The side with the most points at the end wins.
    ''')

num_locations = st.number_input(
    "How many locations are the two sides fighting to control?", value=4)
num_forces = st.number_input(
    "How many soldiers does each side have to allocate?", value=2)
pop = Population(1000, num_locations, num_forces, 0.01)
pop.run_simulation_dashboard(10000)
