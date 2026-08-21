import streamlit as st

from .. import game_state, persona


def render():
    st.title(persona.GAME_TITLE)
    st.subheader(persona.PATH_A_PROMPT)

    st.session_state.setdefault("path_a_pending_candidates", None)
    st.session_state.setdefault("path_a_error", None)

    with st.form("path_a_form", clear_on_submit=False):
        name = st.text_input(persona.PATH_A_PROMPT, label_visibility="collapsed")
        submitted = st.form_submit_button(persona.PATH_A_SUBMIT)

    if submitted and name.strip():
        st.session_state.path_a_error = None
        st.session_state.path_a_pending_candidates = None
        with st.spinner(persona.FAME_CHECK_LOADING):
            try:
                result = game_state.check_name(name.strip())
            except game_state.GameError as exc:
                st.session_state.path_a_error = str(exc)
                result = None

        if result is not None:
            if result["status"] == "OK":
                with st.spinner(persona.DOSSIER_LOADING):
                    try:
                        game_state.start_round_from_fame_result(result, path="A")
                        st.rerun()
                    except game_state.GameError as exc:
                        st.session_state.path_a_error = str(exc)
            elif result["status"] == "AMBIGUOUS":
                st.session_state.path_a_pending_candidates = result["candidates"]
            else:  # NOT_FOUND or TOO_OBSCURE
                st.session_state.path_a_error = persona.FAME_CHECK_REJECTION

    if st.session_state.path_a_error:
        st.error(st.session_state.path_a_error)

    if st.session_state.path_a_pending_candidates:
        st.write(persona.DISAMBIGUATION_PROMPT)
        for candidate in st.session_state.path_a_pending_candidates:
            label = f"{candidate['title']} — {candidate['descriptor']}"
            if st.button(label, key=f"cand_{candidate['title']}"):
                st.session_state.path_a_pending_candidates = None
                with st.spinner(persona.FAME_CHECK_LOADING):
                    try:
                        fame_result = game_state.check_candidate_title(candidate["title"])
                    except game_state.GameError as exc:
                        st.session_state.path_a_error = str(exc)
                        fame_result = None
                if fame_result is not None:
                    if fame_result["status"] == "OK":
                        with st.spinner(persona.DOSSIER_LOADING):
                            try:
                                game_state.start_round_from_fame_result(fame_result, path="A")
                            except game_state.GameError as exc:
                                st.session_state.path_a_error = str(exc)
                    else:
                        st.session_state.path_a_error = persona.FAME_CHECK_REJECTION
                st.rerun()

    if st.button("← Back"):
        st.session_state.path_a_error = None
        st.session_state.path_a_pending_candidates = None
        game_state.go_to("landing")
        st.rerun()


def render_handoff():
    st.title(persona.GAME_TITLE)
    st.write(persona.HANDOFF_TITLE)
    if st.button(persona.HANDOFF_BUTTON, use_container_width=True):
        game_state.go_to("game")
        st.rerun()
