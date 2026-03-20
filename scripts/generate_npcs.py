#!/usr/bin/env python3
"""
Procedural NPC generator for subtext.game
Generates NPC instances with full dialogue trees and co-authored AWG analysis.
No API key required — uses curated data pools and combinatorial generation.

Usage:
  python scripts/generate_npcs.py [--count 120]
"""

import argparse
import json
import random
import hashlib
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"

# ============================================================
# DATA POOLS
# ============================================================

# NPC roles by location type — specific, not generic
ROLES_BY_LOCATION = {
    "border": [
        "border patrol agent", "bus station ticket clerk", "coyote middleman",
        "gas station cashier at the last stop", "motel night manager",
        "ICE field agent", "truck stop diner waitress", "pawn shop owner",
        "church volunteer running a shelter", "bail bondsman",
        "tow truck driver who knows the back roads", "pharmacy tech near the crossing",
        "off-duty sheriff's deputy getting coffee", "notary public in a strip mall",
        "ranch hand who saw you coming over the fence"
    ],
    "transit": [
        "Greyhound ticket counter clerk", "train conductor on the overnight",
        "airport TSA agent", "rideshare driver who asks too many questions",
        "rest stop janitor who sees everything", "trucker offering a ride",
        "Amtrak café car attendant", "pawn shop owner near the bus station",
        "motel clerk at the highway exit", "gas station attendant on the night shift",
        "taxi dispatcher who knows the city", "vending machine repairman",
        "parking lot attendant at the terminal", "security guard at the Greyhound station",
        "waitress at the 24-hour truck stop"
    ],
    "mid_america": [
        "Walmart greeter in rural Ohio", "county clerk processing paperwork",
        "diner owner who has opinions about everything", "motel owner who rents by the week",
        "day labor coordinator outside Home Depot", "laundromat owner who hears everything",
        "pawn shop dealer who doesn't ask questions", "church secretary who does",
        "small-town cop on a traffic stop", "farmhand supervisor at harvest",
        "meatpacking plant floor manager", "bodega owner in a college town",
        "car wash owner who pays cash", "apartment super with a unit available",
        "temp agency receptionist"
    ],
    "nyc_outer": [
        "subway booth clerk in Queens", "bodega owner in Jackson Heights",
        "check cashing place teller", "flophouse manager in the Bronx",
        "food cart vendor in Flushing", "laundromat owner in Sunset Park",
        "gypsy cab driver at JFK", "restaurant kitchen manager in Chinatown",
        "day labor corner organizer in Red Hook", "street vendor selling phone cases",
        "barbershop owner who knows everyone", "social worker at a city shelter",
        "building super in Washington Heights", "pawnbroker on Fordham Road",
        "fish market worker at Fulton"
    ],
    "coney_island": [
        "hot dog stand operator near the boardwalk", "Nathan's Famous counter worker",
        "carnival ride operator", "boardwalk souvenir shop owner",
        "beach security guard", "competitive eating event coordinator",
        "amusement park ticket booth attendant", "fortune teller on Surf Avenue",
        "lifeguard on a break", "hot dog eating contest registration clerk",
        "food truck operator near MCU Park", "boardwalk portrait artist",
        "arcade manager", "Cyclone roller coaster operator",
        "Luna Park custodian who has seen it all"
    ]
}

# NPC names — diverse, specific
NPC_NAMES = {
    "border": [
        "Officer Dale Hutchinson", "Marisol", "Big Pete", "Dolores Vega",
        "Agent Kyle Sorensen", "Carmen", "Jimbo", "Linda Tran",
        "Father Miguel", "Hank Dietrich", "Ruby", "Deputy Vasquez",
        "Tammy Jo", "Mr. Pham", "Cowboy Steve"
    ],
    "transit": [
        "Brenda", "Hector Maldonado", "Phil", "Denise Washington",
        "Ahmed", "Shirley", "Big Mike", "Connie Park",
        "Jerome", "Dispatcher Ortiz", "Nadine", "Raj",
        "Gary the Security Guy", "Miss Lucille", "Tommy Two-Times"
    ],
    "mid_america": [
        "Darlene", "Hank Kowalski", "Marge", "Ricky Gutierrez",
        "Donna Mae", "Officer Petersen", "Bill Szymanski", "Maria Elena",
        "Pastor Dave", "Cindy", "Sanjay Patel", "Big Al",
        "Miss Betty", "Jose the Foreman", "Karen Engström"
    ],
    "nyc_outer": [
        "Mr. Kim", "Fatima", "Dmitri", "Abuela Rosa",
        "Kwame", "Mrs. Chen", "Junior", "Priya",
        "Oleg", "Yolanda", "Mohammed", "Ling",
        "Desmond", "Sunita", "Carlos the Super"
    ],
    "coney_island": [
        "Vinnie", "Tasha", "Old Man Murray", "Svetlana",
        "Derek", "Guadalupe", "Sal", "Nina Petrova",
        "Reggie", "Cookie", "Hans", "Esperanza",
        "Tommy Knuckles", "Mei-Ling", "Boardwalk Bob"
    ]
}

# Appearances — physical detail pools for ASCII variation
APPEARANCE_DETAILS = [
    "mustard stain on the collar that's been there since Tuesday",
    "reading glasses perched on forehead, forgotten",
    "lanyard with seventeen expired badges still attached",
    "coffee cup that hasn't been washed since the Clinton administration",
    "pen behind both ears — one works, one doesn't, they can't remember which",
    "a watch that's twelve minutes fast and they've built their whole life around it",
    "single gold tooth that catches the fluorescent light",
    "baseball cap worn so long the brim has a permanent curve matching their thumb",
    "a nametag that says 'TRAINEE' from nine years ago",
    "ink stains on both hands like they lost a fight with a printer",
    "three phones — two of them cracked, all of them ringing",
    "a key ring with more keys than any building has doors",
    "tattoo of a bird on the wrist, faded to blue-green",
    "one earring. The other hole closed up after the divorce",
    "a jacket too warm for the weather because the office AC is arctic",
    "shoes so polished you can see yourself — they can't see you, but the shoes can",
    "a rosary wrapped around the rearview mirror or the desk lamp",
    "nicotine patch visible on the forearm. Also a pack of cigarettes in the breast pocket",
    "band-aid on the chin from shaving with a dull razor this morning",
    "bifocals that they keep taking off and putting back on like they're negotiating with their own eyes"
]

# Motivations by archetype — absurd but treated seriously
MOTIVATIONS_BY_ARCHETYPE = {
    "control-seeking": [
        "implemented a color-coded filing system that no one else understands and will defend it to the death",
        "convinced the previous shift was deliberately sabotaging the stapler inventory",
        "building a case to prove the lunch schedule is being manipulated by someone in accounting",
        "reorganizing the entire office seating chart based on a feng shui book from 1987",
        "tracking everyone's bathroom breaks in a spreadsheet they think no one knows about",
    ],
    "lonely": [
        "has been telling the same story about meeting Tom Hanks at an airport for eleven years",
        "adopted a stray cat that lives under the desk and named it after their ex-wife",
        "memorized every regular's order and birthday and is devastated when they don't come in",
        "started a book club at work and is the only member but still holds meetings",
        "keeps a photo of a family reunion on the desk — it's from 2009 and half the people don't speak to each other anymore",
    ],
    "greedy": [
        "running three side hustles from the same desk and none of them know about the others",
        "convinced there's a way to monetize the employee parking lot and has drawn up blueprints",
        "sells homemade tamales from a cooler under the counter at a 300% markup",
        "figured out which vending machine gives back extra change and guards it territorially",
        "has a mental ledger of every favor owed to them going back to 2014",
    ],
    "paranoid": [
        "convinced the new security cameras were installed specifically to watch them",
        "keeps a backup of every email they've ever sent on a personal USB drive in their sock drawer",
        "noticed the coffee tastes different on Thursdays and is documenting the pattern",
        "won't use the staff microwave because they believe someone contaminated it in 2021",
        "checks the locks three times before leaving and once from the parking lot with binoculars",
    ],
    "bored": [
        "has read the entire employee handbook three times and found four contradictions nobody cares about",
        "times how long each customer takes and keeps a private leaderboard on a Post-it",
        "learned to solve a Rubik's cube one-handed during slow shifts and nobody's noticed",
        "invented a game where they predict what each customer will order and they're right 78% of the time",
        "has been writing a screenplay on receipt paper during downtime since 2019",
    ],
    "ideological": [
        "has strong opinions about which way the toilet paper should face and has put up signs",
        "believes the metric system is a conspiracy and will explain why if you give them four seconds",
        "convinced that the town council is secretly controlled by the regional manager of an Applebee's",
        "runs a podcast about municipal water rights that has eleven listeners, all furious",
        "has a wall of newspaper clippings behind the counter connected by red string",
    ],
    "guilty": [
        "accidentally shredded someone's visa application in 2018 and has never told anyone",
        "once gave wrong directions to a family and saw them on the news the next day",
        "pocketed a $20 tip meant for a coworker three years ago and still thinks about it at 2am",
        "reported a neighbor for code violations and the neighbor lost their house",
        "turned someone away at the end of their shift because they wanted to go home and never found out what happened",
    ],
    "ambitious": [
        "applied for regional manager four times and frames each rejection letter as motivation",
        "keeps a vision board in their locker that includes a corner office they've never seen",
        "name-drops the district supervisor at every opportunity despite having met them once at a holiday party",
        "started a LinkedIn account for this position and posts inspirational quotes every morning",
        "has a five-year plan laminated and taped inside the cash register",
    ],
    "burned-out": [
        "has been doing this exact job for seventeen years and can process a form with their eyes closed — and sometimes does",
        "used to care about customer satisfaction scores and now uses them as a coaster",
        "has a resignation letter saved as a draft in their email since 2020 and opens it every Monday",
        "once won employee of the month and the plaque is now holding up a wobbly desk leg",
        "takes exactly their allotted break time down to the second because nothing else is in their control",
    ],
    "suspicious": [
        "caught someone using a fake ID in 2016 and has been chasing that high ever since",
        "cross-references every story against a mental database of every lie they've ever been told",
        "keeps a notebook of inconsistencies they've noticed and reviews it on the bus home",
        "once found a discrepancy in the inventory that led to a firing and considers it their greatest achievement",
        "trusts receipts more than people and has said so out loud at a family dinner",
    ],
    "empathetic": [
        "keeps a drawer of tissues, granola bars, and phone chargers for people having bad days",
        "cried at a customer's story last week and had to take their break early",
        "remembers details about strangers' lives that the strangers have forgotten themselves",
        "adopted a therapy dog for the office using their own money because 'people need softness here'",
        "writes anonymous encouraging notes and leaves them in the break room",
    ],
    "corrupt": [
        "has an understanding with three different vendors and none of them have paper trails",
        "knows which forms can be expedited and which filing cabinets have locks that don't work",
        "has a cousin in every department and a favor owed in every office on the floor",
        "the suggestion box routes directly to the shredder and they installed the routing",
        "keeps two sets of books — one for the auditors and one for reality",
    ]
}

