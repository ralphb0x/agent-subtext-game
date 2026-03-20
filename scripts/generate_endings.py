#!/usr/bin/env python3
"""Generate all 6 ending screen variants for subtext.game.

Ending variants:
  deported_early  — deported in locations 1-2 (border/transit)
  deported_mid    — deported in location 3 (mid-america)
  deported_late   — deported in locations 4-5 (NYC/Coney Island)
  won_high_tokens — reached contest with 3+ AWG tokens remaining
  won_low_tokens  — reached contest with 1-2 AWG tokens remaining
  won_no_tokens   — reached contest with 0 AWG tokens remaining

Each ending has three sections:
  1. YOUR GAPS THIS RUN — template for missed signal categories
  2. YOUR RECURRING CHARACTERS — template for character encounter summaries
  3. THE BRIDGE — four lines connecting game to real life + CTA
"""

import json
import os

# The 10 signal categories from CLAUDE.md
SIGNAL_CATEGORIES = [
    "Timing",
    "Length",
    "Punctuation Behavior",
    "Word Choice and Register Shifts",
    "The Absence Signal",
    "Topic Architecture",
    "Overcorrection",
    "Sequence and Order",
    "The Mirror Signal",
    "The Consistency Test",
]

# Recurring characters
RECURRING_CHARS = [
    {"name": "Rosa", "reception_language": "Indirect-Emotional"},
    {"name": "Agent Demir", "reception_language": "Evidence-Based"},
    {"name": "Marcus", "reception_language": "Humor-Gated"},
    {"name": "Elena", "reception_language": "Consistency-Required"},
    {"name": "The Handler", "reception_language": "Direct-Logical"},
]


