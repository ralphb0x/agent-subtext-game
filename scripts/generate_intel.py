#!/usr/bin/env python3
"""Generate 30 intel items with synergy outcome matrix for subtext.game.

Intel items are collectible information fragments that provide gameplay advantages.
When combined (synergies), they unlock special options or outcomes in NPC encounters.
"""

import json
import random
from itertools import combinations

random.seed(42)

# 5 locations from the game
LOCATIONS = ["border", "transit", "mid_america", "nyc_outer", "coney_island"]

# 12 archetypes
ARCHETYPES = [
    "control-seeking", "lonely", "greedy", "paranoid", "bored", "ideological",
    "guilty", "ambitious", "burned-out", "suspicious", "empathetic", "corrupt"
]

# Intel items: each has an ID, name, description, location found, effects on archetypes,
# and flavor text. Items are documents, overheard conversations, objects, observations.

INTEL_ITEMS = [
    # --- BORDER (6 items) ---
    {
        "intel_id": "intel_001",
        "name": "Crumpled Visa Application",
        "description": "Someone else's rejected visa application. The denial reason is circled in red: 'insufficient ties to home country.' The applicant's photo has been torn off.",
        "location_found": "border",
        "category": "document",
        "narrator_line": "The paper smells like the inside of a government envelope. Which is to say, like disappointment with postage.",
        "effects": {
            "control-seeking": {"rapport_delta": 1, "reason": "Proves you understand bureaucratic process"},
            "paranoid": {"suspicion_delta": -1, "reason": "Physical evidence they can verify"},
            "suspicious": {"rapport_delta": 1, "reason": "Unprompted documentation builds credibility"}
        },
        "unlocks_option_tag": "has_visa_knowledge",
        "flavor": "The circled reason tells you more about the officer than the applicant."
    },
    {
        "intel_id": "intel_002",
        "name": "Border Agent's Coffee Order",
        "description": "A sticky note fallen from a clipboard: 'Hector — oat milk latte, NO foam, double shot. DO NOT get the regular milk again.' Written in aggressive capitals.",
        "location_found": "border",
        "category": "overheard",
        "narrator_line": "The lactose intolerance of federal employees is not classified information, but it probably should be.",
        "effects": {
            "control-seeking": {"suspicion_delta": -1, "reason": "Knowing personal details signals you pay attention to hierarchy"},
            "lonely": {"rapport_delta": 1, "reason": "Personal detail creates connection opportunity"},
            "burned-out": {"rapport_delta": 1, "reason": "Acknowledging their humanity costs you nothing and means everything"}
        },
        "unlocks_option_tag": "knows_agent_personal",
        "flavor": "Everyone is somebody between their second and third coffee."
    },
    {
        "intel_id": "intel_003",
        "name": "Shift Change Schedule",
        "description": "A photocopied schedule taped inside a bathroom stall. Someone has drawn a frowning face next to the 2am-10am shift. The 10am-6pm shift has three stars.",
        "location_found": "border",
        "category": "document",
        "narrator_line": "The graffiti underneath reads 'Rodriguez owes me Tuesday.' The debt economy of civil servants operates on a currency no bank recognizes.",
        "effects": {
            "burned-out": {"rapport_delta": 1, "reason": "Mentioning shift timing shows you see them as workers, not obstacles"},
            "control-seeking": {"suspicion_delta": 1, "reason": "Knowing internal schedules implies surveillance"},
            "corrupt": {"rapport_delta": 1, "reason": "Operational knowledge signals you understand how things actually work"}
        },
        "unlocks_option_tag": "knows_schedule",
        "flavor": "The three-star shift is when the vending machine gets refilled."
    },
    {
        "intel_id": "intel_004",
        "name": "Overheard Radio Call",
        "description": "A fragment caught through a closing door: '...tell Martinez the audit team pushed to Thursday. He can relax.' The door closed before you could hear the response.",
        "location_found": "border",
        "category": "overheard",
        "narrator_line": "The distance between Monday and Thursday is four days or one career, depending on what Martinez did.",
        "effects": {
            "paranoid": {"suspicion_delta": -1, "reason": "Knowing about the audit proves you're not part of it"},
            "ambitious": {"rapport_delta": 1, "reason": "Insider knowledge is social currency"},
            "guilty": {"rapport_delta": 1, "reason": "Suggesting you know about institutional pressure without judgment"}
        },
        "unlocks_option_tag": "knows_audit",
        "flavor": "Martinez will not, in fact, relax."
    },
    {
        "intel_id": "intel_005",
        "name": "Religious Medallion",
        "description": "A small Saint Christopher medallion found wedged in a bench seat. Patron saint of travelers. The chain is broken — pulled off, not unclasped.",
        "location_found": "border",
        "category": "object",
        "narrator_line": "Saint Christopher was removed from the official Catholic calendar in 1969. He still shows up for work every day.",
        "effects": {
            "empathetic": {"rapport_delta": 2, "reason": "Shared symbol of human vulnerability"},
            "ideological": {"rapport_delta": 1, "reason": "Religious objects signal shared values"},
            "lonely": {"rapport_delta": 1, "reason": "A lost thing seeking its owner — they relate"}
        },
        "unlocks_option_tag": "has_medallion",
        "flavor": "The broken chain means someone left in a hurry."
    },
    {
        "intel_id": "intel_006",
        "name": "Detention Center Layout Sketch",
        "description": "A hand-drawn map on the back of a commissary receipt. X marks the phone that works. Arrow points to 'camera blind spot (maybe).'",
        "location_found": "border",
        "category": "document",
        "narrator_line": "The question mark after 'maybe' is the most honest piece of cartography you've ever seen.",
        "effects": {
            "suspicious": {"suspicion_delta": -1, "reason": "Showing you've been through the system earns grudging respect"},
            "corrupt": {"rapport_delta": 1, "reason": "Knowledge of blind spots implies useful discretion"},
            "control-seeking": {"suspicion_delta": 2, "reason": "Possessing this marks you as a flight risk"}
        },
        "unlocks_option_tag": "knows_layout",
        "flavor": "Every institution has a map its architects didn't draw."
    },

    # --- TRANSIT HUB (6 items) ---
    {
        "intel_id": "intel_007",
        "name": "Bus Driver's Union Card",
        "description": "Found under seat 14C. Expired last month. The photo shows a man who has driven the same route so long his face has become the landscape.",
        "location_found": "transit",
        "category": "document",
        "narrator_line": "Local 1181. The '1' stands for the one bathroom break per eight-hour shift.",
        "effects": {
            "burned-out": {"rapport_delta": 2, "reason": "Union solidarity is the last religion of the exhausted"},
            "ideological": {"rapport_delta": 1, "reason": "Labor affiliation signals political alignment"},
            "greedy": {"suspicion_delta": -1, "reason": "Proves you understand the value of credentials"}
        },
        "unlocks_option_tag": "has_union_card",
        "flavor": "An expired card still opens some doors. Just not the ones with locks."
    },
    {
        "intel_id": "intel_008",
        "name": "Overheard Phone Call — Spanish",
        "description": "A woman on the phone, crying quietly: 'Tell mama I'm fine. Tell her the bus is nice. Don't tell her about the man in Dallas.' She hung up before saying which man.",
        "location_found": "transit",
        "category": "overheard",
        "narrator_line": "The things we ask people not to say become the only things worth knowing.",
        "effects": {
            "empathetic": {"rapport_delta": 1, "reason": "Shared migrant experience creates instant trust"},
            "lonely": {"rapport_delta": 1, "reason": "You heard someone's truth — you can be trusted with theirs"},
            "paranoid": {"suspicion_delta": 1, "reason": "You were listening. Why were you listening?"}
        },
        "unlocks_option_tag": "heard_spanish_call",
        "flavor": "The man in Dallas is everyone's man in Dallas."
    },
    {
        "intel_id": "intel_009",
        "name": "Greyhound Route Map (Annotated)",
        "description": "A standard route map with handwritten notes: 'checkpoint here,' 'safe Walmart,' 'avoid Tulsa bus station after 9pm,' 'church = food Tues/Thurs.'",
        "location_found": "transit",
        "category": "document",
        "narrator_line": "This is the other America: the one drawn in ballpoint pen by people who can't afford to be wrong about Tuesday.",
        "effects": {
            "suspicious": {"rapport_delta": 1, "reason": "Detailed local knowledge proves you're a real traveler"},
            "paranoid": {"suspicion_delta": -1, "reason": "Sharing escape routes shows you're not a threat"},
            "control-seeking": {"suspicion_delta": 1, "reason": "Detailed movement planning implies evasion"}
        },
        "unlocks_option_tag": "has_route_map",
        "flavor": "The safe Walmart is in Amarillo. It has a 24-hour parking lot and a security guard named Deb who looks the other way."
    },
    {
        "intel_id": "intel_010",
        "name": "Prepaid Phone (Dead Battery)",
        "description": "A burner phone with a cracked screen, found in a seat pocket. Dead battery. The last text visible before it died: 'Bus 2847. Blue jacket. He's good.'",
        "location_found": "transit",
        "category": "object",
        "narrator_line": "Someone vouched for you before you existed. This is either very comforting or very concerning.",
        "effects": {
            "corrupt": {"rapport_delta": 2, "reason": "You're in the network now, whether you wanted to be or not"},
            "suspicious": {"suspicion_delta": -2, "reason": "Third-party vouching is the highest form of proof"},
            "control-seeking": {"suspicion_delta": 1, "reason": "Unknown networks are uncontrolled variables"}
        },
        "unlocks_option_tag": "has_burner_phone",
        "flavor": "The blue jacket could be anyone. That's the point."
    },
    {
        "intel_id": "intel_011",
        "name": "Gas Station Receipt — Wichita",
        "description": "Diesel, two hot dogs, one Gatorade. Paid cash. The timestamp is 3:47am. On the back, in pencil: a phone number and the word 'Carlos.'",
        "location_found": "transit",
        "category": "document",
        "narrator_line": "3:47am purchases tell you everything about a person's week. This one says: moving, hungry, hydrating, and not using a credit card.",
        "effects": {
            "greedy": {"rapport_delta": 1, "reason": "A contact name has transactional value"},
            "ambitious": {"rapport_delta": 1, "reason": "Network connections signal resourcefulness"},
            "lonely": {"rapport_delta": 1, "reason": "Carlos is someone's person. You can be someone's person too."}
        },
        "unlocks_option_tag": "knows_carlos",
        "flavor": "Carlos does not answer calls from numbers he doesn't recognize. You will need to text."
    },
    {
        "intel_id": "intel_012",
        "name": "ICE Checkpoint Warning (Text Chain)",
        "description": "A screenshot printed on copy paper, passed hand to hand: a group text listing checkpoint locations updated hourly. Already eight hours old.",
        "location_found": "transit",
        "category": "document",
        "narrator_line": "Eight hours is either perfectly current or catastrophically outdated. There is no middle ground.",
        "effects": {
            "paranoid": {"rapport_delta": 1, "reason": "Sharing threat intelligence is an act of alliance"},
            "suspicious": {"rapport_delta": 1, "reason": "You have verifiable, specific, actionable information"},
            "ideological": {"rapport_delta": 1, "reason": "Resistance networks signal political alignment"}
        },
        "unlocks_option_tag": "has_checkpoint_intel",
        "flavor": "The text chain has 200 members. None of them have met."
    },

    # --- MID-AMERICA CITY (6 items) ---
    {
        "intel_id": "intel_013",
        "name": "Help Wanted Sign (Cash Only)",
        "description": "Handwritten on neon poster board in a restaurant window: 'DISHWASHER NEEDED. CASH DAILY. NO QUESTIONS.' The 'no questions' is underlined twice.",
        "location_found": "mid_america",
        "category": "observation",
        "narrator_line": "Two underlines is the universal font for 'we know, you know, let's not make this weird.'",
        "effects": {
            "greedy": {"rapport_delta": 1, "reason": "Cash employment signals you understand off-book economics"},
            "corrupt": {"rapport_delta": 1, "reason": "No-questions arrangements are their native language"},
            "burned-out": {"rapport_delta": 1, "reason": "You're just trying to work. They respect that."}
        },
        "unlocks_option_tag": "knows_cash_work",
        "flavor": "The restaurant is called 'American Dream Diner.' The owner is from Puebla."
    },
    {
        "intel_id": "intel_014",
        "name": "Church Bulletin — Spanish Service",
        "description": "Sunday bulletin from First Presbyterian. The English service is at 9am. The Spanish service is at 6pm. The English bulletin is two pages. The Spanish one is six, and includes legal aid numbers.",
        "location_found": "mid_america",
        "category": "document",
        "narrator_line": "The four-page difference between the 9am and 6pm bulletins contains the entire immigration debate.",
        "effects": {
            "empathetic": {"rapport_delta": 1, "reason": "Church community signals shared values of care"},
            "ideological": {"rapport_delta": 1, "reason": "Faith community involvement signals moral alignment"},
            "guilty": {"rapport_delta": 1, "reason": "Churches are where guilt goes to sit down and breathe"}
        },
        "unlocks_option_tag": "has_church_contacts",
        "flavor": "The legal aid number on page four has been circled so many times the paper is worn through."
    },
    {
        "intel_id": "intel_015",
        "name": "Landlord's Business Card",
        "description": "Gerald T. Kowalski, Property Management. On the back, handwritten: '2BR $400/mo. First + last. No lease needed. No inspectors.' The card stock is expensive.",
        "location_found": "mid_america",
        "category": "document",
        "narrator_line": "A man who spends money on card stock but not building inspectors has made a series of very specific financial calculations.",
        "effects": {
            "corrupt": {"rapport_delta": 2, "reason": "You speak the language of arrangements"},
            "greedy": {"rapport_delta": 1, "reason": "Below-market rent implies mutual benefit opportunity"},
            "suspicious": {"suspicion_delta": 1, "reason": "How did you get this? Who gave it to you?"}
        },
        "unlocks_option_tag": "knows_kowalski",
        "flavor": "Gerald's buildings pass inspection the same way Gerald's taxes pass audit: by never being examined."
    },
    {
        "intel_id": "intel_016",
        "name": "Local News Clipping",
        "description": "Headline: 'City Council Votes 4-3 to Continue Sanctuary Policy.' Below the fold: a photo of protesters. One sign reads 'THEY TOOK OUR JOBS.' Another reads 'THEY TOOK OUR HEARTS.' Both protesters look equally angry.",
        "location_found": "mid_america",
        "category": "document",
        "narrator_line": "The 4-3 vote means this city's compassion passes by a single person's margin. That person is Councilwoman Debra Huang, who is up for re-election.",
        "effects": {
            "ideological": {"rapport_delta": 1, "reason": "Knowing local politics signals engagement"},
            "ambitious": {"rapport_delta": 1, "reason": "Political awareness implies strategic thinking"},
            "paranoid": {"suspicion_delta": -1, "reason": "Sanctuary city status is verifiable fact, not claim"}
        },
        "unlocks_option_tag": "knows_sanctuary_policy",
        "flavor": "Councilwoman Huang's margin of victory last time was 47 votes. She is very aware of this number."
    },
    {
        "intel_id": "intel_017",
        "name": "Meatpacking Plant Badge",
        "description": "Employee ID for Heartland Premium Meats. Name: 'Juan Doe.' Employee number: 00847. The photo is clearly not the same person listed on the name.",
        "location_found": "mid_america",
        "category": "object",
        "narrator_line": "Employee number 00847 has had four different faces in two years. HR has noticed zero of them.",
        "effects": {
            "corrupt": {"rapport_delta": 1, "reason": "You understand the system of convenient blindness"},
            "ambitious": {"rapport_delta": 1, "reason": "Employment history, however fictional, shows initiative"},
            "control-seeking": {"suspicion_delta": 1, "reason": "False documents are a control violation"}
        },
        "unlocks_option_tag": "has_fake_id",
        "flavor": "Heartland Premium Meats supplies hot dogs to fourteen states. Including the ones served at Coney Island."
    },
    {
        "intel_id": "intel_018",
        "name": "Motel Room Bible Notes",
        "description": "A Gideon Bible with margin notes in three languages. Page 847 (Psalms): 'If you are reading this in the Super 8 off I-70, the ice machine works but the phone in the lobby does not. God bless. — Maria, Tegucigalpa.'",
        "location_found": "mid_america",
        "category": "observation",
        "narrator_line": "The Psalms have always been a travel guide. Maria just made them more specific.",
        "effects": {
            "empathetic": {"rapport_delta": 2, "reason": "Human kindness is their love language"},
            "lonely": {"rapport_delta": 1, "reason": "Maria left a message for a stranger. You can be that stranger for them."},
            "bored": {"rapport_delta": 1, "reason": "This is genuinely interesting and they appreciate novelty"}
        },
        "unlocks_option_tag": "has_maria_note",
        "flavor": "The ice machine does, in fact, work. Maria was right about everything."
    },

    # --- NYC OUTER BOROUGH (6 items) ---
    {
        "intel_id": "intel_019",
        "name": "Subway Map (Unofficial)",
        "description": "A hand-annotated MTA map. Official stations in black. Handwritten additions in red: 'cops here after 10pm,' 'free transfer walk,' 'bathroom that's actually open.' Queens is heavily annotated. Manhattan is blank.",
        "location_found": "nyc_outer",
        "category": "document",
        "narrator_line": "Manhattan is blank because if you need a map for Manhattan you can afford to get lost there.",
        "effects": {
            "suspicious": {"rapport_delta": 1, "reason": "Local knowledge is the hardest currency to fake"},
            "burned-out": {"rapport_delta": 1, "reason": "You know where the bathroom is. This is huge."},
            "paranoid": {"suspicion_delta": -1, "reason": "Knowing where cops are means you can avoid them — and aren't one"}
        },
        "unlocks_option_tag": "has_subway_map",
        "flavor": "The bathroom that's actually open is at the Steinway Street station. The attendant's name is Paul. He's been there since 1997."
    },
    {
        "intel_id": "intel_020",
        "name": "Day Labor Corner Photo",
        "description": "A polaroid: seven men standing at a street corner at 5:30am, breath visible. Someone has written names on the back. One name is crossed out. No explanation.",
        "location_found": "nyc_outer",
        "category": "object",
        "narrator_line": "The crossed-out name could mean he got a real job, went home, or stopped showing up for a reason no one asks about.",
        "effects": {
            "empathetic": {"rapport_delta": 1, "reason": "You carry proof of people who exist"},
            "guilty": {"rapport_delta": 1, "reason": "The crossed-out name haunts them too"},
            "lonely": {"rapport_delta": 1, "reason": "Seven men at 5:30am is a community. You can be the eighth."}
        },
        "unlocks_option_tag": "knows_day_labor",
        "flavor": "5:30am is early enough to get work and late enough to have had coffee. This is the calculus."
    },
    {
        "intel_id": "intel_021",
        "name": "Restaurant Kitchen Conversation",
        "description": "Overheard through a propped-open kitchen door: 'The inspector comes Thursday. Tell everyone Thursday is their day off. Friday we're open again. Everyone comes back Friday.' Pots clashing. Laughter.",
        "location_found": "nyc_outer",
        "category": "overheard",
        "narrator_line": "The health inspector checks for rats. The other kind of inspector checks for people. Both are scheduled for Thursday.",
        "effects": {
            "corrupt": {"rapport_delta": 2, "reason": "You understand Thursday"},
            "greedy": {"rapport_delta": 1, "reason": "Operational intelligence has cash value"},
            "control-seeking": {"suspicion_delta": 1, "reason": "You know things you shouldn't know about their operation"}
        },
        "unlocks_option_tag": "knows_thursday",
        "flavor": "Thursday is a day of the week and also a lifestyle."
    },
    {
        "intel_id": "intel_022",
        "name": "Immigration Lawyer Flyer",
        "description": "Bilingual flyer: 'FREE CONSULTATION. Asylum, TPS, DACA renewals. Se habla español, créole, العربية.' The lawyer's name is followed by 'Esq.' and also 'formerly undocumented.' Bold choice.",
        "location_found": "nyc_outer",
        "category": "document",
        "narrator_line": "Putting 'formerly undocumented' on your business card is either radical transparency or the most effective marketing in immigration law.",
        "effects": {
            "suspicious": {"rapport_delta": 1, "reason": "A lawyer who discloses their past can be trusted with yours"},
            "paranoid": {"rapport_delta": 1, "reason": "Legal expertise is the ultimate documentation"},
            "ideological": {"rapport_delta": 1, "reason": "This lawyer chose a side. It's the right one."}
        },
        "unlocks_option_tag": "has_lawyer_contact",
        "flavor": "Her win rate is 73%. The national average is 37%. She does not advertise this number because she thinks it would be bragging."
    },
    {
        "intel_id": "intel_023",
        "name": "Bodega Owner's Favor",
        "description": "You bought water. He gave you change for a $20 when you gave him a $10. When you tried to correct him, he said 'I know what you gave me' and turned to the next customer.",
        "location_found": "nyc_outer",
        "category": "observation",
        "narrator_line": "The bodega economy operates on a currency the Federal Reserve doesn't track.",
        "effects": {
            "empathetic": {"rapport_delta": 1, "reason": "Someone showed you unexpected kindness — you carry that now"},
            "greedy": {"rapport_delta": 1, "reason": "Extra cash is extra cash. They respect the hustle."},
            "bored": {"rapport_delta": 1, "reason": "This is the most interesting thing that's happened to them today"}
        },
        "unlocks_option_tag": "has_bodega_story",
        "flavor": "His name is Mahmoud. He's from Aleppo. He's been giving away $10 at a time since 2015."
    },
    {
        "intel_id": "intel_024",
        "name": "7 Train Schedule (Rush Hour)",
        "description": "A printout of the 7 train schedule with highlighted windows: 'Express 7:12, 7:24, 7:36 — no cops in last car. Local after 9 — always cops middle car.' Annotated by someone who rides this train every day.",
        "location_found": "nyc_outer",
        "category": "document",
        "narrator_line": "The last car of the 7:12 express is a republic of people who do not wish to be noticed. It has its own social norms. One of them is silence.",
        "effects": {
            "paranoid": {"suspicion_delta": -2, "reason": "Precise, verifiable safety intelligence — the gold standard"},
            "suspicious": {"rapport_delta": 1, "reason": "You ride the same train. You see the same things."},
            "burned-out": {"rapport_delta": 1, "reason": "You know the system. You don't need to be managed."}
        },
        "unlocks_option_tag": "knows_7_train",
        "flavor": "The 7 train goes from Flushing to Times Square. It is the most diverse subway line in the world. It does not advertise this."
    },

    # --- CONEY ISLAND (6 items) ---
    {
        "intel_id": "intel_025",
        "name": "Nathan's Employee Handbook (Excerpt)",
        "description": "Pages 47-48, found in a trash can behind the boardwalk. Section 12.3: 'Contest participants must sign waiver acknowledging hot dog consumption is voluntary and management is not responsible for outcomes including but not limited to: nausea, fame, existential questioning.'",
        "location_found": "coney_island",
        "category": "document",
        "narrator_line": "The legal team at Nathan's Famous has, at some point, had to define 'existential questioning' for insurance purposes.",
        "effects": {
            "bored": {"rapport_delta": 2, "reason": "This is genuinely hilarious and they are delighted"},
            "ambitious": {"rapport_delta": 1, "reason": "Insider contest knowledge signals preparation"},
            "control-seeking": {"rapport_delta": 1, "reason": "Documentation, even absurd documentation, is still documentation"}
        },
        "unlocks_option_tag": "has_contest_rules",
        "flavor": "Page 49, which is missing, allegedly covers the protocol for ties. No one has ever needed it."
    },
    {
        "intel_id": "intel_026",
        "name": "Last Year's Winner Interview",
        "description": "A torn magazine page. The winner is quoted: 'It's not about the hot dogs. It was never about the hot dogs. It's about proving that the human body is a suggestion, not a rule.' They ate 76.",
        "location_found": "coney_island",
        "category": "document",
        "narrator_line": "76 hot dogs in 10 minutes. The human body is not a suggestion. It is a complaint filed in triplicate.",
        "effects": {
            "ambitious": {"rapport_delta": 2, "reason": "This is aspiration in its purest, most intestinal form"},
            "ideological": {"rapport_delta": 1, "reason": "The winner has a philosophy. It involves condiments."},
            "empathetic": {"rapport_delta": 1, "reason": "The quote is sincere. They meant every word and every hot dog."}
        },
        "unlocks_option_tag": "knows_contest_history",
        "flavor": "The winner retired the next year. They now sell insurance in Paramus, New Jersey."
    },
    {
        "intel_id": "intel_027",
        "name": "Boardwalk Security Rotation",
        "description": "Overheard from two security guards: 'I got the east end today. You got west. Nobody's covering the middle because Dave called in sick again. Dave's always sick on July 3rd.'",
        "location_found": "coney_island",
        "category": "overheard",
        "narrator_line": "Dave's July 3rd illness has a 100% recurrence rate and a 0% investigation rate.",
        "effects": {
            "corrupt": {"rapport_delta": 1, "reason": "Security gaps are operational intelligence"},
            "burned-out": {"rapport_delta": 1, "reason": "Dave is their spirit animal"},
            "paranoid": {"suspicion_delta": -1, "reason": "Sharing security info means you're not security"}
        },
        "unlocks_option_tag": "knows_security_gap",
        "flavor": "Dave is not sick. Dave is in Atlantic City. Everyone knows this. Dave's supervisor also knows this. Dave's supervisor is also in Atlantic City."
    },
    {
        "intel_id": "intel_028",
        "name": "Contest Registration Form",
        "description": "A blank registration form for the amateur division. Requirements: valid ID (any country), signed waiver, $25 entry fee. The amateur division was added in 2019. It has fewer rules than the professional one. Significantly fewer.",
        "location_found": "coney_island",
        "category": "document",
        "narrator_line": "The amateur division accepts ID from any country. The founding fathers would have had opinions about this, but they didn't eat competitively.",
        "effects": {
            "control-seeking": {"rapport_delta": 1, "reason": "Official form. Official process. They approve."},
            "suspicious": {"suspicion_delta": -1, "reason": "Valid ID from any country — your presence is sanctioned"},
            "greedy": {"rapport_delta": 1, "reason": "$25 is a small price for a legitimate reason to be here"}
        },
        "unlocks_option_tag": "has_registration",
        "flavor": "The professional division requires a competitive eating ranking. The amateur division requires $25 and hubris."
    },
    {
        "intel_id": "intel_029",
        "name": "Mustard Stain on a Federal Lanyard",
        "description": "You watched a man in a suit eat a hot dog on the boardwalk. Mustard fell on his DHS lanyard. He looked around. No one saw. You saw. He doesn't know you saw.",
        "location_found": "coney_island",
        "category": "observation",
        "narrator_line": "The distance between federal authority and a mustard stain is exactly one Nathan's Famous original.",
        "effects": {
            "control-seeking": {"suspicion_delta": -2, "reason": "You have something on them. The dynamic has shifted."},
            "bored": {"rapport_delta": 1, "reason": "This is the best thing that's happened all day"},
            "guilty": {"rapport_delta": 1, "reason": "Everyone has a moment they hope nobody witnessed. You're holding theirs gently."}
        },
        "unlocks_option_tag": "saw_mustard_incident",
        "flavor": "He tried to wipe it with his thumb. This made it worse. Authority is fragile."
    },
    {
        "intel_id": "intel_030",
        "name": "Fireworks Logistics Memo",
        "description": "A crumpled memo from Grucci Fireworks to Coney Island Events: 'July 4th setup begins 4am. Perimeter closes 6am. ALL non-crew must be clear of beach staging area by 5:30am. This means you, Kevin.'",
        "location_found": "coney_island",
        "category": "document",
        "narrator_line": "Kevin's relationship with restricted areas is apparently well-documented enough to make it into official logistics.",
        "effects": {
            "ambitious": {"rapport_delta": 1, "reason": "Event logistics signal you're here for the contest, not randomly"},
            "paranoid": {"suspicion_delta": -1, "reason": "Official timing means you can prove where you should be and when"},
            "bored": {"rapport_delta": 2, "reason": "Kevin is their new favorite person and they want to know everything about Kevin"}
        },
        "unlocks_option_tag": "knows_fireworks_schedule",
        "flavor": "Kevin is the Events Director's nephew. Kevin is 34 years old. Kevin still tries to light fireworks himself."
    }
]

