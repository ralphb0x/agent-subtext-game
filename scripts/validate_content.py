#!/usr/bin/env python3
"""Validate all content JSON files against CLAUDE.md schemas."""

import json
import sys
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'content')

errors = []
warnings = []

def err(file, msg):
    errors.append(f"  ERROR [{file}]: {msg}")

def warn(file, msg):
    warnings.append(f"  WARN  [{file}]: {msg}")

def check_keys(obj, required_keys, file, context=""):
    missing = [k for k in required_keys if k not in obj]
    if missing:
        err(file, f"{context}missing keys: {missing}")
    return len(missing) == 0

def validate_characters(data):
    file = "characters.json"
    if not isinstance(data, list):
        err(file, "expected array")
        return
    print(f"  characters: {len(data)} profiles")
    if len(data) < 1000:
        warn(file, f"only {len(data)} profiles (target: 1000+)")

    required = ["id", "name", "origin_country", "origin_city", "occupation",
                 "savings_usd", "language_skill", "asset", "burden",
                 "motivation", "entry_vector", "visa_status"]
    valid_entries = ["land_border", "air_legal", "air_illegal", "ocean", "internal"]
    valid_visa = ["none", "tourist", "student", "work", "expired"]

    for i, char in enumerate(data[:50]):  # spot check first 50
        check_keys(char, required, file, f"char[{i}] ")
        if "language_skill" in char:
            ls = char["language_skill"]
            if ls not in [1, 2, 3, 4, 5, "1", "2", "3", "4", "5"]:
                err(file, f"char[{i}] invalid language_skill: {ls}")
        if "entry_vector" in char and char["entry_vector"] not in valid_entries:
            err(file, f"char[{i}] invalid entry_vector: {char['entry_vector']}")
        if "visa_status" in char and char["visa_status"] not in valid_visa:
            err(file, f"char[{i}] invalid visa_status: {char['visa_status']}")

def validate_archetypes(data):
    file = "archetypes.json"
    if not isinstance(data, list):
        err(file, "expected array")
        return
    print(f"  archetypes: {len(data)} entries")
    if len(data) != 12:
        err(file, f"expected 12 archetypes, got {len(data)}")

    expected_ids = {"control-seeking", "lonely", "greedy", "paranoid", "bored",
                    "ideological", "guilty", "ambitious", "burned-out",
                    "suspicious", "empathetic", "corrupt"}
    found_ids = set()
    for arch in data:
        aid = arch.get("archetype_id", arch.get("id", ""))
        if aid:
            found_ids.add(aid)

    missing = expected_ids - found_ids
    if missing:
        err(file, f"missing archetypes: {missing}")

def validate_npcs(data):
    file = "npcs.json"
    if not isinstance(data, list):
        err(file, "expected array")
        return
    print(f"  npcs: {len(data)} instances")
    if len(data) < 100:
        err(file, f"only {len(data)} NPCs (minimum: 100)")

    for i, npc in enumerate(data[:30]):  # spot check first 30
        for key in ["npc_id", "archetype_id", "dialogue_tree"]:
            if key not in npc:
                err(file, f"npc[{i}] missing key: {key}")

        if "dialogue_tree" in npc:
            tree = npc["dialogue_tree"]
            if not isinstance(tree, list) or len(tree) == 0:
                err(file, f"npc[{i}] empty dialogue_tree")
                continue

            for j, node in enumerate(tree[:5]):  # check first 5 nodes
                node_keys = ["node_id", "emotional_state", "npc_line", "options"]
                for k in node_keys:
                    if k not in node:
                        err(file, f"npc[{i}].node[{j}] missing: {k}")

                if "options" in node:
                    for oi, opt in enumerate(node["options"]):
                        for ok in ["text", "tags", "rapport_delta", "suspicion_delta"]:
                            if ok not in opt:
                                err(file, f"npc[{i}].node[{j}].opt[{oi}] missing: {ok}")

                if "awg" in node:
                    awg = node["awg"]
                    for ak in ["gap_category", "surface", "actual", "tell",
                               "recommendation", "bridge_line", "closer"]:
                        if ak not in awg:
                            err(file, f"npc[{i}].node[{j}].awg missing: {ak}")

