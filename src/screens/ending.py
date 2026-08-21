import streamlit as st

from .. import game_state, persona


def render():
    st.title(persona.GAME_TITLE)

    dossier = st.session_state.get("dossier", {})
    name = st.session_state.get("secret_name", "???")
    fact = game_state.pick_reveal_fact(dossier)
    turns_used = st.session_state.get("turns_used", 0)
    result = st.session_state.get("game_result")

    if result == "WIN":
        st.success(persona.win_text(name, turns_used, fact))
        if st.session_state.get("path") == "A":
            if turns_used <= 8:
                st.caption(persona.PATH_A_ACK_EASY)
            else:
                st.caption(persona.PATH_A_ACK_GOOD)
    elif result == "LOSS_TURNS":
        st.error(persona.loss_turns_text(name, fact))
    elif result == "LOSS_GIVEUP":
        st.error(persona.loss_giveup_text(name, fact))
    else:
        st.write("Round over.")

    if st.button(persona.REPLAY_BUTTON, use_container_width=True):
        game_state.reset_for_replay()
        st.rerun()
