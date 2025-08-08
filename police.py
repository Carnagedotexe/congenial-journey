import random
import time
import textwrap
import os
from datetime import date, timedelta

# ==============================================================================
# GAME STATE AND PLAYER DATA
# ==============================================================================
player = {}
call_queue = []
shift_time_remaining = 600
START_DATE = date(2025, 8, 1)
call_id_counter = 1

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print(f"\n{'='*60}\n {title.upper().center(58)} \n{'='*60}")

def print_text(text, delay=0.75):
    print(textwrap.fill(text, width=70))
    time.sleep(delay)

def get_input(prompt="> "):
    return input(prompt).strip().lower()

def skill_check(skill_name):
    skill_key = skill_name.lower().replace(" ", "_")
    if skill_key not in player:
        return False
    roll = random.randint(1, 100)
    rookie_bonus = 30
    effective_skill = player[skill_key] + rookie_bonus
    print_text(f"// Rolling for {skill_name}... Target: {effective_skill} (Skill: {player[skill_key]} + Bonus: {rookie_bonus}). Roll: {roll}. //")
    if roll <= effective_skill:
        return True
    else:
        return False

# ==============================================================================
# CHARACTER CREATION
# ==============================================================================
def display_creation_screen(stats, points):
    clear_screen()
    print_header("Create Your Officer")
    print(f"You have {points} points to spend.")
    print("All stats start at 5 and cannot exceed 30.")
    print("-" * 40)
    for stat, value in stats.items():
        display_name = stat.replace("_", " ").title()
        print(f"{display_name}: {value}")
    print("-" * 40)
    print("Commands:")
    print("  '+ [stat] [amount]' (e.g., '+ strength 5')")
    print("  '- [stat] [amount]' (e.g., '- de_escalation 3')")
    print("  'randomize' to randomly assign all points.")
    print("  'done' when you have 0 points remaining.")

def character_creation():
    global player
    stats = {
        "strength": 5, "stamina": 5, "perception": 5,
        "de_escalation": 5, "command_presence": 5, "marksmanship": 5,
        "law_knowledge": 5
    }
    points = 40
    while True:
        display_creation_screen(stats, points)
        if points == 0:
            print("\nAll points spent! Type 'done' to begin your first shift.")
        choice = get_input()
        parts = choice.split()
        if not parts:
            continue
        action = parts[0]
        if action == "done":
            if points == 0:
                break
            else:
                print_text(f"You still have {points} points to spend!")
        elif action == "randomize":
            stats = {key: 5 for key in stats}
            points_to_distribute = 40
            stat_keys = list(stats.keys())
            while points_to_distribute > 0:
                chosen_stat = random.choice(stat_keys)
                if stats[chosen_stat] < 30:
                    stats[chosen_stat] += 1
                    points_to_distribute -= 1
            points = 0
        elif action in ['+', '-']:
            if len(parts) < 2:
                print_text("Please specify which stat."); continue
            amount = 1; stat_parts = parts[1:]
            if parts[-1].isdigit():
                try:
                    amount = int(parts[-1]); stat_parts = parts[1:-1]
                    if amount <= 0: print_text("Please provide a positive number."); continue
                except ValueError: pass
            if not stat_parts: print_text("Please specify which stat."); continue
            stat_name = "_".join(stat_parts).lower()
            if stat_name not in stats: print_text(f"Invalid stat: '{stat_name}'."); continue
            if action == '+':
                if points < amount: print_text(f"You only have {points} points.")
                elif stats[stat_name] + amount > 30: print_text(f"{stat_name.title()} can't be higher than 30.")
                else: stats[stat_name] += amount; points -= amount
            elif action == '-':
                if stats[stat_name] - amount < 5: print_text(f"{stat_name.title()} can't be lower than 5.")
                else: stats[stat_name] -= amount; points += amount
        else:
            print_text("Invalid command.")
    player = stats
    player["squad_reputation"] = 50
    player["dispatch_reputation"] = 50
    player["investigative_reputation"] = 10
    player["current_day"] = 1
    player["unit_number"] = 0
    player["vehicle_issue"] = False
    player["special_assignment"] = None
    print_header("Officer Profile Confirmed")
    print_text("Welcome to the Department, rookie. Time to hit the streets.")
    input("\nPress Enter to continue to your first Roll Call...")

# ==============================================================================
# PRE-SHIFT AND END-OF-SHIFT ROUTINES
# ==============================================================================
def pre_shift_routine():
    global player
    clear_screen(); print_header("Roll Call")
    player['vehicle_issue'] = False
    event = random.choice(["bolo", "chew_out", "policy_update", "quick_roll_call"])
    player["unit_number"] = f"1-ADAM-{random.randint(10, 99)}"
    print_text(f"The Sergeant slaps the roster. 'Alright, listen up... Rookie, you're in {player['unit_number']} today.'")
    if event == "bolo": print_text("He drones on about a BOLO for a stolen sedan. Pay attention, it might be important.")
    elif event == "chew_out": print_text("He's pissed about some fuck-up on the last shift and rips into the whole squad. 'Don't be that guy,' he growls, looking right at you.")
    else: print_text("It's a quick, quiet roll call. The calm before the storm.")
    input("\nPress Enter to check out your shop...")
    clear_screen(); print_header("Vehicle Inspection")
    print_text("You grab the keys to your unit and do a quick walk-around.")
    if not skill_check("Perception"):
        print_text("Looks good to you. What could go wrong?")
        if random.randint(1, 4) == 1:
            player['vehicle_issue'] = True
            print_text("// You missed the slow leak in the front-right tire. That's gonna be a problem later. //", 0)
    else:
        print_text("Good catch. You spot a new dent on the fender that wasn't on the last checkout sheet. You log it, saving your ass some trouble with the fleet sergeant.")
        player['squad_reputation'] += 1
    print_text("You're logged into the CAD and ready to 10-8 (go in-service).")
    input("\nPress Enter to start your shift...")

