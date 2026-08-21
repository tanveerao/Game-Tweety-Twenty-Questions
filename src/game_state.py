"""
Game engine: session_state schema, turn-counting, log management, and the
orchestration of Wikipedia + Claude calls into game actions.

Screens call into this module rather than touching st.session_state
directly for anything beyond simple widget bindings, and rather than
calling wikipedia.py / claude_client.py directly.
"""

import random

import requests
import streamlit as st

from . import claude_client, config, persona, wikipedia


class GameError(Exception):
    """User-facing wrapper around any network/API failure."""


def _wrap_errors(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except claude_client.ClaudeError:
        raise GameError(persona.ERROR_GENERIC)
    except requests.exceptions.RequestException:
        raise GameError(persona.ERROR_GENERIC)


# ---------------------------------------------------------------------------
# Session bootstrap
# ---------------------------------------------------------------------------

def init_session():
    if "screen" not in st.session_state:
        st.session_state.screen = "landing"
    if "used_names_b" not in st.session_state:
        st.session_state.used_names_b = set()
    if "pending_confirm" not in st.session_state:
        st.session_state.pending_confirm = None


def go_to(screen: str):
    st.session_state.screen = screen


# ---------------------------------------------------------------------------
# Round setup
# ---------------------------------------------------------------------------

def check_name(name: str) -> dict:
    """Path A: fame-check a player-typed name. Returns the raw wikipedia.py result."""
    return _wrap_errors(wikipedia.fame_check, name)


def check_candidate_title(title: str) -> dict:
    """Path A: fame-check an already-resolved disambiguation candidate."""
    return _wrap_errors(wikipedia.fame_check_exact_title, title)


def _build_dossier(title: str, extract: str) -> dict:
    notes = _wrap_errors(claude_client.dossier_research, title, extract)
    dossier = _wrap_errors(claude_client.structure_dossier, title, notes)
    return dossier


def start_round_from_fame_result(fame_result: dict, path: str):
    """fame_result must have status == 'OK'."""
    title = fame_result["title"]
    dossier = _build_dossier(title, fame_result["extract"])
    _start_round(dossier, title, path)


def _start_round(dossier: dict, fallback_name: str, path: str):
    st.session_state.dossier = dossier
    st.session_state.secret_name = dossier.get("canonical_name") or fallback_name
    st.session_state.turns_used = 0
    st.session_state.log = []
    st.session_state.hint_used = False
    st.session_state.game_result = None
    st.session_state.path = path
    st.session_state.pending_confirm = None
    st.session_state.screen = "handoff" if path == "A" else "game"


def choose_for_player(age_range: str, region: str) -> bool:
    """Path B: generate + resolve a candidate, retrying the pool once if it
    fully exhausts. Returns True on success, False if both pools exhausted."""
    used = st.session_state.used_names_b
    for _attempt in range(config.MAX_POOL_REGENERATIONS + 1):
        pool = _wrap_errors(
            claude_client.generate_candidate_pool, age_range, region, list(used)
        )
        random.shuffle(pool)
        for candidate in pool:
            if candidate in used:
                continue
            fame_result = _wrap_errors(wikipedia.fame_check, candidate)
            if fame_result["status"] != "OK":
                continue  # silently redraw
            used.add(fame_result["title"])
            dossier = _build_dossier(fame_result["title"], fame_result["extract"])
            _start_round(dossier, fame_result["title"], "B")
            return True
    return False


# ---------------------------------------------------------------------------
# Log helpers
# ---------------------------------------------------------------------------

def _next_display_number() -> int:
    return 1 + sum(1 for e in st.session_state.log if e["kind"] in ("qa", "guess"))


def _append_qa(text: str, classification: str, note: str, counted: bool):
    st.session_state.log.append({
        "kind": "qa",
        "number": _next_display_number(),
        "text": text,
        "classification": classification,
        "result_label": persona.RESULT_LABELS[classification],
        "note": note,
        "counted": counted,
    })


def _append_guess(text: str, is_match: bool):
    classification = "GUESS_RIGHT" if is_match else "GUESS_WRONG"
    st.session_state.log.append({
        "kind": "guess",
        "number": _next_display_number(),
        "text": text,
        "classification": classification,
        "result_label": persona.RESULT_LABELS[classification],
        "note": None,
        "counted": True,
    })


def _append_hint(hint_text: str):
    st.session_state.log.append({
        "kind": "hint",
        "number": None,
        "text": None,
        "classification": None,
        "result_label": None,
        "note": hint_text,
        "counted": False,
    })


def _summarize_revealed() -> str:
    lines = [
        f"- {e['text']} -> {e['result_label']}: {e['note']}"
        for e in st.session_state.log
        if e["kind"] == "qa" and e["classification"] in ("YES", "NO") and e.get("note")
    ]
    return "\n".join(lines) if lines else "(nothing revealed yet)"


# ---------------------------------------------------------------------------
# Turn actions
# ---------------------------------------------------------------------------

def submit_question(question_text: str):
    dossier_summary = claude_client.dossier_to_text(st.session_state.dossier)
    result = _wrap_errors(claude_client.classify_question, dossier_summary, question_text)
    classification = result["classification"]
    note = result["answer_note"]

    if classification == "DONT_KNOW" and result.get("worth_live_search"):
        finding = _wrap_errors(
            claude_client.live_search_answer,
            st.session_state.secret_name, dossier_summary, question_text,
        )
        result2 = _wrap_errors(claude_client.classify_search_result, question_text, finding)
        classification = result2["classification"]
        note = result2["answer_note"]

    counted = classification in ("YES", "NO")
    _append_qa(question_text, classification, note, counted)
    if counted:
        st.session_state.turns_used += 1
        _check_loss_by_turns()


def confirm_guess(guess_text: str):
    is_match = _wrap_errors(
        claude_client.match_guess, guess_text, st.session_state.secret_name
    )
    _append_guess(guess_text, is_match)
    st.session_state.turns_used += 1
    if is_match:
        _end_round("WIN")
    else:
        _check_loss_by_turns()


def give_up():
    _end_round("LOSS_GIVEUP")


def request_hint():
    dossier_summary = claude_client.dossier_to_text(st.session_state.dossier)
    revealed = _summarize_revealed()
    hint_text = _wrap_errors(claude_client.pick_hint, dossier_summary, revealed)
    _append_hint(hint_text)
    st.session_state.hint_used = True


def _check_loss_by_turns():
    if st.session_state.turns_used >= config.TURN_BUDGET and st.session_state.game_result is None:
        _end_round("LOSS_TURNS")


def _end_round(result: str):
    st.session_state.game_result = result
    st.session_state.screen = "ending"


# ---------------------------------------------------------------------------
# Confirm-before-locking-in (Guess / Give Up)
# ---------------------------------------------------------------------------

def start_guess_confirm(text: str):
    st.session_state.pending_confirm = {"action": "guess", "text": text}


def start_giveup_confirm():
    st.session_state.pending_confirm = {"action": "giveup", "text": None}


def cancel_confirm():
    st.session_state.pending_confirm = None


# ---------------------------------------------------------------------------
# Derived state
# ---------------------------------------------------------------------------

def hint_unlocked() -> bool:
    return st.session_state.get("turns_used", 0) >= config.HINT_UNLOCK_AT_TURNS_USED


def hint_already_used() -> bool:
    return st.session_state.get("hint_used", False)


def pick_reveal_fact(dossier: dict) -> str:
    """Deterministic, non-LLM pick of one dossier fact for the reveal screen."""
    for key in (
        "notable_achievements", "awards_or_records", "associations",
        "profession_or_role", "name_note", "region_or_franchise",
    ):
        value = dossier.get(key)
        if isinstance(value, list) and value:
            return value[0]
        if isinstance(value, str) and value:
            return value
    return "Tweety's not telling you more than that."


def reset_for_replay():
    for key in (
        "dossier", "secret_name", "turns_used", "log", "hint_used",
        "game_result", "path", "pending_confirm",
    ):
        st.session_state.pop(key, None)
    st.session_state.screen = "landing"