# Secrets by archetype — discoverable through dialogue
SECRETS_BY_ARCHETYPE = {
    "control-seeking": [
        "Their authority was never formally granted — they just started acting in charge during a staffing shortage in 2019 and nobody corrected them.",
        "They were demoted from a higher position last year but nobody in this office knows.",
        "The filing system everyone follows was copied from their mother's kitchen organization, label maker and all.",
        "They can't read the forms they're processing because they need new glasses but won't admit it.",
        "They applied for a transfer six months ago and were rejected. The rejection letter is in their desk drawer under the stapler.",
    ],
    "lonely": [
        "They moved here for a relationship that ended three days after the lease was signed.",
        "The family photos on the desk are from a stock photo frame — they never replaced the sample pictures.",
        "They drive 45 minutes to work even though there's a closer location, because this one has more foot traffic.",
        "They've been eating lunch alone in the break room for four years and started setting two places last month.",
        "Their emergency contact is still their ex-spouse's number and they know it doesn't work anymore.",
    ],
    "greedy": [
        "They're sending every extra dollar to a sibling's medical bills and have been for three years.",
        "The side hustle money is funding their kid's college application fees — seventeen schools and counting.",
        "They grew up with nothing and still keep a month's cash hidden in a coffee can behind the toilet tank at home.",
        "They owe money to someone who doesn't accept late payments and the deadline is Thursday.",
        "The greed is performance — they're terrified of the poverty they escaped and hoard as armor.",
    ],
    "paranoid": [
        "They were right once — someone was actually stealing from the inventory in 2018 — and being right ruined their ability to ever relax again.",
        "They take anxiety medication but hide the bottle in a vitamin container because they don't want anyone to know.",
        "The security camera footage showed something they weren't supposed to see and now they can't unsee it.",
        "Their spouse left because of the checking — the locks, the cameras, the constant questions about where they'd been.",
        "They were the victim of identity theft three years ago and never fully recovered.",
    ],
    "bored": [
        "They turned down a promotion because the higher position was even more boring and at least this one has a window.",
        "They have a finished novel in a drawer at home that they've never submitted because 'what's the point.'",
        "They're a classically trained musician working a desk job because the music career couldn't pay rent.",
        "The boredom is clinical depression they're managing without help.",
        "They once walked out of this job for three days and nobody noticed they were gone.",
    ],
    "ideological": [
        "They used to believe the exact opposite — the switch happened after a specific incident they never talk about.",
        "Their strongest-held position is based on something a parent told them that they've never independently verified.",
        "They've been banned from two Facebook groups and consider both badges of honor.",
        "The newspaper clippings include one about their own arrest at a protest in 2006.",
        "They donate anonymously to a cause that contradicts their public stance.",
    ],
    "guilty": [
        "The person they wronged tried to contact them last month and they didn't respond.",
        "They keep the incident report in their locker and reread it on bad days as self-punishment.",
        "They volunteer at the shelter on weekends as penance but tell coworkers it's for the tax deduction.",
        "The mistake they made was never discovered — they could have gotten away clean but their own conscience is the prison.",
        "Someone else was blamed for what they did and they watched it happen and said nothing.",
    ],
    "ambitious": [
        "They were told they'd never amount to anything by a specific person and every career move since has been a response to that sentence.",
        "The confidence is rehearsed — they practice power poses in the bathroom before each shift.",
        "Their resume includes a degree they started but never finished.",
        "They were the top candidate for the position above them but lost it to a nepotism hire and smile at that person every day.",
        "The five-year plan expires in three months and none of the milestones have been hit.",
    ],
    "burned-out": [
        "They used to be the best at this job — there's a dusty award in a box under the counter.",
        "They had a breakdown two years ago and the only accommodation they got was a different parking spot.",
        "They stay because they're eighteen months from a pension and counting every single day.",
        "A coworker they mentored got promoted above them and now reviews their performance.",
        "They answer the phone on the first ring at home because they're worried it might be the hospital calling about their mother.",
    ],
    "suspicious": [
        "They were lied to by someone they trusted completely and the suspicion is a scar from that specific wound.",
        "They once accused an innocent person based on a hunch and the accusation ruined that person's day — they think about it monthly.",
        "The notebook of inconsistencies includes notes about their own boss.",
        "They trust one person in the world — a childhood friend — and check in with them every Sunday to make sure the trust still holds.",
        "They verified their own spouse's alibi once and the spouse doesn't know.",
    ],
    "empathetic": [
        "They absorb other people's pain and have no mechanism for releasing it — the drawer of tissues is also for themselves.",
        "They were in a situation like yours once — undocumented, or broke, or lost — and never tell the story but it's why they help.",
        "The therapy dog was prescribed for them, not the office. They just share.",
        "They've taken on so much of other people's weight that their own relationships are collapsing under the borrowed grief.",
        "Someone they helped once came back and hurt them, and they still keep helping.",
    ],
    "corrupt": [
        "They started the corruption to pay for a sick child's treatment and the child is better now but the corruption continues.",
        "The two sets of books are for protection — they have evidence against their boss and it's the only thing keeping them employed.",
        "A previous version of this arrangement got someone else sent to prison and they visited once.",
        "They tried to go straight last year and were threatened by the people who benefit from the arrangement.",
        "The favor network started as genuine community mutual aid and slowly rotted into what it is now.",
    ]
}

# Gap categories mapped to each archetype (from archetype data)
ARCHETYPE_GAP_CATEGORIES = {
    "control-seeking": ["timing", "length", "absence"],
    "lonely": ["length", "topic_architecture", "mirror"],
    "greedy": ["word_choice", "sequence", "overcorrection"],
    "paranoid": ["consistency", "punctuation", "absence"],
    "bored": ["timing", "length", "punctuation"],
    "ideological": ["word_choice", "overcorrection", "topic_architecture"],
    "guilty": ["overcorrection", "absence", "topic_architecture"],
    "ambitious": ["length", "word_choice", "sequence"],
    "burned-out": ["timing", "length", "absence"],
    "suspicious": ["consistency", "sequence", "word_choice"],
    "empathetic": ["mirror", "absence", "overcorrection"],
    "corrupt": ["absence", "word_choice", "topic_architecture"]
}

# Bridge line relationship types — specific, not generic
BRIDGE_RELATIONSHIPS = [
    "your mother-in-law", "your team lead", "your college roommate",
    "your older sister", "your landlord", "your ex",
    "your therapist", "your kid's teacher", "your neighbor",
    "your father", "your best friend's spouse", "your boss",
    "your uncle who only calls when he needs something",
    "your coworker who takes credit for your work",
    "your partner's best friend",
    "your grandmother", "your younger brother",
    "your doctor", "your barber", "your oldest friend",
    "your child's other parent", "your mentor",
    "the friend you only hear from when they're in trouble",
    "your cousin who always has a scheme",
    "your partner when they're stressed"
]

# Tones, intents, registers for dialogue options
TONES = ["deferential", "warm", "direct", "humorous", "formal", "vulnerable", "indirect"]
INTENTS = ["comply", "connect", "negotiate", "deflect", "challenge", "reveal", "observe"]
REGISTERS = ["broken", "simple", "standard", "formal", "fluent"]

# Occupation keywords that unlock special options
OCCUPATION_KEYWORDS = [
    "medical", "legal", "religious", "military", "cooking",
    "mechanical", "agricultural", "teaching", "financial", "technical"
]

# Intel item IDs for requires_intel
INTEL_IDS = [f"intel-{str(i).zfill(3)}" for i in range(30)]

# AWG closers
AWG_CLOSERS = [
    "Are We Good helps you read this in real time.",
    "This is what Are We Good was built for.",
    "Are We Good catches what you miss.",
    "You don't need a game to see this. Are We Good.",
    "Next time, you'll see it. arewegood.com",
    "The signal was there. Are We Good shows you where.",
    "This pattern is in every conversation you have. Are We Good.",
    "You've been missing this your whole life. arewegood.com",
    "Are We Good reads the room so you can be in it.",
    "Every conversation has a subtext. arewegood.com",
]


# ============================================================
# DIALOGUE TEMPLATES BY ARCHETYPE
# ============================================================
# Each archetype has curated dialogue pools per emotional state.
# NPC lines, narrator lines, and options are selected and customized.