def end_of_shift_summary(old_rep):
    print_header("End of Shift Summary")
    print_text("You're back at the station, logging off the computer. Another 10 hours in the bag.")
    
    print("\n--- REPUTATION CHANGES ---")
    squad_change = player['squad_reputation'] - old_rep['squad']
    dispatch_change = player['dispatch_reputation'] - old_rep['dispatch']
    investigative_change = player['investigative_reputation'] - old_rep['investigative']

    print(f"Squad Reputation: {player['squad_reputation']} ({squad_change:+.0f})")
    print(f"Dispatch Reputation: {player['dispatch_reputation']} ({dispatch_change:+.0f})")
    print(f"Investigative Reputation: {player['investigative_reputation']} ({investigative_change:+.0f})")
    print("--------------------------\n")

    if squad_change > 3:
        print_text("The squad seems impressed with your work today. You handled your shit.")
    elif squad_change < -3:
        print_text("You hear some guys talking shit as you walk to the locker room. You pissed off the wrong people today.")

    if dispatch_change > 2:
        print_text("Dispatch gives you a cheerful 'See you tomorrow!' over the radio. They like how you work.")
    
    if investigative_change > 4:
        print_text("A detective stops you on your way out, nods, and says 'Good work today.' You're getting noticed.")

    player['current_day'] += 1

# ==============================================================================
# --- MASSIVELY EXPANDED CALL DATABASE ---
# ==============================================================================

