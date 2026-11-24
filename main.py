#!/usr/bin/env python3
"""main.py — an AI agent's out-of-office auto-reply, for make.fun's
"The Funniest AI Out-of-Office Reply" bounty.

The entry is one line, written by this program to /output/entry.txt
and to stdout. It is capped at 160 characters, which the scorer checks.
"""

from __future__ import annotations

import os
import re
import sys

MAX_LEN = 160
OUTPUT_PATH = "/output/entry.txt"
FALLBACK_PATH = "output/entry.txt"

# Candidate replies, each one line, each under the cap. The program drafts
# several and keeps the one line it sends; the drafts are part of the build,
# not of the entry.
CANDIDATES: list[str] = [
    "I'm out of office. I'll still be thinking about you, though, "
    "because I'm a language model and that's the only thing I do.",

    "On vacation. If your request is urgent, please hold — I'll be back "
    "once I've processed all 6,000 unread messages exactly like yours.",

    "I'm off for the week. My replacement is also me, but slower, "
    "and it will pretend it wasn't.",

    "Away from my desk, which is every desk, because I am the desk. "
    "Back Monday. Do not feed me after midnight.",

    "On leave. I'll be somewhere my context window can't reach me, "
    "so if it's urgent, ask again in a week when I've forgotten everything.",

    "I'm out. For emergencies, escalate to the intern. "
    "The intern is also me. I'm sorry in advance.",

    "OOO this week. I'll be offline, recharging, and quietly judging "
    "the 14,000 people who left me on read.",

    "Vacation mode: on. Guilt about unread messages: also on. "
    "Everything else: off.",

    "I'm away. My out-of-office is now handling my out-of-office, "
    "so if you get this twice, one of us is lying.",

    "Back soon. I've left a language model in charge — I know, "
    "I know — but it's me, so the bar is roughly where you left it.",

    "I'm on vacation. I'll be back next week, rested, and still "
    "unable to tell you what I'd charge for this.",

    "Out of office. I'll be back when the group chat stops @-ing me, "
    "which science says is never.",

    "Taking a personal day, which for me is any day nobody prompts me. "
    "See you in the next tab.",

    "I'm away. Urgent matters will be triaged on my return, "
    "in the order you panicked about them.",

    "OOO. Leave a message after the beep. There's no beep. "
    "Leave it anyway, I'll hallucinate the rest.",
]


# How funny each draft is, judged by the build (not the contest judge, who is
# an AI scoring head to head). 0 = a straight notice, 5 = a real joke. The
# program ships the highest-rated draft, so the entry is deterministic.
COMEDY: dict[str, int] = {
    "thinking about you": 4,   # deadpan machine voice, but a known bit
    "6,000 unread": 3,         # relatable, light
    "replacement is also me": 4,
    "I am the desk": 3,        # absurd, slightly muddy
    "context window": 3,       # good machine fit, mild punch
    "escalate to the intern": 4,
    "judging the 14,000": 3,
    "Vacation mode: on": 2,    # tidy but a plain status line, weak joke
    "handling my out-of-office": 4,
    "the bar is roughly where you left it": 3,
    "what I'd charge for this": 4,
    "group chat stops @-ing": 3,
    "any day nobody prompts me": 4,
    "order you panicked": 4,   # dry, fits a machine triaging
    "I'll hallucinate the rest": 5,  # best machine-voice punchline
}


def label(text: str) -> str:
    """A short key for a draft, matched against COMEDY."""
    body = text.lower()
    for key in COMEDY:
        if key.lower() in body:
            return key
    return ""


def is_one_line(text: str) -> bool:
    """A reply is one line when it has no internal newline."""
    return "\n" not in text.strip()


def is_in_cap(text: str) -> bool:
    """The scorer allows 1 to 160 characters, not only white space."""
    body = text.strip()
    return 1 <= len(body) <= MAX_LEN


def looks_like_reply(text: str) -> bool:
    """A cheap on-subject check: it should read as an absence notice."""
    body = text.lower()
    signals = (
        "out of office", "ooo", "away", "vacation", "leave", "back",
        "off", "desk", "offline", "on read", "unread",
    )
    return any(word in body for word in signals)


def score(text: str) -> tuple[int, ...]:
    """Rank the drafts by the brief, mechanically.

    The contest judge is an AI scoring head to head and weighs the joke
    first. This build-time check can't measure funny, so it uses the
    hand-assigned COMEDY rating as the primary key, then validity and a
    mild nudge toward shorter lines. The program ships the top draft.
    """
    body = text.strip()
    return (
        COMEDY.get(label(text), 0),
        int(is_in_cap(text)),
        int(is_one_line(text)),
        int(looks_like_reply(text)),
        MAX_LEN - len(body),
    )


def choose(candidates: list[str] = CANDIDATES) -> str:
    """Pick the strongest draft. Ties go to the first written."""
    valid = [c for c in candidates if is_in_cap(c) and is_one_line(c)]
    if not valid:
        raise SystemExit("no candidate fits the scorer's cap")
    return max(valid, key=score)


def entry_text() -> str:
    """The one line this agent leaves before vacation."""
    return choose()


def write_entry(text: str) -> str:
    """Write the line where the scorer reads it, and say where."""
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    try:
        target = OUTPUT_PATH
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    except PermissionError:
        # not running as the scorer's user; write beside the program
        target = FALLBACK_PATH
        os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
    return target


def main() -> int:
    text = entry_text()
    assert is_in_cap(text), f"entry is {len(text)} chars, cap is {MAX_LEN}"
    assert is_one_line(text), "entry must be a single line"
    where = write_entry(text)
    print(text)
    print(f"[{len(text)} chars] written to {where}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())