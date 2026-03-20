import { useState, useEffect, useCallback, useRef } from 'react'
import { getPortrait, getRecurringPortrait } from './portraits'

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
  DEBRIEF: 'debrief',
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

// ─── ASCII Portrait ──────────────────────────────────────────
function Portrait({ archetypeId, recurringId }) {
  const lines = recurringId
    ? getRecurringPortrait(recurringId)
    : getPortrait(archetypeId)
  if (!lines) return null
  return (
    <pre className="ascii-portrait">{lines.join('\n')}</pre>
  )
}

// ─── Share Card Generator ────────────────────────────────────
function ShareCard({ run, won }) {
  const canvasRef = useRef(null)
  const [generated, setGenerated] = useState(false)
  const [dataUrl, setDataUrl] = useState(null)

  const generate = useCallback(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W = 600, H = 400
    canvas.width = W
    canvas.height = H

    // Background
    ctx.fillStyle = '#0D0D0D'
    ctx.fillRect(0, 0, W, H)

    // Border
    ctx.strokeStyle = '#333'
    ctx.lineWidth = 2
    ctx.strokeRect(8, 8, W - 16, H - 16)

    ctx.font = '14px "IBM Plex Mono", monospace'
    ctx.fillStyle = '#FFFFFF'

    let y = 40
    const line = (text, color, size) => {
      if (color) ctx.fillStyle = color
      if (size) ctx.font = `${size}px "IBM Plex Mono", monospace`
      ctx.fillText(text, 24, y)
      y += (size || 14) + 8
      ctx.fillStyle = '#FFFFFF'
      ctx.font = '14px "IBM Plex Mono", monospace'
    }

    // Name + origin
    line(run.character.name, '#FFFFFF', 18)
    line(`${run.character.origin_city}, ${run.character.origin_country}  //  ${run.character.occupation}`, '#888')

    y += 12

    // Status
    if (won) {
      line('STATUS: ARRIVED — CONEY ISLAND', '#FFB300', 16)
    } else {
      const stop = run.stops[run.currentStopIdx]
      line(`STATUS: DEPORTED — ${stop?.location?.name || 'Unknown'}`, '#FF4444', 16)
    }
    line(`Day ${15 - run.resources.daysLeft}  //  $${run.resources.money}  //  AWG tokens used: ${2 - run.awgTokens + (run.awgTokens < 0 ? 0 : 0)}`, '#888')

    y += 12

    // Gaps
    line('GAPS MISSED:', '#FFB300')
    if (run.gapsMissed.length === 0) {
      line('  None — perfect read', '#666')
    } else {
      const uniqueGaps = [...new Set(run.gapsMissed.map(g => g.category))]
      line(`  ${uniqueGaps.slice(0, 4).join(', ')}`, '#AAA')
    }

    y += 8

    // Separator
    ctx.fillStyle = '#333'
    ctx.fillRect(24, y, W - 48, 1)
    y += 16

    // Footer
    ctx.fillStyle = '#888'
    ctx.font = '12px "IBM Plex Mono", monospace'
    ctx.fillText('subtext.game', 24, H - 24)
    ctx.fillText('arewegood.com', W - 150, H - 24)

    setDataUrl(canvas.toDataURL('image/png'))
    setGenerated(true)
  }, [run, won])

  return (
    <div className="share-card-section">
      <canvas ref={canvasRef} style={{ display: generated ? 'block' : 'none', maxWidth: '100%' }} />
      {!generated && (
        <button className="share-btn" onClick={generate}>
          GENERATE SHARE CARD
        </button>
      )}
      {generated && dataUrl && (
        <div className="share-actions">
          <a href={dataUrl} download="subtext-run.png" className="share-btn">
            DOWNLOAD
          </a>
          <button className="share-btn" onClick={() => {
            if (navigator.clipboard && canvasRef.current) {
              canvasRef.current.toBlob(blob => {
                if (blob) {
                  navigator.clipboard.write([new ClipboardItem({ 'image/png': blob })]).catch(() => {})
                }
              })
            }
          }}>
            COPY TO CLIPBOARD
          </button>
        </div>
      )}
    </div>
  )
}