CALL_DATABASE = {
    # ==========================================================================
    # --- SERIOUS & IN-PROGRESS CRIMES (HIGH PRIORITY) ---
    # ==========================================================================
    "Assault In Progress": [
        {"summary": "A caller reports a fistfight between two men in a parking lot.", "twist": "It's a staged fight to distract from a car burglary.", "unfounded": "They were just roughhousing."},
        {"summary": "A woman is screaming for help as a man tries to drag her into a van.", "twist": "It's an undercover sting operation.", "unfounded": "They're filming an indie movie."},
        {"summary": "Report of a bouncer at a nightclub beating a patron bloody.", "twist": "The patron had a knife and tried to stab the bouncer.", "unfounded": "The 'blood' is just spilled red wine."},
        {"summary": "A caller sees a group of teenagers kicking someone on the ground.", "twist": "The 'victim' is a rival gang member who started the fight.", "unfounded": "It's a new member initiation for a martial arts club."},
        {"summary": "Report of an assault at a protest; someone is hitting people with a sign.", "twist": "The attacker is an undercover officer from another agency.", "unfounded": "It's performance art."},
        {"summary": "A road rage incident has escalated to a physical fight on the freeway shoulder.", "twist": "One of the drivers is a wanted fugitive and is desperate to get away.", "unfounded": "They are old friends who recognized each other and are play-fighting."},
        {"summary": "A landlord is physically trying to evict a tenant.", "twist": "The tenant is a sovereign citizen who has booby-trapped the apartment.", "unfounded": "It's a loud, dramatic argument with no physical contact."},
        {"summary": "A patient is attacking a nurse in a hospital room.", "twist": "The patient is having a severe reaction to medication.", "unfounded": "The nurse tripped and fell, and the patient was trying to help them up."},
        {"summary": "Caller reports someone being assaulted with a baseball bat.", "twist": "The 'victim' is a piñata at a birthday party.", "unfounded": "It was a heated argument over a baseball game, but no assault occurred."},
        {"summary": "A man is assaulting a vending machine that ate his dollar.", "twist": "The man is trying to retrieve a bag of drugs he stashed inside.", "unfounded": "He's just really, really angry at the machine."},
        {"summary": "Report of a sexual assault in a public library restroom.", "twist": "The 'victim' and 'assailant' are known con artists who stage this to sue businesses.", "unfounded": "Two people were just making out loudly."},
        {"summary": "A bus driver reports a passenger assaulting another passenger.", "twist": "It's a pickpocket who got caught and is now fighting the victim.", "unfounded": "One passenger accidentally fell onto the other."},
        {"summary": "A man is choking another man in a restaurant.", "twist": "He's performing the Heimlich maneuver.", "unfounded": "They were laughing so hard one started choking on their food."},
        {"summary": "Report of a fan assaulting a referee at a high school sports game.", "twist": "The referee is known for taking bribes to throw games.", "unfounded": "A fan just got too excited and stumbled into the ref."},
        {"summary": "A person is being attacked by a group of people in costume.", "twist": "It's a flash mob, and the 'victim' is in on it.", "unfounded": "A local LARPing group is having a very public battle."},
        {"summary": "Report of an assault with a deadly weapon: a skillet.", "twist": "It's a domestic dispute, and the skillet is full of hot oil.", "unfounded": "A chef dramatically flipped a pancake and it landed on someone."},
        {"summary": "A customer is throwing hot coffee on a barista.", "twist": "The barista is an ex-partner who has been stalking the customer.", "unfounded": "The customer tripped and accidentally spilled the coffee."},
        {"summary": "A mail carrier is being attacked by a resident.", "twist": "The resident suffers from dementia and thinks the mail carrier is an intruder.", "unfounded": "The resident's dog was just overly friendly and jumped on the carrier."},
        {"summary": "Caller reports seeing someone pushed off a bridge.", "twist": "It's a mannequin being used for a physics experiment.", "unfounded": "Someone threw a large bag of trash off the bridge."},
        {"summary": "A person is being held down and forcibly tattooed.", "twist": "It's a gang initiation.", "unfounded": "A fraternity prank has gotten out of hand."}
    ],
    "Robbery/Burglary In Progress": [
        {"summary": "Silent alarm at a downtown jewelry store.", "twist": "The robbers are professionals who have cut the phone lines.", "unfounded": "The owner's cat tripped the alarm."},
        {"summary": "A homeowner calls from a closet, whispering that someone is in their house.", "twist": "The 'burglar' is their son, sneaking back in after being grounded.", "unfounded": "The house is old and making strange noises."},
        {"summary": "Hold-up alarm at a check-cashing business.", "twist": "The robber is a disgruntled ex-employee who knows the layout.", "unfounded": "An employee accidentally leaned on the panic button."},
        {"summary": "A caller sees two men in ski masks breaking into a neighbor's home.", "twist": "They are bounty hunters, and the neighbor is a violent fugitive.", "unfounded": "The neighbors are having a ski-themed party."},
        {"summary": "Bank robbery in progress, caller is a teller.", "twist": "The robber's note claims there's a bomb in the building.", "unfounded": "A customer was trying to pass a note to the teller to ask them out."},
        {"summary": "Smash-and-grab at a high-end electronics store.", "twist": "The suspects are part of an organized retail crime ring.", "unfounded": "A car lost control and crashed through the front window."},
        {"summary": "A woman reports a man just broke into her apartment.", "twist": "It's her abusive ex-husband who has a restraining order against him.", "unfounded": "It's a new delivery person who went to the wrong apartment."},
        {"summary": "Report of a pharmacy robbery; suspect is demanding opioids.", "twist": "The suspect is an undercover DEA agent testing security.", "unfounded": "A patient was yelling at the pharmacist about a prescription."},
        {"summary": "Burglary in progress at a warehouse; security guard is not answering his phone.", "twist": "The robbers have taken the guard hostage.", "unfounded": "The guard is asleep."},
        {"summary": "A gas station clerk reports a man is robbing them with a syringe.", "twist": "The suspect is a known stick-up artist who is HIV positive.", "unfounded": "A diabetic was trying to show the clerk what kind of insulin they needed."},
        {"summary": "A man reports he is following a burglar who just left his home.", "twist": "The 'burglar' is actually the homeowner, and the caller is the burglar.", "unfounded": "A misunderstanding between a house-sitter and the homeowner."},
        {"summary": "A group of people are looting a store during a power outage.", "twist": "The store owner is among them, encouraging the looting for an insurance scam.", "unfounded": "The owner is giving away perishable goods before they spoil."},
        {"summary": "Burglary at a gun store; multiple firearms stolen.", "twist": "The burglars are arming themselves for a larger terrorist act.", "unfounded": "An employee who was recently fired is trying to get revenge."},
        {"summary": "A caller reports seeing someone climbing into the window of a church.", "twist": "The person is a homeless man who knows the priest lets him sleep there.", "unfounded": "A priest locked himself out and is trying to get back in."},
        {"summary": "A home invasion is in progress; caller says the intruders are armed.", "twist": "The intruders are rival drug dealers looking for a stash.", "unfounded": "The 'intruders' are the homeowner's kids playing a very realistic video game."},
        {"summary": "Robbery of an armored car. Guards are down.", "twist": "It was an inside job; one of the guards was part of the crew.", "unfounded": "A movie is being filmed in the street."},
        {"summary": "Burglary at a vet clinic.", "twist": "The burglars are animal rights activists 'liberating' the animals.", "unfounded": "An animal escaped its cage and is causing chaos."},
        {"summary": "A caller reports a real estate agent is being held up during an open house.", "twist": "The 'robber' is a potential buyer who is actually casing the house.", "unfounded": "The agent was just having a very loud, animated phone call."},
        {"summary": "A man is trying to break into a car in a parking garage.", "twist": "It's his own car, but he's being carjacked and is being forced to open it.", "unfounded": "He locked his keys in the car and is trying to get them out."},
        {"summary": "A convenience store is being robbed by a man in a Mickey Mouse costume.", "twist": "The man is a beloved local eccentric who is having a mental breakdown.", "unfounded": "It's a prank for a YouTube channel."}
    ],
    "Shooting/Stabbing": [
        {"summary": "Multiple calls reporting gunshots in an apartment complex.", "twist": "It's a murder-suicide over a love triangle.", "unfounded": "Someone is setting off powerful fireworks in the courtyard."},
        {"summary": "A man stumbles into a fire station with a stab wound to his chest.", "twist": "He's a government witness who was just attacked by a hitman.", "unfounded": "He fell on a piece of rebar at a construction site."},
        {"summary": "911 call with sounds of a gunshot and then silence.", "twist": "The caller shot an intruder who broke into their home.", "unfounded": "A phone was dropped, and the 'gunshot' was a car backfiring outside."},
        {"summary": "Report of a drive-by shooting in a residential neighborhood.", "twist": "The target was a high-ranking gang member under house arrest.", "unfounded": "A teenager's car with a modified, loud exhaust drove by."},
        {"summary": "A school principal reports a student has been stabbed in the hallway.", "twist": "The stabbing is related to a drug deal that went bad on campus.", "unfounded": "A student was injured in shop class, and another student is panicking."},
        {"summary": "Reports of an active shooter in a shopping mall.", "twist": "The 'shooter' is a disgruntled employee targeting a specific store manager.", "unfounded": "A large sign fell in the food court, creating a loud bang that caused a panic."},
        {"summary": "A caller reports their neighbor was just shot through the window.", "twist": "The shooter was aiming for the caller, not the neighbor.", "unfounded": "A stray bullet from hunters in a nearby woods."},
        {"summary": "A man has been stabbed with a broken bottle during a bar fight.", "twist": "The man who did the stabbing is an off-duty police officer.", "unfounded": "Someone just broke a bottle; no one was actually stabbed."},
        {"summary": "Gunshots reported at a wedding reception.", "twist": "The bride's ex-boyfriend showed up and started shooting.", "unfounded": "It was a traditional celebratory gunfire, but it scared some guests."},
        {"summary": "A park ranger reports finding a body with multiple gunshot wounds.", "twist": "The body is a federal agent who was working undercover.", "unfounded": "It's a realistic mannequin used for a search-and-rescue drill."},
        {"summary": "A stabbing occurred on a public bus; the bus is stopped and the suspect is still on board.", "twist": "The suspect is a mentally ill person who is now terrified and cornered.", "unfounded": "A passenger with a fake knife prop was joking around and caused a panic."},
        {"summary": "A person has been shot with a crossbow.", "twist": "It's a dispute between two medieval reenactors that got too real.", "unfounded": "A hunter's bow misfired, sending an arrow into a backyard."},
        {"summary": "A caller reports hearing a single gunshot and seeing a man run from a house.", "twist": "The man who ran is the victim, trying to escape.", "unfounded": "A tire blew out on a car, and a man was running to catch a bus."},
        {"summary": "Report of a stabbing at a homeless encampment.", "twist": "The stabbing was over a stolen pair of shoes.", "unfounded": "Two people were in a loud argument, but no weapon was involved."},
        {"summary": "Gunshots fired in a library.", "twist": "The shooter is a conspiracy theorist trying to destroy 'government propaganda.'", "unfounded": "A librarian dropped a very large stack of books."},
        {"summary": "A woman was stabbed with a pair of scissors at a hair salon.", "twist": "It was a rival stylist trying to ruin her competitor's career.", "unfounded": "The stylist tripped while holding scissors, causing an accidental injury."},
        {"summary": "Gunfire exchanged between two moving vehicles on the highway.", "twist": "It's a rolling gun battle between two rival biker gangs.", "unfounded": "Both drivers had malfunctioning cars that were backfiring loudly."},
        {"summary": "A man was shot in the leg with a nail gun at a construction site.", "twist": "It was an intentional act by a coworker over a gambling debt.", "unfounded": "A simple, but serious, workplace accident."},
        {"summary": "Report of a stabbing at a political rally.", "twist": "The victim is a politician, and the attacker is from an extremist group.", "unfounded": "Someone accidentally stuck another person with their protest sign."},
        {"summary": "A person was shot during a hunting trip.", "twist": "It wasn't an accident; the shooter mistook the victim for a person they had a grudge against.", "unfounded": "A classic, tragic hunting accident."}
    ],
    "Violent Domestic": [
        {"summary": "A child calls 911 and says 'Daddy is hurting Mommy.'", "twist": "Daddy is a wanted felon for domestic violence and has a firearm.", "unfounded": "The parents were watching a violent movie and the child got scared."},
        {"summary": "A neighbor reports a woman screaming and sounds of breaking glass.", "twist": "The couple are meth addicts, and the fight is over a stolen stash.", "unfounded": "The couple dropped a large mirror while trying to hang it."},
        {"summary": "A man calls and says his wife came at him with a knife.", "twist": "The man is the primary abuser and is trying to set his wife up.", "unfounded": "The wife was just chopping vegetables very aggressively during an argument."},
        {"summary": "A woman calls from a bathroom, whispering that her husband is threatening to kill her.", "twist": "The husband is a police officer.", "unfounded": "She has a history of making false reports against her husband during arguments."},
        {"summary": "A third-party caller reports a fight in the apartment above them; they heard a body hit the floor.", "twist": "It's an elderly couple, and one has fallen and needs medical aid.", "unfounded": "Someone just moved a heavy piece of furniture."},
        {"summary": "A man is outside his ex-wife's house, trying to break down the door.", "twist": "He believes she is harming their child inside.", "unfounded": "He's drunk and went to the wrong house."},
        {"summary": "A couple is fighting in a car, and the woman is trying to jump out while it's moving.", "twist": "The man just told her he's a confidential informant and their lives are in danger.", "unfounded": "She's car sick and he won't pull over."},
        {"summary": "A call from a motel room; a woman is heard crying and a man is yelling about money.", "twist": "It's a pimp beating one of his prostitutes.", "unfounded": "They're arguing over gambling losses from a nearby casino."},
        {"summary": "A landlord reports a violent domestic from a tenant's apartment; he sees blood under the door.", "twist": "The 'blood' is red paint from an art project, but the tenant is being held hostage inside.", "unfounded": "The tenant spilled a bottle of wine and is now loudly blaming his partner."},
        {"summary": "A caller reports seeing a man hold a gun to a woman's head in a neighboring house.", "twist": "It's a realistic-looking toy gun, but the man is still threatening her.", "unfounded": "They are actors rehearsing for a play."},
        {"summary": "A teenage girl calls, saying her father is attacking her mother because she's leaving him.", "twist": "The father has barricaded the family in the house.", "unfounded": "The father is just yelling and throwing his own clothes around."},
        {"summary": "A postal worker reports a domestic disturbance; a woman ran out of the house with a black eye.", "twist": "The woman is a victim of human trafficking and is trying to escape.", "unfounded": "She walked into a door and was running out to stop the mail carrier for a package."},
        {"summary": "A man reports his brother is smashing up the house and threatening their elderly mother.", "twist": "The brother is high on PCP and is extremely violent.", "unfounded": "The brother is just having a massive tantrum, but isn't a physical threat."},
        {"summary": "A woman calls, saying her boyfriend is drunk and has firearms all over the house.", "twist": "He's a gun collector, but he's also a paranoid schizophrenic off his meds.", "unfounded": "He's cleaning his collection, and she's uncomfortable with it."},
        {"summary": "A fight has spilled out from a house into the front yard.", "twist": "It's two brothers fighting over the inheritance from their recently deceased parents.", "unfounded": "They're fighting over the rules of a backyard football game."},
        {"summary": "A man calls 911, states his name and address, says 'I'm sorry,' and then a gunshot is heard.", "twist": "It's a murder-suicide.", "unfounded": "He shot a hole in the wall out of anger and is now remorseful."},
        {"summary": "A neighbor reports a couple is fighting and has thrown their baby's crib out the window.", "twist": "The couple's baby died recently, and this is a grief-fueled breakdown.", "unfounded": "They were throwing out old, broken furniture."},
        {"summary": "A woman is locked on a balcony, screaming that her husband has a knife.", "twist": "The husband is a chef who is just trying to show her a new knife he bought.", "unfounded": "She locked herself out by accident and is panicking."},
        {"summary": "A son reports his stepfather is attacking his mother in their garage.", "twist": "The stepfather is a mechanic who has rigged the garage door to trap her.", "unfounded": "A car fell off a jack, pinning the mother, and the stepfather is trying to free her."},
        {"summary": "Silent 911 call. On callback, a woman answers and says everything is fine, using a known verbal code for duress.", "twist": "Her abuser is standing right next to her, monitoring the call.", "unfounded": "The dispatcher made a mistake; there was no duress code used."}
    ],
    "Carjacking In Progress": [
        {"summary": "A woman reports a man with a gun just stole her car from a gas station pump.", "twist": "Her child is still in the back seat.", "unfounded": "The 'carjacker' is a valet from a nearby restaurant who took the wrong car."},
        {"summary": "A man reports he's just been carjacked in a parking garage.", "twist": "The carjackers were waiting for him; it's a targeted attack.", "unfounded": "His car was repossessed, and he thought it was being stolen."},
        {"summary": "A driver calls 911, stating a man on a motorcycle is pointing a gun at him, forcing him to pull over.", "twist": "The man on the motorcycle is an off-duty cop who witnessed the driver commit a felony.", "unfounded": "It's an aggressive case of road rage."},
        {"summary": "An elderly man reports his classic car was just stolen from him at a red light.", "twist": "The carjacker is a member of a high-end international car theft ring.", "unfounded": "He forgot he had lent the car to his grandson for the day."},
        {"summary": "A food delivery driver has been carjacked; the suspect is now driving the car.", "twist": "The car has a GPS tracker, but the suspect is heading towards the state line.", "unfounded": "The driver's friend was playing a prank and took the car."},
        {"summary": "A caller reports a carjacking at a car wash.", "twist": "The suspect is an escaped prisoner from a nearby correctional facility.", "unfounded": "An employee got into the wrong car by mistake."},
        {"summary": "A rideshare driver reports his passenger pulled a knife on him and stole the vehicle.", "twist": "The passenger is a fugitive who is trying to flee the state.", "unfounded": "The passenger was angry about the fare and just ran off without paying."},
        {"summary": "A woman reports her car was just taken by a man who claimed to be a plainclothes officer.", "twist": "The man is a known police impersonator who targets women.", "unfounded": "It was a legitimate plainclothes officer commandeering the vehicle for an emergency."},
        {"summary": "A carjacking has occurred, and the victim's dog is still inside the vehicle.", "twist": "The dog is a trained K-9, and the victim is a retired officer.", "unfounded": "The dog is just a pet, but the owner is hysterical."},
        {"summary": "A parent reports their minivan was stolen from their driveway while their child was getting in.", "twist": "It's a custody dispute; the other parent took the child and the van.", "unfounded": "The parent's older child took the van without asking."},
        {"summary": "A carjacking victim is clinging to the roof of their stolen car as it speeds down the street.", "twist": "The victim is a trained stuntman and is trying to get his car back.", "unfounded": "This is a scene for a movie being filmed without proper permits."},
        {"summary": "A car dealer reports a potential customer pulled a gun during a test drive and stole the car.", "twist": "The 'customer' left behind a fake ID that is linked to a terrorist watch list.", "unfounded": "The customer just had a medical emergency and drove off erratically."},
        {"summary": "A valet reports a customer's car was stolen at gunpoint from the valet stand.", "twist": "The car belongs to a notorious mob boss.", "unfounded": "The car's owner took their own car back without giving the valet the ticket."},
        {"summary": "A carjacking is reported, but the victim seems oddly calm.", "twist": "The victim arranged the carjacking to commit insurance fraud.", "unfounded": "The victim is in shock."},
        {"summary": "A man reports his work van, full of expensive tools, was just carjacked.", "twist": "The tools are for breaking into safes; the victim is a professional burglar.", "unfounded": "The tools are just standard construction equipment."},
        {"summary": "A carjacking is reported at a national park scenic overlook.", "twist": "The carjackers are poachers who were interrupted while loading an illegal kill.", "unfounded": "A bear scared the driver out of their car, and another tourist jumped in to move it."},
        {"summary": "A truck driver reports his semi-truck was stolen while he was sleeping at a rest stop.", "twist": "The truck is carrying millions of dollars worth of pharmaceuticals.", "unfounded": "He parked in the wrong spot, and it was towed."},
        {"summary": "A carjacker took a car, but didn't realize it was an electric vehicle with very low battery.", "twist": "The car is now stranded, and the suspect is on foot nearby.", "unfounded": "The car's GPS is just lagging."},
        {"summary": "A car was carjacked from an airport rental lot.", "twist": "The suspect is trying to flee the country and is heading for a private airfield.", "unfounded": "A rental employee took the wrong car to a customer."},
        {"summary": "A carjacking reported by a third party who saw it happen.", "twist": "The 'victim' and 'carjacker' are undercover officers practicing a maneuver.", "unfounded": "The caller misunderstood a couple having a loud argument over the car keys."}
    ],
    # --- The absolute highest priority calls are handled specially ---
    # These are placeholders; the real logic will be handled by a special function.
    "Homicide": [{"summary": "Initial report of a deceased person.", "twist": "Scene is contaminated.", "unfounded": "False report."}],
    "Kidnapping": [{"summary": "Initial report of an abduction.", "twist": "Victim is not who they seem.", "unfounded": "Custody dispute."}],
    "Bomb Threat": [{"summary": "Report of an explosive device.", "twist": "Secondary device suspected.", "unfounded": "Swatting incident."}],
    "Officer Needs Assistance": [{"summary": "Officer in trouble.", "twist": "Ambush.", "unfounded": "Accidental activation."}],

    # ==========================================================================
    # --- Standard Low-Priority Calls ---
    # ==========================================================================
    "Welfare Check": [
        {"summary": "Caller worried about their elderly neighbor. Mail is piling up.", "twist": "medical emergency", "unfounded": "on vacation"},
        {"summary": "A mail carrier reports a foul smell from a residence.", "twist": "deceased person", "unfounded": "dead animal under porch"},
        {"summary": "A child called 911 saying they can't wake up their mommy.", "twist": "drug overdose", "unfounded": "heavy sleeper"},
        {"summary": "A woman hasn't shown up for work for two days.", "twist": "being held against her will", "unfounded": "won lottery and quit"},
        {"summary": "Medical alert company lost signal from a client's pendant.", "twist": "pendant broke during a fall", "unfounded": "pendant battery died"}
    ],
    "Suspicious Person": [
        {"summary": "A man in a hoodie has been loitering near an alley for an hour.", "twist": "has a warrant", "unfounded": "waiting for a friend"},
        {"summary": "A caller reports someone looking into parked cars with a flashlight.", "twist": "car burglary in progress", "unfounded": "looking for dropped keys"},
        {"summary": "Reports of someone trying door handles at a strip mall late at night.", "twist": "new owner who forgot keys", "unfounded": "prank call"},
        {"summary": "A person is sitting on a park bench, staring at a playground.", "twist": "registered sex offender", "unfounded": "parent waiting for kid"},
        {"summary": "A well-dressed person is taking photos of a bank.", "twist": "casing the bank for robbery", "unfounded": "architecture student"}
    ],
    "Vandalism Report": [
        {"summary": "A business owner reports fresh graffiti on his storefront.", "twist": "gang-related tag", "unfounded": "commissioned art"},
        {"summary": "A caller reports their car tires have been slashed.", "twist": "angry ex-partner", "unfounded": "ran over nails"},
        {"summary": "Someone threw a rock through a homeowner's window.", "twist": "bullying escalation", "unfounded": "stray baseball"},
        {"summary": "All the mailboxes on a street have been smashed.", "twist": "intoxicated college students filmed it", "unfounded": "drunk driver"},
        {"summary": "A car has been covered in eggs and toilet paper.", "twist": "witness intimidation", "unfounded": "senior prank"}
    ],
    "Noise Complaint": [
        {"summary": "Loud music and shouting from an apartment.", "twist": "domestic dispute", "unfounded": "TV too loud"},
        {"summary": "A caller complains about their neighbor mowing their lawn at 6 AM.", "twist": "ongoing property line dispute", "unfounded": "inconsiderate neighbor"},
        {"summary": "Reports of what sounds like a gunshot from a nearby home.", "twist": "homicide", "unfounded": "car backfiring"},
        {"summary": "A party has gotten out of control and is spilling into the street.", "twist": "cover for a drug deal", "unfounded": "standard college party"},
        {"summary": "A neighbor reports a baby has been crying non-stop for hours.", "twist": "baby has been abandoned", "unfounded": "colicky baby"}
    ],
    "Trespassing": [
        {"summary": "Manager wants a person sleeping in their doorway removed.", "twist": "missing person", "unfounded": "person leaves without issue"},
        {"summary": "A group of teenagers are skateboarding on private property.", "twist": "drugs on one teen", "unfounded": "they leave when told"},
        {"summary": "A homeowner reports someone is in their backyard.", "twist": "burglary attempt", "unfounded": "neighbor's kid looking for lost dog"},
        {"summary": "A farmer reports people on his land with metal detectors.", "twist": "they found human remains", "unfounded": "hobbyists who didn't know"},
        {"summary": "A security guard at a construction site has detained a trespasser.", "twist": "investigative journalist", "unfounded": "drunk who wandered in"}
    ],
    "Intoxicated Person": [
        {"summary": "A person is stumbling in and out of traffic.", "twist": "medical issue", "unfounded": "just tripped badly"},
        {"summary": "A man is passed out on a park bench.", "twist": "parole violation", "unfounded": "just napping"},
        {"summary": "A caller reports a drunk person trying to start a fight at a bar.", "twist": "undercover vice cop", "unfounded": "regular drunk asshole"},
        {"summary": "A woman is crying and appears very drunk sitting on a curb.", "twist": "victim of a recent sexual assault", "unfounded": "bad breakup"},
        {"summary": "A driver is passed out behind the wheel of a running car at a green light.", "twist": "heroin overdose", "unfounded": "dangerously sleep-deprived"}
    ],
    "Animal Problem": [
        {"summary": "An aggressive-looking dog is roaming loose.", "twist": "protecting puppies", "unfounded": "it's a friendly dog"},
        {"summary": "A caller reports a large snake in their garage.", "twist": "escaped exotic pet", "unfounded": "harmless garden snake"},
        {"summary": "A woman reports a cat is stuck in a tree.", "twist": "cat's microchip links to a homicide victim", "unfounded": "just a cat in a tree"},
        {"summary": "A driver reports a large deer is injured on the side of the road.", "twist": "hit by a car involved in a hit-and-run", "unfounded": "just a deer hit by a car"},
        {"summary": "A caller reports a swarm of bees is attacking people.", "twist": "illegal, unregistered apiary", "unfounded": "someone disturbed a wild hive"}
    ]
}

