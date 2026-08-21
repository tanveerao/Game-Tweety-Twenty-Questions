"""
One-time (rerunnable) offline builder for the preset name pool.

Runs the exact same grounded research pipeline the live app uses
(wikipedia.fame_check + claude_client.dossier_research +
claude_client.structure_dossier) for a curated list of well-known real
people and fictional characters, and writes the results to
data/preset_pool.json. The app then loads that file at runtime instead
of paying the research latency on every round.

Run from the repo root: python scripts/build_preset_pool.py
Rerun any time to add/refresh entries -- it's idempotent per name.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import claude_client, wikipedia  # noqa: E402

OUTPUT_PATH = ROOT / "data" / "preset_pool.json"
MAX_WORKERS = 5

NAMES = [
    # Real people -- spread across category/era/region.
    "Albert Einstein", "Barack Obama", "Taylor Swift", "LeBron James",
    "Serena Williams", "Marie Curie", "Leonardo da Vinci", "Oprah Winfrey",
    "Elon Musk", "Beyoncé", "Michael Jordan", "Cleopatra",
    "Abraham Lincoln", "Stephen Hawking", "Freddie Mercury",
    # Fictional / cartoon characters -- spread across franchise/medium.
    "Mickey Mouse", "Mario", "Sherlock Holmes", "Batman",
    "Harry Potter", "SpongeBob SquarePants", "Spider-Man", "Elsa (Frozen)",
    "Pikachu", "Darth Vader", "Homer Simpson", "Wonder Woman",
    "Shrek", "Gandalf", "Hermione Granger",
]


def build_one(name: str) -> dict | None:
    fame_result = wikipedia.fame_check(name)
    if fame_result["status"] != "OK":
        print(f"SKIP {name}: fame_check -> {fame_result['status']}")
        return None
    title = fame_result["title"]
    try:
        notes = claude_client.dossier_research(title, fame_result["extract"])
        dossier = claude_client.structure_dossier(title, notes)
    except claude_client.ClaudeError as exc:
        print(f"FAIL {name}: {exc}")
        return None
    print(f"OK   {name} -> {title}")
    return {"name": title, "dossier": dossier}


def main():
    existing = []
    if OUTPUT_PATH.exists():
        existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    have = {e["name"] for e in existing}

    todo = [n for n in NAMES if n not in have]
    print(f"{len(have)} already built, {len(todo)} to build.")

    results = list(existing)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(build_one, name): name for name in todo}
        for future in as_completed(futures):
            entry = future.result()
            if entry is not None:
                results.append(entry)
                # Write incrementally so progress survives an interruption.
                OUTPUT_PATH.write_text(
                    json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
                )

    print(f"\nDone. {len(results)} entries in {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
