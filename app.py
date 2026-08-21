import streamlit as st

from src import game_state
from src.screens import ending, game, landing, setup_a, setup_b

st.set_page_config(page_title="Tweety's Twenty Questions", page_icon="🐤")

game_state.init_session()

SCREENS = {
    "landing": landing.render,
    "setup_a": setup_a.render,
    "handoff": setup_a.render_handoff,
    "setup_b": setup_b.render,
    "game": game.render,
    "ending": ending.render,
}

render_fn = SCREENS.get(st.session_state.screen, landing.render)
render_fn()