# This list will be used to trigger immediate, game-interrupting events.
CRITICAL_CALL_TYPES = ["Officer Needs Assistance", "Homicide", "Kidnapping", "Bomb Threat"]

# ==============================================================================
# MISSION & ACTION HANDLERS
# ==============================================================================
def display_call_slip(call):
    clear_screen(); print_header(f"CALL SLIP: {call['type']}")
    print_text(f"ID: {call['id']}\nPRIORITY: {call['priority']}\nADDRESS: {call['address']}\nSUMMARY: {call['summary']}")
    input("\nPress Enter to proceed...")

def clear_call_menu(outcomes):
    global shift_time_remaining
    print_header("Clear Call")
    for i, outcome in enumerate(outcomes): print(f"{i+1}: {outcome['desc']} ({outcome['time_cost']} mins)")
    print(f"{len(outcomes)+1}: Ride the call... (90 mins)")
    while True:
        choice = get_input()
        if choice.isdigit() and 1 <= int(choice) <= len(outcomes) + 1:
            if int(choice) - 1 < len(outcomes):
                selected = outcomes[int(choice) - 1]
                shift_time_remaining -= selected['time_cost']
                end_call(selected['message'], **selected.get('rep_changes', {}))
            else:
                shift_time_remaining -= 90
                end_call("You take your sweet time on the report, burning the clock. The squad won't like that.", squad_reputation=-3, dispatch_reputation=-2)
            return

