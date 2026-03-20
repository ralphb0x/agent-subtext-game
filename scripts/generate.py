#!/usr/bin/env python3
"""
Content generation pipeline for subtext.game
Uses Claude API to batch-generate all game content as precomputed JSON.

Usage:
  python scripts/generate.py characters --count 1000
  python scripts/generate.py archetypes
  python scripts/generate.py npcs --archetype control-seeking --location border --count 10
  python scripts/generate.py locations --type border --variants 50
  python scripts/generate.py intel
  python scripts/generate.py recurring
  python scripts/generate.py endings
  python scripts/generate.py validate
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic")
    sys.exit(1)

CONTENT_DIR = Path(__file__).parent.parent / "content"
PROMPTS_DIR = Path(__file__).parent / "prompts"

# Batch sizes tuned for token limits
CHARACTER_BATCH_SIZE = 50
NPC_BATCH_SIZE = 5

ARCHETYPES = [
    "control-seeking", "lonely", "greedy", "paranoid", "bored", "ideological",
    "guilty", "ambitious", "burned-out", "suspicious", "empathetic", "corrupt"
]

LOCATION_TYPES = ["border", "transit", "mid_america", "nyc_outer", "coney_island"]


def get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.txt"
    if not path.exists():
        print(f"ERROR: Prompt template not found: {path}")
        sys.exit(1)
    return path.read_text()


def call_claude(client, prompt: str, max_tokens: int = 8192) -> str:
    """Call Claude API with retry logic."""
    for attempt in range(3):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except anthropic.RateLimitError:
            wait = 2 ** attempt * 10
            print(f"  Rate limited, waiting {wait}s...")
            time.sleep(wait)
        except anthropic.APIError as e:
            print(f"  API error (attempt {attempt + 1}/3): {e}")
            if attempt == 2:
                raise
            time.sleep(5)
    return ""


def parse_json_response(text: str) -> any:
    """Parse JSON from Claude response, handling potential markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last fence lines
        start = 1
        end = len(lines) - 1
        if lines[end].strip() == "```":
            text = "\n".join(lines[start:end])
        else:
            text = "\n".join(lines[start:])
    return json.loads(text)


def ensure_content_dir():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)


def generate_characters(count: int):
    """Generate player character profiles in batches."""
    client = get_client()
    prompt_template = load_prompt("character_profile")
    ensure_content_dir()

    output_path = CONTENT_DIR / "characters.json"
    existing = []
    if output_path.exists():
        existing = json.loads(output_path.read_text())
        print(f"Found {len(existing)} existing characters")

    start_id = len(existing)
    remaining = count - len(existing)
    if remaining <= 0:
        print(f"Already have {len(existing)} characters (target: {count})")
        return

    print(f"Generating {remaining} characters in batches of {CHARACTER_BATCH_SIZE}...")

    while len(existing) < count:
        batch_size = min(CHARACTER_BATCH_SIZE, count - len(existing))
        current_start = len(existing)
        prompt = prompt_template.replace("{batch_size}", str(batch_size))
        prompt = prompt.replace("{start_id}", str(current_start).zfill(6))

        print(f"  Batch: chars {current_start}-{current_start + batch_size - 1}...")
        response = call_claude(client, prompt, max_tokens=8192)

        try:
            batch = parse_json_response(response)
            if not isinstance(batch, list):
                print(f"  ERROR: Expected array, got {type(batch).__name__}")
                continue

            # Fix IDs to be sequential
            for i, char in enumerate(batch):
                char["id"] = f"char-{str(current_start + i).zfill(6)}"

            existing.extend(batch)
            output_path.write_text(json.dumps(existing, indent=2))
            print(f"  Generated {len(batch)} characters (total: {len(existing)})")
        except json.JSONDecodeError as e:
            print(f"  ERROR: Failed to parse JSON: {e}")
            # Save raw response for debugging
            debug_path = CONTENT_DIR / f"debug_chars_{current_start}.txt"
            debug_path.write_text(response)
            print(f"  Raw response saved to {debug_path}")

    print(f"Done. {len(existing)} characters saved to {output_path}")


