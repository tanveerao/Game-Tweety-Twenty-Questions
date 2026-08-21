import streamlit as st

from src import game_state, persona
from src.screens import ending, game, landing, setup_a, setup_b

st.set_page_config(page_title="Tweety's Twenty Questions", page_icon="🐤")


def _passphrase_gate() -> bool:
    """Optional access gate for public deployments. If APP_PASSPHRASE isn't
    set in secrets (the normal local-dev case), the gate is skipped
    entirely. Set it in secrets.toml (or the Streamlit Cloud Secrets panel)
    to require it before a visitor can play."""
    required = st.secrets.get("APP_PASSPHRASE", "")
    if not required:
        return True
    if st.session_state.get("authenticated"):
        return True

    st.title(persona.GAME_TITLE)
    st.write(persona.GATE_PROMPT)
    with st.form("gate_form"):
        entered = st.text_input(
            persona.GATE_PROMPT, type="password", label_visibility="collapsed"
        )
        submitted = st.form_submit_button(persona.GATE_SUBMIT)
    if submitted:
        if entered == required:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error(persona.GATE_WRONG)
    return False


game_state.init_session()

if not _passphrase_gate():
    st.stop()

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