def end_call(message, **kwargs):
    print_header("Call Concluded"); print_text(message)
    for rep, change in kwargs.items():
        if rep in player:
            player[rep] += change
            print_text(f"// {rep.replace('_', ' ').title()} changed by {change:+.0f} //", 0.5)
    input("\nPress Enter to return to service...")

def handle_generic_call(call):
    display_call_slip(call)
    print_text("You arrive on scene and assess the situation.")
    
    if random.randint(1, 10) == 1:
        print_text("You get there and... nothing. The call was completely unfounded. What a waste of time.")
        clear_call_menu([{"desc": "Clear the call as unfounded.", "time_cost": 15, "message": "You clear the call. Dispatch appreciates the quick turnaround.", "rep_changes": {"dispatch_reputation": 1}}])
        return

    print("\n1: Investigate the scene (Perception)\n2: Talk to people involved (De-escalation)\n3: Take command of the situation (Command Presence)")
    choice = get_input()

    if choice == '1':
        if skill_check("Perception"):
            print_text("Your sharp eyes notice something important that changes the call entirely.")
            if random.randint(1, 4) == 1:
                 print_text(f"Turns out, the situation is completely baseless. It was just {call['unfounded']}.")
                 clear_call_menu([{"desc": "Report the call as unfounded.", "time_cost": 20, "message": "Good police work. You figured out the call was bogus and cleared it fast.", "rep_changes": {"dispatch_reputation": 2, "investigative_reputation": 1}}])
            else:
                print_text(f"The hidden detail is: {call['twist']}")
                clear_call_menu([{"desc": "Act on new info and make a good arrest/report.", "time_cost": 60, "message": "Your key observation leads to a successful resolution and a solid report.", "rep_changes": {"investigative_reputation": 3, "squad_reputation": 1}}])
        else:
            print_text("You look around, but don't see anything out of the ordinary. Just another call.")
            clear_call_menu([{"desc": "File a routine report.", "time_cost": 25, "message": "You handle it as a standard call.", "rep_changes": {"dispatch_reputation": 1}}])
    elif choice == '2':
        if skill_check("De-escalation"):
             print_text("You talk to the people involved and manage to calm the situation down completely.")
             clear_call_menu([{"desc": "De-escalate and clear.", "time_cost": 30, "message": "Your calm demeanor resolved the issue without incident. Solid work.", "rep_changes": {"dispatch_reputation": 1, "squad_reputation": 1}}])
        else:
             print_text("Your attempt to talk things out only makes things more tense. People start shouting over you.")
             clear_call_menu([{"desc": "Back off and let things cool down.", "time_cost": 20, "message": "You couldn't resolve it with words. The situation fizzles out on its own, but you looked ineffective.", "rep_changes": {"squad_reputation": -1}}])
    elif choice == '3':
        if skill_check("Command Presence"):
             print_text("You take charge of the scene with unshakeable authority. Everyone immediately shuts up and complies.")
             clear_call_menu([{"desc": "Take control and clear.", "time_cost": 25, "message": "Your command presence brought a swift end to the situation. Textbook.", "rep_changes": {"squad_reputation": 2}}])
        else:
            print_text("You try to take charge, but they ignore you, seeing you as a rookie with no real authority.")
            clear_call_menu([{"desc": "Call for a supervisor.", "time_cost": 45, "message": "You had to call for a supervisor to get them to comply. Not a good look, rookie.", "rep_changes": {"squad_reputation": -3, "dispatch_reputation": -1}}])
    else:
        print_text("You hesitate, unsure what to do. The situation resolves itself, but you missed your chance to act.")
        clear_call_menu([{"desc": "Clear the call.", "time_cost": 15, "message": "You clear the call without taking any significant action.", "rep_changes": {"squad_reputation": -1}}])