# --- SYNERGY OUTCOME MATRIX ---
# When a player has two specific intel items, a synergy bonus unlocks.
# Synergies provide: new dialogue options, resource bonuses, or NPC disposition changes.

SYNERGY_MATRIX = [
    {
        "synergy_id": "syn_001",
        "items": ["intel_001", "intel_004"],
        "name": "Bureaucratic Insider",
        "description": "A rejected visa application + knowledge of the audit gives you the full picture of how this border post operates.",
        "effect": "Unlocks option to reference the audit casually with any control-seeking or paranoid NPC at the border. Rapport +2.",
        "location": "border",
        "tags": ["bureaucracy", "leverage"],
        "narrator_line": "You know more about this office than some of the people who work here. This is either an advantage or a crime."
    },
    {
        "synergy_id": "syn_002",
        "items": ["intel_002", "intel_003"],
        "name": "Shift Whisperer",
        "description": "The coffee order + the shift schedule means you know who's working and how to approach them.",
        "effect": "Any border NPC encounter: suspicion starts 1 point lower. You arrived at the right time and you know Hector's order.",
        "location": "border",
        "tags": ["personal", "timing"],
        "narrator_line": "Arriving during the good shift with the right coffee order is not a strategy. It's a lifestyle."
    },
    {
        "synergy_id": "syn_003",
        "items": ["intel_005", "intel_014"],
        "name": "Pilgrim's Network",
        "description": "The saint's medallion + the church bulletin connects you to a faith-based support network that stretches from the border to the Midwest.",
        "effect": "Unlocks 'church network' dialogue option with empathetic and ideological NPCs. Energy +2 (food and rest from congregation).",
        "location": "any",
        "tags": ["faith", "network"],
        "narrator_line": "The distance between a lost medallion and a church bulletin is one act of faith."
    },
    {
        "synergy_id": "syn_004",
        "items": ["intel_009", "intel_012"],
        "name": "Shadow Navigator",
        "description": "The annotated route map + checkpoint warnings means you can move through transit zones with minimal heat.",
        "effect": "Transit encounters: Heat -1 at start. You know where NOT to be.",
        "location": "transit",
        "tags": ["movement", "safety"],
        "narrator_line": "Two maps: one drawn by Greyhound, one drawn by survival. You're reading the second one."
    },
    {
        "synergy_id": "syn_005",
        "items": ["intel_010", "intel_011"],
        "name": "The Network Knows You",
        "description": "The burner phone vouching for you + Carlos's number means you're connected to the underground transit network.",
        "effect": "Unlocks 'Carlos sent me' option with corrupt and suspicious NPCs in transit or mid_america. Rapport +3 with corrupt NPCs.",
        "location": "transit",
        "tags": ["network", "trust"],
        "narrator_line": "Carlos sent you. You've never met Carlos. Carlos has never met you. This is how trust works when nothing else does."
    },
    {
        "synergy_id": "syn_006",
        "items": ["intel_007", "intel_013"],
        "name": "Working Class Solidarity",
        "description": "A union card + cash work knowledge establishes you as a worker, not a wanderer.",
        "effect": "Mid-America NPCs: burned-out and greedy archetypes start at cooperative instead of neutral.",
        "location": "mid_america",
        "tags": ["labor", "identity"],
        "narrator_line": "You have a union card and calluses. In mid-America, this is a passport."
    },
    {
        "synergy_id": "syn_007",
        "items": ["intel_015", "intel_017"],
        "name": "The Kowalski-Heartland Connection",
        "description": "The landlord's card + the meatpacking badge reveals the local economy's open secret: everyone knows, nobody says.",
        "effect": "Unlocks option to negotiate with corrupt NPCs using specific local knowledge. Money -$50 but Heat -2.",
        "location": "mid_america",
        "tags": ["corruption", "leverage"],
        "narrator_line": "Gerald T. Kowalski rents apartments to people who work at Heartland Premium Meats. Everyone in town knows this. The inspector comes on Thursday."
    },
    {
        "synergy_id": "syn_008",
        "items": ["intel_016", "intel_022"],
        "name": "Legal Shield",
        "description": "Knowledge of sanctuary policy + an immigration lawyer's number is the closest thing to armor in this country.",
        "effect": "Any encounter where Heat would increase by 2+: reduce by 1. You have legal backup and you know your rights in this jurisdiction.",
        "location": "any",
        "tags": ["legal", "protection"],
        "narrator_line": "Knowing your rights doesn't stop anything. But it changes the math for everyone involved."
    },
    {
        "synergy_id": "syn_009",
        "items": ["intel_019", "intel_024"],
        "name": "Ghost Rider",
        "description": "The unofficial subway map + 7 train intelligence means you can move through NYC like someone who's lived here for years.",
        "effect": "NYC encounters: Time cost reduced by 0.5 days. You don't waste time being lost.",
        "location": "nyc_outer",
        "tags": ["navigation", "efficiency"],
        "narrator_line": "You board the 7:12 express, last car. No one speaks. Everyone understands. You've been here ten minutes and you already belong."
    },
    {
        "synergy_id": "syn_010",
        "items": ["intel_020", "intel_023"],
        "name": "Community Voucher",
        "description": "The day labor photo + the bodega owner's favor proves you're embedded in the outer borough community.",
        "effect": "Unlocks 'I'm with the morning crew' option with empathetic and lonely NPCs. Rapport +2.",
        "location": "nyc_outer",
        "tags": ["community", "trust"],
        "narrator_line": "You know the names on the back of the polaroid. Mahmoud gave you extra change. You're not passing through — you're here."
    },
    {
        "synergy_id": "syn_011",
        "items": ["intel_025", "intel_028"],
        "name": "Legitimate Competitor",
        "description": "The employee handbook excerpt + the registration form means you can present yourself as an actual contest participant.",
        "effect": "Coney Island encounters: suspicious and control-seeking NPCs treat you as authorized. Heat cannot exceed 6 at this location.",
        "location": "coney_island",
        "tags": ["legitimacy", "contest"],
        "narrator_line": "You're registered for the amateur hot dog eating contest. You have a number. You have a waiver. You are, technically, supposed to be here."
    },
    {
        "synergy_id": "syn_012",
        "items": ["intel_029", "intel_027"],
        "name": "The Mustard Gambit",
        "description": "You saw the DHS agent's mustard incident + you know security has a gap. Maximum leverage, minimum confrontation.",
        "effect": "Unlocks 'I noticed your...' option with the DHS agent. Suspicion -3. He suddenly needs to be somewhere else.",
        "location": "coney_island",
        "tags": ["leverage", "humor"],
        "narrator_line": "You don't say the word 'mustard.' You don't have to. You both know. He nods. You walk."
    },
    {
        "synergy_id": "syn_013",
        "items": ["intel_006", "intel_019"],
        "name": "Infrastructure Reader",
        "description": "The detention center layout + the subway map — you read buildings and systems like blueprints.",
        "effect": "Any location: unlocks hidden intel items. You notice things other people walk past.",
        "location": "any",
        "tags": ["perception", "systems"],
        "narrator_line": "You see the camera angles, the blind spots, the doors that don't quite close. Institutions are all the same institution."
    },
    {
        "synergy_id": "syn_014",
        "items": ["intel_008", "intel_018"],
        "name": "The Kindness Chain",
        "description": "The overheard Spanish call + Maria's Bible note — you carry the stories of people who carried you.",
        "effect": "Empathetic NPCs: rapport starts at +2 instead of 0. Your stories are their stories.",
        "location": "any",
        "tags": ["humanity", "connection"],
        "narrator_line": "Maria left a note in the Psalms. A woman on a bus said 'don't tell mama.' You carry them both now."
    },
    {
        "synergy_id": "syn_015",
        "items": ["intel_026", "intel_030"],
        "name": "July 4th Insider",
        "description": "Contest history + fireworks logistics. You know the schedule, the stakes, and Kevin.",
        "effect": "Final Coney Island encounters: all archetypes start 1 rapport higher. You're clearly here for the contest.",
        "location": "coney_island",
        "tags": ["endgame", "legitimacy"],
        "narrator_line": "You know the winner ate 76. You know the fireworks start at dusk. You know about Kevin. You are, against all odds, prepared."
    }
]


