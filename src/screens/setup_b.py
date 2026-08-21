import streamlit as st

from .. import config, game_state, persona


def render():
    st.title(persona.GAME_TITLE)
    st.write(persona.PATH_B_FRAMING)

    st.session_state.setdefault("path_b_error", None)

    with st.form("path_b_form"):
        age = st.selectbox(persona.PATH_B_AGE_LABEL, config.AGE_RANGES)
        region = st.selectbox(persona.PATH_B_REGION_LABEL, config.REGIONS)
        submitted = st.form_submit_button(persona.PATH_B_SUBMIT)

    if submitted:
        st.session_state.path_b_error = None
        with st.spinner(persona.PATH_B_THINKING):
            try:
                success = game_state.choose_for_player(age, region)
            except game_state.GameError as exc:
                st.session_state.path_b_error = str(exc)
                success = False
        if success:
            st.rerun()
        elif not st.session_state.path_b_error:
            st.session_state.path_b_error = persona.POOL_EXHAUSTED_ERROR

    if st.session_state.path_b_error:
        st.error(st.session_state.path_b_error)

    if st.button("← Back"):
        st.session_state.path_b_error = None
        game_state.go_to("landing")
        st.rerun()