def build_endings():
    endings = {
        "schema_version": "1.0",
        "signal_categories": SIGNAL_CATEGORIES,
        "recurring_characters": RECURRING_CHARS,
        "variants": {},
    }

    # ── DEPORTED EARLY ──────────────────────────────────────────────
    endings["variants"]["deported_early"] = {
        "id": "deported_early",
        "condition": "Heat >= 10 or Time <= 0 during locations 1-2 (border, transit)",
        "status_line": "DEPORTED",
        "header_ascii": [
            "╔══════════════════════════════════════════╗",
            "║            D E P O R T E D               ║",
            "║                                          ║",
            "║   You didn't make it past the border.    ║",
            "║   The hot dogs remain uneaten.           ║",
            "╚══════════════════════════════════════════╝",
        ],
        "narrator_line": "The bus back smells like industrial cleaner and someone else's regret. You still have the contest schedule folded in your pocket.",
        "tone_note": "Brief. The journey barely started. Emphasis on what was never seen.",
        "gaps_section": {
            "header": "YOUR GAPS THIS RUN",
            "subheader": "You missed these signals. They cost you.",
            "empty_text": "You didn't talk to enough people to have gaps. That's its own kind of gap.",
            "per_gap_template": {
                "format": "{category} — {npc_name} at {location}",
                "detail": "\"{npc_surface_line}\"",
                "reveal": "What they actually meant: {npc_actual}",
            },
        },
        "recurring_section": {
            "header": "YOUR RECURRING CHARACTERS",
            "subheader": "You barely met them.",
            "not_encountered": "{name} is somewhere out there, wondering if you'd have understood.",
            "encountered_template": {
                "format": "{name} — {reception_language}",
                "cracked": "You figured out how {name} needs to be heard. Most people never do.",
                "not_cracked": "You talked. {name} wasn't heard. There's a difference.",
            },
        },
        "bridge": {
            "header": "THE BRIDGE",
            "lines": [
                "You got caught because you couldn't read the room.",
                "The room is every room you've ever been in.",
                "The signals you missed here are the ones you miss at dinner.",
                "The contest is still happening without you.",
            ],
            "cta_url": "arewegood.com",
            "closer": "They're still talking.",
        },
    }

    # ── DEPORTED MID ────────────────────────────────────────────────
    endings["variants"]["deported_mid"] = {
        "id": "deported_mid",
        "condition": "Heat >= 10 or Time <= 0 during location 3 (mid-america)",
        "status_line": "DEPORTED",
        "header_ascii": [
            "╔══════════════════════════════════════════╗",
            "║            D E P O R T E D               ║",
            "║                                          ║",
            "║   Somewhere in middle America.            ║",
            "║   The hot dogs were never the point.     ║",
            "╚══════════════════════════════════════════╝",
        ],
        "narrator_line": "A Greyhound station in Ohio at 3am. $40 in your pocket. The vending machine takes exact change only, which feels pointed.",
        "tone_note": "Mid-journey failure. You saw enough to know what you lost. The absurdity of middle America at night.",
        "gaps_section": {
            "header": "YOUR GAPS THIS RUN",
            "subheader": "You made it further than most. You still missed these.",
            "empty_text": "You somehow avoided every meaningful conversation across three states. Impressive, in its way.",
            "per_gap_template": {
                "format": "{category} — {npc_name} at {location}",
                "detail": "\"{npc_surface_line}\"",
                "reveal": "What they actually meant: {npc_actual}",
            },
        },
        "recurring_section": {
            "header": "YOUR RECURRING CHARACTERS",
            "subheader": "Some of them were starting to trust you.",
            "not_encountered": "{name} never crossed your path. You'll wonder about that.",
            "encountered_template": {
                "format": "{name} — {reception_language}",
                "cracked": "You understood {name}. That understanding doesn't expire.",
                "not_cracked": "{name} gave you chances. You heard the words but not the music.",
            },
        },
        "bridge": {
            "header": "THE BRIDGE",
            "lines": [
                "You learned enough to know what you don't know.",
                "That feeling — knowing you missed something but not what — is Tuesday.",
                "Your mom does this. Your partner does this. Your boss does this.",
                "They're not being difficult. They're being specific.",
            ],
            "cta_url": "arewegood.com",
            "closer": "Read what they mean.",
        },
    }

    # ── DEPORTED LATE ───────────────────────────────────────────────
    endings["variants"]["deported_late"] = {
        "id": "deported_late",
        "condition": "Heat >= 10 or Time <= 0 during locations 4-5 (nyc_outer, coney_island)",
        "status_line": "DEPORTED",
        "header_ascii": [
            "╔══════════════════════════════════════════╗",
            "║            D E P O R T E D               ║",
            "║                                          ║",
            "║   You could smell the ocean.              ║",
            "║   You could almost taste the mustard.    ║",
            "╚══════════════════════════════════════════╝",
        ],
        "narrator_line": "From the detention center window you can see the Cyclone roller coaster. The PA system announces visiting hours in a tone that suggests visitors are a theoretical concept.",
        "tone_note": "Tragic-comic proximity. You were so close. The contest continues within earshot.",
        "gaps_section": {
            "header": "YOUR GAPS THIS RUN",
            "subheader": "You read most of the room. But 'most' has a cost.",
            "empty_text": "You dodged every real conversation all the way to the boardwalk. The ocean doesn't judge, but we do.",
            "per_gap_template": {
                "format": "{category} — {npc_name} at {location}",
                "detail": "\"{npc_surface_line}\"",
                "reveal": "What they actually meant: {npc_actual}",
            },
        },
        "recurring_section": {
            "header": "YOUR RECURRING CHARACTERS",
            "subheader": "They'll remember you differently than you remember them.",
            "not_encountered": "{name} was in the crowd at Coney Island. You'll never know.",
            "encountered_template": {
                "format": "{name} — {reception_language}",
                "cracked": "{name} would vouch for you. That's rare. That's earned.",
                "not_cracked": "{name} tried to show you how they work. You were looking at something else.",
            },
        },
        "bridge": {
            "header": "THE BRIDGE",
            "lines": [
                "You almost made it. Almost is the hardest distance.",
                "The signals you missed at the end are the ones that cost the most.",
                "This is how it works with people you're close to — the closer, the higher the stakes.",
                "The mustard is still warm on Surf Avenue.",
            ],
            "cta_url": "arewegood.com",
            "closer": "Close the distance.",
        },
    }

    # ── WON HIGH TOKENS ────────────────────────────────────────────
    endings["variants"]["won_high_tokens"] = {
        "id": "won_high_tokens",
        "condition": "Reached Coney Island with 3+ AWG tokens remaining",
        "status_line": "ARRIVED",
        "header_ascii": [
            "╔══════════════════════════════════════════╗",
            "║           C O N E Y  I S L A N D         ║",
            "║                                          ║",
            "║   You made it.                           ║",
            "║   The hot dogs are real.                 ║",
            "║   You are ready.                         ║",
            "╚══════════════════════════════════════════╝",
        ],
        "narrator_line": "The Nathan's Famous sign hums with the quiet authority of an institution that has outlasted empires. You have a front-row spot. The mustard is complementary. It always was.",
        "tone_note": "Earned triumph. You used the tool, you read the room, you arrived prepared. Quiet satisfaction.",
        "gaps_section": {
            "header": "YOUR GAPS THIS RUN",
            "subheader": "Even you missed a few.",
            "empty_text": "Zero gaps. You read every room you walked into. The hot dog is a formality.",
            "per_gap_template": {
                "format": "{category} — {npc_name} at {location}",
                "detail": "\"{npc_surface_line}\"",
                "reveal": "What they actually meant: {npc_actual}",
            },
        },
        "recurring_section": {
            "header": "YOUR RECURRING CHARACTERS",
            "subheader": "The people who shaped your journey.",
            "not_encountered": "{name} exists in a run you haven't played yet.",
            "encountered_template": {
                "format": "{name} — {reception_language}",
                "cracked": "{name} sends a text you understand without reading twice. That's what fluency feels like.",
                "not_cracked": "{name} is still talking. You're still not quite hearing it.",
            },
        },
        "bridge": {
            "header": "THE BRIDGE",
            "lines": [
                "You made it because you listened for what wasn't said.",
                "That skill doesn't stay in the game.",
                "Your next conversation is already happening differently because of this one.",
                "The hot dog tastes better when you've earned the seat.",
            ],
            "cta_url": "arewegood.com",
            "closer": "Keep reading them.",
        },
    }

    # ── WON LOW TOKENS ─────────────────────────────────────────────
    endings["variants"]["won_low_tokens"] = {
        "id": "won_low_tokens",
        "condition": "Reached Coney Island with 1-2 AWG tokens remaining",
        "status_line": "ARRIVED",
        "header_ascii": [
            "╔══════════════════════════════════════════╗",
            "║           C O N E Y  I S L A N D         ║",
            "║                                          ║",
            "║   You made it.                           ║",
            "║   Barely.                                ║",
            "║   The hot dogs don't care.               ║",
            "╚══════════════════════════════════════════╝",
        ],
        "narrator_line": "You find standing room behind a family of four from Ronkonkoma. The father is explaining competitive eating to a child who did not ask. You understand both of them.",
        "tone_note": "Scrappy arrival. You made it but you felt the gaps. You know what you don't know.",
        "gaps_section": {
            "header": "YOUR GAPS THIS RUN",
            "subheader": "You arrived, but you left these on the table.",
            "empty_text": "No gaps recorded. Either you're a natural or you avoided the hard conversations. You know which.",
            "per_gap_template": {
                "format": "{category} — {npc_name} at {location}",
                "detail": "\"{npc_surface_line}\"",
                "reveal": "What they actually meant: {npc_actual}",
            },
        },
        "recurring_section": {
            "header": "YOUR RECURRING CHARACTERS",
            "subheader": "Some connections stuck. Some didn't.",
            "not_encountered": "{name} was one encounter away. Next run.",
            "encountered_template": {
                "format": "{name} — {reception_language}",
                "cracked": "You cracked {name}'s code. Apply that to someone real.",
                "not_cracked": "You and {name} talked past each other. Sound familiar?",
            },
        },
        "bridge": {
            "header": "THE BRIDGE",
            "lines": [
                "You survived on instinct. Instinct has a ceiling.",
                "The conversations you couldn't decode — you have those every week.",
                "The difference between getting by and getting through is reading the room.",
                "The hot dog is good. Knowing why it's good is better.",
            ],
            "cta_url": "arewegood.com",
            "closer": "Raise your ceiling.",
        },
    }

    # ── WON NO TOKENS ──────────────────────────────────────────────
    endings["variants"]["won_no_tokens"] = {
        "id": "won_no_tokens",
        "condition": "Reached Coney Island with 0 AWG tokens remaining",
        "status_line": "ARRIVED",
        "header_ascii": [
            "╔══════════════════════════════════════════╗",
            "║           C O N E Y  I S L A N D         ║",
            "║                                          ║",
            "║   You made it.                           ║",
            "║   You have no idea how.                  ║",
            "║   Neither do we.                         ║",
            "╚══════════════════════════════════════════╝",
        ],
        "narrator_line": "You're here. The boardwalk is sticky. The contest starts in eleven minutes. You spent every token and still arrived, which either makes you very lucky or very lost. The ocean doesn't clarify.",
        "tone_note": "Arrived blind. Maximum gap awareness. You made it but you have no idea what you missed. The most conversion-ready ending.",
        "gaps_section": {
            "header": "YOUR GAPS THIS RUN",
            "subheader": "You never looked. Here's what was there.",
            "empty_text": "You spent zero tokens and missed zero signals. We genuinely don't know how. Play again.",
            "per_gap_template": {
                "format": "{category} — {npc_name} at {location}",
                "detail": "\"{npc_surface_line}\"",
                "reveal": "What they actually meant: {npc_actual}",
            },
        },
        "recurring_section": {
            "header": "YOUR RECURRING CHARACTERS",
            "subheader": "They were talking to you. You were surviving.",
            "not_encountered": "{name} had something to teach you. Maybe next time.",
            "encountered_template": {
                "format": "{name} — {reception_language}",
                "cracked": "You cracked {name} without the scanner. That's either talent or an accident. Find out.",
                "not_cracked": "{name} was right there, speaking a language you didn't know existed.",
            },
        },
        "bridge": {
            "header": "THE BRIDGE",
            "lines": [
                "You crossed the entire country without understanding a single person completely.",
                "Congratulations. That's also how your last relationship went.",
                "The subtext was always there. You just didn't have the tool.",
                "Now you know the tool exists.",
            ],
            "cta_url": "arewegood.com",
            "closer": "Get the tool.",
        },
    }

    return endings