def validate_intel_item(item):
    """Validate a single intel item against the schema."""
    errors = []
    required_fields = [
        "intel_id", "name", "description", "location_found",
        "category", "narrator_line", "effects", "unlocks_option_tag", "flavor"
    ]
    for field in required_fields:
        if field not in item:
            errors.append(f"{item.get('intel_id', '???')}: missing field '{field}'")

    if item.get("location_found") not in LOCATIONS:
        errors.append(f"{item['intel_id']}: invalid location '{item.get('location_found')}'")

    if item.get("category") not in ["document", "overheard", "object", "observation"]:
        errors.append(f"{item['intel_id']}: invalid category '{item.get('category')}'")

    effects = item.get("effects", {})
    if len(effects) < 2:
        errors.append(f"{item['intel_id']}: needs at least 2 archetype effects, has {len(effects)}")

    for arch, effect in effects.items():
        if arch not in ARCHETYPES:
            errors.append(f"{item['intel_id']}: invalid archetype '{arch}' in effects")
        if "reason" not in effect:
            errors.append(f"{item['intel_id']}: effect for '{arch}' missing 'reason'")
        if "rapport_delta" not in effect and "suspicion_delta" not in effect:
            errors.append(f"{item['intel_id']}: effect for '{arch}' needs rapport_delta or suspicion_delta")

    return errors