def validate_intel(data):
    file = "intel.json"
    if isinstance(data, dict):
        items = data.get("intel_items", data.get("items", data.get("intel", [])))
    elif isinstance(data, list):
        items = data
    else:
        err(file, "unexpected format")
        return

    print(f"  intel: {len(items)} items")
    if len(items) < 30:
        err(file, f"only {len(items)} intel items (target: 30)")

def validate_locations(data):
    file = "locations.json"
    if isinstance(data, dict):
        data = data.get("locations", [])
    if not isinstance(data, list):
        err(file, "expected array")
        return
    print(f"  locations: {len(data)} packs")
    if len(data) != 5:
        err(file, f"expected 5 locations, got {len(data)}")

    for i, loc in enumerate(data):
        for key in ["location_id", "name", "events"]:
            if key not in loc:
                err(file, f"location[{i}] missing: {key}")
        if "events" in loc:
            events = loc["events"]
            if isinstance(events, list) and len(events) < 10:
                warn(file, f"location[{i}] only {len(events)} events (target: 50)")

def validate_recurring(data):
    file = "recurring.json"
    if not isinstance(data, list):
        err(file, "expected array")
        return
    print(f"  recurring: {len(data)} characters")
    if len(data) != 5:
        err(file, f"expected 5 recurring characters, got {len(data)}")

    expected_names = {"rosa", "demir", "marcus", "elena", "handler"}
    found = set()
    for char in data:
        cid = char.get("character_id", char.get("id", "")).lower()
        found.add(cid)
        for key in ["name", "reception_language", "arc_states"]:
            if key not in char:
                err(file, f"recurring[{cid}] missing: {key}")
        if "arc_states" in char and len(char["arc_states"]) < 2:
            warn(file, f"recurring[{cid}] only {len(char['arc_states'])} arc states")

    missing = expected_names - found
    if missing:
        err(file, f"missing recurring characters: {missing}")

def validate_endings(data):
    file = "endings.json"
    if isinstance(data, dict):
        variants_raw = data.get("variants", data.get("endings", {}))
    elif isinstance(data, list):
        variants_raw = data
    else:
        err(file, "unexpected format")
        return

    # variants can be a dict keyed by variant id or a list
    if isinstance(variants_raw, dict):
        found = set(variants_raw.keys())
        print(f"  endings: {len(found)} variants")
    elif isinstance(variants_raw, list):
        found = set()
        for v in variants_raw:
            if isinstance(v, dict):
                vid = v.get("id", v.get("variant_id", ""))
                found.add(vid)
        print(f"  endings: {len(found)} variants")
    else:
        err(file, "unexpected variants format")
        return

    expected_ids = {"deported_early", "deported_mid", "deported_late",
                    "won_high_tokens", "won_low_tokens", "won_no_tokens"}
    missing = expected_ids - found
    if missing:
        err(file, f"missing ending variants: {missing}")

def main():
    print("Validating subtext.game content...\n")

    validators = {
        "characters.json": validate_characters,
        "archetypes.json": validate_archetypes,
        "npcs.json": validate_npcs,
        "intel.json": validate_intel,
        "locations.json": validate_locations,
        "recurring.json": validate_recurring,
        "endings.json": validate_endings,
    }

    for filename, validator in validators.items():
        path = os.path.join(CONTENT_DIR, filename)
        if not os.path.exists(path):
            err(filename, "FILE NOT FOUND")
            continue
        try:
            with open(path) as f:
                data = json.load(f)
            validator(data)
        except json.JSONDecodeError as e:
            err(filename, f"invalid JSON: {e}")

    print()
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(w)
        print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print("ALL CONTENT VALID")
        sys.exit(0)

if __name__ == "__main__":
    main()