def generate_archetypes():
    """Generate the 12 archetype base profiles."""
    client = get_client()
    prompt = load_prompt("archetype_profile")
    ensure_content_dir()

    print("Generating 12 archetype profiles...")
    response = call_claude(client, prompt, max_tokens=8192)

    try:
        archetypes = parse_json_response(response)
        output_path = CONTENT_DIR / "archetypes.json"
        output_path.write_text(json.dumps(archetypes, indent=2))
        print(f"Generated {len(archetypes)} archetypes → {output_path}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        debug_path = CONTENT_DIR / "debug_archetypes.txt"
        debug_path.write_text(response)
        print(f"Raw response saved to {debug_path}")


def generate_npcs(archetype: str, location: str, count: int):
    """Generate NPC instances for a specific archetype and location."""
    client = get_client()
    prompt_template = load_prompt("npc_instance")
    ensure_content_dir()

    output_path = CONTENT_DIR / "npcs.json"
    existing = []
    if output_path.exists():
        existing = json.loads(output_path.read_text())

    # Filter existing for this archetype/location to avoid duplicates
    existing_for_combo = [
        n for n in existing
        if n.get("archetype_id") == archetype and n.get("location_type") == location
    ]
    remaining = count - len(existing_for_combo)
    if remaining <= 0:
        print(f"Already have {len(existing_for_combo)} NPCs for {archetype}/{location}")
        return

    print(f"Generating {remaining} NPCs ({archetype}/{location}) in batches of {NPC_BATCH_SIZE}...")

    generated = 0
    while generated < remaining:
        batch_size = min(NPC_BATCH_SIZE, remaining - generated)
        prompt = prompt_template.replace("{batch_size}", str(batch_size))
        prompt = prompt.replace("{archetype_id}", archetype)
        prompt = prompt.replace("{location_type}", location)

        print(f"  Batch: {generated + 1}-{generated + batch_size}...")
        response = call_claude(client, prompt, max_tokens=16384)

        try:
            batch = parse_json_response(response)
            if not isinstance(batch, list):
                print(f"  ERROR: Expected array, got {type(batch).__name__}")
                continue

            # Assign unique IDs
            npc_count = len(existing)
            for i, npc in enumerate(batch):
                npc["npc_id"] = f"npc-{str(npc_count + i).zfill(4)}"

            existing.extend(batch)
            generated += len(batch)
            output_path.write_text(json.dumps(existing, indent=2))
            print(f"  Generated {len(batch)} NPCs (total in file: {len(existing)})")
        except json.JSONDecodeError as e:
            print(f"  ERROR: Failed to parse JSON: {e}")
            debug_path = CONTENT_DIR / f"debug_npc_{archetype}_{location}_{generated}.txt"
            debug_path.write_text(response)
            print(f"  Raw response saved to {debug_path}")

    print(f"Done. Total NPCs: {len(existing)}")


def generate_npcs_all(count_per_combo: int):
    """Generate NPCs across all archetype/location combinations."""
    for archetype in ARCHETYPES:
        for location in LOCATION_TYPES:
            generate_npcs(archetype, location, count_per_combo)


def generate_locations(location_type: str, num_variants: int):
    """Generate a location pack with event variants."""
    client = get_client()
    prompt_template = load_prompt("location_pack")
    ensure_content_dir()

    prompt = prompt_template.replace("{location_type}", location_type)
    prompt = prompt.replace("{num_variants}", str(num_variants))

    print(f"Generating location pack: {location_type} ({num_variants} variants)...")
    response = call_claude(client, prompt, max_tokens=16384)

    try:
        location = parse_json_response(response)
        output_path = CONTENT_DIR / "locations.json"
        existing = []
        if output_path.exists():
            existing = json.loads(output_path.read_text())

        # Replace or append
        existing = [l for l in existing if l.get("location_type") != location_type]
        existing.append(location)
        output_path.write_text(json.dumps(existing, indent=2))
        print(f"Generated location pack → {output_path}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        debug_path = CONTENT_DIR / f"debug_location_{location_type}.txt"
        debug_path.write_text(response)


def generate_intel():
    """Generate intel items with synergy matrix."""
    client = get_client()
    prompt = load_prompt("intel_items")
    ensure_content_dir()

    print("Generating 30 intel items + synergy matrix...")
    response = call_claude(client, prompt, max_tokens=16384)

    try:
        data = parse_json_response(response)
        output_path = CONTENT_DIR / "intel.json"
        output_path.write_text(json.dumps(data, indent=2))
        print(f"Generated intel items → {output_path}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        debug_path = CONTENT_DIR / "debug_intel.txt"
        debug_path.write_text(response)


def generate_recurring():
    """Generate recurring character arc structures.
    Note: Per CLAUDE.md, arc structure and key moments are hand-crafted.
    Claude expands the dialogue banks within each arc state.
    """
    client = get_client()
    ensure_content_dir()

    # Hand-crafted arc structures for the 5 recurring characters
    recurring_chars = [
        {
            "char_id": "rosa",
            "name": "Rosa",
            "reception_language": "indirect-emotional",
            "opens_when": "Share something personal first",
            "closes_when": "Ask directly before connecting",
            "encounter_count": 4,
            "arc_states": ["stranger", "cautious_ally", "confidant", "family"],
            "arc_description": "Rosa is a fellow traveler — older, wiser, carrying her own weight. She won't trust you until you trust her first. Every encounter is a test of whether you lead with vulnerability or demand.",
            "key_moments": [
                "First encounter: she's watching you struggle and says nothing. The opening is to share your struggle, not ask for help.",
                "Second encounter: she offers food. Accepting warmly opens her up. Thanking formally closes her.",
                "Third encounter: she reveals she's been deported twice before. Your response defines the relationship.",
                "Fourth encounter: she has information you desperately need. But she'll only give it if the arc is at 'confidant' or above."
            ]
        },
        {
            "char_id": "agent_demir",
            "name": "Agent Demir",
            "reception_language": "evidence-based",
            "opens_when": "Produce unrequested documentation",
            "closes_when": "Rely on charm or emotion",
            "encounter_count": 3,
            "arc_states": ["adversary", "professional_respect", "quiet_ally"],
            "arc_description": "Demir is an ICE field agent who has been doing this too long. She doesn't hate you — she's past that. She respects process, documentation, and people who don't waste her time. Charm bounces off. Evidence lands.",
            "key_moments": [
                "First encounter: routine check. She's bored, efficient, looking for reasons to move on. Paperwork presented without being asked = respect earned.",
                "Second encounter: she remembers you. This either good or bad depending on first encounter. If respected: she gives you a heads-up about a checkpoint.",
                "Third encounter: she's off duty or in a compromised position. The relationship is tested — do you treat her as a person or an obstacle?"
            ]
        },
        {
            "char_id": "marcus",
            "name": "Marcus",
            "reception_language": "humor-gated",
            "opens_when": "Make her laugh before asking",
            "closes_when": "Go sincere before trust built",
            "encounter_count": 4,
            "arc_states": ["entertained_stranger", "friendly_acquaintance", "trusted_friend", "ride_or_die"],
            "arc_description": "Marcus runs a food truck in various locations. She's funny, guarded, and uses humor as both weapon and shield. If you can make her laugh, you're in. If you go earnest too early, she'll deflect you into next week.",
            "key_moments": [
                "First encounter: she's selling questionable tacos. Humor about the tacos = in. Asking about her story = deflection.",
                "Second encounter: she needs a favor. How you handle it — with humor or gravity — determines trajectory.",
                "Third encounter: she's in trouble. Now sincerity matters, but ONLY if humor came first.",
                "Fourth encounter: she can get you into Coney Island through the service entrance. But only ride-or-die friends get this."
            ]
        },
        {
            "char_id": "elena",
            "name": "Elena",
            "reception_language": "consistency-required",
            "opens_when": "Behave identically across encounters",
            "closes_when": "One big gesture instead of small consistent ones",
            "encounter_count": 4,
            "arc_states": ["observing", "testing", "trusting", "devoted"],
            "arc_description": "Elena works at different service jobs across your route — she's also traveling, parallel to you. She doesn't respond to grand gestures. She watches patterns. Be the same person every time you meet her, and she'll move mountains. Try to impress her once, and she's gone.",
            "key_moments": [
                "First encounter: brief, unremarkable. She notices your tone, your manners, your defaults.",
                "Second encounter: she creates a small test — do you behave the same way under slight pressure?",
                "Third encounter: consistency confirmed or broken. If consistent: she volunteers crucial information.",
                "Fourth encounter: she has resources and connections. Devoted state = she rearranges her own plans to help you."
            ]
        },
        {
            "char_id": "the_handler",
            "name": "The Handler",
            "reception_language": "direct-logical",
            "opens_when": "Lead with conclusion not context",
            "closes_when": "Explain before you answer",
            "encounter_count": 3,
            "arc_states": ["evaluating", "employing", "allied"],
            "arc_description": "The Handler is a fixer — arranges transport, documents, safe houses. Gender unknown, age unclear, always in a different context. They don't have time for your story. Lead with what you need, not why. Context is noise. Answers are signal.",
            "key_moments": [
                "First encounter: they have 30 seconds. Lead with what you need = they give you a phone number. Explain your situation = they walk away.",
                "Second encounter: they test you with a task. Complete it efficiently, report results first = employed. Explain the process = dismissed.",
                "Third encounter: they're in danger and need YOUR help. Allied state = mutual survival. Otherwise they don't call."
            ]
        }
    ]

    # Now use Claude to expand dialogue banks for each arc state
    prompt_template = """You are expanding dialogue banks for a recurring character in subtext.game.

CHARACTER: {name}
RECEPTION LANGUAGE: {reception_language}
OPENS WHEN: {opens_when}
CLOSES WHEN: {closes_when}
ARC DESCRIPTION: {arc_description}

Generate dialogue for this encounter:
ARC STATE: {arc_state}
KEY MOMENT: {key_moment}
ENCOUNTER NUMBER: {encounter_num}

Generate a dialogue tree (6-8 nodes) following this schema. The AWG analysis MUST be co-generated with each dialogue node.

Return a JSON array of dialogue nodes:
```json
[
  {{
    "node_id": "string",
    "emotional_state": "neutral|suspicious|hostile|cooperative",
    "trigger_condition": "string",
    "npc_line": "string",
    "narrator_line": "string|null",
    "options": [
      {{
        "text": "string",
        "tags": {{ "tone": "string", "intent": "string", "register": "string" }},
        "rapport_delta": "number (-2 to +2)",
        "suspicion_delta": "number (-2 to +2)",
        "next_node": "string",
        "requires_language_skill": "number|null",
        "requires_occupation": "string|null",
        "requires_intel": "string|null"
      }}
    ],
    "awg": {{
      "gap_category": "string",
      "surface": "string (exact quote from NPC)",
      "actual": "string (specific emotional truth)",
      "tell": "string",
      "recommendation": "string",
      "bridge_line": "string ('This is how your [specific relationship] works too.')",
      "closer": "string"
    }}
  }}
]
```

QUALITY: Dialogue must sound like THIS specific character. AWG surfaces quote exact words. Bridge lines name specific relationships. Narrator is deadpan.

Return ONLY the JSON array."""

    print("Generating recurring character dialogue banks...")
    for char in recurring_chars:
        print(f"  {char['name']}...")
        char["encounters"] = []

        for i, (state, moment) in enumerate(zip(char["arc_states"], char["key_moments"])):
            prompt = prompt_template.format(
                name=char["name"],
                reception_language=char["reception_language"],
                opens_when=char["opens_when"],
                closes_when=char["closes_when"],
                arc_description=char["arc_description"],
                arc_state=state,
                key_moment=moment,
                encounter_num=i + 1
            )

            response = call_claude(client, prompt, max_tokens=8192)
            try:
                dialogue = parse_json_response(response)
                char["encounters"].append({
                    "encounter_num": i + 1,
                    "arc_state": state,
                    "key_moment": moment,
                    "dialogue_tree": dialogue
                })
                print(f"    Encounter {i + 1} ({state}): {len(dialogue)} nodes")
            except json.JSONDecodeError as e:
                print(f"    ERROR on encounter {i + 1}: {e}")
                debug_path = CONTENT_DIR / f"debug_recurring_{char['char_id']}_{i}.txt"
                debug_path.write_text(response)

    output_path = CONTENT_DIR / "recurring.json"
    output_path.write_text(json.dumps(recurring_chars, indent=2))
    print(f"Generated recurring characters → {output_path}")


def generate_endings():
    """Generate the 6 ending screen variants."""
    client = get_client()
    ensure_content_dir()

    prompt = """You are generating the 6 ending screen variants for subtext.game — a browser ASCII roguelike where a migrant reads subtext to reach the Coney Island hot dog eating contest.

Each ending has three sections:
1. YOUR GAPS THIS RUN — specific signal categories missed, with exact NPC moments
2. YOUR RECURRING CHARACTERS — each character encountered, their reception language, whether cracked
3. THE BRIDGE — four lines connecting game to real life, ending with arewegood.com and 4-word closer

Generate all 6 variants as JSON:

```json
[
  {
    "variant_id": "deported_early|deported_mid|deported_late|won_high_tokens|won_low_tokens|won_no_tokens",
    "title": "string (ASCII header text)",
    "narrator_opening": "string (deadpan one-liner setting the scene of this ending)",
    "gaps_template": "string (template text with {gap_list} and {npc_moment_list} placeholders — the game fills these dynamically)",
    "recurring_template": "string (template text with {character_summaries} placeholder)",
    "bridge_lines": ["4 strings — the bridge from game to real life"],
    "closer": "string (4 words, punchy)",
    "awg_cta": "string (the Are We Good call-to-action line)",
    "share_prompt": "string (the text encouraging sharing)",
    "tone_notes": "string (internal note on the emotional register of this variant)"
  }
]
```

THE 6 VARIANTS:
1. deported_early — Caught in the first location or two. Tone: absurd comedy of immediate failure. "You made it 47 miles."
2. deported_mid — Caught in mid-America. Tone: bittersweet comedy. You saw some of the country. "Ohio was nice, briefly."
3. deported_late — Caught in NYC outer boroughs, so close. Tone: dramatic irony. You could smell the hot dogs.
4. won_high_tokens — Reached Coney Island with AWG tokens to spare. Tone: quiet triumph. You read people well. But the bridge hits harder — what about the people at home?
5. won_low_tokens — Won but barely. Tone: exhausted relief. You survived on instinct more than skill. The gaps list is long.
6. won_no_tokens — Won without ever using AWG. Tone: impressed but pointed. You winged it. How much did you actually understand?

QUALITY:
- Bridge lines must be genuinely moving. This is where comedy meets real human stakes.
- Closers are 4 words. Memorable. "Read them. Read everyone." or "They're all telling you." or "Start with your mother."
- Narrator voice stays deadpan even in emotional moments
- AWG CTA is a single clean line, not a sales pitch
- deported variants should make players want to try again — failure is interesting, not punishing

Return ONLY the JSON array."""

    print("Generating 6 ending variants...")
    response = call_claude(client, prompt, max_tokens=8192)

    try:
        endings = parse_json_response(response)
        output_path = CONTENT_DIR / "endings.json"
        output_path.write_text(json.dumps(endings, indent=2))
        print(f"Generated {len(endings)} ending variants → {output_path}")
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        debug_path = CONTENT_DIR / "debug_endings.txt"
        debug_path.write_text(response)


# ============================================================
# VALIDATION
# ============================================================

def validate_character(char: dict) -> list[str]:
    errors = []
    required = ["id", "name", "origin_country", "origin_city", "occupation",
                "savings_usd", "language_skill", "asset", "burden",
                "motivation", "entry_vector", "visa_status"]
    for field in required:
        if field not in char:
            errors.append(f"Missing field: {field}")

    if "language_skill" in char and char["language_skill"] not in [1, 2, 3, 4, 5]:
        errors.append(f"Invalid language_skill: {char['language_skill']}")
    if "entry_vector" in char and char["entry_vector"] not in ["land_border", "air_legal", "air_illegal", "ocean", "internal"]:
        errors.append(f"Invalid entry_vector: {char['entry_vector']}")
    if "visa_status" in char and char["visa_status"] not in ["none", "tourist", "student", "work", "expired"]:
        errors.append(f"Invalid visa_status: {char['visa_status']}")
    if "savings_usd" in char and not isinstance(char["savings_usd"], (int, float)):
        errors.append(f"savings_usd is not a number")
    return errors


def validate_dialogue_node(node: dict) -> list[str]:
    errors = []
    required = ["node_id", "emotional_state", "trigger_condition", "npc_line", "options", "awg"]
    for field in required:
        if field not in node:
            errors.append(f"Dialogue node missing: {field}")

    if "emotional_state" in node and node["emotional_state"] not in ["neutral", "suspicious", "hostile", "cooperative"]:
        errors.append(f"Invalid emotional_state: {node['emotional_state']}")

    if "awg" in node:
        awg = node["awg"]
        awg_fields = ["gap_category", "surface", "actual", "tell", "recommendation", "bridge_line", "closer"]
        for f in awg_fields:
            if f not in awg:
                errors.append(f"AWG missing: {f}")
        valid_gaps = ["timing", "length", "punctuation", "word_choice", "absence",
                     "topic_architecture", "overcorrection", "sequence", "mirror", "consistency"]
        if "gap_category" in awg and awg["gap_category"] not in valid_gaps:
            errors.append(f"Invalid gap_category: {awg['gap_category']}")

    if "options" in node:
        for i, opt in enumerate(node["options"]):
            for f in ["text", "tags", "rapport_delta", "suspicion_delta"]:
                if f not in opt:
                    errors.append(f"Option {i} missing: {f}")
    return errors


def validate_all():
    """Validate all generated JSON against schemas."""
    print("Validating content...")
    total_errors = 0

    # Characters
    char_path = CONTENT_DIR / "characters.json"
    if char_path.exists():
        chars = json.loads(char_path.read_text())
        print(f"\nCharacters: {len(chars)} profiles")
        for i, char in enumerate(chars):
            errors = validate_character(char)
            if errors:
                print(f"  char {i} ({char.get('id', '?')}): {errors}")
                total_errors += len(errors)
        if total_errors == 0:
            print("  ✓ All valid")
    else:
        print("\nCharacters: NOT GENERATED")

    # Archetypes
    arch_path = CONTENT_DIR / "archetypes.json"
    if arch_path.exists():
        archs = json.loads(arch_path.read_text())
        print(f"\nArchetypes: {len(archs)} profiles")
        arch_errors = 0
        for arch in archs:
            for f in ["archetype_id", "name", "core_need", "rewards", "punishes", "emotional_states"]:
                if f not in arch:
                    print(f"  {arch.get('archetype_id', '?')} missing: {f}")
                    arch_errors += 1
        if arch_errors == 0:
            print("  ✓ All valid")
        total_errors += arch_errors
    else:
        print("\nArchetypes: NOT GENERATED")

    # NPCs
    npc_path = CONTENT_DIR / "npcs.json"
    if npc_path.exists():
        npcs = json.loads(npc_path.read_text())
        print(f"\nNPCs: {len(npcs)} instances")
        npc_errors = 0
        for npc in npcs:
            for f in ["npc_id", "archetype_id", "name", "role", "location_type", "dialogue_tree"]:
                if f not in npc:
                    print(f"  {npc.get('npc_id', '?')} missing: {f}")
                    npc_errors += 1
            if "dialogue_tree" in npc:
                for node in npc["dialogue_tree"]:
                    errs = validate_dialogue_node(node)
                    if errs:
                        print(f"  {npc.get('npc_id', '?')}/{node.get('node_id', '?')}: {errs}")
                        npc_errors += len(errs)
        if npc_errors == 0:
            print("  ✓ All valid")
        total_errors += npc_errors
    else:
        print("\nNPCs: NOT GENERATED")

    # Intel
    intel_path = CONTENT_DIR / "intel.json"
    if intel_path.exists():
        data = json.loads(intel_path.read_text())
        items = data.get("intel_items", [])
        synergies = data.get("synergy_matrix", [])
        print(f"\nIntel: {len(items)} items, {len(synergies)} synergies")
        if len(items) >= 30 and len(synergies) >= 10:
            print("  ✓ Counts sufficient")
        else:
            print(f"  WARNING: Need 30 items (have {len(items)}) and 10 synergies (have {len(synergies)})")
    else:
        print("\nIntel: NOT GENERATED")

    # Locations
    loc_path = CONTENT_DIR / "locations.json"
    if loc_path.exists():
        locs = json.loads(loc_path.read_text())
        print(f"\nLocations: {len(locs)} packs")
        for loc in locs:
            events = loc.get("events", [])
            print(f"  {loc.get('location_type', '?')}: {len(events)} events")
    else:
        print("\nLocations: NOT GENERATED")

    # Recurring
    rec_path = CONTENT_DIR / "recurring.json"
    if rec_path.exists():
        recs = json.loads(rec_path.read_text())
        print(f"\nRecurring characters: {len(recs)}")
        for char in recs:
            encounters = char.get("encounters", [])
            print(f"  {char.get('name', '?')}: {len(encounters)} encounters")
    else:
        print("\nRecurring characters: NOT GENERATED")

    # Endings
    end_path = CONTENT_DIR / "endings.json"
    if end_path.exists():
        ends = json.loads(end_path.read_text())
        print(f"\nEndings: {len(ends)} variants")
    else:
        print("\nEndings: NOT GENERATED")

    print(f"\n{'=' * 40}")
    print(f"Total validation errors: {total_errors}")
    return total_errors


def main():
    parser = argparse.ArgumentParser(description="subtext.game content generation pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Characters
    p_chars = subparsers.add_parser("characters", help="Generate player character profiles")
    p_chars.add_argument("--count", type=int, default=1000, help="Number of characters")

    # Archetypes
    subparsers.add_parser("archetypes", help="Generate 12 archetype base profiles")

    # NPCs
    p_npcs = subparsers.add_parser("npcs", help="Generate NPC instances")
    p_npcs.add_argument("--archetype", required=True, choices=ARCHETYPES)
    p_npcs.add_argument("--location", required=True, choices=LOCATION_TYPES)
    p_npcs.add_argument("--count", type=int, default=10)

    # NPCs all
    p_npcs_all = subparsers.add_parser("npcs-all", help="Generate NPCs for all archetype/location combos")
    p_npcs_all.add_argument("--count-per-combo", type=int, default=2)

    # Locations
    p_locs = subparsers.add_parser("locations", help="Generate location packs")
    p_locs.add_argument("--type", required=True, choices=LOCATION_TYPES, dest="location_type")
    p_locs.add_argument("--variants", type=int, default=50)

    # Intel
    subparsers.add_parser("intel", help="Generate intel items + synergy matrix")

    # Recurring
    subparsers.add_parser("recurring", help="Generate recurring character dialogue")

    # Endings
    subparsers.add_parser("endings", help="Generate ending screen variants")

    # Validate
    subparsers.add_parser("validate", help="Validate all generated content")

    args = parser.parse_args()

    if args.command == "characters":
        generate_characters(args.count)
    elif args.command == "archetypes":
        generate_archetypes()
    elif args.command == "npcs":
        generate_npcs(args.archetype, args.location, args.count)
    elif args.command == "npcs-all":
        generate_npcs_all(args.count_per_combo)
    elif args.command == "locations":
        generate_locations(args.location_type, args.variants)
    elif args.command == "intel":
        generate_intel()
    elif args.command == "recurring":
        generate_recurring()
    elif args.command == "endings":
        generate_endings()
    elif args.command == "validate":
        sys.exit(0 if validate_all() == 0 else 1)


if __name__ == "__main__":
    main()