def validate_synergy(synergy):
    """Validate a single synergy entry."""
    errors = []
    required_fields = [
        "synergy_id", "items", "name", "description",
        "effect", "location", "tags", "narrator_line"
    ]
    for field in required_fields:
        if field not in synergy:
            errors.append(f"{synergy.get('synergy_id', '???')}: missing field '{field}'")

    items = synergy.get("items", [])
    if len(items) != 2:
        errors.append(f"{synergy['synergy_id']}: needs exactly 2 items, has {len(items)}")

    valid_ids = {item["intel_id"] for item in INTEL_ITEMS}
    for item_id in items:
        if item_id not in valid_ids:
            errors.append(f"{synergy['synergy_id']}: invalid intel_id '{item_id}'")

    valid_locations = LOCATIONS + ["any"]
    if synergy.get("location") not in valid_locations:
        errors.append(f"{synergy['synergy_id']}: invalid location '{synergy.get('location')}'")

    return errors


def main():
    print("=== Intel Item Generator ===\n")

    # Validate all items
    all_errors = []
    for item in INTEL_ITEMS:
        all_errors.extend(validate_intel_item(item))

    for synergy in SYNERGY_MATRIX:
        all_errors.extend(validate_synergy(synergy))

    if all_errors:
        print("VALIDATION ERRORS:")
        for e in all_errors:
            print(f"  ✗ {e}")
        return

    # Build output
    output = {
        "intel_items": INTEL_ITEMS,
        "synergy_matrix": SYNERGY_MATRIX,
        "metadata": {
            "total_items": len(INTEL_ITEMS),
            "total_synergies": len(SYNERGY_MATRIX),
            "items_per_location": {},
            "categories": {},
            "archetypes_affected": set()
        }
    }

    # Compute stats
    for item in INTEL_ITEMS:
        loc = item["location_found"]
        output["metadata"]["items_per_location"][loc] = output["metadata"]["items_per_location"].get(loc, 0) + 1
        cat = item["category"]
        output["metadata"]["categories"][cat] = output["metadata"]["categories"].get(cat, 0) + 1
        for arch in item["effects"]:
            output["metadata"]["archetypes_affected"].add(arch)

    output["metadata"]["archetypes_affected"] = sorted(output["metadata"]["archetypes_affected"])

    # Write
    with open("content/intel.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(INTEL_ITEMS)} intel items")
    print(f"Generated {len(SYNERGY_MATRIX)} synergy combos")
    print(f"\nItems per location:")
    for loc, count in sorted(output["metadata"]["items_per_location"].items()):
        print(f"  {loc}: {count}")
    print(f"\nCategories:")
    for cat, count in sorted(output["metadata"]["categories"].items()):
        print(f"  {cat}: {count}")
    print(f"\nArchetypes affected: {len(output['metadata']['archetypes_affected'])}/12")
    print(f"  {', '.join(output['metadata']['archetypes_affected'])}")
    print(f"\nValidation: 0 errors")
    print(f"Output: content/intel.json")


if __name__ == "__main__":
    main()
