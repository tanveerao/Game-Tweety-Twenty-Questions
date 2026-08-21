import streamlit as st

from .. import config, game_state, persona


def _render_log_entry(entry):
    if entry["kind"] == "hint":
        st.warning(f"{persona.HINT_TAG}: {entry['note']}")
        return

    if entry["kind"] == "guess":
        label = f"#{entry['number']}  GUESS: '{entry['text']}'  —  {entry['result_label']}"
        if entry["classification"] == "GUESS_RIGHT":
            st.success(label)
        else:
            st.error(label)
        return

    # kind == "qa"
    label = f"#{entry['number']}  {entry['text']}  —  {entry['result_label']}"
    classification = entry["classification"]
    if classification == "YES":
        st.success(label)
    elif classification == "NO":
        st.error(label)
    else:
        st.info(label)
    if entry.get("note"):
        st.caption(entry["note"])


def _render_confirm_bar():
    pending = st.session_state.pending_confirm
    if pending["action"] == "guess":
        st.warning(persona.guess_confirm_text(pending["text"]))
    else:
        st.warning(persona.GIVE_UP_CONFIRM)

    col_yes, col_cancel = st.columns(2)
    with col_yes:
        if st.button(persona.CONFIRM_YES, use_container_width=True, key="confirm_yes"):
            if pending["action"] == "guess":
                with st.spinner(persona.LIVE_SEARCH_LOADING):
                    try:
                        game_state.confirm_guess(pending["text"])
                    except game_state.GameError as exc:
                        st.session_state.game_error = str(exc)
                st.session_state._clear_game_input = True
            else:
                game_state.give_up()
            game_state.cancel_confirm()
            st.rerun()
    with col_cancel:
        if st.button(persona.CONFIRM_CANCEL, use_container_width=True, key="confirm_cancel"):
            game_state.cancel_confirm()
            st.rerun()


def render():
    if st.session_state.get("_clear_game_input"):
        st.session_state.game_input = ""
        st.session_state._clear_game_input = False

    st.session_state.setdefault("game_error", None)

    turns_used = st.session_state.get("turns_used", 0)
    header_col, counter_col = st.columns([3, 1])
    with header_col:
        st.title(persona.GAME_TITLE)
    with counter_col:
        st.markdown(f"### Turns: {turns_used}/{config.TURN_BUDGET}")

    if st.session_state.game_error:
        st.error(st.session_state.game_error)

    with st.container(height=420):
        for entry in st.session_state.get("log", []):
            _render_log_entry(entry)

    if st.session_state.pending_confirm is not None:
        _render_confirm_bar()
        return

    text = st.text_input(
        persona.INPUT_PLACEHOLDER, key="game_input", label_visibility="collapsed",
        placeholder=persona.INPUT_PLACEHOLDER,
    )

    ask_col, guess_col, hint_col, giveup_col = st.columns(4)

    with ask_col:
        if st.button(persona.ASK_BUTTON, use_container_width=True):
            if text.strip():
                st.session_state.game_error = None
                with st.spinner(persona.DOSSIER_LOADING):
                    try:
                        game_state.submit_question(text.strip())
                        st.session_state._clear_game_input = True
                    except game_state.GameError as exc:
                        st.session_state.game_error = str(exc)
                st.rerun()

    with guess_col:
        if st.button(persona.GUESS_BUTTON, use_container_width=True):
            if text.strip():
                game_state.start_guess_confirm(text.strip())
                st.rerun()

    with hint_col:
        if game_state.hint_unlocked():
            if game_state.hint_already_used():
                st.button(persona.HINT_BUTTON_USED, use_container_width=True, disabled=True)
            else:
                if st.button(persona.HINT_BUTTON, use_container_width=True):
                    st.session_state.game_error = None
                    with st.spinner(persona.DOSSIER_LOADING):
                        try:
                            game_state.request_hint()
                        except game_state.GameError as exc:
                            st.session_state.game_error = str(exc)
                    st.rerun()

    with giveup_col:
        if st.button(persona.GIVE_UP_BUTTON, use_container_width=True):
            game_state.start_giveup_confirm()
            st.rerun()
