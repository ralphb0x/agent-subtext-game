# subtext.game

A browser-based ASCII roguelike where a migrant navigates NPCs to reach the Coney Island hot dog eating contest. Read people or get deported. Top-of-funnel for [Are We Good](https://arewegood.com).

```
Your mom needs to be asked twice before she'll say what's wrong.
Your boss needs solutions before context or he stops reading.
Your best friend needs humor before vulnerability or she deflects.
Your partner needs acknowledgment before advice or he shuts down.
```

## Quick Start

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Press any key past the opening. Play.

## How the Game Works

You pick a migrant character (from 1,000 precomputed profiles) and travel through 5 locations from your origin to Coney Island, NYC. At each stop you encounter NPCs. Every NPC has an archetype (Lonely, Paranoid, Greedy, etc.) that determines what they actually want beneath what they say.

Pick the right dialogue option and you build rapport, get help, save money, avoid suspicion. Pick wrong and your Heat rises. Hit Heat 10 or run out of days and you're deported.

**AWG Tokens** are the core mechanic. Spend one during a conversation to reveal the subtext analysis — what the NPC actually means, what signal you missed, and a bridge line connecting the moment to your real relationships. You start with 2. Earn more by completing conversations clean or finding secrets. Run out and you can enter your email for 3 more (that's the lead gen).

### Controls

| Key | Action |
|-----|--------|
| `1` `2` `3` `4` | Select dialogue option |
| `A` | Use AWG token |
| `Enter` / `Space` | Continue / advance text |

## Project Structure

```
src/
  App.jsx          # Game engine — single-file React app (~1400 lines)
  index.css        # Terminal aesthetic (black bg, monospace, amber AWG state)
  portraits.js     # ASCII portrait generator per archetype
  main.jsx         # React entry point

content/           # All precomputed JSON — zero runtime API calls
  characters.json  # 1,000 player profiles
  archetypes.json  # 12 NPC archetype definitions
  npcs.json        # 120 NPC instances with full dialogue trees + AWG analysis
  locations.json   # 5 location packs with events and ASCII headers
  recurring.json   # 5 recurring character arcs (Rosa, Demir, Marcus, Elena, Handler)
  intel.json       # 30 intel items with synergy matrix
  endings.json     # 6 ending screen variants

scripts/           # Content generation pipeline (Claude API)
  generate.py      # Main orchestrator
  generate_characters.py
  generate_npcs.py
  generate_locations.py
  generate_intel.py
  generate_endings.py
  validate_content.py
  prompts/         # Claude API prompt templates

public/
  content -> ../content  # Symlink so Vite serves JSON statically
  favicon.svg
```

## Commands

### Development

```bash
npm run dev        # Start Vite dev server with HMR
npm run build      # Production build to dist/
npm run preview    # Preview production build locally
npm run lint       # Run ESLint
npm run validate   # Validate all content JSON against schemas
```

### Content Generation

Requires Python 3 and an Anthropic API key (`ANTHROPIC_API_KEY` env var).

```bash
pip install -r scripts/requirements.txt

python3 scripts/generate.py characters --count 1000
python3 scripts/generate.py npcs --archetype control-seeking --count 10
python3 scripts/generate.py locations
python3 scripts/generate.py validate
```

Content is precomputed and checked into the repo. You don't need to regenerate it to play.

## Deployment

Configured for Vercel. The `vercel.json` sets up:
- Vite build (`npm run build` -> `dist/`)
- Immutable caching for `/content/*` and `/assets/*`
- SPA fallback routing

```bash
# Deploy (requires Vercel CLI + project linked)
vercel

# Or just push to main if Vercel git integration is connected
git push origin master
```

Domain: `subtext.game`

## Testing Checklist

Use this to verify the game works end-to-end.

### Boot & Opening

- [ ] `npm run dev` starts without errors
- [ ] Black screen with 4 opening sentences typewriters in
- [ ] "press any key" prompt appears
- [ ] Any keypress advances to character selection

### Character & Run Assembly

- [ ] Character profile displays (name, origin, occupation, savings, language skill)
- [ ] Resource bar shows at top: name, day, money, days left, heat, energy
- [ ] First location is a border/port of entry type
- [ ] ASCII location header renders

### NPC Dialogue

- [ ] NPC appears with ASCII portrait and opening line
- [ ] 4 dialogue options display (fewer if language skill is low)
- [ ] Pressing 1-4 selects an option
- [ ] NPC responds and emotional state can shift (neutral/suspicious/hostile/cooperative)
- [ ] Rapport and suspicion update after each choice
- [ ] Narrator lines appear between exchanges (deadpan, one sentence)

### AWG Token System

- [ ] Token count shows in UI (starts at 2)
- [ ] Pressing A during dialogue activates AWG analysis
- [ ] 800ms loading animation with dots plays
- [ ] Screen shifts to amber text on dark brown background
- [ ] Analysis shows: surface (exact NPC words), actual (emotional truth), tell, recommendation
- [ ] Bridge line appears: "This is how your [relationship] works too."
- [ ] Token count decrements
- [ ] At 0 tokens, email capture prompt appears
- [ ] Entering email grants 3 more tokens

### Resources & Progression

- [ ] Money changes after events/conversations
- [ ] Days count down as you move between locations
- [ ] Heat bar animates when suspicion rises (green -> yellow -> red)
- [ ] Energy depletes and affects available options
- [ ] Moving to next location triggers new ASCII header + NPCs

### Recurring Characters

- [ ] Rosa, Agent Demir, Marcus, Elena, or The Handler appear across locations
- [ ] Their state persists between encounters
- [ ] Debrief screen shows after recurring character encounters
- [ ] Second+ encounter with AWG token shows relationship arc, not just current moment

### Intel Items

- [ ] Intel items can be found/collected during events
- [ ] Collected intel appears in inventory
- [ ] Intel provides bonuses in relevant conversations (archetype synergy)

### Endings

- [ ] **Deportation (Heat 10)**: glitch effect on "DEPORTED", ending screen with gaps
- [ ] **Deportation (Time 0)**: same ending flow
- [ ] **Win (reach Coney Island)**: punctuation typewriter animation, sparse and still
- [ ] Ending screen shows: YOUR GAPS THIS RUN, YOUR RECURRING CHARACTERS, bridge text
- [ ] `arewegood.com` link appears with UTM parameters
- [ ] Ending variant matches condition (deported_early/mid/late, won_high/low/no_tokens)

### Mobile

- [ ] Playable on iOS Safari (safe area insets for notch)
- [ ] Playable on Android Chrome
- [ ] Text readable, options tappable, no horizontal scroll

### Cross-Browser

- [ ] Chrome
- [ ] Firefox
- [ ] Safari

### Build & Deploy

- [ ] `npm run build` completes without errors
- [ ] `npm run preview` serves the built game correctly
- [ ] `npm run validate` passes all JSON schema checks
- [ ] `npm run lint` passes

## Architecture Notes

- **Zero runtime API calls** during gameplay. Everything is precomputed JSON.
- **Seeded RNG**: same seed = same run. Enables reproducible bug reports and share cards.
- **Single JSX file**: the entire game engine is `App.jsx`. Intentionally monolithic for simplicity.
- **Content is ~3.5MB total** in the repo. Lazy-loaded by location at runtime.
- **Analytics**: Plausible (privacy-respecting, no cookie banner).
- **Email capture**: the only runtime API call — sends to AWG CRM endpoint.

## The 12 NPC Archetypes

| Archetype | Core Need | Rewards | Punishes |
|-----------|-----------|---------|----------|
| Control-Seeking | Dominance | Deference, stillness | Challenge, humor |
| Lonely | Connection | Warmth, listening | Brevity, rushing |
| Greedy | Gain | Offers, incentives | Empty hands |
| Paranoid | Certainty | Documentation, consistency | Vagueness, emotion |
| Bored | Stimulation | Entertainment, novelty | Routine, compliance |
| Ideological | Validation | Agreement, shared values | Challenge, nuance |
| Guilty | Absolution | Empathy, discretion | Accusation, pressure |
| Ambitious | Status | Flattery, recognition | Indifference |
| Burned Out | Ease | Brevity, simplicity | Complexity, neediness |
| Suspicious | Proof | Evidence, receipts | Emotional appeals |
| Empathetic | Story | Vulnerability, honesty | Deflection, walls |
| Corrupt | Deniability | Indirection, hints | Explicit asks |

## License

Proprietary. All rights reserved.