def handle_proactive_patrol():
    global shift_time_remaining
    print_text("You decide to skip the queue and go looking for trouble...")
    shift_time_remaining -= 45
    
    event_roll = random.randint(1, 10)
    if event_roll <= 3:
        end_call("You spend an hour on proactive patrol. The city is quiet. For now.")
    elif event_roll <= 6:
        print_text("While cruising the back alleys, you spot a car that looks out of place.")
        if skill_check("Law Knowledge"):
            end_call("You run the plates and it comes back stolen. You recover the vehicle. Easy win.", investigative_reputation=3, dispatch_reputation=1)
        else:
            end_call("You run the plates but screw up the number. Comes back clean. You move on, not realizing you just missed a stolen car.", investigative_reputation=-1)
    elif event_roll <= 9:
        print_text("You see what looks like a hand-to-hand drug deal going down on a street corner.")
        if skill_check("Strength"):
            end_call("You catch the dealer after a short foot chase. A bag of dope and a warrant. Great bust.", investigative_reputation=5, squad_reputation=1)
        else:
            end_call("The dealer is too fast. He disappears into an alleyway and you lose him. Dammit.", investigative_reputation=-2, squad_reputation=-1)
    else:
        print_text("Holy shit. You just witnessed a felony traffic stop turn into a shootout.")
        if skill_check("Marksmanship"):
            end_call("You engage the suspect and win the gunfight. You're a hero. Command is ecstatic and the squad is buying you drinks.", investigative_reputation=15, squad_reputation=5)
        else:
            end_call("Your shots go wide. The suspect gets away. You're not hurt, but you'll be answering for every missed round to Internal Affairs.", investigative_reputation=-5, squad_reputation=-3)