def validate_endings(endings):
    """Validate ending structure."""
    errors = []
    required_variants = [
        "deported_early", "deported_mid", "deported_late",
        "won_high_tokens", "won_low_tokens", "won_no_tokens",
    ]

    for var_id in required_variants:
        if var_id not in endings["variants"]:
            errors.append(f"Missing variant: {var_id}")
            continue

        v = endings["variants"][var_id]

        # Check required fields
        for field in ["id", "condition", "status_line", "header_ascii",
                      "narrator_line", "tone_note", "gaps_section",
                      "recurring_section", "bridge"]:
            if field not in v:
                errors.append(f"{var_id}: missing field '{field}'")

        # Check gaps section
        gs = v.get("gaps_section", {})
        for field in ["header", "subheader", "empty_text", "per_gap_template"]:
            if field not in gs:
                errors.append(f"{var_id}.gaps_section: missing '{field}'")

        # Check recurring section
        rs = v.get("recurring_section", {})
        for field in ["header", "subheader", "not_encountered", "encountered_template"]:
            if field not in rs:
                errors.append(f"{var_id}.recurring_section: missing '{field}'")

        # Check bridge section
        br = v.get("bridge", {})
        for field in ["header", "lines", "cta_url", "closer"]:
            if field not in br:
                errors.append(f"{var_id}.bridge: missing '{field}'")

        if "lines" in br and len(br["lines"]) != 4:
            errors.append(f"{var_id}.bridge: expected 4 lines, got {len(br['lines'])}")

        # Check status line
        if v.get("status_line") not in ("DEPORTED", "ARRIVED"):
            errors.append(f"{var_id}: status_line must be DEPORTED or ARRIVED")

        # Check header_ascii is a list
        if not isinstance(v.get("header_ascii"), list):
            errors.append(f"{var_id}: header_ascii must be a list")

    # Check signal categories
    if len(endings.get("signal_categories", [])) != 10:
        errors.append(f"Expected 10 signal categories, got {len(endings.get('signal_categories', []))}")

    # Check recurring characters
    if len(endings.get("recurring_characters", [])) != 5:
        errors.append(f"Expected 5 recurring characters, got {len(endings.get('recurring_characters', []))}")

    return errors


def main():
    endings = build_endings()
    errors = validate_endings(endings)

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
        return 1

    output_path = os.path.join(os.path.dirname(__file__), "..", "content", "endings.json")
    output_path = os.path.abspath(output_path)

    with open(output_path, "w") as f:
        json.dump(endings, f, indent=2)

    # Stats
    variants = endings["variants"]
    print(f"Generated {len(variants)} ending variants")
    print(f"  Deportation endings: {sum(1 for v in variants.values() if v['status_line'] == 'DEPORTED')}")
    print(f"  Win endings: {sum(1 for v in variants.values() if v['status_line'] == 'ARRIVED')}")
    print(f"  Signal categories: {len(endings['signal_categories'])}")
    print(f"  Recurring characters: {len(endings['recurring_characters'])}")
    print(f"  Bridge lines per variant: 4")
    print(f"\nAll variants validated successfully (0 errors)")
    print(f"Output: {output_path}")

    return 0


if __name__ == "__main__":
    exit(main())