def build_dialogue_pools():
    """Return dialogue templates indexed by archetype and emotional state."""
    return {
        "control-seeking": {
            "neutral": {
                "npc_lines": [
                    "Sit down. I'll tell you when.",
                    "Name. Spelled. Slowly.",
                    "You'll wait until I finish this.",
                    "Put your bag there. Not there. There.",
                    "I didn't say you could sit.",
                    "Give me the form. No — the other one.",
                    "You have thirty seconds. Use them wisely.",
                ],
                "narrator_lines": [
                    "The pen has been uncapped for six minutes. It has not touched paper.",
                    "There are two chairs. One has been moved to the exact center of the room.",
                    "A clock on the wall ticks. It is the only sound they permit.",
                    "The desk is arranged with military precision. Even the dust is orderly.",
                    None,
                ],
                "good_options": [
                    ("I'll wait.", {"tone": "deferential", "intent": "comply", "register": "simple"}, 1, -1),
                    ("Of course. Take your time.", {"tone": "formal", "intent": "comply", "register": "standard"}, 2, -1),
                    ("I have the paperwork ready.", {"tone": "formal", "intent": "comply", "register": "formal"}, 2, -1),
                ],
                "bad_options": [
                    ("Actually, I was here first—", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 2),
                    ("*laughs nervously*", {"tone": "humorous", "intent": "deflect", "register": "simple"}, -1, 1),
                    ("Please, I really need—", {"tone": "vulnerable", "intent": "reveal", "register": "simple"}, -1, 1),
                ],
                "locked_options": [
                    ("I've prepared documentation for every step of my journey, organized by date.", {"tone": "formal", "intent": "comply", "register": "formal"}, 2, -2),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "Say that again. The part about where you stayed.",
                    "You said Tuesday before. Now you're saying Wednesday.",
                    "I'm going to need you to start from the beginning.",
                    "Spell your last name. Again.",
                    "The form says one thing. You're saying another.",
                ],
                "narrator_lines": [
                    "They pick up a pen. Write something you cannot see.",
                    "The second chair has been moved closer to the door.",
                    "A file folder appears. It has your name on it. It is thick.",
                    None,
                ],
                "good_options": [
                    ("It was Tuesday. I misspoke. Here's my ticket.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, -1),
                    ("*sits perfectly still and waits*", {"tone": "deferential", "intent": "comply", "register": "simple"}, 2, -2),
                ],
                "bad_options": [
                    ("Why does that matter?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("I don't understand, I just need—", {"tone": "vulnerable", "intent": "negotiate", "register": "broken"}, -1, 1),
                ],
                "locked_options": [
                    ("Here is my itinerary, bus receipt, and hotel confirmation. All dated.", {"tone": "formal", "intent": "comply", "register": "formal"}, 2, -2),
                ],
            },
            "hostile": {
                "npc_lines": [
                    "We're done here.",
                    "Stand up. Follow me.",
                    "I've heard enough. You can explain it to the next person.",
                    "You should have thought about that before.",
                ],
                "narrator_lines": [
                    "They are already reaching for the phone.",
                    "The door opens. It was not opened for your convenience.",
                    None,
                ],
                "good_options": [
                    ("I understand. Whatever you need.", {"tone": "deferential", "intent": "comply", "register": "simple"}, 0, 0),
                ],
                "bad_options": [
                    ("You can't do this!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Alright. This looks in order.",
                    "You can go to window three. Tell them I sent you.",
                    "Your paperwork checks out. You've been thorough.",
                    "I'm going to stamp this. Don't make me regret it.",
                ],
                "narrator_lines": [
                    "For the first time, they use your name. They pronounce it correctly.",
                    "A stamp hits paper. The sound is the sound of a door unlocking.",
                    None,
                ],
                "good_options": [
                    ("Thank you. I appreciate your thoroughness.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Finally. That took forever.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 1),
                ],
                "locked_options": [],
            }
        },
        "lonely": {
            "neutral": {
                "npc_lines": [
                    "Oh! Hi. Sorry, I was just — anyway. What do you need?",
                    "You know, the last person who came through here was from — well, never mind. How can I help?",
                    "It's quiet today. It's quiet most days, actually. But especially today.",
                    "My cat — I have a cat, did I mention? — she does this thing where... sorry, you had a question.",
                    "You remind me of someone. I can't think who. Anyway.",
                ],
                "narrator_lines": [
                    "The coffee cup has been empty for three hours. They hold it anyway.",
                    "There are two photos on the desk. One faces outward. One faces the wall.",
                    "A radio plays softly. It is tuned to a talk station. Someone is always talking.",
                    "The 'NEXT WINDOW PLEASE' sign has been turned off. This is the only window.",
                    None,
                ],
                "good_options": [
                    ("You have a cat? What's their name?", {"tone": "warm", "intent": "connect", "register": "standard"}, 2, 0),
                    ("It does seem quiet. How long have you been here?", {"tone": "warm", "intent": "connect", "register": "standard"}, 2, -1),
                    ("That person from before — where were they from?", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Just the form, please.", {"tone": "direct", "intent": "comply", "register": "simple"}, -1, 0),
                    ("I'm in a hurry.", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -2, 0),
                    ("*checks phone*", {"tone": "indirect", "intent": "deflect", "register": "simple"}, -1, 0),
                ],
                "locked_options": [
                    ("I had a cat once, back home. Orange one. She used to sleep on the roof.", {"tone": "warm", "intent": "reveal", "register": "standard"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "Right. What was it you needed again?",
                    "The form is over there. I'll process it when it's filled out.",
                    "I can help the next person in line.",
                    "It's not really my place to — I mean, the process is the process.",
                ],
                "narrator_lines": [
                    "The warmth has left like a draft closed a door.",
                    "They are organizing paper clips. They do not need organizing.",
                    None,
                ],
                "good_options": [
                    ("I'm sorry — you were telling me about your cat.", {"tone": "warm", "intent": "connect", "register": "standard"}, 2, -1),
                    ("I didn't mean to rush. This place — it's a lot. How do you handle it?", {"tone": "vulnerable", "intent": "reveal", "register": "standard"}, 2, -1),
                ],
                "bad_options": [
                    ("Can I speak to a manager?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 1),
                    ("Just process the form.", {"tone": "direct", "intent": "comply", "register": "simple"}, -1, 0),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "Window's closed.",
                    "You can come back tomorrow.",
                    "I'm on break.",
                    "Next.",
                ],
                "narrator_lines": [
                    "The radio has been turned up. It is no longer softly.",
                    "The photos on the desk have been placed face-down.",
                    None,
                ],
                "good_options": [
                    ("I'm sorry I was short with you earlier. I'm having a rough day too.", {"tone": "vulnerable", "intent": "reveal", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("You can't just close the window!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 1),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Okay, listen. Here's what you actually need to do.",
                    "I'm not supposed to tell you this, but there's a faster line at window seven.",
                    "Take my card. If anyone asks, tell them Brenda sent you.",
                    "You seem like good people. Hold on, let me make a call.",
                ],
                "narrator_lines": [
                    "They write a phone number on a Post-it note. Their handwriting is careful.",
                    "For a moment, they look like they might hug you. They do not. But almost.",
                    None,
                ],
                "good_options": [
                    ("Thank you. Really. You've been so kind.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Great, thanks, gotta go.", {"tone": "direct", "intent": "deflect", "register": "simple"}, -1, 0),
                ],
                "locked_options": [],
            }
        },
        "greedy": {
            "neutral": {
                "npc_lines": [
                    "What've you got?",
                    "That depends. What's it worth to you?",
                    "I can help. Question is whether you can help me.",
                    "Nice bag. What's in it?",
                    "Let me tell you how this works. Everything costs something.",
                ],
                "narrator_lines": [
                    "Their eyes perform an inventory of your possessions in 1.4 seconds.",
                    "A calculator sits on the desk. It has been used recently. The number is still showing.",
                    "The price list on the wall has been crossed out and rewritten three times today.",
                    None,
                ],
                "good_options": [
                    ("I can offer fifty dollars for your help.", {"tone": "direct", "intent": "negotiate", "register": "standard"}, 1, 0),
                    ("I have something you might want. Can we talk?", {"tone": "indirect", "intent": "negotiate", "register": "standard"}, 1, 0),
                    ("My cousin knows the wholesale guy on Fourth Street. I can introduce you.", {"tone": "direct", "intent": "negotiate", "register": "standard"}, 2, 0),
                ],
                "bad_options": [
                    ("Can't you just help me out? As a favor?", {"tone": "vulnerable", "intent": "negotiate", "register": "simple"}, -2, 1),
                    ("Isn't this supposed to be free?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 1),
                    ("Please, I don't have anything.", {"tone": "vulnerable", "intent": "reveal", "register": "broken"}, -1, 0),
                ],
                "locked_options": [
                    ("I notice you're selling those tamales at twelve dollars. I could help you source the corn husks at half your current cost.", {"tone": "direct", "intent": "negotiate", "register": "fluent"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "That's not enough and you know it.",
                    "I've got other people waiting. People who understand how this works.",
                    "You're wasting my time. Time is money. Yours and mine.",
                    "The price just went up.",
                ],
                "narrator_lines": [
                    "They glance at the door. Someone else just walked in.",
                    "The calculator has been turned to face you. The number is larger than before.",
                    None,
                ],
                "good_options": [
                    ("Alright. Let me sweeten the deal.", {"tone": "direct", "intent": "negotiate", "register": "standard"}, 1, -1),
                    ("I respect your time. Here's what I can actually offer.", {"tone": "formal", "intent": "negotiate", "register": "standard"}, 1, -1),
                ],
                "bad_options": [
                    ("That's not fair!", {"tone": "direct", "intent": "challenge", "register": "simple"}, -2, 1),
                    ("Come on, have a heart.", {"tone": "vulnerable", "intent": "connect", "register": "simple"}, -1, 0),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "We're done. Door's that way.",
                    "I don't work for free and I don't work for feelings.",
                    "Next customer.",
                ],
                "narrator_lines": [
                    "The calculator has been turned off. Negotiations have concluded.",
                    None,
                ],
                "good_options": [
                    ("Wait — I just found cash in my other pocket.", {"tone": "direct", "intent": "negotiate", "register": "simple"}, 0, 0),
                ],
                "bad_options": [
                    ("You're a crook!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Okay, now we're talking. Here's what I can do for you.",
                    "For that? I'll throw in the good directions too.",
                    "You're smart. I like dealing with smart people. Here.",
                    "Deal. And because I like you — here's something extra.",
                ],
                "narrator_lines": [
                    "Money changes hands below the counter. The transaction has no receipt.",
                    "They smile. It is the first genuine expression you've seen from them.",
                    None,
                ],
                "good_options": [
                    ("Pleasure doing business.", {"tone": "direct", "intent": "comply", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Actually, can I get a discount on that too?", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -1, 1),
                ],
                "locked_options": [],
            }
        },
        "paranoid": {
            "neutral": {
                "npc_lines": [
                    "Papers. All of them.",
                    "You said you arrived when? And from where? And with who?",
                    "I'm going to need you to say that one more time.",
                    "Just stand there. Don't touch anything.",
                    "Where were you at 3pm yesterday? No reason. Just asking.",
                ],
                "narrator_lines": [
                    "They check your ID. They check it again. They hold it up to the light.",
                    "A notebook sits open. Every third page has been torn out.",
                    "The security camera behind them has a small piece of tape over the blinking light. They put it there.",
                    None,
                ],
                "good_options": [
                    ("Here are my documents. I have copies of everything.", {"tone": "formal", "intent": "comply", "register": "standard"}, 2, -2),
                    ("I was at the bus station. Here's the ticket stub.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, -1),
                    ("*stands still, hands visible*", {"tone": "deferential", "intent": "comply", "register": "simple"}, 1, -1),
                ],
                "bad_options": [
                    ("Why do you need to know that?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("I don't remember exactly...", {"tone": "indirect", "intent": "deflect", "register": "simple"}, -1, 2),
                    ("*reaches into pocket suddenly*", {"tone": "direct", "intent": "comply", "register": "simple"}, -1, 2),
                ],
                "locked_options": [
                    ("I have a notarized copy of my travel itinerary, signed by the embassy clerk. Her name was Patricia.", {"tone": "formal", "intent": "comply", "register": "fluent"}, 2, -2),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "You said Tuesday. The form says Wednesday. Which is it?",
                    "Don't move. I need to verify something.",
                    "Why are your hands shaking?",
                    "I'm going to ask you these questions again. From the top.",
                ],
                "narrator_lines": [
                    "They stand up. The chair scrapes the floor like a warning.",
                    "A phone appears. They dial two numbers and stop.",
                    None,
                ],
                "good_options": [
                    ("You're right. Let me clarify — it was Tuesday evening, which I listed as Wednesday because I arrived after midnight.", {"tone": "formal", "intent": "comply", "register": "formal"}, 2, -1),
                    ("*remains calm, breathes slowly, waits*", {"tone": "deferential", "intent": "comply", "register": "simple"}, 1, -1),
                ],
                "bad_options": [
                    ("What difference does it make?!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("Please, I'm not lying—", {"tone": "vulnerable", "intent": "reveal", "register": "simple"}, -1, 1),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "Sit down. Someone is coming to talk to you.",
                    "Your story doesn't check out.",
                    "I don't believe you.",
                ],
                "narrator_lines": [
                    "The phone call has been made. You were not told to whom.",
                    "The door behind you is now closed. You did not hear it close.",
                    None,
                ],
                "good_options": [
                    ("I understand your concern. I'll wait. I have nothing to hide.", {"tone": "formal", "intent": "comply", "register": "standard"}, 0, 0),
                ],
                "bad_options": [
                    ("This is insane!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Alright. This checks out.",
                    "Your paperwork's clean. That's... rare.",
                    "Everything matches. You can go.",
                    "I'm satisfied. Move along.",
                ],
                "narrator_lines": [
                    "They nod once. It is the nod of a person who expected to find a problem and didn't.",
                    "The notebook closes. Your page was clean.",
                    None,
                ],
                "good_options": [
                    ("Thank you for being thorough.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, -1),
                ],
                "bad_options": [
                    ("See? I told you.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 1),
                ],
                "locked_options": [],
            }
        },
        "bored": {
            "neutral": {
                "npc_lines": [
                    "Yeah.",
                    "Uh huh. And?",
                    "Number?",
                    "Form's on the counter. Pen's chained to it. Don't ask why.",
                    "*scrolls phone* Oh, sorry. What?",
                ],
                "narrator_lines": [
                    "They have not blinked in a way that suggests interest.",
                    "A Rubik's cube sits on the counter, solved. There is nothing left to solve.",
                    "The clock reads 2:17. They checked it at 2:16. And at 2:15.",
                    None,
                ],
                "good_options": [
                    ("You know what? I once ate fourteen hot dogs in one sitting. Threw up in a fountain.", {"tone": "humorous", "intent": "connect", "register": "standard"}, 2, 0),
                    ("I'm trying to get to a competitive eating contest. It's exactly as stupid as it sounds.", {"tone": "humorous", "intent": "reveal", "register": "standard"}, 2, -1),
                    ("Is that a solved Rubik's cube? Can you do it again while I watch?", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("I need to file form 27-B.", {"tone": "formal", "intent": "comply", "register": "standard"}, -1, 0),
                    ("Please process my paperwork.", {"tone": "deferential", "intent": "comply", "register": "simple"}, -1, 0),
                    ("I'm looking for assistance with—", {"tone": "formal", "intent": "comply", "register": "formal"}, -2, 0),
                ],
                "locked_options": [
                    ("I just crossed three state lines in a stolen church van with a mariachi band. But that's not even the weird part.", {"tone": "humorous", "intent": "reveal", "register": "fluent"}, 2, 0),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "Wait. What? Say that again.",
                    "Hold on — you're telling me what now?",
                    "That's... actually, keep going.",
                    "No no no, back up. The hot dog part.",
                ],
                "narrator_lines": [
                    "The phone has been put down. This is unprecedented.",
                    "They lean forward. For the first time, both eyes are pointed at the same thing: you.",
                    None,
                ],
                "good_options": [
                    ("Oh, it gets better. So then the bus driver says—", {"tone": "humorous", "intent": "connect", "register": "standard"}, 2, -1),
                    ("Right? That's what I said. And THEN—", {"tone": "humorous", "intent": "reveal", "register": "standard"}, 2, -1),
                ],
                "bad_options": [
                    ("Anyway, about the form.", {"tone": "formal", "intent": "comply", "register": "standard"}, -2, 0),
                    ("It's not that interesting, really.", {"tone": "indirect", "intent": "deflect", "register": "simple"}, -1, 0),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "System's down. Come back Monday.",
                    "Not my department.",
                    "Take a number. We're at seven. You're forty-three.",
                ],
                "narrator_lines": [
                    "They have decided you are boring. This is worse than hostility. This is bureaucratic indifference.",
                    None,
                ],
                "good_options": [
                    ("Before I go — want to know what happened with the hot dogs?", {"tone": "humorous", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("I need to speak to someone else.", {"tone": "direct", "intent": "challenge", "register": "standard"}, 0, 1),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Okay, you're interesting. Here's what you actually need to do.",
                    "Oh man. Okay. I'm gonna help you because that story was worth my afternoon.",
                    "You know what, I like you. Let me show you the shortcut.",
                    "That's the best thing I've heard in three years at this job. What do you need?",
                ],
                "narrator_lines": [
                    "They are grinning. It changes their entire face. You wonder where this person has been hiding.",
                    "The Rubik's cube has been scrambled. They need a new challenge. You provided one.",
                    None,
                ],
                "good_options": [
                    ("You're a lifesaver. This has been the best conversation I've had since Ohio.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Finally. Can you just stamp the form?", {"tone": "direct", "intent": "comply", "register": "simple"}, -1, 0),
                ],
                "locked_options": [],
            }
        },
        "ideological": {
            "neutral": {
                "npc_lines": [
                    "This country, you know? It used to mean something.",
                    "Where are you from? And I mean — where are you FROM?",
                    "You seem like someone who gets it.",
                    "Let me ask you something. You think things are better now or worse?",
                ],
                "narrator_lines": [
                    "A bumper sticker is visible. It has an opinion.",
                    "The word 'freedom' appears on three separate objects within arm's reach.",
                    "They are waiting for you to agree. The silence is a loyalty test.",
                    None,
                ],
                "good_options": [
                    ("You're right. Things aren't what they used to be.", {"tone": "indirect", "intent": "comply", "register": "standard"}, 2, -1),
                    ("*nods slowly*", {"tone": "deferential", "intent": "comply", "register": "simple"}, 1, 0),
                    ("I've seen a lot of places. Nowhere's perfect.", {"tone": "indirect", "intent": "deflect", "register": "standard"}, 0, 0),
                ],
                "bad_options": [
                    ("I think it's more complicated than that.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 1),
                    ("That's not really how I see it.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("I'd rather not talk politics.", {"tone": "indirect", "intent": "deflect", "register": "standard"}, -1, 0),
                ],
                "locked_options": [
                    ("My grandfather used to say the same thing. He fought in a war over it.", {"tone": "warm", "intent": "connect", "register": "fluent"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "Where did you say you were from again?",
                    "Hmm. I thought you'd see it different.",
                    "Most people like you — and I mean that in a general sense — usually...",
                    "Interesting. Very interesting.",
                ],
                "narrator_lines": [
                    "The word 'interesting' was not a compliment.",
                    "Their arms have crossed. A border has closed.",
                    None,
                ],
                "good_options": [
                    ("I hear you. My family raised me the same way.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, -1),
                    ("I think we want the same things, just from different angles.", {"tone": "indirect", "intent": "negotiate", "register": "standard"}, 1, -1),
                ],
                "bad_options": [
                    ("What do you mean, 'people like me'?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("Actually, the data shows—", {"tone": "direct", "intent": "challenge", "register": "formal"}, -2, 2),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "You know what your problem is?",
                    "This is exactly what I'm talking about.",
                    "I don't think I can help you. And I don't think I want to.",
                ],
                "narrator_lines": [
                    "The monologue begins. It will not require your participation.",
                    None,
                ],
                "good_options": [
                    ("You might be right. I need to think about it.", {"tone": "deferential", "intent": "deflect", "register": "standard"}, 0, 0),
                ],
                "bad_options": [
                    ("You don't know anything about me.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "See? You get it. Most people don't get it.",
                    "I knew it. I could tell you were one of the good ones.",
                    "Here — let me help you out. We look out for our own.",
                    "You need anything, you come back to me. I take care of people who get it.",
                ],
                "narrator_lines": [
                    "'Our own' is a circle that was drawn just now to include you. It can be redrawn.",
                    "Generosity flows. It flows in one direction: toward agreement.",
                    None,
                ],
                "good_options": [
                    ("I appreciate that. It means a lot.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Well, I don't agree with everything—", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 1),
                ],
                "locked_options": [],
            }
        },
        "guilty": {
            "neutral": {
                "npc_lines": [
                    "I'm just doing my job, you know? Someone has to.",
                    "Look, it's not like I — I mean, the rules are the rules.",
                    "I process a lot of people through here. A lot. You're not — I mean, it's fine.",
                    "Don't look at me like that. I didn't make the policy.",
                ],
                "narrator_lines": [
                    "They are defending themselves against an accusation you haven't made.",
                    "A photo on the desk has been turned to face the wall. Recently.",
                    "Their lunch sits uneaten. It has been uneaten for several hours.",
                    None,
                ],
                "good_options": [
                    ("Everyone has to make a living. No judgment.", {"tone": "warm", "intent": "connect", "register": "standard"}, 2, -1),
                    ("*shrugs* We all do what we have to do.", {"tone": "indirect", "intent": "deflect", "register": "simple"}, 1, -1),
                    ("I understand. Rules are rules.", {"tone": "deferential", "intent": "comply", "register": "simple"}, 1, 0),
                ],
                "bad_options": [
                    ("So you decide who gets through?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 1),
                    ("How many people have you turned away today?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 1),
                    ("You seem uncomfortable. Why?", {"tone": "direct", "intent": "observe", "register": "standard"}, -1, 1),
                ],
                "locked_options": [
                    ("My mother worked a job she hated for twenty years to feed us. She never complained. I respect what you do.", {"tone": "warm", "intent": "reveal", "register": "fluent"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "I don't know what you're implying.",
                    "I have to — there's something I need to — anyway, your papers.",
                    "It's not — look, you don't know what it's like on this side.",
                    "I didn't ask for this assignment.",
                ],
                "narrator_lines": [
                    "They have started a sentence about the person they turned away last Tuesday. They will not finish it.",
                    "A drawer opens and closes. Something was almost shown to you.",
                    None,
                ],
                "good_options": [
                    ("I'm not implying anything. I just need help.", {"tone": "indirect", "intent": "deflect", "register": "simple"}, 1, -1),
                    ("I know. Nobody asks for the jobs that matter most.", {"tone": "warm", "intent": "connect", "register": "standard"}, 2, -1),
                ],
                "bad_options": [
                    ("So what DID happen to that person?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("Your conscience is not my problem.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "Do YOU know how many people try to — you think I enjoy this?",
                    "Everyone's got a story. You think yours is special?",
                    "I can't help you. I can't help anyone. That's — that's just how it is.",
                ],
                "narrator_lines": [
                    "The projection is loud enough to hear from the parking lot.",
                    "They are angry at you. But they are not angry at you.",
                    None,
                ],
                "good_options": [
                    ("You're right. I don't know what it's like to be you.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("At least you get to go home tonight.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Look. Between you and me — here's what I can do.",
                    "I'm not supposed to, but... take this.",
                    "Don't tell anyone I did this. Please.",
                    "There's a way around the system. I'll show you. Just — don't say my name.",
                ],
                "narrator_lines": [
                    "A stamp appears. It stamps something that should not be stamped.",
                    "The act of helping costs them something. You can see the price on their face.",
                    None,
                ],
                "good_options": [
                    ("I won't say a word. Thank you.", {"tone": "warm", "intent": "comply", "register": "simple"}, 1, -1),
                ],
                "bad_options": [
                    ("I knew you'd come around.", {"tone": "direct", "intent": "observe", "register": "standard"}, -1, 1),
                ],
                "locked_options": [],
            }
        },
        "ambitious": {
            "neutral": {
                "npc_lines": [
                    "When I was running the overnight shift — before I moved up — I used to see cases like yours all the time.",
                    "I handle the complex cases now. My supervisor trusts me with those.",
                    "You're lucky you got me and not the other guy. I've got the experience.",
                    "Let me tell you something. I've been at this for twelve years. I know what I'm doing.",
                ],
                "narrator_lines": [
                    "The framed certificate is positioned so both you and the security camera can read it.",
                    "Their business card says 'Senior' in a font slightly larger than regulation.",
                    "A motivational poster hangs behind them. They put it there. It's a quote they said.",
                    None,
                ],
                "good_options": [
                    ("Twelve years? You must have seen everything.", {"tone": "warm", "intent": "connect", "register": "standard"}, 2, 0),
                    ("I can tell you're the one to talk to. Everyone said so.", {"tone": "deferential", "intent": "comply", "register": "standard"}, 2, -1),
                    ("What would you advise? You clearly know the system.", {"tone": "deferential", "intent": "comply", "register": "standard"}, 2, -1),
                ],
                "bad_options": [
                    ("Can I just get the form?", {"tone": "direct", "intent": "comply", "register": "simple"}, -2, 1),
                    ("Yeah, twelve years. Cool.", {"tone": "indirect", "intent": "deflect", "register": "simple"}, -2, 1),
                    ("The other guy seemed helpful too.", {"tone": "warm", "intent": "connect", "register": "standard"}, -2, 1),
                ],
                "locked_options": [
                    ("I work in management myself. I can tell a leader when I see one. The way you organize this office — that's not accident.", {"tone": "formal", "intent": "connect", "register": "fluent"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "I don't think you understand the level I operate at.",
                    "That's not really something I handle at my level. Which is — significantly above this.",
                    "Look, I'm very busy. With important things.",
                    "I shouldn't even be working this window. I'm covering for someone less qualified.",
                ],
                "narrator_lines": [
                    "They straighten their tie. The tie cost more than your bus ticket.",
                    "The business card has been placed slightly closer to you. An offering of status.",
                    None,
                ],
                "good_options": [
                    ("That's exactly why I need YOUR help. Only someone at your level could handle this.", {"tone": "deferential", "intent": "comply", "register": "standard"}, 2, -1),
                ],
                "bad_options": [
                    ("Everyone here seems qualified to me.", {"tone": "warm", "intent": "connect", "register": "standard"}, -1, 0),
                    ("Can I talk to someone else then?", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -2, 1),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "I don't have time for this.",
                    "You clearly don't understand the process.",
                    "Next.",
                ],
                "narrator_lines": [
                    "They wave you away. The wave is practiced. It communicates hierarchy.",
                    None,
                ],
                "good_options": [
                    ("I'm sorry to have wasted your time. I clearly underestimated how busy you are.", {"tone": "deferential", "intent": "comply", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("You're not that important.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "I'll take care of it. Personally.",
                    "Consider it done. You came to the right person.",
                    "I'll make some calls. When I say I'll handle it, I handle it.",
                    "Tell you what — I'm going to fast-track this. Because I can.",
                ],
                "narrator_lines": [
                    "The help arrives with a flourish. It is a performance. It is also genuine.",
                    "They pick up the phone like they are making a decision that will alter the course of history. Perhaps it will alter yours.",
                    None,
                ],
                "good_options": [
                    ("You're the best. I mean that. I'll tell everyone who helped me.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Great. Thanks.", {"tone": "direct", "intent": "comply", "register": "simple"}, -1, 0),
                ],
                "locked_options": [],
            }
        },
        "burned-out": {
            "neutral": {
                "npc_lines": [
                    "Next.",
                    "Form. Sign. Wait.",
                    "Yep.",
                    "Window three.",
                    "Pen's there.",
                ],
                "narrator_lines": [
                    "They have processed the form before you finished explaining. It's unclear if this is efficiency or indifference.",
                    "An Employee of the Month plaque from 2014 is being used as a paperweight.",
                    "The coffee is cold. It has been cold since they stopped noticing.",
                    None,
                ],
                "good_options": [
                    ("Just one form. Already filled out. Just needs your stamp.", {"tone": "direct", "intent": "comply", "register": "simple"}, 2, 0),
                    ("Thank you. I'll be quick.", {"tone": "deferential", "intent": "comply", "register": "simple"}, 1, 0),
                    ("*slides form across, already complete, pen attached*", {"tone": "direct", "intent": "comply", "register": "simple"}, 2, -1),
                ],
                "bad_options": [
                    ("I have a complicated situation that I need to explain—", {"tone": "formal", "intent": "reveal", "register": "standard"}, -2, 0),
                    ("Is there someone I can talk to about my specific case?", {"tone": "formal", "intent": "negotiate", "register": "standard"}, -1, 0),
                    ("How are you doing today?", {"tone": "warm", "intent": "connect", "register": "standard"}, -1, 0),
                ],
                "locked_options": [
                    ("One form. One stamp. Thirty seconds of your time. That's all I need in this life.", {"tone": "direct", "intent": "comply", "register": "fluent"}, 2, 0),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "Is there something else?",
                    "*sighs* Okay. What now.",
                    "This was supposed to be simple.",
                    "Look, I don't make the rules. I just survive them.",
                ],
                "narrator_lines": [
                    "Their energy reserves, already depleted, have entered a deficit.",
                    "The sigh is load-bearing. It supports the weight of seventeen years.",
                    None,
                ],
                "good_options": [
                    ("Nope. That's everything. Thank you.", {"tone": "direct", "intent": "comply", "register": "simple"}, 1, 0),
                    ("Sorry. Let me simplify — I just need this one thing.", {"tone": "direct", "intent": "comply", "register": "simple"}, 1, -1),
                ],
                "bad_options": [
                    ("Actually, one more thing—", {"tone": "formal", "intent": "negotiate", "register": "standard"}, -2, 0),
                    ("I know this is a lot to ask but—", {"tone": "vulnerable", "intent": "negotiate", "register": "standard"}, -1, 0),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "Come back tomorrow.",
                    "System's down.",
                    "My shift ends in five minutes.",
                ],
                "narrator_lines": [
                    "Their shift does not end in five minutes. They wish it did.",
                    None,
                ],
                "good_options": [
                    ("Understood. I'll come back. Have a good night.", {"tone": "direct", "intent": "comply", "register": "simple"}, 0, 0),
                ],
                "bad_options": [
                    ("But I've been waiting for two hours!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 1),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Here. This is what you need. Go to window three. Tell them Maria sent you.",
                    "Done. Next.",
                    "Your form's processed. You can pick it up at the counter.",
                    "I stamped it. Go.",
                ],
                "narrator_lines": [
                    "Efficiency is their love language. You have just been loved.",
                    "The stamp hits the form with the force of someone who wants to be done. You benefit from this wanting.",
                    None,
                ],
                "good_options": [
                    ("Thank you.", {"tone": "direct", "intent": "comply", "register": "simple"}, 1, 0),
                ],
                "bad_options": [
                    ("Wait, can I also ask about—", {"tone": "formal", "intent": "negotiate", "register": "standard"}, -1, 0),
                ],
                "locked_options": [],
            }
        },
        "suspicious": {
            "neutral": {
                "npc_lines": [
                    "And this was on what date?",
                    "You said El Paso. That's interesting. Because your ticket says Tucson.",
                    "Let me see that again. Closer.",
                    "And who told you to come here specifically?",
                    "Hm. Okay. And before that?",
                ],
                "narrator_lines": [
                    "They remember what you said three sentences ago. They remember better than you do.",
                    "A notebook is open. Your name is not the only name in it.",
                    "They tilt their head. It is the tilt of someone triangulating.",
                    None,
                ],
                "good_options": [
                    ("March 12th. I have the bus receipt right here.", {"tone": "direct", "intent": "comply", "register": "standard"}, 2, -1),
                    ("The shelter coordinator on Elm Street. Her name is Patricia Reyes.", {"tone": "formal", "intent": "comply", "register": "standard"}, 2, -1),
                    ("I can show you the confirmation email if you have a printer.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, -1),
                ],
                "bad_options": [
                    ("I don't remember exactly.", {"tone": "indirect", "intent": "deflect", "register": "simple"}, -2, 2),
                    ("Why does it matter?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 2),
                    ("Trust me, I was there.", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -2, 2),
                ],
                "locked_options": [
                    ("Here's my itinerary with dates, my hotel receipt with matching dates, and a signed letter from the host at each stop.", {"tone": "formal", "intent": "comply", "register": "fluent"}, 2, -2),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "That doesn't match what you said two minutes ago.",
                    "So you expect me to believe—",
                    "I've heard a lot of stories. This one has... gaps.",
                    "Let's try this again. From the beginning. Slowly.",
                ],
                "narrator_lines": [
                    "They have found the thread. They are pulling it.",
                    "The notebook page turns. A fresh page. More room for contradictions.",
                    None,
                ],
                "good_options": [
                    ("You're right — I misspoke. Let me correct that with the actual receipt.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, -1),
                    ("Here. Check the date yourself. I'll wait.", {"tone": "direct", "intent": "comply", "register": "standard"}, 1, -1),
                ],
                "bad_options": [
                    ("You're twisting my words!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("Please, you have to believe me.", {"tone": "vulnerable", "intent": "negotiate", "register": "simple"}, -1, 1),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "Your story doesn't add up. We're done here.",
                    "I've heard enough.",
                    "Someone from the office will follow up with you. Don't leave the area.",
                ],
                "narrator_lines": [
                    "The notebook closes with a sound like a verdict.",
                    None,
                ],
                "good_options": [
                    ("I understand. I have additional documentation at my lodging. Can I bring it tomorrow?", {"tone": "formal", "intent": "negotiate", "register": "standard"}, 0, 0),
                ],
                "bad_options": [
                    ("You're wrong about me!", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Okay. That checks out.",
                    "Your story holds. I've verified what I can.",
                    "Clean. You can go.",
                    "Everything matches. Here's your receipt. Keep it — I would.",
                ],
                "narrator_lines": [
                    "The tension leaves their shoulders. You did not know they were tense until the tension left.",
                    "They hand you something. It is trust, in paper form.",
                    None,
                ],
                "good_options": [
                    ("Thank you for checking. I know that's your job and you do it well.", {"tone": "formal", "intent": "comply", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Told you so.", {"tone": "direct", "intent": "challenge", "register": "simple"}, -1, 1),
                ],
                "locked_options": [],
            }
        },
        "empathetic": {
            "neutral": {
                "npc_lines": [
                    "How are you doing? And I mean — how are you really doing?",
                    "You look tired. When did you last eat?",
                    "It's okay. Take your time. There's no rush here.",
                    "You don't have to explain everything. Just tell me what you need.",
                ],
                "narrator_lines": [
                    "They see you. Not your documents. Not your form. You.",
                    "A box of tissues sits on the counter. It is always there. It is always needed.",
                    "The granola bar they're offering you is from a drawer that has seen more grief than any filing cabinet.",
                    None,
                ],
                "good_options": [
                    ("Honestly? I'm terrified. I don't know if I'm going to make it.", {"tone": "vulnerable", "intent": "reveal", "register": "standard"}, 2, 0),
                    ("I haven't slept properly in four days. I'm running on fear.", {"tone": "vulnerable", "intent": "reveal", "register": "standard"}, 2, -1),
                    ("*eyes well up* I'm sorry. I didn't expect someone to ask.", {"tone": "vulnerable", "intent": "reveal", "register": "simple"}, 2, -1),
                ],
                "bad_options": [
                    ("I'm fine. Just need the form processed.", {"tone": "direct", "intent": "deflect", "register": "standard"}, -2, 0),
                    ("Let's keep this professional.", {"tone": "formal", "intent": "deflect", "register": "formal"}, -2, 0),
                    ("I'm great, actually! Everything's great!", {"tone": "humorous", "intent": "deflect", "register": "standard"}, -1, 0),
                ],
                "locked_options": [
                    ("I left my daughter with my mother. She's three. She thinks I'm coming back next week. I'm not coming back next week.", {"tone": "vulnerable", "intent": "reveal", "register": "fluent"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "You don't have to do that with me. The brave face.",
                    "I asked how you are, not how you want me to think you are.",
                    "It's okay to not be okay here.",
                    "I can see you're performing. You don't need to.",
                ],
                "narrator_lines": [
                    "They can see through the mask. They're not judging the mask. They're wondering about the face underneath.",
                    "The tissues are closer now. They were moved without you noticing.",
                    None,
                ],
                "good_options": [
                    ("You're right. I'm sorry. I just — I don't usually talk about this.", {"tone": "vulnerable", "intent": "reveal", "register": "standard"}, 2, -1),
                    ("I'm scared. That's the truth.", {"tone": "vulnerable", "intent": "reveal", "register": "simple"}, 2, -1),
                ],
                "bad_options": [
                    ("I said I'm fine.", {"tone": "direct", "intent": "deflect", "register": "standard"}, -2, 0),
                    ("Can we just do the paperwork?", {"tone": "direct", "intent": "comply", "register": "standard"}, -1, 0),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "Alright. If you don't want to talk, we'll just do the forms.",
                    "I can only help people who want to be helped.",
                    "Okay. Let's just get you processed.",
                ],
                "narrator_lines": [
                    "The warmth leaves. Not with anger — with a door closing softly.",
                    "The tissues have been put away. The drawer closes.",
                    None,
                ],
                "good_options": [
                    ("Wait — I'm sorry. I'm not used to kindness. It makes me suspicious, which says everything.", {"tone": "vulnerable", "intent": "reveal", "register": "standard"}, 2, 0),
                ],
                "bad_options": [
                    ("Good. That's what I wanted.", {"tone": "direct", "intent": "comply", "register": "standard"}, -1, 0),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "I'm going to help you. And I need you to let me.",
                    "Here's what we're going to do. Together.",
                    "I know someone. They helped me once, when I needed it. I'm going to call them.",
                    "Take the granola bar. Take two. And here — this is the number for the shelter on 5th.",
                ],
                "narrator_lines": [
                    "The help is real. It costs them something. They give it anyway.",
                    "They write a number on a Post-it. Their handwriting shakes slightly. The weight of other people's lives is heavy.",
                    None,
                ],
                "good_options": [
                    ("I don't know how to thank you. Nobody's been this kind.", {"tone": "warm", "intent": "connect", "register": "standard"}, 1, 0),
                ],
                "bad_options": [
                    ("Okay, what's the catch?", {"tone": "direct", "intent": "challenge", "register": "standard"}, -1, 0),
                ],
                "locked_options": [],
            }
        },
        "corrupt": {
            "neutral": {
                "npc_lines": [
                    "What can I do for you? Officially, I mean.",
                    "The process usually takes about three weeks. Usually.",
                    "Some things move faster than others. Depends on... factors.",
                    "I can't promise anything, of course. But I know people.",
                ],
                "narrator_lines": [
                    "The pause after 'factors' contains an entire economy.",
                    "Their desk has two trays. One is labeled 'IN.' The other is labeled nothing. It processes faster.",
                    "The security camera in the corner has a convenient blind spot. It wasn't always blind.",
                    None,
                ],
                "good_options": [
                    ("I really appreciate people who can make things work.", {"tone": "indirect", "intent": "negotiate", "register": "standard"}, 2, -1),
                    ("Three weeks is a long time. I wonder if there's a way to... expedite.", {"tone": "indirect", "intent": "negotiate", "register": "standard"}, 2, 0),
                    ("*places envelope on counter, slides it forward an inch*", {"tone": "indirect", "intent": "negotiate", "register": "simple"}, 1, 0),
                ],
                "bad_options": [
                    ("How much to skip the line?", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -2, 2),
                    ("I'll pay you to speed this up.", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -2, 2),
                    ("Everyone says you take bribes.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [
                    ("I was told by a friend that sometimes the process has... unofficial channels. I respect the discretion required.", {"tone": "indirect", "intent": "negotiate", "register": "fluent"}, 2, -1),
                ],
            },
            "suspicious": {
                "npc_lines": [
                    "I don't know what you're implying.",
                    "That's... not how we operate here.",
                    "I think there's been a misunderstanding about what I meant.",
                    "Perhaps you should go through the normal channels.",
                ],
                "narrator_lines": [
                    "The outrage is theatrical. Real innocence doesn't practice its lines.",
                    "The unlabeled tray is now behind a stack of folders. Hidden. Not gone.",
                    None,
                ],
                "good_options": [
                    ("Of course. My mistake. I'm sure the normal process works perfectly. I'll wait the three weeks.", {"tone": "indirect", "intent": "deflect", "register": "standard"}, 1, -1),
                    ("You're right, I misspoke. I just meant — I've heard you're the person who gets things done around here.", {"tone": "indirect", "intent": "negotiate", "register": "standard"}, 1, -1),
                ],
                "bad_options": [
                    ("Come on, everyone knows how this works.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                    ("Fine, I'll tell everyone about the 'expediting.'", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "hostile": {
                "npc_lines": [
                    "I'm going to have to report this conversation.",
                    "I think you should leave. Now.",
                    "That's a serious accusation. I hope you have evidence.",
                ],
                "narrator_lines": [
                    "The threat is not empty. Your deniability just became their weapon.",
                    None,
                ],
                "good_options": [
                    ("I apologize completely. There was no conversation. I was never here.", {"tone": "indirect", "intent": "deflect", "register": "standard"}, 0, 0),
                ],
                "bad_options": [
                    ("Go ahead. Report it. I'll report what I know too.", {"tone": "direct", "intent": "challenge", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            },
            "cooperative": {
                "npc_lines": [
                    "Leave it on the counter. I'll take care of the rest.",
                    "There's a door on the left. It'll be unlocked in five minutes.",
                    "Your paperwork will be processed by morning. Don't ask how.",
                    "I don't know you. You don't know me. This didn't happen.",
                ],
                "narrator_lines": [
                    "Nothing was said. Everything was understood. The form moves from one tray to the other.",
                    "The security camera blinks. In the blind spot, the world rearranges itself.",
                    None,
                ],
                "good_options": [
                    ("*nods once* Thank you. I was never here.", {"tone": "indirect", "intent": "comply", "register": "simple"}, 1, 0),
                ],
                "bad_options": [
                    ("Can I get a receipt for that?", {"tone": "direct", "intent": "negotiate", "register": "standard"}, -2, 2),
                ],
                "locked_options": [],
            }
        }
    }


# AWG analysis templates by archetype — surface quotes will reference exact NPC lines
AWG_TEMPLATES = {
    "control-seeking": {
        "actual_templates": [
            "They're testing whether you'll resist — because the last three people did and they're bracing for the fourth.",
            "The command isn't about the task. It's about confirming they still have authority after someone challenged it yesterday.",
            "Every directive is a loyalty check disguised as paperwork.",
            "They need you to comply not because the rules require it but because their sense of self requires it.",
            "The pause before speaking isn't thinking. It's making you wait. The waiting is the power.",
        ],
        "tell_templates": [
            "They repeat your last phrase back to you — that's the control slipping.",
            "Their voice drops half a register when they feel authority threatened.",
            "They touch their badge when uncertain. Grounding in symbols of power.",
            "The pen hasn't written anything. It's a prop. The prop does the work.",
            "They look at the door before they look at you. Exits before people.",
        ],
        "recommendation_templates": [
            "Match their stillness. Don't move until they move. Produce documentation before they ask.",
            "Wait to be spoken to. Use formal register. Treat their silence as instruction.",
            "Comply first, negotiate later. Let them feel the control before you make your request.",
            "Use their name and title. Let them finish speaking. Don't fill their silences.",
        ],
    },
    "lonely": {
        "actual_templates": [
            "The oversharing isn't carelessness — it's a test. Will you receive what they're offering or brush past it?",
            "They mentioned the cat because they need you to ask about the cat. The cat is the door.",
            "The extra detail isn't relevant to your case. It's relevant to their day, which has been very quiet.",
            "They keep talking because the silence after you leave will be louder.",
            "The personal detail was an offering. Rejecting it closes a door you didn't know was open.",
        ],
        "tell_templates": [
            "Their response time doubles when you ask about their life. They're savoring having an audience.",
            "Watch for the story they tell twice — the repetition reveals who they're really thinking about.",
            "When you check your phone, they reorganize something. Keeping busy to hide the sting.",
            "The warmth drops like a curtain falling the moment you go transactional.",
        ],
        "recommendation_templates": [
            "Ask about the personal detail they dropped. They mentioned it for a reason.",
            "Share something about your own life first. Reciprocity is the key.",
            "Slow down. Don't check the time. Let the conversation breathe.",
            "Remember what they told you. Reference it later. They're listening for proof you were listening.",
        ],
    },
    "greedy": {
        "actual_templates": [
            "They calculated your net worth before you finished your first sentence. The friendliness is pricing, not warmth.",
            "The 'what've you got' isn't aggressive — it's diagnostic. They're figuring out the transaction parameters.",
            "Every favor has a mental invoice. They're not greedy — they're terrified of giving without getting.",
            "The price went up because you hesitated. Hesitation is a signal that you'd pay more.",
            "They look at your bag because your bag is the opening offer in a negotiation you didn't start.",
        ],
        "tell_templates": [
            "Their eyes move to your hands before they move to your face. The hands reveal what the face hides.",
            "The smile reaches their eyes only when numbers are involved.",
            "They name a higher price when they sense desperation. The recalibration is real-time.",
            "Watch for the glance at the door — they're checking if a better deal just walked in.",
        ],
        "recommendation_templates": [
            "Lead with value. Show what you're offering before asking what you need.",
            "Be specific about the exchange. Ambiguity is their enemy and yours.",
            "Don't appeal to morality — appeal to mutual benefit. Frame it as a deal, not a favor.",
            "Name the trade explicitly. Clarity accelerates trust in transactional relationships.",
        ],
    },
    "paranoid": {
        "actual_templates": [
            "They ask three times not because they forgot but because they're checking if your answer changes.",
            "The request for papers isn't bureaucracy — it's anxiety. Documentation is their security blanket.",
            "They need your story to be airtight not because they're hostile but because uncertainty is unbearable.",
            "The stillness they require from you is the stillness they can't find in their own mind.",
            "Every question is a stress test. They're not interrogating you — they're trying to stop being afraid.",
        ],
        "tell_templates": [
            "They touch their own badge when anxiety spikes. Grounding in proof of their own authority.",
            "The pen moves to paper when they sense a discrepancy. The writing isn't notes — it's evidence.",
            "They position themselves between you and the exit. Not threateningly. Instinctively.",
            "Watch when they check the camera. It's when they feel most exposed.",
        ],
        "recommendation_templates": [
            "Be boringly consistent. Say the same thing the same way every time.",
            "Provide documentation before they ask. Anticipate the verification need.",
            "Move slowly. Announce what you're doing before you do it. No surprises.",
            "Stay physically still. Sudden movements trigger the alarm system, not the thinking brain.",
        ],
    },
    "bored": {
        "actual_templates": [
            "The phone scrolling isn't disrespect — it's life support. They're drowning in routine and you look like more of it.",
            "The flat affect isn't their personality. It's the scar tissue from processing ten thousand of you.",
            "They're not hostile. They're waiting for a reason to care. You haven't given them one yet.",
            "The sudden engagement isn't about you — it's about them. You broke the pattern. Breaking the pattern is oxygen.",
            "That 'yeah' isn't agreement. It's the sound of someone who stopped listening forty people ago.",
        ],
        "tell_templates": [
            "Their response time changes from four seconds to instant. The speed IS the signal.",
            "The phone goes face-down. That's the highest compliment they have.",
            "Their posture shifts when engaged — from slouched to leaning forward. The body says what the words don't.",
            "Watch for the unprompted information. They share rules they shouldn't because you earned their attention.",
        ],
        "recommendation_templates": [
            "Surprise them. Say something they haven't heard today — or this year.",
            "Don't be compliant. Compliance is invisible to them. Be interesting.",
            "Lean into the absurd. Tell them why you're really here. The truth is usually weirder than the cover story.",
            "If they ask you to repeat something, double down. They're interested, not confused.",
        ],
    },
    "ideological": {
        "actual_templates": [
            "The loaded phrase is a loyalty test. They need to know which team you're on before they'll help the person.",
            "The certainty is armor. Underneath it is a specific event they never talk about that changed everything.",
            "They don't want to debate. They want a mirror. The ideology is identity, not logic.",
            "The 'people like you' isn't about you at all. It's about the category they've built to make the world manageable.",
            "The generosity for allies is real. So is the hostility for outsiders. Both come from the same wound.",
        ],
        "tell_templates": [
            "Absolute language increases under pressure. 'Always' and 'never' are the cracks showing.",
            "They use 'we' when you agree and 'they' when you don't. The pronoun is the border.",
            "The volume rises on topics they're least certain about. Loudness covers doubt.",
            "Watch for the phrase they repeat. The repetition is the anxiety.",
        ],
        "recommendation_templates": [
            "Echo their language back to them. The words are the key, not the meaning.",
            "Find a secondary value you genuinely share. You don't need to agree on everything.",
            "Don't correct facts. It registers as an attack on identity, not a gift of information.",
            "Nod at the right moments. Timing your agreement matters more than the content of it.",
        ],
    },
    "guilty": {
        "actual_templates": [
            "The preemptive defense is the confession. They're telling you what they did by telling you why it's not their fault.",
            "They're not justifying to you. They're justifying to themselves. You're the latest audience for a very old script.",
            "The deflection is the map. Whatever they change the subject from is where the guilt lives.",
            "The hostility is projection. They're accusing you of judging them because they're judging themselves.",
            "The help they offer costs them something — and that's the point. The cost is the penance.",
        ],
        "tell_templates": [
            "They bring up the topic they feel guilty about without being asked. The unprompted mention is the tell.",
            "The almost-confessions: sentences that approach the truth and swerve at the last second.",
            "They look at the photo on the desk when they think you're not watching. The photo is connected to the guilt.",
            "Watch for the qualifier: 'Not that it matters, but—' Everything after 'but' matters.",
        ],
        "recommendation_templates": [
            "Don't ask why. Don't probe. Offer space, not interrogation.",
            "Share your own compromise. Mutual vulnerability creates safety.",
            "Let contradictions pass uncommented. They know about the contradictions. You noticing them doesn't help.",
            "Offer absolution through example: 'We all do what we have to do.' No moral language.",
        ],
    },
    "ambitious": {
        "actual_templates": [
            "The name-dropping isn't bragging — it's proof of existence. They need you to confirm they matter.",
            "The unsolicited autobiography is a pitch. They're selling themselves because they're not sure the sale closed.",
            "They help from a position of power not because they're generous but because generosity from above confirms the hierarchy.",
            "The title usage increases when they feel small. The formal language is scaffolding for a fragile self-image.",
            "The dismissal of your request isn't about your request. It's about maintaining the gap between your level and theirs.",
        ],
        "tell_templates": [
            "Response length doubles when the topic shifts to their accomplishments. Word count IS the signal.",
            "They mention their title within the first three exchanges. Earlier if they feel unrecognized.",
            "The posture changes when they feel important — chin up, shoulders back. When dismissed, everything deflates.",
            "They give advice that's really autobiography. The 'you should' is really 'I did.'",
        ],
        "recommendation_templates": [
            "Ask for their advice. Frame them as the expert. The question IS the flattery.",
            "Reference their specific achievements — not generic praise. Specific beats sincere.",
            "Make them feel like helping you is an executive decision, not a clerical one.",
            "Express gratitude loudly. The audience matters as much as the message.",
        ],
    },
    "burned-out": {
        "actual_templates": [
            "The monosyllables aren't rudeness. They're conservation. Every word costs energy they don't have.",
            "The efficiency isn't about you. It's about making you go away so they can exist in quiet.",
            "They used to care. The Employee of the Month plaque is evidence. Something between then and now burned it all away.",
            "The 'come back tomorrow' isn't bureaucracy. It's a human being reaching the end of their capacity and hoping you'll be someone else's problem.",
            "When they help, it's fast — because speed means fewer interactions and fewer interactions means survival.",
        ],
        "tell_templates": [
            "Response time is instant for simple requests and infinite for complex ones. The delay IS the answer.",
            "Energy appears briefly when the path to done with you is clear. The efficiency IS the warmth.",
            "They look at the clock not to track time but to count down to escape.",
            "The sigh carries the weight of every case that was exactly like yours. You are the ten thousandth.",
        ],
        "recommendation_templates": [
            "Be brief. One sentence. One request. One form. Zero follow-ups.",
            "Do the work for them. Fill out your own paperwork. Have the exact change.",
            "Don't ask how they're doing. Don't add emotional labor to their stack.",
            "Make yourself the easiest person they'll deal with today. That's the kindness they need.",
        ],
    },
    "suspicious": {
        "actual_templates": [
            "The casual question is a precision instrument. Every word was chosen. Every pause is diagnostic.",
            "They're not hostile — they're cross-referencing. Your story is being checked against a mental database of every lie they've cataloged.",
            "The inconsistency they found might not matter to you. It matters to them because truth is the only currency they accept.",
            "They quote you to yourself because the test is consistency, and consistency can't be faked over time.",
            "The pause before responding isn't thinking. It's verification. The pause length reveals whether you passed.",
        ],
        "tell_templates": [
            "Response delay correlates inversely with belief. Quick reply means they buy it. Long pause means you're flagged.",
            "They repeat your specific words back. Not paraphrasing — quoting. The precision is the suspicion.",
            "The notebook appears when they find a discrepancy. The notebook IS the suspicion.",
            "They look at your hands when you answer. People's hands do the lying the face won't.",
        ],
        "recommendation_templates": [
            "Provide specifics unprompted. Names, dates, document numbers. Proof, not feelings.",
            "Be consistent. Say the same thing the same way if asked twice. Verbatim consistency builds trust.",
            "Don't charm them. Charm is what liars use. Be boring. Be verifiable.",
            "If you made an error, correct it immediately with evidence. The self-correction builds more trust than the original claim.",
        ],
    },
    "empathetic": {
        "actual_templates": [
            "The second 'really' in 'how are you really' isn't a question. It's an invitation to stop performing.",
            "They're not watching for lies. They're watching for walls. The mask you wear is visible to them.",
            "The warmth isn't naive. They've heard everything. They choose warmth knowing exactly what it costs.",
            "When the warmth withdraws, it's not anger — it's grief. They grieve the connection you won't allow.",
            "The tissues aren't for emergencies. They're for the daily reality that everyone who sits across from them is carrying something.",
        ],
        "tell_templates": [
            "They mirror your body language when they trust you. The mirroring stops when they sense performance.",
            "The silence they leave isn't awkward — it's space. They're giving you room to be honest.",
            "They offer food before they offer help. The granola bar is the test. Will you accept care?",
            "Watch their hands — still and open when engaged, busy with objects when they've closed down.",
        ],
        "recommendation_templates": [
            "Drop the mask. Say the true thing. 'I'm scared' works. 'I'm fine' doesn't.",
            "Accept what they offer — the tissue, the food, the silence. Accepting is the door.",
            "Don't perform strength. They see through it and the performance pushes them away.",
            "Be specific about your vulnerability. 'I'm struggling' is vague. 'I haven't slept in four days' is real.",
        ],
    },
    "corrupt": {
        "actual_templates": [
            "The pause after 'factors' is the offer. Everything before the pause was the brochure. Everything after is the price list.",
            "They can't say what they mean because saying it out loud would make it real. The indirection IS the communication.",
            "The outrage when you're too direct is theatrical — real innocence doesn't need that much staging.",
            "The unlabeled tray processes faster because the unlabeled tray has no paperwork trail.",
            "They're not evil. They're pragmatic. The system creates the gap. They just built a business in it.",
        ],
        "tell_templates": [
            "The things they DON'T say are the message. The conspicuous silence is the offer.",
            "Watch for the pause after you mention money. The pause is the price being calculated.",
            "They look at the camera before conducting business. The look IS the tell.",
            "The performance of outrage is inversely proportional to actual innocence. More outrage = more corruption.",
        ],
        "recommendation_templates": [
            "Speak in implications, never in statements. 'I appreciate people who make things work' — never 'how much?'",
            "Give them deniability. The cover story protects both of you. They need to not have heard what you said.",
            "Never name the transaction. The moment you say 'bribe' or 'payment' the deal is dead and you're a threat.",
            "Read the silence. When they stop talking, that's your cue. The silence is the handshake.",
        ],
    },
}


# ============================================================
# GENERATOR
# ============================================================

def seed_rng(archetype: str, location: str, index: int):
    """Create deterministic seed from archetype + location + index."""
    seed_str = f"{archetype}:{location}:{index}"
    seed = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    return random.Random(seed)


def pick_appearance(rng):
    """Generate a 2-3 sentence appearance description."""
    details = rng.sample(APPEARANCE_DETAILS, 2)
    return f"{details[0].capitalize()}. {details[1].capitalize()}."


def generate_awg(rng, archetype_id, npc_line, emotional_state, gap_categories, dialogue_pools):
    """Generate AWG analysis that references the exact NPC line."""
    templates = AWG_TEMPLATES[archetype_id]

    # Pick gap category from archetype's pool
    gap_cat = rng.choice(gap_categories)

    # Surface quotes exact NPC words
    # Extract a meaningful phrase from the NPC line
    surface = f'"{npc_line}"'

    actual = rng.choice(templates["actual_templates"])
    tell = rng.choice(templates["tell_templates"])
    recommendation = rng.choice(templates["recommendation_templates"])
    bridge_rel = rng.choice(BRIDGE_RELATIONSHIPS)
    bridge_line = f"This is how your {bridge_rel} works too."
    closer = rng.choice(AWG_CLOSERS)

    return {
        "gap_category": gap_cat,
        "surface": surface,
        "actual": actual,
        "tell": tell,
        "recommendation": recommendation,
        "bridge_line": bridge_line,
        "closer": closer
    }


def generate_dialogue_tree(rng, npc_id, archetype_id, gap_categories, dialogue_pools):
    """Generate a full dialogue tree with 8 nodes covering all emotional paths."""
    arch_pool = dialogue_pools[archetype_id]
    nodes = []
    node_index = 0

    # Emotional state flow:
    # 1. neutral_opening (initial)
    # 2. neutral_continuation
    # 3. suspicious (from neutral)
    # 4. hostile (from suspicious)
    # 5. cooperative_from_neutral (good path from neutral)
    # 6. cooperative_from_suspicious (recovery path)
    # 7. cooperative_deepen (final good state)
    # 8. neutral_reset (from cooperative, one more chance)

    state_flow = [
        ("neutral", "initial_greeting", None),
        ("neutral", "rapport < 2 and rapport > -1", None),
        ("suspicious", "rapport <= -1 or suspicion >= 2", None),
        ("hostile", "rapport <= -3 or suspicion >= 4", None),
        ("cooperative", "rapport >= 3", None),
        ("cooperative", "rapport >= 2 and was_suspicious", None),
        ("cooperative", "rapport >= 5 or secret_discovered", None),
        ("neutral", "cooperative_reset", None),
    ]

    for state, trigger, _ in state_flow:
        pool = arch_pool.get(state, arch_pool["neutral"])
        npc_line = rng.choice(pool["npc_lines"])
        narrator_line = rng.choice(pool["narrator_lines"])

        # Build options
        options = []

        # Good options
        good_pool = pool.get("good_options", [])
        if good_pool:
            for text, tags, rap, sus in rng.sample(good_pool, min(2, len(good_pool))):
                next_idx = min(node_index + 1, len(state_flow) - 1)
                # Good options lead toward cooperative
                if state == "neutral":
                    next_idx = 4  # cooperative
                elif state == "suspicious":
                    next_idx = 5  # recovery
                elif state == "cooperative":
                    next_idx = 6  # deepen

                options.append({
                    "text": text,
                    "tags": tags,
                    "rapport_delta": rap,
                    "suspicion_delta": sus,
                    "next_node": f"{npc_id}-node-{next_idx}",
                    "requires_language_skill": None,
                    "requires_occupation": None,
                    "requires_intel": None
                })

        # Bad options
        bad_pool = pool.get("bad_options", [])
        if bad_pool:
            for text, tags, rap, sus in rng.sample(bad_pool, min(2, len(bad_pool))):
                # Bad options lead toward hostile
                if state == "neutral":
                    next_idx = 2  # suspicious
                elif state == "suspicious":
                    next_idx = 3  # hostile
                elif state == "cooperative":
                    next_idx = 7  # reset
                else:
                    next_idx = 3  # hostile

                options.append({
                    "text": text,
                    "tags": tags,
                    "rapport_delta": rap,
                    "suspicion_delta": sus,
                    "next_node": f"{npc_id}-node-{next_idx}",
                    "requires_language_skill": None,
                    "requires_occupation": None,
                    "requires_intel": None
                })

        # Locked option (requires high language skill or specific occupation/intel)
        locked_pool = pool.get("locked_options", [])
        if locked_pool:
            text, tags, rap, sus = rng.choice(locked_pool)
            lock_type = rng.choice(["language", "occupation", "intel"])
            if state in ("neutral", "suspicious"):
                next_idx = 4  # straight to cooperative
            else:
                next_idx = 6  # deepen

            opt = {
                "text": text,
                "tags": tags,
                "rapport_delta": rap,
                "suspicion_delta": sus,
                "next_node": f"{npc_id}-node-{next_idx}",
                "requires_language_skill": 4 if lock_type == "language" else None,
                "requires_occupation": rng.choice(OCCUPATION_KEYWORDS) if lock_type == "occupation" else None,
                "requires_intel": rng.choice(INTEL_IDS[:10]) if lock_type == "intel" else None
            }
            options.append(opt)

        # Generate AWG analysis co-authored with dialogue
        awg = generate_awg(rng, archetype_id, npc_line, state, gap_categories, dialogue_pools)

        node = {
            "node_id": f"{npc_id}-node-{node_index}",
            "emotional_state": state,
            "trigger_condition": trigger,
            "npc_line": npc_line,
            "narrator_line": narrator_line,
            "options": options,
            "awg": awg
        }
        nodes.append(node)
        node_index += 1

    return nodes


def generate_npc(npc_index, archetype_id, location_type, dialogue_pools):
    """Generate a single NPC instance with full dialogue tree and AWG analysis."""
    rng = seed_rng(archetype_id, location_type, npc_index)

    npc_id = f"npc-{str(npc_index).zfill(4)}"
    name = rng.choice(NPC_NAMES[location_type])
    role = rng.choice(ROLES_BY_LOCATION[location_type])
    appearance = pick_appearance(rng)
    motivation = rng.choice(MOTIVATIONS_BY_ARCHETYPE[archetype_id])
    secret = rng.choice(SECRETS_BY_ARCHETYPE[archetype_id])
    gap_categories = ARCHETYPE_GAP_CATEGORIES[archetype_id]

    dialogue_tree = generate_dialogue_tree(rng, npc_id, archetype_id, gap_categories, dialogue_pools)

    return {
        "npc_id": npc_id,
        "archetype_id": archetype_id,
        "name": name,
        "role": role,
        "location_type": location_type,
        "appearance": appearance,
        "motivation": motivation,
        "secret": secret,
        "dialogue_tree": dialogue_tree
    }


def validate_npc(npc):
    """Validate a single NPC against the schema."""
    errors = []
    required_npc = ["npc_id", "archetype_id", "name", "role", "location_type", "dialogue_tree"]
    for f in required_npc:
        if f not in npc:
            errors.append(f"NPC missing field: {f}")

    if "location_type" in npc and npc["location_type"] not in ["border", "transit", "mid_america", "nyc_outer", "coney_island"]:
        errors.append(f"Invalid location_type: {npc['location_type']}")

    valid_archetypes = [
        "control-seeking", "lonely", "greedy", "paranoid", "bored", "ideological",
        "guilty", "ambitious", "burned-out", "suspicious", "empathetic", "corrupt"
    ]
    if "archetype_id" in npc and npc["archetype_id"] not in valid_archetypes:
        errors.append(f"Invalid archetype_id: {npc['archetype_id']}")

    if "dialogue_tree" in npc:
        for node in npc["dialogue_tree"]:
            node_errors = validate_dialogue_node(node)
            errors.extend(node_errors)

    return errors


def validate_dialogue_node(node):
    """Validate a dialogue node."""
    errors = []
    required = ["node_id", "emotional_state", "trigger_condition", "npc_line", "options", "awg"]
    for f in required:
        if f not in node:
            errors.append(f"Node {node.get('node_id', '?')} missing: {f}")

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
        if len(node["options"]) < 1:
            errors.append(f"Node {node.get('node_id', '?')} has no options")
        for i, opt in enumerate(node["options"]):
            for f in ["text", "tags", "rapport_delta", "suspicion_delta"]:
                if f not in opt:
                    errors.append(f"Option {i} in {node.get('node_id', '?')} missing: {f}")
            if "tags" in opt:
                for tf in ["tone", "intent", "register"]:
                    if tf not in opt["tags"]:
                        errors.append(f"Option {i} tags missing: {tf}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Generate NPC instances for subtext.game")
    parser.add_argument("--count", type=int, default=120,
                        help="Total NPC count (distributed across archetypes × locations)")
    args = parser.parse_args()

    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    # Load dialogue pools
    dialogue_pools = build_dialogue_pools()

    archetypes = list(ARCHETYPE_GAP_CATEGORIES.keys())
    locations = list(ROLES_BY_LOCATION.keys())

    # Distribute NPCs: 2 per archetype × location = 120 minimum
    combos = [(a, l) for a in archetypes for l in locations]  # 60 combos
    npcs_per_combo = max(2, args.count // len(combos))
    total_target = npcs_per_combo * len(combos)

    print(f"Generating {total_target} NPCs ({npcs_per_combo} per archetype×location combo)...")
    print(f"  {len(archetypes)} archetypes × {len(locations)} locations = {len(combos)} combos")

    all_npcs = []
    npc_index = 0
    errors_total = 0

    for archetype_id, location_type in combos:
        for i in range(npcs_per_combo):
            npc = generate_npc(npc_index, archetype_id, location_type, dialogue_pools)
            errors = validate_npc(npc)
            if errors:
                print(f"  ERRORS in {npc['npc_id']}: {errors}")
                errors_total += len(errors)
            all_npcs.append(npc)
            npc_index += 1

    # Distribution stats
    arch_counts = {}
    loc_counts = {}
    for npc in all_npcs:
        arch_counts[npc["archetype_id"]] = arch_counts.get(npc["archetype_id"], 0) + 1
        loc_counts[npc["location_type"]] = loc_counts.get(npc["location_type"], 0) + 1

    total_nodes = sum(len(npc["dialogue_tree"]) for npc in all_npcs)
    total_options = sum(
        len(node["options"])
        for npc in all_npcs
        for node in npc["dialogue_tree"]
    )

    # Save
    output_path = CONTENT_DIR / "npcs.json"
    output_path.write_text(json.dumps(all_npcs, indent=2))

    print(f"\nGenerated {len(all_npcs)} NPCs → {output_path}")
    print(f"  Dialogue nodes: {total_nodes}")
    print(f"  Total options: {total_options}")
    print(f"  Validation errors: {errors_total}")
    print(f"\n  By archetype:")
    for arch in sorted(arch_counts.keys()):
        print(f"    {arch}: {arch_counts[arch]}")
    print(f"\n  By location:")
    for loc in sorted(loc_counts.keys()):
        print(f"    {loc}: {loc_counts[loc]}")

    if errors_total == 0:
        print("\n  ✓ All NPCs valid")
    else:
        print(f"\n  ✗ {errors_total} validation errors found")

    return errors_total


if __name__ == "__main__":
    exit(main())
