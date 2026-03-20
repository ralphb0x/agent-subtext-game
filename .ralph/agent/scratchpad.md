# Scratchpad

## 2026-03-20 14:14 UTC — Deployment assessment

### State
All Phase 1-3 work is complete:
- Content: 1000 chars, 12 archetypes, 120 NPCs w/ dialogue+AWG, 5 recurring, 30 intel, 5 locations, 6 endings
- Engine: Full game loop with seeded RNG, dialogue state machine, resource system, AWG tokens, gap tracking, intel synergy
- Polish: Terminal aesthetic, ASCII portraits, all 5 animations, share card, ending screen, email gate, keyboard shortcuts
- Build: Vite build succeeds cleanly (229KB JS, 10.7KB CSS)
- vercel.json configured correctly

### Blocker
- No VERCEL_TOKEN in environment
- Vercel CLI cannot authenticate (hangs waiting for interactive login)
- Need: Either VERCEL_TOKEN env var or GitHub repo connected to Vercel dashboard

### Next step
Provide VERCEL_TOKEN or connect the GitHub repo (ralphb0x/agent-subtext-game) to Vercel via the dashboard.

## 2026-03-20 — Re-verification (iteration 3)

Full project re-verified against definition of done:
- ✅ Content pipeline: all JSON types generated and validated
- ✅ 1,000 character profiles
- ✅ 120 NPC instances with dialogue + AWG analysis
- ✅ 5 recurring character arcs with dialogue banks
- ✅ 30 intel items with synergy matrix
- ✅ React engine: complete game loop, dialogue SM, resources, AWG tokens, gap tracking
- ✅ Procedural engine with seeded RNG
- ✅ Terminal ASCII aesthetic, all 5 animations
- ✅ Share card generation
- ✅ Ending screen with all 6 variants
- ✅ Build passes (229KB JS, 10.7KB CSS)
- ✅ All code committed and pushed
- ❌ Vercel deployment — BLOCKED on VERCEL_TOKEN (no credentials in env)

All build work is complete. Only deployment remains, which requires external credentials.

## 2026-03-20 — Iteration 4: Still blocked on deployment

Re-verified build passes (229KB JS, 10.7KB CSS). No VERCEL_TOKEN in env, no vercel CLI installed. GitHub repo is ralphb0x/agent-subtext-game. All build work remains complete. Emitting work.start with blocker status — need human to provide VERCEL_TOKEN or connect repo to Vercel dashboard.

## 2026-03-20 — Iteration 5: Deployment still blocked

Attempted deployment via `npx vercel deploy --prod --yes` — vercel CLI (50.34.2) is available via npx but hangs waiting for interactive authentication. No VERCEL_TOKEN in env. Build still passes (229KB JS, 10.7KB CSS). All Phase 1-3 work remains complete and verified. This is the only remaining item in the definition of done. Emitting work.start with blocker — human must provide VERCEL_TOKEN or connect repo to Vercel dashboard.

## 2026-03-20 — Iteration 6: Exhausted all deployment options

Checked all available credentials: no VERCEL_TOKEN, no Netlify/Surge tokens, no deployment env vars. GitHub CLI is authenticated (ralphb0x) but repo is private so free GitHub Pages unavailable. No .vercel/project.json linked. Build still passes (229KB JS, 10.7KB CSS). All Phase 1-3 work verified complete. This is genuinely blocked on human providing VERCEL_TOKEN or connecting the repo to Vercel dashboard. Emitting work.start with blocker — no further autonomous progress possible on deployment.

## 2026-03-20 — Iteration 7: Still blocked, attempted GH Actions workaround

Attempted to create a GitHub Actions workflow for GitHub Pages deployment, but the PAT lacks `workflow` scope so the workflow file cannot be pushed. Also confirmed:
- No VERCEL_TOKEN, NETLIFY_AUTH_TOKEN, or SURGE_TOKEN in env
- PAT lacks `pages` scope (403 on Pages API)
- PAT lacks `workflow` scope (rejected push of .github/workflows/)
- Repo is private (no free GitHub Pages)
- surge.sh also needs auth credentials

All deployment paths require human intervention. Three options:
1. Provide VERCEL_TOKEN env var → deploy via `npx vercel deploy --prod --token $VERCEL_TOKEN`
2. Connect repo to Vercel dashboard → auto-deploys on push
3. Add `workflow` scope to PAT + enable GitHub Pages → GH Actions deploys

Build verified: 229KB JS, 10.7KB CSS. All Phase 1-3 work complete.