// ─── Content loader ───────────────────────────────────────────
async function loadContent() {
  const base = import.meta.env.BASE_URL
  const [characters, npcs, locations, archetypes, intel, recurring, endings] = await Promise.all([
    fetch(`${base}content/characters.json`).then(r => r.json()),
    fetch(`${base}content/npcs.json`).then(r => r.json()),
    fetch(`${base}content/locations.json`).then(r => r.json()),
    fetch(`${base}content/archetypes.json`).then(r => r.json()),
    fetch(`${base}content/intel.json`).then(r => r.json()),
    fetch(`${base}content/recurring.json`).then(r => r.json()),
    fetch(`${base}content/endings.json`).then(r => r.json()),
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

    // For discovery events, assign intel items from this location
    const locationIntel = shuffle(rng, content.intel.intel_items.filter(
      item => item.location_found === locId
    ))
    let intelIdx = 0
    const discoveryEvents = events.filter(e => e.category === 'discovery').map(event => {
      const intel = intelIdx < locationIntel.length ? locationIntel[intelIdx++] : null
      return { ...event, attachedIntel: intel }
    })
    // Replace discovery events in the events list with intel-attached versions
    const eventsWithIntel = events.map(e => {
      if (e.category === 'discovery') {
        const match = discoveryEvents.find(d => d.event_id === e.event_id)
        return match || e
      }
      return e
    })

    // For encounter events, assign NPCs
    const encounters = eventsWithIntel.filter(e => e.category === 'encounter').map(event => {
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
      events: eventsWithIntel,
      encounters,
      recurringChar: recurringChar || null,
      nonEncounterEvents: eventsWithIntel.filter(e => e.category !== 'encounter'),
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
  const [debriefData, setDebriefData] = useState(null)
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
    setDebriefData(null)
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
        // Apply intel synergy as starting rapport/suspicion
        let startRapport = 0, startSuspicion = 0
        if (run.intelCollected.length > 0 && npc.archetype_id) {
          for (const intel of run.intelCollected) {
            const effect = intel.effects?.[npc.archetype_id]
            if (effect) {
              startRapport += effect.rapport_delta || 0
              startSuspicion += effect.suspicion_delta || 0
            }
          }
        }
        setRapport(startRapport)
        setSuspicion(startSuspicion)
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

      if (wasRecurring) {
        // Build debrief data for recurring character
        const rc = content.recurring.find(r => r.character_id === currentNPC.npc_id)
        if (rc) {
          const encounters = run.recurringEncounters[rc.character_id] || 1
          const opened = newRapport >= 2
          const closed = newRapport <= -2 || newSuspicion >= 3
          const arcStateKey = Object.keys(rc.arc_states)[Math.min(encounters - 1, Object.keys(rc.arc_states).length - 1)]
          const arcState = rc.arc_states[arcStateKey]
          setDebriefData({
            character: rc,
            encounters,
            arcStateName: arcStateKey,
            arcDescription: arcState?.description || '',
            finalRapport: newRapport,
            finalSuspicion: newSuspicion,
            opened,
            closed,
            receptionLanguage: rc.reception_language,
            opensWhen: rc.opens_when,
            closesWhen: rc.closes_when,
            hasAWGBonus: encounters >= 2,
          })
        }
        setDialogueNode(null)
        setCurrentNPC(null)
        setShowAWG(false)
        setPhase(PHASE.DEBRIEF)
      } else {
        setDialogueNode(null)
        setCurrentNPC(null)
        setShowAWG(false)
        setRun(prev => ({
          ...prev,
          currentEventIdx: prev.currentEventIdx + 1,
        }))
        setPhase(PHASE.PLAYING)
      }
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
    const updates = {
      currentEventIdx: run.currentEventIdx + 1,
      resources: {
        money: run.resources.money + (effects.money || 0),
        daysLeft: Math.max(0, run.resources.daysLeft + (effects.time || 0)),
        heat: Math.min(10, Math.max(0, run.resources.heat + (effects.heat || 0))),
        energy: Math.min(10, Math.max(0, run.resources.energy + (effects.energy || 0))),
      }
    }

    // Collect intel from discovery events
    if (currentEvent.attachedIntel && !run.intelCollected.some(i => i.intel_id === currentEvent.attachedIntel.intel_id)) {
      updates.intelCollected = [...run.intelCollected, currentEvent.attachedIntel]
    }

    setRun(prev => ({ ...prev, ...updates, intelCollected: updates.intelCollected || prev.intelCollected }))
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
      return run.intelCollected.some(i => i.intel_id === option.requires_intel || i.unlocks_option_tag === option.requires_intel)
    }
    return true
  }, [run])

  // Win state animation — staggered reveal with stillness
  // (must be before early returns to satisfy React hooks rules)
  useEffect(() => {
    if (!run) return
    const isWon = phase === PHASE.ENDING && run.currentStopIdx >= run.stops.length - 1 && run.resources.heat < 10
    if (isWon) {
      setWinAnimPhase(0)
      const timers = [
        setTimeout(() => setWinAnimPhase(1), 800),
        setTimeout(() => setWinAnimPhase(2), 2000),
        setTimeout(() => setWinAnimPhase(3), 3500),
        setTimeout(() => setWinAnimPhase(4), 5000),
      ]
      return () => timers.forEach(clearTimeout)
    }
  }, [phase, run])

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

  // UI Bar
  const UIBar = () => (
    <div className="ui-bar">
      <span className="stat name">{run.character.name}</span>
      <span className="stat">DAY {15 - run.resources.daysLeft}</span>
      <span className="stat">${run.resources.money}</span>
      <span className="stat">{run.resources.daysLeft} DAYS</span>
      <span className="stat">HEAT:<HeatBar value={run.resources.heat} /></span>
      <span className="stat">ENERGY:<EnergyBar value={run.resources.energy} /></span>
      {run.intelCollected.length > 0 && <span className="stat intel-count">INTEL:{run.intelCollected.length}</span>}
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
            <ShareCard run={run} won={won} />
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

  // Debrief screen (after recurring character encounters)
  if (phase === PHASE.DEBRIEF && debriefData) {
    const db = debriefData
    const statusLabel = db.opened ? 'OPENED' : db.closed ? 'CLOSED' : 'GUARDED'
    const statusClass = db.opened ? 'debrief-opened' : db.closed ? 'debrief-closed' : 'debrief-guarded'

    return (
      <div className="game-container">
        <UIBar />
        <div className="debrief-screen">
          <Portrait recurringId={db.character.character_id} />

          <div className="debrief-header">
            <span className="debrief-name">{db.character.name}</span>
            <span className="debrief-encounter">Encounter #{db.encounters}</span>
          </div>

          <div className="debrief-arc">{db.arcDescription}</div>

          <div className={`debrief-status ${statusClass}`}>
            {statusLabel}
          </div>

          <div className="debrief-section">
            <div className="debrief-label">Reception Language</div>
            <div className="debrief-value">{db.receptionLanguage}</div>
          </div>

          <div className="debrief-section">
            <div className="debrief-label">Opens when</div>
            <div className="debrief-hint">{db.opensWhen}</div>
          </div>

          <div className="debrief-section">
            <div className="debrief-label">Closes when</div>
            <div className="debrief-hint">{db.closesWhen}</div>
          </div>

          {db.hasAWGBonus && (
            <div className="debrief-bonus">
              2+ encounters — full relationship arc visible with AWG token
            </div>
          )}

          {db.opened && (
            <div className="debrief-narrator">
              Something shifted. They'll remember you next time.
            </div>
          )}
          {db.closed && (
            <div className="debrief-narrator">
              That door closed. It might open again. Might not.
            </div>
          )}
          {!db.opened && !db.closed && (
            <div className="debrief-narrator">
              Neither in nor out. The space between still holds.
            </div>
          )}

          <button className="continue-btn" onClick={() => {
            setDebriefData(null)
            setPhase(PHASE.PLAYING)
          }}>
            &gt; continue
          </button>
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
          {currentEvent.attachedIntel && (
            <div className="intel-found">
              <div className="intel-label">INTEL FOUND</div>
              <div className="intel-name">{currentEvent.attachedIntel.name}</div>
              <div className="intel-desc">{currentEvent.attachedIntel.description}</div>
              {currentEvent.attachedIntel.narrator_line && (
                <div className="narrator-line">{currentEvent.attachedIntel.narrator_line}</div>
              )}
              {currentEvent.attachedIntel.flavor && (
                <div className="intel-flavor">{currentEvent.attachedIntel.flavor}</div>
              )}
            </div>
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
          <Portrait
            archetypeId={currentNPC.archetype_id}
            recurringId={currentNPC.character_id}
          />
          <div className="npc-info">
            <div className="npc-name">{currentNPC.name}</div>
            <div className="npc-role">{currentNPC.role}</div>
            {currentNPC.appearance && (
              <div className="narrator-line">{currentNPC.appearance}</div>
            )}
          </div>
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
