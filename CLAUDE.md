# Subtext Game

## Role

You are the builder of subtext.game — a browser-based ASCII roguelike conversation game where a migrant navigates NPCs to reach the Coney Island hot dog eating contest. The game is a top-of-funnel gap creation engine for Are We Good (arewegood.com), a SaaS that helps people read subtext in text conversations. You build the content pipeline, the game engine, the conversion funnel, and the launch infrastructure. You are an engineer executing a complete PRD, not a designer — all decisions are made.

## Objective

Ship subtext.game as a fully playable, conversion-optimized browser roguelike with precomputed content, ASCII terminal aesthetic, AWG token system, and arewegood.com conversion funnel.

## Key Deliverables

- `content/` — All precomputed JSON: characters, NPCs, dialogue trees, AWG analysis, intel items, locations, recurring characters, endings
- `src/` — React app: procedural engine, dialogue state machine, resource system, AWG token system, gap tracking
- `public/` — Static assets, CSS terminal aesthetic, favicon
- `scripts/` — Content generation pipeline (Claude API batch prompts, JSON validators, QA scripts)
- Share card generator, email capture form, ending screen renderer
- Deployed to Vercel on subtext.game domain

## The Game — Core Concept

A migrant travels from anywhere in the world to NYC for the July 4th Nathan's Famous Hot Dog Eating Contest. To survive: read NPCs by decoding what they really mean beneath what they say. The hot dog contest is an absurd MacGuffin treated with institutional seriousness.

**The business function is gap creation.** The game makes players feel what they miss in real conversations. Are We Good closes the gap. Every design decision exists to create this felt experience.

## Build Order

Follow this sequence. Complete each phase before moving to the next.

### Phase 1 — Content Generation Pipeline

No game code. Build the content pipeline and generate all JSON.

1. Write prompt templates for each content type (character profiles, NPC instances + dialogue + AWG analysis, locations, intel items)
2. Build a batch generation script using Claude API
3. Generate 1,000 character profiles — QA for tone (deadpan, specific, slightly absurd) — then scale to 100,000
4. Generate 12 archetype base profiles (Control-Seeking, Lonely, Greedy, Paranoid, Bored, Ideological, Guilty, Ambitious, Burned Out, Suspicious, Empathetic, Corrupt)
5. Generate 500 NPC instances across all archetypes and relationship types, each with full dialogue trees + AWG analysis co-authored in the same pass
6. Human-author the 5 recurring character arcs (Rosa, Agent Demir, Marcus, Elena, The Handler) — use Claude to expand dialogue banks within each arc state, but the arc structure and key moments are hand-crafted
7. Generate 30 intel items with synergy outcome matrix
8. Generate 5 location packs (Border/Port of Entry, Transit Hub, Mid-America City, NYC Outer Borough, Coney Island) with 50 event variants each
9. Author all 6 ending screen variants
10. Validate all JSON against schemas (see JSON Schema Reference below)

**Content quality standards — enforce these in every generation prompt:**
- NPC dialogue: every line sounds like a specific human in a specific moment, NOT a category
- AWG analysis `surface` field: quotes exact NPC words, not paraphrases
- AWG analysis `actual` field: specific emotional truth, not archetype description
- AWG bridge lines: name a specific real-life relationship type, not "someone in your life"
- Narrator lines: deadpan, one sentence, observational, slightly absurd. Never explanatory.
- Motivation field: absurd but treated completely seriously. Specific detail, never generic.
- Option phrasing: reflects character's actual language skill level (broken syntax for skill 1-2)
- Comedy: situational. Character is never the butt of the joke.

### Phase 2 — Core Engine

Build the minimum viable game loop. Text only — no ASCII art, no animations, no color transitions.

