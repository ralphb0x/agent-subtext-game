#!/usr/bin/env python3
"""
Procedural character profile generator for subtext.game.
Generates 1,000+ unique player character profiles from curated data pools.
No API key required — uses combinatorial generation with quality constraints.
"""

import json
import random
import hashlib
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"

# === DATA POOLS ===

# (country, [cities], base_language_range, typical_entry_vectors)
ORIGINS = [
    # Latin America
    ("Guatemala", ["Quetzaltenango", "Huehuetenango", "Antigua Guatemala", "Cobán"], (1, 3), ["land_border"]),
    ("Honduras", ["San Pedro Sula", "La Ceiba", "Comayagua", "Tegucigalpa"], (1, 3), ["land_border"]),
    ("El Salvador", ["Santa Ana", "San Miguel", "Soyapango", "Usulután"], (1, 3), ["land_border"]),
    ("Mexico", ["Oaxaca", "Puebla", "Guadalajara", "Monterrey", "Chiapas", "Veracruz"], (2, 4), ["land_border", "air_legal"]),
    ("Colombia", ["Medellín", "Cali", "Barranquilla", "Bucaramanga", "Cartagena"], (1, 3), ["air_legal", "air_illegal", "land_border"]),
    ("Venezuela", ["Maracaibo", "Valencia", "Barquisimeto", "Ciudad Guayana"], (1, 3), ["air_legal", "air_illegal", "land_border"]),
    ("Ecuador", ["Guayaquil", "Cuenca", "Ambato", "Manta"], (1, 3), ["air_legal", "air_illegal"]),
    ("Peru", ["Arequipa", "Cusco", "Trujillo", "Huancayo"], (1, 3), ["air_legal", "air_illegal"]),
    ("Brazil", ["Recife", "Manaus", "Belém", "Fortaleza", "Salvador"], (1, 2), ["air_legal", "air_illegal", "land_border"]),
    ("Cuba", ["Havana", "Santiago de Cuba", "Camagüey", "Holguín"], (1, 3), ["ocean", "air_legal"]),
    ("Haiti", ["Port-au-Prince", "Cap-Haïtien", "Gonaïves", "Les Cayes"], (1, 2), ["ocean", "air_illegal"]),
    ("Dominican Republic", ["Santo Domingo", "Santiago", "La Romana"], (1, 3), ["air_legal", "air_illegal"]),
    ("Nicaragua", ["Managua", "León", "Granada", "Matagalpa"], (1, 3), ["land_border"]),

    # Eastern Europe
    ("Ukraine", ["Lviv", "Kharkiv", "Odesa", "Dnipro", "Zaporizhzhia"], (1, 3), ["air_legal", "air_illegal"]),
    ("Moldova", ["Chișinău", "Bălți", "Tiraspol", "Cahul"], (1, 2), ["air_legal", "air_illegal"]),
    ("Romania", ["Cluj-Napoca", "Timișoara", "Iași", "Constanța"], (2, 4), ["air_legal"]),
    ("Georgia", ["Tbilisi", "Batumi", "Kutaisi", "Rustavi"], (1, 3), ["air_legal", "air_illegal"]),
    ("Albania", ["Tirana", "Durrës", "Vlorë", "Shkodër"], (1, 3), ["air_legal", "air_illegal"]),
    ("Serbia", ["Belgrade", "Novi Sad", "Niš", "Kragujevac"], (2, 4), ["air_legal"]),
    ("Bosnia", ["Sarajevo", "Banja Luka", "Tuzla", "Mostar"], (1, 3), ["air_legal"]),
    ("Poland", ["Kraków", "Gdańsk", "Wrocław", "Łódź"], (2, 4), ["air_legal"]),

    # Sub-Saharan Africa
    ("Nigeria", ["Lagos", "Kano", "Ibadan", "Port Harcourt", "Enugu", "Benin City"], (2, 4), ["air_legal", "air_illegal"]),
    ("Ghana", ["Accra", "Kumasi", "Tamale", "Cape Coast"], (3, 5), ["air_legal"]),
    ("Senegal", ["Dakar", "Saint-Louis", "Thiès", "Kaolack"], (1, 3), ["air_illegal", "ocean"]),
    ("Ethiopia", ["Addis Ababa", "Dire Dawa", "Gondar", "Hawassa"], (1, 3), ["air_legal", "air_illegal"]),
    ("Somalia", ["Mogadishu", "Hargeisa", "Kismayo", "Bosaso"], (1, 2), ["air_illegal", "ocean"]),
    ("Cameroon", ["Douala", "Yaoundé", "Bamenda", "Bafoussam"], (2, 4), ["air_legal", "air_illegal"]),
    ("Democratic Republic of Congo", ["Kinshasa", "Lubumbashi", "Mbuji-Mayi", "Kisangani"], (1, 2), ["air_illegal"]),
    ("Kenya", ["Nairobi", "Mombasa", "Kisumu", "Nakuru"], (3, 5), ["air_legal"]),
    ("Eritrea", ["Asmara", "Keren", "Massawa", "Assab"], (1, 2), ["air_illegal", "ocean"]),
    ("Ivory Coast", ["Abidjan", "Bouaké", "Yamoussoukro", "Daloa"], (1, 3), ["air_legal", "air_illegal"]),

    # South Asia
    ("India", ["Mumbai", "Hyderabad", "Chennai", "Kolkata", "Jaipur", "Lucknow", "Kochi", "Chandigarh"], (2, 5), ["air_legal", "air_illegal"]),
    ("Bangladesh", ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna"], (1, 3), ["air_legal", "air_illegal"]),
    ("Pakistan", ["Lahore", "Karachi", "Peshawar", "Faisalabad", "Islamabad"], (1, 4), ["air_legal", "air_illegal"]),
    ("Sri Lanka", ["Colombo", "Kandy", "Jaffna", "Galle"], (2, 4), ["air_legal", "ocean"]),
    ("Nepal", ["Kathmandu", "Pokhara", "Biratnagar", "Lalitpur"], (1, 3), ["air_legal", "air_illegal"]),

    # Southeast Asia
    ("Philippines", ["Manila", "Cebu City", "Davao", "Zamboanga", "Iloilo"], (3, 5), ["air_legal", "air_illegal"]),
    ("Vietnam", ["Ho Chi Minh City", "Hanoi", "Da Nang", "Huế", "Haiphong"], (1, 3), ["air_legal", "air_illegal"]),
    ("Myanmar", ["Yangon", "Mandalay", "Naypyidaw", "Mawlamyine"], (1, 2), ["air_illegal"]),
    ("Cambodia", ["Phnom Penh", "Siem Reap", "Battambang", "Sihanoukville"], (1, 2), ["air_legal", "air_illegal"]),
    ("Indonesia", ["Jakarta", "Surabaya", "Medan", "Bandung", "Makassar"], (1, 3), ["air_legal", "air_illegal", "ocean"]),

    # East Asia
    ("China", ["Fuzhou", "Wenzhou", "Guangzhou", "Shenyang", "Qingdao", "Chengdu"], (1, 4), ["air_legal", "air_illegal"]),
    ("Mongolia", ["Ulaanbaatar", "Erdenet", "Darkhan", "Choibalsan"], (1, 2), ["air_legal"]),

    # Middle East / Central Asia
    ("Syria", ["Aleppo", "Damascus", "Homs", "Latakia", "Deir ez-Zor"], (1, 3), ["air_illegal", "ocean"]),
    ("Iraq", ["Baghdad", "Erbil", "Basra", "Sulaymaniyah", "Mosul"], (1, 3), ["air_legal", "air_illegal"]),
    ("Afghanistan", ["Kabul", "Herat", "Mazar-i-Sharif", "Kandahar", "Jalalabad"], (1, 2), ["air_illegal"]),
    ("Iran", ["Tehran", "Isfahan", "Shiraz", "Tabriz", "Mashhad"], (1, 3), ["air_legal", "air_illegal"]),
    ("Turkey", ["Istanbul", "Ankara", "Izmir", "Antalya", "Gaziantep"], (2, 4), ["air_legal"]),
    ("Uzbekistan", ["Tashkent", "Samarkand", "Bukhara", "Nukus"], (1, 2), ["air_legal", "air_illegal"]),
    ("Tajikistan", ["Dushanbe", "Khujand", "Kulob", "Bokhtar"], (1, 2), ["air_illegal"]),

    # Pacific Islands / Other
    ("Fiji", ["Suva", "Nadi", "Lautoka", "Labasa"], (3, 5), ["air_legal", "ocean"]),
    ("Tonga", ["Nukuʻalofa", "Neiafu", "Pangai"], (2, 4), ["air_legal", "ocean"]),
    ("Samoa", ["Apia", "Salelologa"], (2, 4), ["air_legal", "ocean"]),
    ("Papua New Guinea", ["Port Moresby", "Lae", "Mount Hagen", "Madang"], (1, 3), ["air_legal", "air_illegal"]),

    # North Africa
    ("Egypt", ["Cairo", "Alexandria", "Luxor", "Aswan", "Port Said"], (1, 3), ["air_legal", "air_illegal"]),
    ("Morocco", ["Casablanca", "Fez", "Tangier", "Marrakech", "Rabat"], (1, 3), ["air_legal", "air_illegal"]),
    ("Tunisia", ["Tunis", "Sfax", "Sousse", "Kairouan"], (1, 3), ["air_legal", "air_illegal"]),

    # Caribbean
    ("Jamaica", ["Kingston", "Montego Bay", "Spanish Town", "Mandeville"], (4, 5), ["air_legal", "air_illegal", "ocean"]),
    ("Trinidad and Tobago", ["Port of Spain", "San Fernando", "Chaguanas"], (4, 5), ["air_legal"]),
    ("Guyana", ["Georgetown", "Linden", "New Amsterdam"], (4, 5), ["air_legal", "air_illegal"]),

    # Internal (already in US)
    ("United States", ["El Paso", "Miami", "Houston", "Chicago", "Los Angeles", "Phoenix", "Minneapolis"], (5, 5), ["internal"]),
]

# Hyper-specific occupations with (title, savings_range, language_modifier)
OCCUPATIONS = [
    ("third-shift security guard at a ceramics factory", (200, 1200), 0),
    ("assistant dog groomer specializing in poodle cuts", (300, 900), 0),
    ("unlicensed electrician who only does commercial kitchens", (500, 2500), 0),
    ("backup singer for a regional cumbia band", (100, 800), 0),
    ("motorcycle taxi dispatcher", (150, 600), 0),
    ("night manager at a 24-hour laundromat", (400, 1500), 0),
    ("freelance wedding videographer with exactly one camera", (300, 1800), 0),
    ("fish market ice delivery driver", (200, 900), 0),
    ("retired middle school geography teacher", (800, 3000), 1),
    ("apprentice welder at a shipyard", (400, 1600), 0),
    ("street food vendor specializing in fried plantains", (100, 500), 0),
    ("part-time church organist and full-time accountant", (1000, 4000), 1),
    ("maternity ward nurse with 22 years experience", (600, 2500), 1),
    ("cell phone repair technician working from a folding table", (200, 1000), 0),
    ("forklift operator at a cement plant", (500, 2000), 0),
    ("subsistence rice farmer with a side business in duck eggs", (50, 400), -1),
    ("dental hygienist who was actually a dentist back home", (800, 3500), 1),
    ("former physics professor who learned English from YouTube cooking videos", (500, 2000), -1),
    ("licensed boat captain for a lake ferry that no longer runs", (300, 1200), 0),
    ("assistant baker at a French patisserie in a non-French-speaking country", (400, 1500), 0),
    ("overnight pharmacy clerk at the only pharmacy in town", (300, 1000), 0),
    ("competitive pigeon breeder and part-time taxi driver", (200, 800), 0),
    ("kindergarten art teacher with a minor gambling habit", (400, 1200), 0),
    ("auto body painter who only paints trucks", (600, 2200), 0),
    ("beekeeper managing 300 hives for an export company", (400, 1500), 0),
    ("hospital cafeteria cook who once catered a presidential dinner", (300, 1000), 0),
    ("satellite dish installer for rural villages", (200, 800), 0),
    ("retired army sergeant now selling insurance door to door", (600, 2500), 0),
    ("tailor specializing in military uniforms", (400, 1800), 0),
    ("undocumented construction crane operator", (800, 3000), 0),
    ("school bus driver who also drives the hearse on weekends", (400, 1200), 0),
    ("data entry clerk at a customs office", (500, 2000), 1),
    ("coconut water vendor on a specific beach", (50, 300), -1),
    ("backup goalkeeper for a third-division football club", (200, 1000), 0),
    ("radio station sound engineer for the overnight shift", (400, 1500), 0),
    ("agricultural extension officer for a province with no budget", (300, 1000), 1),
    ("veterinary assistant who mainly handles chickens", (200, 800), 0),
    ("typewriter repair technician in a city that still uses typewriters", (300, 1200), 0),
    ("silk factory quality inspector", (400, 1500), 0),
    ("hotel lobby pianist who knows exactly 40 songs", (300, 1200), 0),
    ("shrimp boat deckhand saving for his own boat", (200, 900), -1),
    ("municipal garbage truck driver with a law degree", (500, 1800), 1),
    ("private math tutor to the children of a regional governor", (600, 2500), 1),
    ("portrait photographer at a shopping mall that is closing", (300, 1000), 0),
    ("cemetery groundskeeper and occasional gravedigger", (200, 800), 0),
    ("copy shop owner whose printer is always breaking", (400, 1500), 0),
    ("night shift orderly at a psychiatric hospital", (300, 1200), 0),
    ("mango wholesaler at a regional market", (500, 2500), 0),
    ("part-time tour guide at a ruin nobody visits", (100, 600), 1),
    ("assembly line worker at a sneaker factory", (300, 1200), 0),
    ("coin-operated laundry machine repairman", (400, 1600), 0),
    ("unpaid intern at a human rights NGO for the past two years", (100, 500), 2),
    ("freelance translator who has never translated English", (300, 1000), -1),
    ("rubber plantation foreman", (400, 1800), 0),
    ("mosque janitor who memorized the entire Quran", (100, 500), 0),
    ("bowling alley mechanic", (400, 1200), 0),
    ("government meteorologist for a region where it never rains", (500, 2000), 1),
    ("street barber with a chair under a specific tree", (100, 400), -1),
    ("ferry ticket collector on a river crossing", (200, 700), 0),
    ("aquaculture technician at a tilapia farm", (400, 1500), 0),
    ("piano tuner who travels between three cities by bus", (300, 1200), 0),
    ("retired circus acrobat now teaching gymnastics to children", (200, 800), 0),
    ("counterfeit handbag vendor with real brand knowledge", (300, 1500), 0),
    ("municipal librarian at a library with 200 books", (400, 1200), 1),
    ("professional mourner for hire at funerals", (100, 500), 0),
    ("scrap metal sorter at a recycling yard", (200, 800), -1),
    ("emergency room receptionist who has seen everything", (500, 1800), 0),
    ("long-haul trucker on the route between two specific cities", (400, 1800), 0),
    ("butcher specializing in goat for festival season", (300, 1200), 0),
    ("unlicensed midwife trusted by the entire village", (200, 900), 0),
    ("parking lot attendant at the national airport", (300, 1000), 0),
    ("tea plantation supervisor during harvest season only", (300, 1200), 0),
    ("karaoke bar DJ who secretly hates karaoke", (200, 800), 0),
    ("volunteer firefighter who also repairs refrigerators", (400, 1500), 0),
    ("traveling Bible salesman covering three provinces", (200, 900), 0),
    ("court stenographer who types 180 words per minute", (600, 2200), 1),
    ("night watchman at an abandoned textile mill", (200, 700), 0),
    ("professional cricket scorer for domestic matches", (300, 1000), 1),
    ("papaya farmer who lost this year's crop to a storm", (50, 300), -1),
    ("motorcycle mechanic who has never ridden a motorcycle", (300, 1000), 0),
    ("former child actor from a soap opera nobody remembers", (200, 1200), 1),
    ("civil servant processing land title disputes", (500, 2000), 1),
    ("glassblower at a tourist factory", (300, 1200), 0),
    ("bread delivery driver for a bakery chain", (300, 1000), 0),
    ("sewing machine operator at a denim factory", (200, 800), 0),
    ("train station announcer who never takes the train", (300, 1000), 0),
    ("prosthetic limb technician at a rehabilitation center", (500, 2000), 1),
    ("sugarcane harvester during season and carpenter off-season", (200, 800), -1),
    ("secondhand bookshop owner with a philosophy degree", (400, 1500), 2),
    ("salt mine supervisor on the night shift", (500, 2000), 0),
    ("rickshaw driver with an engineering degree", (100, 600), 1),
    ("flower arranger for hotel lobbies", (300, 1000), 0),
    ("submarine cable technician who is afraid of the ocean", (800, 3500), 1),
    ("municipal water meter reader", (300, 1000), 0),
    ("itinerant shoe cobbler who travels village to village", (100, 400), -1),
    ("warehouse inventory specialist for a pharmaceutical company", (500, 2000), 0),
    ("palm oil press operator", (300, 1200), 0),
    ("nightclub bouncer with a degree in early childhood education", (400, 1500), 0),
    ("orthopedic surgeon who lost her license over a paperwork dispute", (1000, 5000), 2),
    ("catfish farm manager", (400, 1800), 0),
    ("assistant to a local politician who just lost the election", (200, 1000), 1),
]

ASSETS = [
    "can fix any diesel engine built before 2005",
    "has a cousin in Queens who owes a favor",
    "speaks four languages, none of them English",
    "knows how to forge a convincing utility bill",
    "can cook for 200 people with nothing but rice and spices",
    "has a valid but expiring work permit for Canada",
    "possesses an encyclopedic knowledge of American baseball statistics",
    "trained as a combat medic and carries a full first aid kit",
    "has $800 sewn into the lining of a winter coat",
    "memorized the entire New York subway map from a library book",
    "can identify any bird by its call, which is useless but calming",
    "has a letter of recommendation from a former US ambassador",
    "knows how to pick simple locks with a hairpin",
    "carries a satellite phone with 14 minutes of airtime remaining",
    "has a brother who drives a delivery truck in Brooklyn",
    "can perform basic dental procedures",
    "knows three card tricks that actually work on border agents",
    "has a stamp collection worth approximately $2,000 to the right buyer",
    "carries notarized copies of every document ever issued to them",
    "can rewire any electrical panel to code",
    "has a photographic memory for faces and names",
    "owns a fully paid-off food cart stored in a friend's garage in New Jersey",
    "was a competitive swimmer and can cross any river",
    "has a nursing certification recognized in 23 countries but not the US",
    "carries a flip phone with the number of a immigration lawyer in Miami",
    "knows how to butcher and sell a whole cow in under three hours",
    "has completed a FEMA emergency response online course",
    "possesses a genuine-looking but expired US driver's license",
    "can sew anything — clothes, wounds, leather, canvas",
    "has a YouTube channel with 40,000 subscribers about fixing motorcycles",
    "carries a small toolkit that fits in a jacket pocket",
    "was trained as an accountant and can read any financial document",
    "has a friend who works at JFK airport in baggage handling",
    "can sleep anywhere — moving vehicles, concrete floors, standing up",
    "knows how to make soap, candles, and basic medicines from plants",
    "has a contact at a church in the Bronx that provides shelter",
    "carries a waterproof bag with birth certificates for four family members",
    "can drive any vehicle including buses and light aircraft",
    "has exactly one suit that fits perfectly and looks expensive",
    "knows every Western Union location between Guatemala City and New York",
    "has a gold chain worth about $1,500 that was a grandmother's",
    "can do basic plumbing including soldering copper pipe",
    "has a reputation as someone who always pays debts",
    "speaks enough Russian to navigate former Soviet countries",
    "carries a detailed hand-drawn map of crossing points",
    "has a genuine Social Security card belonging to a dead relative",
    "can type 90 words per minute in two languages",
    "knows a guy who knows a guy at a restaurant in Astoria that hires",
    "has a valid passport from a second country that allows visa-free entry",
    "can perform CPR and has actually saved someone's life with it",
]

BURDENS = [
    "owes $3,000 to the coyote's brother",
    "traveling with a 6-year-old daughter who asks questions constantly",
    "has a heart condition that requires medication every 12 hours",
    "left without telling anyone and the family thinks they're dead",
    "is being followed by someone who wants the debt repaid",
    "carries a secret that would get them killed if they went back",
    "has a warrant in the home country for a crime they didn't commit",
    "traveling with a 74-year-old mother who refuses to complain",
    "promised to send $500 home every month starting immediately",
    "has exactly three days of blood pressure medication left",
    "left a spouse and two children who depend on weekly remittances",
    "was scammed out of half their savings two days ago",
    "has a conspicuous facial scar that makes people remember them",
    "doesn't know that the contact in New York moved to Philadelphia",
    "carrying a package for someone and was told not to open it",
    "has a phobia of confined spaces and cannot ride in car trunks",
    "their passport photo looks nothing like them after losing 30 pounds",
    "is functionally illiterate and cannot read signs or forms",
    "has an 8-month-old baby who is very quiet, which worries them",
    "promised God they would not lie during the entire journey",
    "was a police officer back home and other migrants don't trust them",
    "is fleeing a family arrangement and will be found if they use their real name",
    "needs to arrive by June 30th or the job offer expires",
    "carrying $4,000 in cash because they don't trust banks or wire transfers",
    "has chronic back pain that makes walking more than 2 miles agony",
    "left behind a dog they've had for 11 years",
    "the person who was supposed to meet them at the border never showed up",
    "has type 1 diabetes and a finite supply of insulin",
    "is pretending to be from a different country for safety reasons",
    "speaks a minority language that even other people from the same country don't understand",
    "was a teacher and keeps trying to educate people who don't want lectures",
    "has night terrors that wake up everyone nearby",
    "is carrying their dead father's ashes in a thermos",
    "their phone was stolen yesterday and all their contacts were on it",
    "has a teenage son who is angry about leaving and refuses to cooperate",
    "is pregnant and hasn't told anyone yet",
    "was promised a job that almost certainly doesn't exist",
    "has a gambling debt of $7,000 to people who don't send reminders",
    "cannot swim and the route may involve water crossings",
    "the only family member who knows the plan just had a stroke",
    "has asthma and left the inhaler on the kitchen table at home",
    "is traveling on a friend's documents and looks only vaguely similar",
    "trusted the wrong person with half their money three countries ago",
    "has severe dental pain that is getting worse by the day",
    "left behind a small business that will be seized if they don't return in 90 days",
    "is older than they told the group and can't keep the pace",
    "carries a flip phone with a cracked screen that might die at any moment",
    "their visa expired 47 days ago and every day makes it worse",
    "has exactly one change of clothes and it's getting cold",
    "is afraid of dogs and the route goes through areas with guard dogs",
]

MOTIVATIONS = [
    "promised dying grandmother she would witness competitive eating at its highest level",
    "saw Joey Chestnut eat 76 hot dogs on a hospital TV during chemotherapy and decided that if a human body could do that, anything was possible",
    "believes the Nathan's Famous contest is the last true meritocracy — no connections, no bribes, just stomach capacity and willpower",
    "has a theory that the winner's technique could be applied to speed-eating competitions back home, creating a viable national athletic program",
    "made a bet with a brother-in-law that they would stand on Coney Island on July 4th, and the brother-in-law bet the family car",
    "read a Wikipedia article about competitive eating translated into their language and interpreted it as a religious calling",
    "their late father's last words were about a hot dog he ate on Coney Island in 1987 and they need to understand why",
    "wants to recruit Joey Chestnut for a competitive eating exhibition in their hometown to save the local festival",
    "is writing a doctoral thesis on American spectacle culture and the contest is the primary field research site",
    "has eaten exactly one American hot dog in their life, from a street cart in another country, and it changed their understanding of meat",
    "believes the contest represents everything America promised — abundance, competition, freedom to do something completely useless in public",
    "needs to deliver a hand-carved trophy to the contest organizers, commissioned by a rich uncle who is a competitive eating superfan",
    "was told by a fortune teller that their destiny would be decided at a place where people eat without hunger, and researched until finding Nathan's",
    "promised their children a story worth telling, and 'your father crossed a continent to watch Americans eat hot dogs competitively' qualified",
    "lost a family recipe for sausage casing and believes the answer exists somewhere in the Nathan's Famous supply chain",
    "heard a rumor that the prize money from the contest could pay off the family debt, and refuses to believe the rumor is wrong",
    "considers the hot dog eating contest the purest form of human performance — no technology, no equipment, just the body and the hot dog",
    "was a food scientist studying meat processing and the contest represents the terminal velocity of processed meat consumption",
    "their grandfather claimed to have competed in the 1972 contest and they need to verify this because it's in the family Bible",
    "has been training competitively in their home country and genuinely believes they can place in the top 20",
    "wants to prove to an ex-spouse that they are capable of completing a mission, any mission, even a stupid one",
    "was inspired by a motivational speaker who used the contest as a metaphor, but took the metaphor literally",
    "needs to deliver a letter to someone they were told would be in the crowd, wearing a Nathan's Famous hat, on July 4th",
    "watched a documentary about Takeru Kobayashi and recognized the same look of quiet determination they see in the mirror",
    "their village pooled money to send one representative to witness the contest and report back, treating it as a diplomatic mission",
    "is convinced that the mustard used in the contest has medicinal properties their sick mother needs",
    "had a dream about a beach with thousands of people watching someone eat, and interpreted it as a sign after three separate dream dictionaries agreed",
    "believes attendance at the contest will complete a spiritual journey begun when they fasted for 40 days and saw a vision of hot dogs",
    "their application to culinary school was rejected and they decided to study food consumption from the other end of the discipline",
    "owns the only Nathan's Famous t-shirt in their entire country and has built an identity around it",
    "made a deathbed promise to a friend who collected American contest memorabilia and never made it to New York",
    "correctly identified the contest as a gathering that requires no tickets, no credentials, and no invitation — the last free public spectacle",
    "heard that the contest is broadcast on ESPN and believes being visible in the crowd will help locate a missing family member who watches ESPN",
    "their town's mayor challenged anyone to bring back proof of the contest and promised a government job to whoever did",
    "plans to open a competitive eating academy in their home country and needs to conduct firsthand research",
    "was told by a priest that the excessive consumption at the contest is a form of American prayer and wants to witness American prayer",
    "their therapist suggested they do something completely irrational as a breakthrough exercise and this qualified",
    "has a food blog with 12 followers that has been covering competitive eating from afar for six years and needs field reporting",
    "is carrying a flag from their home country to wave in the crowd because no one from their country has ever been photographed at the contest",
    "believes the hot dog eating contest is a coded signal for something larger and wants to see it in person to understand what",
    "needs exactly one specific photograph — themselves at Coney Island on July 4th — to complete a promise made to someone who is no longer alive",
    "was a competitive eater of a different food in their home country and considers this a pilgrimage to the holy land of the discipline",
    "has been using the contest date as a deadline for every goal in their life and this is the year the deadline applies literally",
    "read that Nathan's Famous hot dogs contain a specific preservative that their chemistry professor once said would be important someday",
    "the hot dog eating contest is the only American cultural event their grandmother approved of, calling it 'honest work'",
    "plans to stand in the crowd holding a sign that says the name of their village, which no American has ever heard of",
    "was told that anyone who reaches Coney Island on July 4th gets a free hot dog, and has been budgeting around this fact",
    "considers it a personal failing that they have crossed three time zones and nine borders but never seen a frankfurter consumed competitively",
    "their favorite number is 76 (the birth year of their mother) and Joey Chestnut ate 76 hot dogs, which cannot be a coincidence",
    "was dared by a coworker who said they would never leave the country, and chose the most American event they could find as proof",
]

# Name pools by region
NAMES = {
    "latin_america": [
        "Carlos Méndez", "María Elena Quispe", "José Luis Hernández", "Ana Patricia Flores",
        "Diego Arévalo", "Lucía Montoya", "Rafael Espinoza", "Carmen Rosa Villanueva",
        "Eduardo Castillo", "Beatriz Solano", "Fernando Aguirre", "Isabel Cristina Ramos",
        "Pedro Miguel Santos", "Gloria Estefanía Díaz", "Andrés Felipe Morales", "Rosa Marina Campos",
        "Héctor Raúl Domínguez", "Silvia Alejandra Torres", "Manuel Ignacio Vargas", "Teresa de Jesús López",
        "Roberto Carlos Medina", "Claudia Patricia Reyes", "Jorge Enrique Paredes", "Marta Lucía Bermúdez",
        "Ramón Alberto Cruz", "Yolanda del Carmen Fuentes", "Gustavo Adolfo Rivera", "Patricia Eugenia Salazar",
        "Luis Fernando Peña", "Sandra Milena Ortiz", "Julio César Navarro", "Marisol de los Ángeles Vega",
        "Alejandro Benítez", "Gabriela Solís", "Óscar René Miranda", "Pilar Constanza Guzmán",
        "Ernesto Joaquín Delgado", "Valentina Rojas", "Fabián Alejandro Ponce", "Nuria Esperanza Cortés",
        "Sergio Iván Maldonado", "Alicia Fernanda Ríos", "Ignacio Tomás Herrera", "Daniela Sofía Estrada",
    ],
    "eastern_europe": [
        "Oleksandr Bondarenko", "Iryna Kovalenko", "Dmitri Volkov", "Natalia Petrescu",
        "Grigori Shevchenko", "Oksana Melnyk", "Viktor Ionescu", "Elena Constantinescu",
        "Artur Tkachenko", "Svetlana Morozova", "Sergei Popov", "Milena Kovačević",
        "Andrei Popa", "Dragana Nikolić", "Giorgi Beridze", "Nino Kharadze",
        "Besnik Hoxha", "Mirjana Babić", "Tomasz Kowalski", "Agnieszka Wiśniewska",
        "Piotr Kamiński", "Bogdan Moldovan", "Luka Jovanović", "Marija Đorđević",
    ],
    "sub_saharan_africa": [
        "Chukwuemeka Okonkwo", "Ngozi Adichie-Okafor", "Kwame Asante", "Adwoa Mensah",
        "Mamadou Diallo", "Fatou Sow", "Tadesse Gebremedhin", "Meron Haile",
        "Abdirahman Hassan", "Amina Yusuf", "Jean-Pierre Nkurunziza", "Chantal Uwimana",
        "Oluwaseun Adeyemi", "Chinelo Nwosu", "Kofi Boateng", "Akua Darko",
        "Moussa Traoré", "Mariama Bâ", "Ibrahim Abdullahi", "Blessing Okonkwo",
        "Ousmane Ndiaye", "Aïssatou Camara", "Yohanes Kidane", "Semhar Tesfai",
        "Pierre Habimana", "Goretti Mukamana", "Emmanuel Osei", "Abena Gyamfi",
    ],
    "south_asia": [
        "Rajesh Kumar Sharma", "Priya Nair", "Mohammad Rafiq Hossain", "Fatima Begum",
        "Suresh Thapa", "Lakshmi Devi Gurung", "Anwar ul-Haq Siddiqui", "Rashida Khatun",
        "Dinesh Wickramasinghe", "Chamari de Silva", "Arun Krishnamurthy", "Deepa Rani Jha",
        "Kamal Uddin Ahmed", "Nasreen Akhtar", "Rohan Perera", "Nirmala Kumari Basnet",
        "Sanjay Patel", "Meera Bhandari", "Md. Zahirul Islam", "Sharmila Tamang",
        "Vikram Singh Thakur", "Sunita Yadav", "Gopal Bahadur Rai", "Anjali Subedi",
    ],
    "southeast_asia": [
        "Maria Consolación Santos", "Juan Carlos Reyes", "Nguyễn Thanh Hùng", "Trần Thị Mai",
        "Phạm Văn Đức", "Lê Thị Hồng", "Sok Channary", "Chea Veasna",
        "Ko Zaw Min", "Ma Thida", "Rizal Hadikusumo", "Siti Nurhaliza Putri",
        "Roberto dela Cruz", "Josephine Bautista", "Mark Anthony Villanueva", "Cherry Mae Gonzales",
        "Bùi Minh Tuấn", "Võ Thị Lan", "Heng Sopheap", "Prak Sokha",
        "Aung Kyaw Moe", "Thin Thin Aye", "Wayan Suardika", "Made Ayu Lestari",
    ],
    "east_asia": [
        "Chen Weijun", "Lin Xiaomei", "Zhang Guoqiang", "Wang Lili",
        "Liu Donghai", "Huang Meifang", "Wu Jianguo", "Zhou Xiuying",
        "Li Pengfei", "Yang Chunhua", "Batbayar Enkhtuul", "Oyungerel Tsetseg",
        "Xu Zhimin", "Gao Yanping", "He Guangming", "Zheng Shulan",
    ],
    "middle_east_central_asia": [
        "Ahmad al-Mustafa", "Fatima Zahra al-Rashid", "Hassan Karimi", "Maryam Hosseini",
        "Omar Bayraktar", "Ayşe Demir", "Khalid al-Jubouri", "Nour al-Din Ibrahim",
        "Farid Noorzai", "Bibi Gul Ahmadi", "Rustam Karimov", "Dilnoza Sultanova",
        "Mehmet Çelik", "Zeynep Yılmaz", "Sayed Rahmatullah", "Parwin Mohammadi",
        "Jamshid Ergashev", "Nigora Rakhimova", "Mustafa Aksoy", "Elif Kaya",
        "Hasan Jassim", "Zahra Mohammed", "Babur Mirzaev", "Gulbahor Tosheva",
    ],
    "pacific": [
        "Sitiveni Rabuka Jr.", "Mere Tuisawau", "Semisi Havea", "ʻAna Taufa",
        "Tuilaepa Sailele", "Leilani Matautia", "Philip Mondo", "Mary Kaiulo",
        "Josefa Natukovou", "Salote Vakacegu", "Tevita Moala", "Mele Finau",
    ],
    "north_africa": [
        "Youssef Benali", "Amina Tazi", "Ahmed Mansouri", "Fatma Bouzid",
        "Karim el-Fassi", "Salma Ouazzani", "Mohamed Trabelsi", "Hana Mejri",
        "Rachid Hammami", "Nadia Slimani", "Omar Cherkaoui", "Leila Bouazizi",
    ],
    "caribbean": [
        "Damion Tulloch", "Shanique Brown", "Kwesi Bowen", "Marcia Campbell",
        "Devendra Doobay", "Asha Persaud", "Tyrone Wilson", "Shanice Clarke",
        "Kevin Doodnauth", "Priya Doobay", "Andre Leckie", "Simone Patterson",
    ],
    "internal": [
        "Miguel Ángel Soto", "Yesenia Cristina Ochoa", "Hai Tran", "Mei-Ling Chen",
        "Olga Petrov", "Emmanuel Oduya", "Park Jin-soo", "Farah Hassan",
    ],
}

# Map countries to name regions
COUNTRY_TO_REGION = {}
for country, cities, _, _ in ORIGINS:
    name = country.lower()
    if country in ["Guatemala", "Honduras", "El Salvador", "Mexico", "Colombia", "Venezuela",
                    "Ecuador", "Peru", "Brazil", "Cuba", "Haiti", "Dominican Republic", "Nicaragua"]:
        COUNTRY_TO_REGION[country] = "latin_america"
    elif country in ["Ukraine", "Moldova", "Romania", "Georgia", "Albania", "Serbia", "Bosnia", "Poland"]:
        COUNTRY_TO_REGION[country] = "eastern_europe"
    elif country in ["Nigeria", "Ghana", "Senegal", "Ethiopia", "Somalia", "Cameroon",
                      "Democratic Republic of Congo", "Kenya", "Eritrea", "Ivory Coast"]:
        COUNTRY_TO_REGION[country] = "sub_saharan_africa"
    elif country in ["India", "Bangladesh", "Pakistan", "Sri Lanka", "Nepal"]:
        COUNTRY_TO_REGION[country] = "south_asia"
    elif country in ["Philippines", "Vietnam", "Myanmar", "Cambodia", "Indonesia"]:
        COUNTRY_TO_REGION[country] = "southeast_asia"
    elif country in ["China", "Mongolia"]:
        COUNTRY_TO_REGION[country] = "east_asia"
    elif country in ["Syria", "Iraq", "Afghanistan", "Iran", "Turkey", "Uzbekistan", "Tajikistan"]:
        COUNTRY_TO_REGION[country] = "middle_east_central_asia"
    elif country in ["Fiji", "Tonga", "Samoa", "Papua New Guinea"]:
        COUNTRY_TO_REGION[country] = "pacific"
    elif country in ["Egypt", "Morocco", "Tunisia"]:
        COUNTRY_TO_REGION[country] = "north_africa"
    elif country in ["Jamaica", "Trinidad and Tobago", "Guyana"]:
        COUNTRY_TO_REGION[country] = "caribbean"
    elif country == "United States":
        COUNTRY_TO_REGION[country] = "internal"

ENTRY_TO_VISA = {
    "land_border": ["none", "none", "none", "expired"],  # mostly no visa
    "air_legal": ["tourist", "student", "work", "expired"],
    "air_illegal": ["none", "expired", "none", "tourist"],
    "ocean": ["none", "none", "none", "none"],
    "internal": ["expired", "none", "work", "expired"],
}


def generate_character(char_id: int, rng: random.Random, used_names: set) -> dict:
    """Generate a single character profile."""
    # Pick origin
    country, cities, lang_range, entry_vectors = rng.choice(ORIGINS)
    city = rng.choice(cities)

    # Pick name from appropriate region
    region = COUNTRY_TO_REGION[country]
    name_pool = NAMES[region]
    # Ensure unique names
    name = rng.choice(name_pool)
    attempts = 0
    while name in used_names and attempts < 50:
        # Generate a variant by swapping first/last or adding suffix
        base_name = rng.choice(name_pool)
        suffixes = ["", " Jr.", " II", " III"]
        name = base_name + rng.choice(suffixes)
        attempts += 1
    if name in used_names:
        # Last resort: add a number
        name = rng.choice(name_pool) + f" ({char_id})"
    used_names.add(name)

    # Pick occupation
    occupation, savings_range, lang_mod = rng.choice(OCCUPATIONS)

    # Language skill
    base_lang = rng.randint(lang_range[0], lang_range[1])
    lang_skill = max(1, min(5, base_lang + lang_mod))

    # Savings
    savings = rng.randint(savings_range[0], savings_range[1])
    # Round to nearest 25
    savings = round(savings / 25) * 25
    savings = max(10, savings)

    # Entry vector and visa
    entry_vector = rng.choice(entry_vectors)
    visa_status = rng.choice(ENTRY_TO_VISA[entry_vector])

    # Asset and burden
    asset = rng.choice(ASSETS)
    burden = rng.choice(BURDENS)

    # Motivation
    motivation = rng.choice(MOTIVATIONS)

    return {
        "id": f"char-{str(char_id).zfill(6)}",
        "name": name,
        "origin_country": country,
        "origin_city": city,
        "occupation": occupation,
        "savings_usd": savings,
        "language_skill": lang_skill,
        "asset": asset,
        "burden": burden,
        "motivation": motivation,
        "entry_vector": entry_vector,
        "visa_status": visa_status,
    }


def validate_character(char: dict) -> list[str]:
    """Validate a character profile against the schema."""
    errors = []
    required = ["id", "name", "origin_country", "origin_city", "occupation",
                 "savings_usd", "language_skill", "asset", "burden", "motivation",
                 "entry_vector", "visa_status"]
    for field in required:
        if field not in char:
            errors.append(f"Missing field: {field}")

    if "language_skill" in char and char["language_skill"] not in [1, 2, 3, 4, 5]:
        errors.append(f"Invalid language_skill: {char['language_skill']}")

    if "entry_vector" in char and char["entry_vector"] not in [
        "land_border", "air_legal", "air_illegal", "ocean", "internal"
    ]:
        errors.append(f"Invalid entry_vector: {char['entry_vector']}")

    if "visa_status" in char and char["visa_status"] not in [
        "none", "tourist", "student", "work", "expired"
    ]:
        errors.append(f"Invalid visa_status: {char['visa_status']}")

    if "savings_usd" in char and (not isinstance(char["savings_usd"], (int, float)) or char["savings_usd"] < 0):
        errors.append(f"Invalid savings_usd: {char['savings_usd']}")

    return errors


def generate_all(count: int = 1000, seed: int = 42):
    """Generate all character profiles."""
    rng = random.Random(seed)
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    characters = []
    used_names = set()
    errors_total = 0

    print(f"Generating {count} character profiles (seed={seed})...")
    for i in range(count):
        char = generate_character(i, rng, used_names)
        char_errors = validate_character(char)
        if char_errors:
            print(f"  Validation errors for {char['id']}: {char_errors}")
            errors_total += len(char_errors)
        characters.append(char)

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{count}...")

    output_path = CONTENT_DIR / "characters.json"
    output_path.write_text(json.dumps(characters, indent=2, ensure_ascii=False))

    # Stats
    countries = set(c["origin_country"] for c in characters)
    entry_vectors = {}
    visa_statuses = {}
    lang_skills = {}
    for c in characters:
        entry_vectors[c["entry_vector"]] = entry_vectors.get(c["entry_vector"], 0) + 1
        visa_statuses[c["visa_status"]] = visa_statuses.get(c["visa_status"], 0) + 1
        lang_skills[c["language_skill"]] = lang_skills.get(c["language_skill"], 0) + 1

    print(f"\nDone! {count} characters → {output_path}")
    print(f"Validation errors: {errors_total}")
    print(f"Unique countries: {len(countries)}")
    print(f"Entry vectors: {json.dumps(entry_vectors, indent=2)}")
    print(f"Visa statuses: {json.dumps(visa_statuses, indent=2)}")
    print(f"Language skills: {json.dumps(lang_skills, indent=2)}")

    return characters


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate character profiles for subtext.game")
    parser.add_argument("--count", type=int, default=1000, help="Number of profiles to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    args = parser.parse_args()
    generate_all(args.count, args.seed)
