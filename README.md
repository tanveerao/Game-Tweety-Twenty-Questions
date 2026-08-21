#Current status: Work in progress, latency issues at initial Name Picking phase

# Tweety's Twenty Questions

A web-based, LLM-powered game of 20 Questions. A well-known real person or fictional
character is the secret; you ask yes/no questions and try to guess who it is within 20
turns. The game master is voiced as Tweety Bird: terse, snappy, impatient, and strictly
yes/no. All gameplay logic — research, fact-checking, and answering — is powered by live
calls to the Claude API grounded in Wikipedia, not hardcoded trivia.

This is a personal project. Text-only, no licensed Looney Tunes assets, and no
monetization plans (Tweety Bird is Warner Bros. Discovery IP).

## Setup

```bash
git clone https://github.com/tanveerao/Game-Twenty-questions.git
cd Game-Twenty-questions
python -m venv venv && source venv/bin/activate   # optional but recommended
python -m pip install -r requirements.txt   # use "python -m pip", not bare "pip" -- many
                                             # setups (e.g. Windows Python from python.org)
                                             # don't put a standalone `pip` on PATH

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and paste in your real ANTHROPIC_API_KEY
```

## Run

```bash
streamlit run app.py
```

This runs locally by default. To put it on a public URL, see Deployment below.

## Deployment (Streamlit Community Cloud)

The original build was local-only; this is how to put it on a public URL like
`https://your-app-name.streamlit.app` via
[Streamlit Community Cloud](https://share.streamlit.io):

1. Push this repo to GitHub (already done if you're reading this from the repo).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick this repo/branch, and set the main file path to `app.py`.
4. Before (or right after) deploying, open the app's **Settings → Secrets** panel and paste
   in the same keys your local `.streamlit/secrets.toml` has:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   APP_PASSPHRASE = "choose-something-only-you-share"
   ```
5. Deploy. First load will be slow (cold start + the research pass on the first round).

**About `APP_PASSPHRASE`:** a public URL means anyone with the link can play — and every
round costs real Anthropic API usage. Setting `APP_PASSPHRASE` puts a simple one-screen
gate in front of the whole app (not a real user-account system, just a shared passphrase)
so only people you've shared it with can play. Leave it unset for local dev, or if you
deploy but are fine leaving it open.

## How it works

- **Two entry points.** *"I'll pick someone for a friend"* is local pass-and-play: you type
  a name, Tweety researches it, then hands the device off to whoever's guessing.
  *"Let Tweety pick"* is single-player: pick an age range and region, and Tweety generates
  and researches a candidate for you.
- **Fame check.** Every candidate name is validated against Wikipedia — resolved via the
  REST summary endpoint, disambiguated if needed, and gated by a measured article-size
  threshold (≥50,000 bytes of wikitext) before it's allowed into the game.
- **Research.** The Wikipedia extract already fetched during the fame check seeds a
  one-time research pass (Claude Sonnet 5 + the `web_search` tool) that builds a private,
  server-side fact dossier. Every question is answered from that cached dossier first; if
  the dossier doesn't cover a question, exactly one live web search is allowed before
  falling back to "don't know." Nothing is ever answered from the model's general
  knowledge — only from the dossier or a live search.
- **Turns.** You have a shared budget of 20 turns. Yes/no questions and guesses (right or
  wrong) both cost a turn; "not yes/no," "don't know," and off-limits responses (including
  attempts to extract the identity directly) are free and don't count.
- **Guessing** is semantic, not exact-string — nicknames and minor misspellings count.
  Guessing costs a turn whether right or wrong, and doesn't end the round unless it's
  correct.
- **Hint** becomes available once 15 turns have been used, one per round, free.
- **Give Up** concedes immediately without touching the turn counter.

## Architecture

```
app.py                 entrypoint / screen router
src/
  config.py             constants: turn budget, thresholds, model IDs
  persona.py             all Tweety-voiced copy, centralized
  wikipedia.py            fame check + disambiguation (pure REST/Action API, no LLM)
  claude_client.py         Claude API integration, two tiers:
                             - research tier (Sonnet 5 + web_search, free text)
                             - structuring tier (Haiku 4.5, JSON schema, no tools)
  game_state.py             session_state schema, turn-counting, orchestration
  screens/                   landing, setup_a, setup_b, game, ending
```

The secret identity and the fact dossier live only in server-side `st.session_state` and
are never rendered to the page outside the intended reveal moment.

## Out of scope for this build

Noted here as possible future features, not implemented:

- Cross-session persistence, win/loss history, or leaderboards
- Timers or difficulty levels
- Multiple hints per round, or difficulty-based hint availability
- Partial-credit feedback on wrong guesses ("warm/cold")
- Real-time multiplayer across separate devices
- User accounts / login
- A player-facing "report this answer as wrong" feedback loop
- Licensed Looney Tunes artwork, audio, or other assets

## Known limitations

- **Answer accuracy isn't guaranteed.** The whole game depends on an LLM correctly
  answering factual questions from research. Medium-fame figures, facts that change over
  time (marital status, current team, whether someone is still alive), and canon disputes
  across different fictional continuities are all realistic failure points. The
  dossier-first architecture and "don't know" fallback reduce this risk but don't
  eliminate it.
- **Latency.** The upfront research pass and any live-search fallback will visibly take a
  few seconds.
- **Trademark/IP.** Tweety Bird is Warner Bros. Discovery IP; this project makes no claim
  to it and has no monetization plans.