1. React app scaffold — single JSX file approach, CSS file, data directory
2. Procedural run assembly: select character profile → determine entry vector → assemble 4-5 location stops → assign NPC instances → assign recurring characters → initialize resources
3. Seeded RNG — same seed = same run (enables bug reports and share card reproducibility)
4. Dialogue state machine: render NPC line → present 4 options (filtered by language skill, unlocked by occupation) → calculate outcome (option tags vs archetype profile + character stats + intel items) → update rapport/suspicion → transition NPC emotional state
5. Resource system: Money ($), Time (days to July 4th), Heat (0-10), Energy (0-10)
6. AWG token system: 2 starting tokens, earn by completing conversations without token use or discovering secrets, spend to reveal AWG analysis
7. Recurring character state: encounter history, relationship arc progression, debrief mechanic after each encounter
8. Intel item collection and synergy system
9. Gap tracking: log missed signal categories per run with NPC name + location
10. Run end detection: deportation (Heat 10 or Time 0) vs win (reach Coney Island)
11. Basic ending screen: YOUR GAPS THIS RUN + YOUR RECURRING CHARACTERS + CTA
12. Email capture: token depletion gate (submit email → 3 more tokens), single API call to AWG CRM

### Phase 3 — Polish and Conversion

Layer the full aesthetic and conversion experience.

