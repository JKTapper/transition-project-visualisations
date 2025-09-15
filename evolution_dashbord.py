import streamlit as st
from population_evolver import Population

num_locations = st.number_input(
    "How many locations are the two sides fighting to control?", value=4)
num_forces = st.number_input(
    "How many soldiers does each side have to allocate?", value=2)
pop = Population(10000, num_locations, num_forces, 0.01)
pop.run_simulation_dashboard(10000)
