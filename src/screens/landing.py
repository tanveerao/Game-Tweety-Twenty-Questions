import streamlit as st

from .. import game_state, persona


def render():
    st.title(persona.GAME_TITLE)
    st.markdown("\n\n".join(f"> {line}" for line in persona.LANDING_INSTRUCTIONS))

    col1, col2 = st.columns(2)
    with col1:
        if st.button(persona.PATH_A_BUTTON, use_container_width=True):
            game_state.go_to("setup_a")
            st.rerun()
    with col2:
        if st.button(persona.PATH_B_BUTTON, use_container_width=True):
            game_state.go_to("setup_b")
            st.rerun()