def handle_critical_incident():
    global shift_time_remaining
    call_type = random.choice(CRITICAL_CALL_TYPES)
    clear_screen(); print_header(f"!!! CRITICAL INCIDENT - {call_type.upper()} !!!")
    print_text("The radio crackles to life. All other traffic stops. The dispatcher's voice is strained with urgency.")
    print_text(f"'All units, all units... we have a confirmed {call_type} at {random.randint(100, 9999)} {random.choice(['MLK Blvd', 'Grand Ave', 'Industrial Pkwy'])}.'")
    print_text(f"'{player['unit_number']}, you are the closest unit. Respond CODE 3! Acknowledge!'")
    
    time_cost = random.randint(150, 240)
    shift_time_remaining -= time_cost
    
    input("\nPress Enter to acknowledge the call and respond...")
    print_text("\nThe next few hours are a whirlwind of adrenaline, fear, and chaos. Sirens, shouting, and sheer sensory overload.")
    print_text("After what feels like an eternity, the scene is secured.")
    
    if call_type == "Officer Needs Assistance":
        end_call("You arrived just in time to save a fellow officer from an ambush. You're a goddamn hero. The entire department owes you one.", squad_reputation=15, investigative_reputation=5)
    elif call_type == "Homicide":
        end_call("You were first on scene at a homicide. You secured the scene perfectly, preserving crucial evidence. Detectives are thrilled.", investigative_reputation=10, squad_reputation=2)
    else:
        end_call("You performed your duties admirably in a high-stress situation that would break most people. Command is impressed.", squad_reputation=5, investigative_reputation=10)