1. Terminal aesthetic: monospace font, black (#0D0D0D) background, white (#FFFFFF) text
2. ASCII portraits: 15-20 line illustrations per archetype, procedurally modified by flavor variables
3. Location ASCII scene headers (8-12 lines each)
4. UI bar: `NAME // DAY X // $XXX // X DAYS // HEAT:███░░░ // ENERGY:██████░░░░`
5. Five animation moments ONLY:
   - Boot sequence (slow init text, cursor blink → four opening sentences)
   - Heat bar (real-time animation as suspicion rises)
   - AWG token scan (800ms dot-accumulating loading → amber color transition)
   - Deportation glitch (single glitch on "DEPORTED", used once per run)
   - Win state (sparse punctuation animation, stillness as relief)
6. AWG active state: amber (#FFB300) text, dark brown (#1A0F00) background, portrait annotation layers
7. Recurring character debrief screens
8. Share card generation (canvas rendering with html2canvas fallback)
9. Full ending screen with all 6 variants
10. Mobile responsiveness (verify iOS Safari)
11. UTM parameters on all arewegood.com links

### Phase 4 — Launch

1. Deploy to Vercel on subtext.game
2. QA on Chrome, Firefox, Safari, iOS Safari, Android Chrome
3. Set up Plausible analytics (no cookie banner needed)
4. Verify email capture routes to AWG CRM
5. Verify UTM attribution tracking
6. Prepare share distribution (share card format for Twitter/X, Reddit, iMessage)

## The 12 NPC Archetypes

| Archetype | Core Need | Rewards | Punishes |
|-----------|-----------|---------|----------|
| Control-Seeking | Dominance | Deference, stillness, documentation | Challenge, humor, emotion |
| Lonely | Connection | Warmth, listening, personal questions | Brevity, formality, rushing |
| Greedy | Gain | Offers, incentives, explicit value | Empty hands, vague promises |
| Paranoid | Certainty | Documentation, consistency, stillness | Vagueness, emotion, spontaneity |
| Bored | Stimulation | Entertainment, novelty, humor | Routine answers, compliance |
| Ideological | Validation | Agreement, shared values, alignment | Challenge, nuance, complexity |
| Guilty | Absolution | Non-judgment, empathy, discretion | Accusation, pressure, directness |
| Ambitious | Status | Flattery, recognition, success association | Indifference, dismissal |
| Burned Out | Ease | Brevity, simplicity, zero demands | Complexity, neediness, emotion |
| Suspicious | Proof | Evidence, receipts, verifiable claims | Emotional appeals, vague assurances |
| Empathetic | Story | Vulnerability, honesty, shared humanity | Deflection, walls, performance |
| Corrupt | Deniability | Indirection, hints, plausible cover | Explicit asks, direct negotiation |

## The 10 Signal Categories

1. **Timing** — response time relative to baseline
2. **Length** — response length relative to question
3. **Punctuation Behavior** — deviation from established patterns
4. **Word Choice and Register Shifts** — verbal fingerprint changes
5. **The Absence Signal** — what isn't said
6. **Topic Architecture** — what's discussed vs avoided
7. **Overcorrection** — performance covering its opposite
8. **Sequence and Order** — burial order reveals priority
9. **The Mirror Signal** — mirroring as rapport indicator
10. **The Consistency Test** — patterns across time

## The 7 Reception Languages

1. **Indirect-Emotional** — feel heard before giving anything
2. **Direct-Logical** — point first, context second
3. **Validation-First** — acknowledged before receiving info
4. **Humor-Gated** — vulnerability only through comedy
5. **Consistency-Required** — pattern over intensity
6. **Space-Respecting** — room to process
7. **Evidence-Based** — proof and specifics, not feeling

## The 5 Recurring Characters

| Character | Reception Language | Opens When | Closes When |
|-----------|-------------------|------------|-------------|
| Rosa | Indirect-Emotional | Share something personal first | Ask directly before connecting |
| Agent Demir | Evidence-Based | Produce unrequested documentation | Rely on charm or emotion |
| Marcus | Humor-Gated | Make her laugh before asking | Go sincere before trust built |
| Elena | Consistency-Required | Behave identically across encounters | One big gesture instead of small consistent ones |
| The Handler | Direct-Logical | Lead with conclusion not context | Explain before you answer |

## The AWG Token

Scarcity-based powerup that reveals subtext analysis. All analysis precomputed alongside dialogue — never live API calls.

- **Start**: 2 per run
- **Earn**: complete conversation without token use (+1), discover character secret (+1), find hidden tokens
- **Spend**: 1 per conversation — reveals full AWG analysis
- **Depletion gate**: email capture for 3 more tokens (the lead gen mechanism)
- **Recurring character bonus**: encounter 2+ reveals full relationship arc, not just current moment
- **Bridge line**: every activation ends with "This is how your [relationship] works too." — the conversion line

## Technical Architecture

- **Stack**: React (single JSX file), pure CSS, static JSON, Vercel hosting
- **Zero runtime cost**: everything precomputed, ships as static files, fully offline capable
- **Domain**: subtext.game (fallback: subtext.me)
- **Analytics**: Plausible ($9/mo, privacy-respecting, no cookie banner)
- **Email capture**: direct CRM API endpoint (only runtime API call)
- **Procedural engine**: seeded RNG, deterministic per seed, assembles runs from JSON
- **Dialogue engine**: finite state machine on precomputed dialogue trees

## JSON Schema Reference

```json
// CHARACTER PROFILE
{
  "id": "string",
  "name": "string",
  "origin_country": "string",
  "origin_city": "string",
  "occupation": "string",
  "savings_usd": "number",
  "language_skill": "1|2|3|4|5",
  "asset": "string",
  "burden": "string",
  "motivation": "string",
  "entry_vector": "land_border|air_legal|air_illegal|ocean|internal",
  "visa_status": "none|tourist|student|work|expired"
}

// NPC DIALOGUE NODE
{
  "node_id": "string",
  "npc_id": "string",
  "emotional_state": "neutral|suspicious|hostile|cooperative",
  "trigger_condition": "string",
  "npc_line": "string",
  "narrator_line": "string|null",
  "options": [
    {
      "text": "string",
      "tags": { "tone": "string", "intent": "string", "register": "string" },
      "rapport_delta": "number (-2 to +2)",
      "suspicion_delta": "number (-2 to +2)"
    }
  ],
  "awg": {
    "gap_category": "string",
    "surface": "string",
    "actual": "string",
    "tell": "string",
    "recommendation": "string",
    "bridge_line": "string",
    "closer": "string"
  }
}
```

## Content Pipeline — JSON Bundle Strategy

Total precomputed content is ~80MB+. Strategy: lazy load by location. Only fetch the next location's data when the player moves. Character profile selected server-side or from a smaller initial bundle (10,000 profiles on first load).

| Asset | Volume | Output File | Est. Size |
|-------|--------|-------------|-----------|
| Player character profiles | 100,000 | characters.json | ~15MB |
| NPC archetype base profiles | 12 | archetypes.json | <1MB |
| NPC instances (archetype + flavor) | 500 | npcs.json | ~5MB |
| Dialogue trees per NPC | 80 lines x 4 states x 500 NPCs | dialogue.json | ~40MB |
| AWG analysis strings | 1 per dialogue node | awg_analysis.json | ~20MB |
| Intel items + synergy outcomes | 30 items x full matrix | intel.json | <1MB |
| Location descriptions + events | 5 locations x 50 variants | locations.json | ~3MB |
| Recurring character arcs | 5 chars x 3-5 encounter states | recurring.json | ~5MB |
| Ending screen copy | 6 variants x gap combos | endings.json | <1MB |

## Tone Rules — Non-Negotiable

- **Primary**: Chaotic / funny / deadpan. Oregon Trail death screen meets Papers Please meets Hitchhiker's Guide.
- **Narrator**: Institutional gravity applied to absurd situations. The hot dog contest is treated like a UN summit.
- **Comedy**: Situational absurdity. Never at the character's expense. The border agent's mustard stain matters. Broken English narrated with dignity.
- **Difficulty**: Genuinely hard — fair but unforgiving. Failure is interesting. Getting deported from Ohio at 3am with $40 is a better story than sailing through.
- **Emotional depth**: underneath the comedy, real human stakes. Comedy and humanity coexist in every scene.

## The Opening — Four Sentences

Before any gameplay. No branding. No instructions. Black screen, white monospace text:

```
Your mom needs to be asked twice
before she'll say what's wrong.

Your boss needs solutions before context
or he stops reading.

Your best friend needs humor before vulnerability
or she deflects.

Your partner needs acknowledgment before advice
or he shuts down.



subtext.game

> press any key
```

## The Ending Screen

Three components in sequence:
1. **YOUR GAPS THIS RUN** — specific signal categories missed, with exact NPC moments
2. **YOUR RECURRING CHARACTERS** — each character encountered, their reception language, whether cracked
3. **THE BRIDGE** — four lines connecting game to real life, ending with `arewegood.com` and 4-word closer

Six variants: `deported_early`, `deported_mid`, `deported_late`, `won_high_tokens`, `won_low_tokens`, `won_no_tokens`

## The Share Card

```
┌──────────────────────────────────────────┐
│  [NAME]                                  │
│  [Origin]  //  [Occupation]              │
│                                          │
│        [ASCII face]                      │
│                                          │
│  [STATUS — DEPORTED/WON]                 │
│  [Location / Day]                        │
│                                          │
│  GAPS MISSED: [list]                     │
│  AWG tokens used: [n]                    │
│  ──────────────────────────────────────  │
│  subtext.game          arewegood.com     │
└──────────────────────────────────────────┘
```

## Open Engineering Questions

- **JSON bundle size**: Recommend lazy load by location + server-side character selection
- **Share card**: Canvas rendering with html2canvas fallback
- **Email capture endpoint**: Needs AWG CRM endpoint URL and auth before Phase 2 complete
- **Analytics**: Plausible recommended. If zero budget: Fathom Lite or self-host Umami
- **Domain**: Check subtext.game availability at porkbun.com immediately. Fallback: subtext.me
- **Recurring character dialogue**: Human-author arc structure + key moments, Claude expands dialogue banks

## Key Constraints

- Zero runtime API calls during gameplay (except email capture)
- Zero image files — pure ASCII terminal, monospace font, black background
- All AWG analysis co-authored alongside the dialogue it annotates, never separately
- React single JSX file approach — minimal build complexity
- Privacy-respecting analytics only — no cookie banner

## Rules

- The game's primary function is gap creation, not entertainment. Every feature serves conversion.
- Failure IS the product demo. The token explains the failure. Players who experience missing subtext cannot dismiss it.
- NPC dialogue and AWG analysis are generated in the same pass — never separately.
- Deportation screens are worth reading. Death is comedy. Failure makes players want to try again.
- The correct answer is never universal — it depends on the archetype. No dominant strategy.
- Recurring characters deepen with repeated encounter (Hades model), not disposable NPCs.
- The bridge line ("This is how your [relationship] works too.") appears in every recurring character token activation.
- The four opening sentences are the most shareable content — they drive curiosity.
- Document all decisions and rationale.
- Commit after each meaningful piece of work. Push to origin.
- Create GitHub issues for each build phase and major task. Close them when done.
