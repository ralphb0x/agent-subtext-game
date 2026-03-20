import { useState, useEffect, useCallback, useRef } from 'react'

// ─── Seeded RNG ───────────────────────────────────────────────
function createRNG(seed) {
  let s = seed
  return function next() {
    s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
    return (s >>> 0) / 0xFFFFFFFF
  }
}

function seedFromString(str) {
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash + str.charCodeAt(i)) | 0
  }
  return hash >>> 0
}

function pick(rng, arr) {
  return arr[Math.floor(rng() * arr.length)]
}

function shuffle(rng, arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

// ─── Game Phases ──────────────────────────────────────────────
const PHASE = {
  BOOT: 'boot',
  PLAYING: 'playing',
  DIALOGUE: 'dialogue',
  EVENT: 'event',
  ENDING: 'ending',
}

// ─── Location order ───────────────────────────────────────────
const LOCATION_ORDER = ['border', 'transit', 'mid_america', 'nyc_outer', 'coney_island']

// ─── Signal categories ───────────────────────────────────────
const SIGNAL_CATEGORIES = [
  'Timing', 'Length', 'Punctuation Behavior', 'Word Choice and Register Shifts',
  'The Absence Signal', 'Topic Architecture', 'Overcorrection',
  'Sequence and Order', 'The Mirror Signal', 'The Consistency Test'
]

// ─── Heat bar renderer ───────────────────────────────────────
function HeatBar({ value, max = 10 }) {
  const filled = Math.min(value, max)
  const empty = max - filled
  const cls = filled <= 3 ? 'bar-filled-low' : filled <= 6 ? 'bar-filled-mid' : 'bar-filled-high'
  return (
    <span className="bar">
      <span className={cls}>{'█'.repeat(filled)}</span>
      <span className="bar-empty">{'░'.repeat(empty)}</span>
    </span>
  )
}

function EnergyBar({ value, max = 10 }) {
  const filled = Math.min(value, max)
  const empty = max - filled
  return (
    <span className="bar">
      <span className="energy-filled">{'█'.repeat(filled)}</span>
      <span className="bar-empty">{'░'.repeat(empty)}</span>
    </span>
  )
}

// ─── Content loader ───────────────────────────────────────────
async function loadContent() {
  const [characters, npcs, locations, archetypes, intel, recurring, endings] = await Promise.all([
    fetch('/content/characters.json').then(r => r.json()),
    fetch('/content/npcs.json').then(r => r.json()),
    fetch('/content/locations.json').then(r => r.json()),
    fetch('/content/archetypes.json').then(r => r.json()),
    fetch('/content/intel.json').then(r => r.json()),
    fetch('/content/recurring.json').then(r => r.json()),
    fetch('/content/endings.json').then(r => r.json()),
  ])
  return { characters, npcs, locations: locations.locations, archetypes, intel, recurring, endings }
}

// ─── Run assembler ────────────────────────────────────────────
function assembleRun(content, seed) {
  const rng = createRNG(seed)

  // Select character
  const character = pick(rng, content.characters)

  // Determine entry vector → starting location
  const startIdx = character.entry_vector === 'internal' ? 2
    : character.entry_vector === 'ocean' ? 1
    : 0

  // Assemble 4-5 location stops
  const locationStops = LOCATION_ORDER.slice(startIdx)

  // Distribute recurring characters across stops (shuffle, then assign one per stop)
  const eligibleRecurring = shuffle(rng, [...content.recurring])
  const usedRecurring = new Set()

  // For each location, pick 2-3 events and assign NPCs
  const stops = locationStops.map(locId => {
    const loc = content.locations.find(l => l.location_id === locId)
    if (!loc) return null

    // Pick 2-3 events from this location
    const eventCount = 2 + Math.floor(rng() * 2)
    const events = shuffle(rng, loc.events).slice(0, eventCount)

    // For encounter events, assign NPCs
    const encounters = events.filter(e => e.category === 'encounter').map(event => {
      const pool = event.npc_archetype_pool || []
      const archetype = pool.length > 0 ? pick(rng, pool) : null
      const matchingNpcs = content.npcs.filter(n =>
        n.archetype_id === archetype && n.location_type === locId
      )
      const fallbackNpcs = content.npcs.filter(n => n.location_type === locId)
      const npc = matchingNpcs.length > 0
        ? pick(rng, matchingNpcs)
        : fallbackNpcs.length > 0
          ? pick(rng, fallbackNpcs)
          : pick(rng, content.npcs)
      return { event, npc }
    })

    // Assign a recurring character — rotate through them, don't always pick the same one
    const matchLoc = locId === 'nyc_outer' ? 'nyc' : locId
    const recurringChar = eligibleRecurring.find(r =>
      r.encounter_locations && r.encounter_locations.includes(matchLoc) && !usedRecurring.has(r.character_id)
    )
    if (recurringChar) usedRecurring.add(recurringChar.character_id)

    return {
      location: loc,
      events,
      encounters,
      recurringChar: recurringChar || null,
      nonEncounterEvents: events.filter(e => e.category !== 'encounter'),
    }
  }).filter(Boolean)

  // Initialize resources
  const daysToJuly4 = 14 - startIdx * 2
  const resources = {
    money: character.savings_usd,
    daysLeft: daysToJuly4,
    heat: 0,
    energy: 10,
  }

  return {
    seed,
    character,
    stops,
    resources,
    awgTokens: 2,
    currentStopIdx: 0,
    currentEventIdx: 0,
    intelCollected: [],
    gapsMissed: [],
    recurringEncounters: {},
    conversationsWithoutToken: 0,
    secretsFound: [],
    showingLocation: true,
  }
}

// ─── AWG Analysis display ─────────────────────────────────────
function AWGDisplay({ awg }) {
  if (!awg) return null
  return (
    <div className="awg-section">
      <div className="awg-label">AWG Analysis — {awg.gap_category}</div>
      <div className="awg-gap awg-surface">Surface: "{awg.surface}"</div>
      <div className="awg-gap awg-actual">Actual: {awg.actual}</div>
      {awg.tell && <div className="awg-gap awg-tell">Tell: {awg.tell}</div>}
      {awg.recommendation && <div className="awg-gap">Rec: {awg.recommendation}</div>}
      <div className="awg-bridge">{awg.bridge_line}</div>
      {awg.closer && <div className="awg-gap" style={{ marginTop: 8, color: '#776622' }}>{awg.closer}</div>}
    </div>
  )
}

// ─── Email capture gate ───────────────────────────────────────
function EmailGate({ onSubmit, onSkip }) {
  const [email, setEmail] = useState('')
  return (
    <div className="email-gate">
      <h3>You're out of AWG tokens.</h3>
      <p>Enter your email to get 3 more tokens and see what you're missing.</p>
      <input
        type="email"
        placeholder="you@email.com"
        value={email}
        onChange={e => setEmail(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && email && onSubmit(email)}
      />
      <button onClick={() => email && onSubmit(email)} disabled={!email}>
        GET 3 TOKENS
      </button>
      <div style={{ marginTop: 8 }}>
        <button
          onClick={onSkip}
          style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', fontFamily: 'inherit', fontSize: 12 }}
        >
          skip
        </button>
      </div>
    </div>
  )
}

// ─── Main App ─────────────────────────────────────────────────
export default function App() {
  const [phase, setPhase] = useState(PHASE.BOOT)
  const [content, setContent] = useState(null)
  const [run, setRun] = useState(null)
  const [dialogueNode, setDialogueNode] = useState(null)
  const [currentNPC, setCurrentNPC] = useState(null)
  const [showAWG, setShowAWG] = useState(false)
  const [rapport, setRapport] = useState(0)
  const [suspicion, setSuspicion] = useState(0)
  const [showEmailGate, setShowEmailGate] = useState(false)
  const [emailSubmitted, setEmailSubmitted] = useState(false)
  const [currentEvent, setCurrentEvent] = useState(null)
  const [deportGlitch, setDeportGlitch] = useState(false)
  const [loading, setLoading] = useState(true)
  const [awgScanning, setAwgScanning] = useState(false)
  const [awgScanDots, setAwgScanDots] = useState(0)
  const [winAnimPhase, setWinAnimPhase] = useState(0)
  const rngRef = useRef(null)

  // Load content on mount
  useEffect(() => {
    loadContent().then(c => {
      setContent(c)
      setLoading(false)
    }).catch(err => {
      console.error('Failed to load content:', err)
      setLoading(false)
    })
  }, [])

  // Start a new run
  const startRun = useCallback((seedStr) => {
    if (!content) return
    const seed = seedStr ? seedFromString(seedStr) : (Date.now() & 0xFFFFFFFF)
    rngRef.current = createRNG(seed)
    const newRun = assembleRun(content, seed)
    setRun(newRun) // showingLocation: true is set in assembleRun
    setPhase(PHASE.PLAYING)
    setRapport(0)
    setSuspicion(0)
    setShowAWG(false)
    setShowEmailGate(false)
    setAwgScanning(false)
    setAwgScanDots(0)
    setWinAnimPhase(0)
    setDialogueNode(null)
    setCurrentNPC(null)
    setCurrentEvent(null)
  }, [content])

  // Boot screen
  const handleBootClick = useCallback(() => {
    if (phase === PHASE.BOOT && content) {
      startRun()
    }
  }, [phase, content, startRun])

  // Key handler for boot
  useEffect(() => {
    const handler = (e) => {
      if (phase === PHASE.BOOT && content) {
        startRun()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [phase, content, startRun])

  // ─── Game logic ───────────────────────────────────────────
  const advanceEvent = useCallback(() => {
    if (!run) return

    const stop = run.stops[run.currentStopIdx]
    if (!stop) {
      setPhase(PHASE.ENDING)
      return
    }

    // Show location overview when first arriving
    if (run.showingLocation) {
      // Just render the location screen — player clicks continue
      return
    }

    const nextEventIdx = run.currentEventIdx

    // Check for recurring character encounter (before regular events, doesn't consume eventIdx)
    if (nextEventIdx === 0 && stop.recurringChar && !run.recurringDoneThisStop) {
      const rc = stop.recurringChar
      const encounters = run.recurringEncounters[rc.character_id] || 0
      const arcState = rc.arc_states[Math.min(encounters, rc.arc_states.length - 1)]
      if (arcState && arcState.dialogue_nodes && arcState.dialogue_nodes.length > 0) {
        const node = arcState.dialogue_nodes[0]
        setCurrentNPC({
          npc_id: rc.character_id,
          name: rc.name,
          role: rc.role,
          appearance: rc.appearance,
          archetype_id: rc.reception_language,
          isRecurring: true,
          secret: rc.secret,
        })
        setDialogueNode(node)
        setRapport(0)
        setSuspicion(0)
        setShowAWG(false)
        setPhase(PHASE.DIALOGUE)
        setRun(prev => ({
          ...prev,
          recurringDoneThisStop: true,
          recurringEncounters: {
            ...prev.recurringEncounters,
            [rc.character_id]: encounters + 1,
          }
        }))
        return
      }
    }

    // Check encounters (indexed from 0)
    if (stop.encounters && nextEventIdx < stop.encounters.length) {
      const enc = stop.encounters[nextEventIdx]
      const npc = enc.npc
      if (npc && npc.dialogue_tree && npc.dialogue_tree.length > 0) {
        setCurrentNPC(npc)
        setDialogueNode(npc.dialogue_tree[0])
        setRapport(0)
        setSuspicion(0)
        setShowAWG(false)
        setPhase(PHASE.DIALOGUE)
        return
      }
    }

    // Non-encounter events
    const nonEnc = stop.nonEncounterEvents || []
    const neIdx = nextEventIdx - (stop.encounters ? stop.encounters.length : 0)
    if (neIdx >= 0 && neIdx < nonEnc.length) {
      setCurrentEvent(nonEnc[neIdx])
      setPhase(PHASE.EVENT)
      return
    }

    // Move to next location
    const nextStopIdx = run.currentStopIdx + 1
    if (nextStopIdx >= run.stops.length) {
      setPhase(PHASE.ENDING)
      return
    }

    setRun(prev => ({
      ...prev,
      currentStopIdx: nextStopIdx,
      currentEventIdx: 0,
      showingLocation: true,
      recurringDoneThisStop: false,
      resources: {
        ...prev.resources,
        daysLeft: Math.max(0, prev.resources.daysLeft - 1),
      },
    }))
  }, [run])

  // Auto-advance when in PLAYING phase and not showing location overview
  useEffect(() => {
    if (phase === PHASE.PLAYING && run && !run.showingLocation && !dialogueNode && !currentEvent) {
      advanceEvent()
    }
  }, [phase, run, dialogueNode, currentEvent, advanceEvent])

  // Handle dialogue option selection
  const selectOption = useCallback((option) => {
    if (!run || !dialogueNode || !currentNPC) return

    const newRapport = rapport + (option.rapport_delta || 0)
    const newSuspicion = suspicion + (option.suspicion_delta || 0)
    setRapport(newRapport)
    setSuspicion(newSuspicion)

    // Update run resources
    const heatDelta = option.suspicion_delta > 0 ? option.suspicion_delta : 0
    const newHeat = Math.min(10, run.resources.heat + heatDelta)

    setRun(prev => ({
      ...prev,
      resources: {
        ...prev.resources,
        heat: newHeat,
      }
    }))

    // Check for deportation
    if (newHeat >= 10) {
      setDeportGlitch(true)
      setTimeout(() => {
        setDeportGlitch(false)
        setPhase(PHASE.ENDING)
      }, 500)
      return
    }

    // Track gap if player missed the signal
    if (dialogueNode.awg && option.rapport_delta < 0) {
      setRun(prev => ({
        ...prev,
        gapsMissed: [...prev.gapsMissed, {
          category: dialogueNode.awg.gap_category,
          npcName: currentNPC.name,
          location: run.stops[run.currentStopIdx]?.location?.name || 'Unknown',
          surface: dialogueNode.awg.surface,
          actual: dialogueNode.awg.actual,
        }]
      }))
    }

    // Find next node
    const nextNodeId = option.next_node
    let nextNode = null
    if (nextNodeId && currentNPC.dialogue_tree) {
      nextNode = currentNPC.dialogue_tree.find(n => n.node_id === nextNodeId)
    }
    // For recurring characters, look in arc states
    if (nextNodeId && currentNPC.isRecurring && !nextNode) {
      const rc = content.recurring.find(r => r.character_id === currentNPC.npc_id)
      if (rc) {
        for (const state of rc.arc_states) {
          nextNode = state.dialogue_nodes.find(n => n.node_id === nextNodeId)
          if (nextNode) break
        }
      }
    }

    if (nextNode) {
      setDialogueNode(nextNode)
      setShowAWG(false)
    } else {
      // Conversation complete
      if (!showAWG) {
        // Track conversation without token use — earn 1 token every 2 clean conversations
        setRun(prev => {
          const newCount = prev.conversationsWithoutToken + 1
          const earnToken = newCount >= 2
          return {
            ...prev,
            conversationsWithoutToken: earnToken ? 0 : newCount,
            awgTokens: earnToken ? prev.awgTokens + 1 : prev.awgTokens,
          }
        })
      }

      // Check if NPC secret was discovered (high rapport)
      if (newRapport >= 4 && currentNPC.secret) {
        setRun(prev => ({
          ...prev,
          secretsFound: [...prev.secretsFound, { npc: currentNPC.name, secret: currentNPC.secret }],
          awgTokens: prev.awgTokens + 1,
        }))
      }

      const wasRecurring = currentNPC.isRecurring
      setDialogueNode(null)
      setCurrentNPC(null)
      setShowAWG(false)
      // Only increment eventIdx for regular NPCs — recurring chars don't consume an event slot
      if (!wasRecurring) {
        setRun(prev => ({
          ...prev,
          currentEventIdx: prev.currentEventIdx + 1,
        }))
      }
      setPhase(PHASE.PLAYING)
    }
  }, [run, dialogueNode, currentNPC, rapport, suspicion, showAWG, content])

  // Activate AWG token with scan animation
  const activateAWG = useCallback(() => {
    if (!run || awgScanning) return
    if (run.awgTokens <= 0) {
      if (!emailSubmitted) {
        setShowEmailGate(true)
      }
      return
    }
    setRun(prev => ({ ...prev, awgTokens: prev.awgTokens - 1 }))
    setAwgScanning(true)
    setAwgScanDots(0)

    // Accumulate dots over 800ms (8 dots, 100ms each)
    let dotCount = 0
    const dotInterval = setInterval(() => {
      dotCount++
      setAwgScanDots(dotCount)
      if (dotCount >= 8) {
        clearInterval(dotInterval)
        setTimeout(() => {
          setAwgScanning(false)
          setAwgScanDots(0)
          setShowAWG(true)
        }, 100)
      }
    }, 100)
  }, [run, emailSubmitted, awgScanning])

  // Email submit
  const handleEmailSubmit = useCallback((email) => {
    // In production, this would POST to AWG CRM
    console.log('Email captured:', email)
    setEmailSubmitted(true)
    setShowEmailGate(false)
    setRun(prev => ({ ...prev, awgTokens: prev.awgTokens + 3 }))
  }, [])

  // Handle event continue
  const handleEventContinue = useCallback(() => {
    if (!currentEvent || !run) return

    // Apply resource effects
    const effects = currentEvent.resource_effects || {}
    setRun(prev => ({
      ...prev,
      currentEventIdx: prev.currentEventIdx + 1,
      resources: {
        money: prev.resources.money + (effects.money || 0),
        daysLeft: Math.max(0, prev.resources.daysLeft + (effects.time || 0)),
        heat: Math.min(10, Math.max(0, prev.resources.heat + (effects.heat || 0))),
        energy: Math.min(10, Math.max(0, prev.resources.energy + (effects.energy || 0))),
      }
    }))

    setCurrentEvent(null)
    setPhase(PHASE.PLAYING)
  }, [currentEvent, run])

  // ─── Determine ending variant ─────────────────────────────
  const getEndingVariant = useCallback(() => {
    if (!run || !content) return null
    const variants = content.endings.variants
    const won = run.currentStopIdx >= run.stops.length - 1 && run.resources.heat < 10
    const heat = run.resources.heat

    if (!won) {
      if (run.currentStopIdx <= 1) return variants.deported_early
      if (run.currentStopIdx <= 2) return variants.deported_mid
      return variants.deported_late
    }

    if (run.awgTokens >= 3) return variants.won_high_tokens
    if (run.awgTokens >= 1) return variants.won_low_tokens
    return variants.won_no_tokens
  }, [run, content])

  // ─── Check for option requirements ────────────────────────
  const isOptionAvailable = useCallback((option) => {
    if (!run) return true
    if (option.requires_language_skill && run.character.language_skill < option.requires_language_skill) {
      return false
    }
    if (option.requires_occupation && run.character.occupation !== option.requires_occupation) {
      return false
    }
    if (option.requires_intel) {
      return run.intelCollected.some(i => i.id === option.requires_intel)
    }
    return true
  }, [run])

  // ─── Render ───────────────────────────────────────────────

  if (loading) {
    return (
      <div className="game-container">
        <div className="boot-screen">
          <div style={{ color: '#666' }}>loading...</div>
        </div>
      </div>
    )
  }

  // Boot screen
  if (phase === PHASE.BOOT) {
    return (
      <div className="game-container" onClick={handleBootClick}>
        <div className="boot-screen">
          <div className="boot-line">
            Your mom needs to be asked twice<br />before she'll say what's wrong.
          </div>
          <div className="boot-line">
            Your boss needs solutions before context<br />or he stops reading.
          </div>
          <div className="boot-line">
            Your best friend needs humor before vulnerability<br />or she deflects.
          </div>
          <div className="boot-line">
            Your partner needs acknowledgment before advice<br />or he shuts down.
          </div>
          <div className="boot-title">subtext.game</div>
          <div className="boot-prompt">&gt; press any key</div>
        </div>
      </div>
    )
  }

  if (!run) return null

  const stop = run.stops[run.currentStopIdx]
  const won = phase === PHASE.ENDING && run.currentStopIdx >= run.stops.length - 1 && run.resources.heat < 10
  const deported = phase === PHASE.ENDING && !won

  // Win state animation — staggered reveal with stillness
  useEffect(() => {
    if (phase === PHASE.ENDING && won) {
      setWinAnimPhase(0)
      const timers = [
        setTimeout(() => setWinAnimPhase(1), 800),
        setTimeout(() => setWinAnimPhase(2), 2000),
        setTimeout(() => setWinAnimPhase(3), 3500),
        setTimeout(() => setWinAnimPhase(4), 5000),
      ]
      return () => timers.forEach(clearTimeout)
    }
  }, [phase, won])

  // UI Bar
  const UIBar = () => (
    <div className="ui-bar">
      <span className="stat name">{run.character.name}</span>
      <span className="stat">DAY {15 - run.resources.daysLeft}</span>
      <span className="stat">${run.resources.money}</span>
      <span className="stat">{run.resources.daysLeft} DAYS</span>
      <span className="stat">HEAT:<HeatBar value={run.resources.heat} /></span>
      <span className="stat">ENERGY:<EnergyBar value={run.resources.energy} /></span>
      <span className="token-count">[AWG:{run.awgTokens}]</span>
    </div>
  )

  // Ending screen
  if (phase === PHASE.ENDING) {
    const variant = getEndingVariant()
    // For win: use staggered reveal. For deported: show all immediately.
    const showHeader = deported || winAnimPhase >= 0
    const showStatus = deported || winAnimPhase >= 1
    const showGaps = deported || winAnimPhase >= 2
    const showRecurring = deported || winAnimPhase >= 3
    const showBridge = deported || winAnimPhase >= 4

    return (
      <div className="game-container">
        <div className={`ending-screen ${deported && deportGlitch ? 'glitch' : ''} ${won ? 'win-ending' : ''}`}>
          {showHeader && variant && variant.header_ascii && (
            <div className={`ending-header ${won ? 'win-fade' : ''}`}>{variant.header_ascii.join('\n')}</div>
          )}

          {showStatus && (
            <>
              <div className={`ending-narrator ${won ? 'win-fade win-title' : ''}`}>
                {deported ? `DEPORTED — ${stop?.location?.name || 'Unknown'}` : 'YOU MADE IT.'}
              </div>

              {variant && (
                <div className={`ending-narrator ${won ? 'win-fade' : ''}`} style={{ fontStyle: 'italic' }}>
                  {variant.narrator_line}
                </div>
              )}
            </>
          )}

          {showGaps && (
            <div className={`ending-section ${won ? 'win-fade' : ''}`}>
              <div className="ending-section-title">YOUR GAPS THIS RUN</div>
              {run.gapsMissed.length === 0 ? (
                <div className="gap-item">None detected. You read everyone perfectly.</div>
              ) : (
                run.gapsMissed.map((gap, i) => (
                  <div key={i} className="gap-item">
                    {gap.category} — {gap.npcName} at {gap.location}
                    <div style={{ color: '#666', fontSize: 12, paddingLeft: 8 }}>
                      They said: "{gap.surface}" — They meant: {gap.actual}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {showRecurring && (
            <div className={`ending-section ${won ? 'win-fade' : ''}`}>
              <div className="ending-section-title">YOUR RECURRING CHARACTERS</div>
              {Object.entries(run.recurringEncounters).map(([id, count]) => {
                const rc = content.recurring.find(r => r.character_id === id)
                if (!rc) return null
                const cracked = count >= 2
                return (
                  <div key={id} className="recurring-char">
                    <span className={cracked ? 'cracked' : 'not-cracked'}>
                      {rc.name} — {rc.reception_language} — {cracked ? 'CRACKED' : `${count} encounter${count > 1 ? 's' : ''}`}
                    </span>
                  </div>
                )
              })}
              {Object.keys(run.recurringEncounters).length === 0 && (
                <div className="recurring-char not-cracked">No recurring characters encountered.</div>
              )}
            </div>
          )}

          {showBridge && variant && variant.bridge && (
            <div className="ending-section win-fade">
              <div className="ending-section-title">THE BRIDGE</div>
              {variant.bridge.lines && variant.bridge.lines.map((line, i) => (
                <div key={i} className="bridge-text">{line}</div>
              ))}
              <a
                className="cta-link"
                href={`https://arewegood.com?utm_source=subtext_game&utm_medium=ending&utm_campaign=${variant.id}`}
                target="_blank"
                rel="noopener noreferrer"
              >
                arewegood.com
              </a>
              {variant.bridge.closer && (
                <div className="closer">{variant.bridge.closer}</div>
              )}
            </div>
          )}

          {showBridge && (
            <button className={`play-again-btn ${won ? 'win-fade' : ''}`} onClick={() => startRun()}>
              &gt; play again
            </button>
          )}
        </div>
      </div>
    )
  }

  // Event screen
  if (phase === PHASE.EVENT && currentEvent) {
    return (
      <div className="game-container">
        <UIBar />
        {stop && (
          <div className="location-name">{stop.location.name}</div>
        )}
        <div className="event-section">
          <div className="event-title">{currentEvent.title}</div>
          <div className="event-desc">{currentEvent.description}</div>
          {currentEvent.narrator_line && (
            <div className="narrator-line">{currentEvent.narrator_line}</div>
          )}
          {currentEvent.resource_effects && (
            <div style={{ color: '#888', fontSize: 12, marginTop: 8 }}>
              {Object.entries(currentEvent.resource_effects).map(([k, v]) => (
                <span key={k} style={{ marginRight: 12 }}>
                  {k}: {v > 0 ? '+' : ''}{v}
                </span>
              ))}
            </div>
          )}
        </div>
        <button className="continue-btn" onClick={handleEventContinue}>
          &gt; continue
        </button>
      </div>
    )
  }

  // Dialogue screen
  if (phase === PHASE.DIALOGUE && dialogueNode && currentNPC) {
    const options = dialogueNode.options || []
    return (
      <div className="game-container">
        <UIBar />
        {stop && <div className="location-name">{stop.location.name}</div>}

        <div className="npc-section">
          <div className="npc-name">{currentNPC.name}</div>
          <div className="npc-role">{currentNPC.role}</div>
          {currentNPC.appearance && (
            <div className="narrator-line">{currentNPC.appearance}</div>
          )}
        </div>

        <div className="npc-line">"{dialogueNode.npc_line}"</div>

        {dialogueNode.narrator_line && (
          <div className="narrator-line">{dialogueNode.narrator_line}</div>
        )}

        {/* AWG token activation */}
        {dialogueNode.awg && !showAWG && !awgScanning && (
          <button
            className="awg-activate-btn"
            onClick={activateAWG}
            disabled={run.awgTokens <= 0 && emailSubmitted}
          >
            USE AWG TOKEN ({run.awgTokens} remaining)
          </button>
        )}

        {awgScanning && (
          <div className="awg-scan">
            <span className="awg-scan-label">SCANNING</span>
            <span className="awg-scan-dots">{'.'.repeat(awgScanDots)}</span>
          </div>
        )}

        {showAWG && dialogueNode.awg && (
          <div className="awg-reveal">
            <AWGDisplay awg={dialogueNode.awg} />
          </div>
        )}

        {showEmailGate && (
          <EmailGate
            onSubmit={handleEmailSubmit}
            onSkip={() => setShowEmailGate(false)}
          />
        )}

        <div className="options">
          {options.map((opt, i) => {
            const available = isOptionAvailable(opt)
            return (
              <button
                key={i}
                className="option-btn"
                onClick={() => selectOption(opt)}
                disabled={!available}
              >
                <span className="option-number">[{i + 1}]</span>
                {opt.text}
                {!available && (
                  <span className="option-lock">
                    {opt.requires_language_skill ? `[Lang ${opt.requires_language_skill}+]` : ''}
                    {opt.requires_occupation ? `[${opt.requires_occupation}]` : ''}
                    {opt.requires_intel ? '[Intel required]' : ''}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>
    )
  }

  // Location overview (playing phase, showing location)
  if (phase === PHASE.PLAYING && stop && run.showingLocation) {
    return (
      <div className="game-container">
        <UIBar />
        <div className="location-header">
          {stop.location.ascii_header && stop.location.ascii_header.join('\n')}
        </div>
        <div className="location-name">{stop.location.name}</div>
        <div className="location-desc">{stop.location.description}</div>
        {stop.location.ambient_details && (
          <div className="ambient">
            {pick(rngRef.current || Math.random, stop.location.ambient_details)}
          </div>
        )}
        <button className="continue-btn" onClick={() => {
          setRun(prev => ({ ...prev, showingLocation: false }))
        }}>
          &gt; continue
        </button>
      </div>
    )
  }

  return null
}