def check_for_random_events():
    global shift_time_remaining
    if player['vehicle_issue'] and random.randint(1, 30) == 1:
        print_header("!!! MECHANICAL FAILURE !!!")
        print_text("That issue you missed earlier? Yeah, your tire just blew out on the highway. Fucking fantastic.")
        shift_time_remaining -= 60
        player['squad_reputation'] -= 2
        player['vehicle_issue'] = False
        input("\nPress Enter to continue after the delay...")
        return True
    return False

# ==============================================================================
# MAIN GAME LOGIC
# ==============================================================================
def generate_calls():
    global call_queue, call_id_counter
    if not call_queue:
        num_calls = random.randint(4, 7)
        all_call_types = list(CALL_DATABASE.keys())
        standard_call_types = [t for t in all_call_types if t not in CRITICAL_CALL_TYPES]
        high_priority_call_types = ["Assault In Progress", "Robbery/Burglary In Progress", "Shooting/Stabbing", "Violent Domestic", "Carjacking In Progress"]

        for _ in range(num_calls):
            priority_roll = random.randint(1, 8)
            if priority_roll == 1:
                call_type = random.choice(high_priority_call_types)
                priority = "HIGH"
            else:
                call_type = random.choice(standard_call_types)
                priority = random.randint(1, 5)

            call_details = random.choice(CALL_DATABASE[call_type])
            new_call = {'id': call_id_counter, 'type': call_type, 'priority': priority, 'address': f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Ln', 'Maple Ct'])}", 'summary': call_details['summary'], 'twist': call_details['twist'], 'unfounded': call_details['unfounded']}
            call_queue.append(new_call)
            call_id_counter += 1

def start_new_shift():
    global shift_time_remaining
    shift_time_remaining = 600
    pre_shift_routine()
    generate_calls()

def main():
    clear_screen()
    print_header("ROOKIE: The First Ten Hours")
    print_text("A gritty, realistic, text-based police RPG.")
    input("\nPress Enter to begin...")
    
    character_creation()

    while True:
        start_new_shift()
        
        old_rep = {'squad': player['squad_reputation'], 'dispatch': player['dispatch_reputation'], 'investigative': player['investigative_reputation']}

        while shift_time_remaining > 0:
            generate_calls()
            
            if check_for_random_events(): continue
            if random.randint(1, 40) == 1: handle_critical_incident(); continue
            
            clear_screen()
            hours, minutes = divmod(shift_time_remaining, 60)
            current_date = START_DATE + timedelta(days=player['current_day'] - 1)
            date_str = current_date.strftime("%A, %B %d, %Y")
            
            print_header(f"ON DUTY - UNIT {player['unit_number']} - {date_str}")
            print(f"Time Left on Shift: {hours:02d}h {minutes:02d}m".center(60))
            
            print("--- CAD (Computer Aided Dispatch) ---")
            
            def sort_key(call):
                p = call['priority']
                if isinstance(p, str): return (0, p)
                return (1, -p) # Sort descending for numbers (5 is higher than 1)
            call_queue.sort(key=sort_key)

            for call in call_queue:
                print(f"ID: {call['id']:<3} | PRI: {str(call['priority']):<5} | TYPE: {call['type']:<30}")
            print("-------------------------------------")

            print("\nCOMMANDS: 'take [id]' | 'lookup [id]' | 'proactive' | 'sheet' | 'quit'")
            
            choice_input = get_input().split()
            if not choice_input: continue
            action = choice_input[0]

            if action == "take":
                if len(choice_input) < 2 or not choice_input[1].isdigit(): 
                    print_text("You gotta specify a valid call ID number."); continue
                call_id = int(choice_input[1])
                call_to_handle = next((c for c in call_queue if c['id'] == call_id), None)
                if call_to_handle:
                    call_queue = [c for c in call_queue if c['id'] != call_id]
                    handle_generic_call(call_to_handle)
                else: 
                    print_text("That call ID doesn't exist.")
            
            elif action == "lookup":
                if len(choice_input) < 2 or not choice_input[1].isdigit(): 
                    print_text("Lookup which call ID?"); continue
                call_id = int(choice_input[1])
                call = next((c for c in call_queue if c['id'] == call_id), None)
                if call: display_call_slip(call)
                else: print_text("Invalid call ID.")

            elif action == "proactive":
                handle_proactive_patrol()
            
            elif action == "sheet":
                clear_screen(); print_header("Officer Character Sheet")
                for key, value in player.items(): 
                    print(f"{key.replace('_', ' ').title():<25}: {value}")
                input("\nPress Enter to return to duty...")
            
            elif action == "quit": 
                shift_time_remaining = 0
            
            else: 
                print_text("That's not a valid command.")

        end_of_shift_summary(old_rep)
        
        print("\nStart next shift? (y/n)")
        if get_input() != 'y':
            print_text("Thanks for playing! Stay safe out there.")
            break

if __name__ == "__main__":
    main()