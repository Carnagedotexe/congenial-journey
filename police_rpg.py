import random
import time
import textwrap
import os

# ==============================================================================
# GAME STATE AND PLAYER DATA
# ==============================================================================
player = {}
call_queue = []
game_time = 0 # Simple turn counter

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    """Prints a nice-looking header for different sections."""
    print("\n" + "="*50)
    print(f" {title.upper()} ".center(50))
    print("="*50)

def print_text(text, delay=0.75):
    """Prints text with word wrapping for better readability."""
    print(textwrap.fill(text, width=60))
    time.sleep(delay)

def get_input(prompt="> "):
    """Gets sanitized input from the player."""
    return input(prompt).strip().lower()

def skill_check(skill_name):
    """Performs a probability check with the 'Rookie Bonus'."""
    skill_key = skill_name.lower().replace(" ", "_")
    if skill_key not in player:
        print(f"ERROR: Skill '{skill_name}' not found!")
        return False
    
    roll = random.randint(1, 100)
    skill_value = player[skill_key]
    rookie_bonus = 30 # <-- THE NEW ROOKIE BONUS
    effective_skill = skill_value + rookie_bonus

    print_text(f"// Rolling for {skill_name}... Target: {effective_skill} (Skill: {skill_value} + Bonus: {rookie_bonus}). Roll: {roll}. //")

    if roll <= effective_skill:
        print_text("// SUCCESS! //")
        return True
    else:
        print_text("// FAILURE! //")
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
        if points == 0: print("\nAll points spent! Type 'done' to begin your first shift.")
        choice = get_input()
        parts = choice.split()
        if not parts: continue
        action = parts[0]
        if action == "done":
            if points == 0: break
            else: print_text(f"You still have {points} points to spend!")
        elif action == "randomize":
            stats = {key: 5 for key in stats}; points = 40
            stat_keys = list(stats.keys())
            for _ in range(40):
                chosen_stat = random.choice(stat_keys)
                if stats[chosen_stat] < 30: stats[chosen_stat] += 1
            points = 0
        elif action in ['+', '-']:
            if len(parts) < 2: print_text("Please specify which stat."); continue
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
        else: print_text("Invalid command.")
    player = stats
    player["squad_reputation"] = 50
    player["dispatch_reputation"] = 50
    player["investigative_reputation"] = 10
    player["unit_number"] = 0
    player["inventory"] = []
    player["vehicle_issue"] = False
    print_header("Officer Profile Confirmed")
    print_text("Time to hit the streets.")
    input("\nPress Enter to continue to Roll Call...")

# ==============================================================================
# PRE-SHIFT ROUTINE
# ==============================================================================

def pre_shift_routine():
    clear_screen()
    print_header("Roll Call")
    print_text("The squad room smells of stale coffee and disinfectant...")
    player["unit_number"] = random.randint(10, 99)
    print_text(f"'You're riding solo today. Unit {player['unit_number']}.'")
    print_text("The Sergeant drones on about a BOLO for a blue Honda Civic involved in recent thefts.")
    input("\nPress Enter to head to the Radio Room...")
    clear_screen()
    print_header("Equipment Checkout")
    print_text("You grab the keys for your shop...")
    input("\nPress Enter to inspect your vehicle...")
    clear_screen()
    print_header("Vehicle Inspection")
    print_text("You walk out to the parking lot and find your shop...")
    if skill_check("Perception"):
        print_text("Good eye. You spot a fresh scratch on the passenger side door that wasn't on the log. You note it down.")
        player['squad_reputation'] += 1
    else:
        print_text("Everything looks fine. You hop in.")
        if random.randint(1, 4) == 1:
             player['vehicle_issue'] = True
             print_text("// You missed something... //", delay=0.2)
    print_text("You load up your gear, fire up the MDT, and log into the CAD system.")
    input("\nPress Enter to go on duty...")

# ==============================================================================
# CALL & EVENT GENERATION
# ==============================================================================

def generate_calls():
    global call_queue
    call_queue = []
    call_options = [
        {"id": 1, "priority": 4, "type": "Noise Complaint", "waiting": random.randint(5, 15), "address": "123 Main St."},
        {"id": 2, "priority": 4, "type": "Suspicious Person", "waiting": random.randint(5, 15), "address": "Oak & 3rd"},
        {"id": 3, "priority": 3, "type": "Shoplifting", "waiting": random.randint(1, 5), "address": "Quick-E-Mart"}
    ]
    random.shuffle(call_options)
    call_queue.extend(call_options)
    call_types = ["Vandalism Report", "Theft Report"]
    for i in range(random.randint(0, 1)):
        call_queue.append({
            "id": i + 4,
            "priority": random.randint(3, 4),
            "type": random.choice(call_types),
            "waiting": random.randint(1, 20),
            "address": f"{random.randint(100, 999)} {random.choice(['Elm', 'Pine', 'Maple'])} St."
        })

# ==============================================================================
# MISSION AND BRANCHING FUNCTIONS
# ==============================================================================

def end_call(message, dispatch_rep=0, squad_rep=0, investigative_rep=0):
    print_header("Call Concluded")
    print_text(message)
    if dispatch_rep != 0: player["dispatch_reputation"] += dispatch_rep; print_text(f"Dispatch Reputation changed by {dispatch_rep}.")
    if squad_rep != 0: player["squad_reputation"] += squad_rep; print_text(f"Squad Reputation changed by {squad_rep}.")
    if investigative_rep != 0: player["investigative_reputation"] += investigative_rep; print_text(f"Investigative Reputation changed by {investigative_rep}.")
    input("\nPress Enter to return to the call queue...")

def handle_generic_call(call):
    clear_screen()
    print_header(f"Responding to: {call['type']}")
    print_text(f"You arrive at {call['address']}. After a brief investigation, you determine it's a simple report call.")
    end_call("The call was routine. Report filed.", dispatch_rep=2, squad_rep=1)

def handle_proactive_choice():
    clear_screen()
    print_header("Proactive Policing")
    is_busy = len(call_queue) >= 3
    if is_busy: print_text("The call board is busy. Going proactive will piss off your squad mates and dispatch.")
    else: print_text("The board is quiet. Time to generate some of your own action.")
    print("1: Patrol for the stolen blue Honda Civic (BOLO).\n2: Run traffic enforcement.\n3: Never mind, back to the queue.")
    choice = get_input()
    squad_penalty = -2 if is_busy else 0
    if choice == '1':
        print_text("You spend an hour patrolling the industrial district...")
        if skill_check("Perception"): end_call("You spot a blue Civic with mismatching plates! You call it in and recover the stolen vehicle.", investigative_rep=10, squad_rep=squad_penalty)
        else: end_call("You don't find anything, but your patrol shows initiative.", investigative_rep=2, squad_rep=squad_penalty)
    elif choice == '2': end_call("You post up on the interstate and write a few tickets.", investigative_rep=1, squad_rep=squad_penalty)
    else: return

def handle_shoplifting_call(call):
    """New detailed mission for a Shoplifting call."""
    clear_screen()
    print_header(f"Responding to: {call['type']}")
    print_text(f"Dispatch sends you to the {call['address']}. The clerk is on the line, reporting a man just stuffed items in his jacket and is heading for the door.")
    print_text("You pull up just as the suspect is walking out of the store.")
    
    saw_weapon_bulge = skill_check("Perception")
    if saw_weapon_bulge:
        print_text("// You spot a suspicious bulge in the man's jacket pocket. Could be a weapon. //")

    print("\nHow do you handle this?")
    print("1: The Stop - Authoritative approach. (Command Presence)")
    print("2: The Talk-Down - De-escalating approach.")
    choice = get_input()

    if choice == '1':
        print_text("You get out of your car. 'Police! Stop right there! Let me see your hands!'")
        if skill_check("Command Presence"):
            end_call("The suspect is startled and immediately freezes, putting his hands up. Leads to an easy arrest.", squad_rep=2, investigative_rep=1)
        else:
            print_text("'Fuck you, pig!' he shouts, and takes off running down the alley.")
            chase_sequence()
    elif choice == '2':
        print_text("You quickly get in his path. 'Hey man, let's not make this a big deal. Just give the stuff back and we can talk.'")
        if skill_check("De_escalation"):
            end_call("The suspect, seeing he's caught, gives up and returns the stolen goods. The clerk agrees not to press charges. You give the suspect a trespass warning.", squad_rep=3, dispatch_rep=1)
        else:
            print_text("He shoves you aside and makes a break for it!")
            chase_sequence()
    else:
        end_call("You hesitate, and the suspect blends into the crowd and disappears.", squad_rep=-1)


def handle_suspicious_person(call):
    clear_screen()
    print_header(f"Responding to: {call['type']}")
    print_text(f"You get a call about a suspicious person at {call['address']}.")
    print_text("You arrive and see a man in a hoodie loitering near an alley.")
    if skill_check("Perception"): print_text("// You notice a slight bulge under his jacket. //")
    print("\nHow do you approach?\n1: Casual (De-escalation)\n2: Authoritative (Command Presence)")
    choice = get_input()
    if choice == '1':
        print_text("You walk up casually. 'Hey man, how's it going?'")
        if skill_check("De_escalation"): end_call("He says he's just waiting for a friend. You run his name and it's clean. Call unfounded.", dispatch_rep=1, squad_rep=1)
        else:
            print_text("'Why are you hassling me?!' he gets defensive.")
            if skill_check("Command Presence"): end_call("You calmly but firmly tell him to knock it off. He backs down and leaves.", squad_rep=1)
            else: end_call("He refuses to cooperate and storms off. You lost him.", squad_rep=-2)
    elif choice == '2':
        print_text("'Police! Let me see your hands! What are you doing here?'")
        if skill_check("Command Presence"): end_call("He's startled but complies. Turns out he has an outstanding warrant. Good bust.", squad_rep=2, investigative_rep=1)
        else: print_text("'Fuck you, pig!' he shouts, and takes off running."); chase_sequence()
    else: end_call("You hesitate, and the man wanders off.", squad_rep=-1)

def handle_noise_complaint(call):
    clear_screen()
    print_header(f"Responding to: {call['type']}")
    print_text(f"You're dispatched to {call['address']}. You arrive and can hear loud music and shouting...")
    if skill_check("Law Knowledge"): print_text("// Legal training reminds you that you must visually verify everyone's well-being. //")
    print("\nWhat do you do?\n1: Knock and announce.\n2: Listen at the door.\n3: Call for backup.")
    choice = get_input()
    if choice == "1":
        if skill_check("De_escalation"): end_call("You talk them down. The situation is resolved peacefully.", dispatch_rep=2, squad_rep=1)
        else: print_text("The door flies open and a man charges out!"); chase_sequence()
    elif choice == "2": listen_at_door()
    elif choice == "3": call_for_backup()
    else: end_call("You hesitate and the noise stops. Call unfounded.", squad_rep=-1)

# All other mission functions (listen_at_door, chase_sequence, etc.) remain the same
# and are omitted here for brevity but are part of the full script.
def listen_at_door():
    # ... logic ...
    pass
def chase_sequence():
    # ... logic ...
    pass
def call_for_backup():
    # ... logic ...
    pass
def brief_miller():
    # ... logic ...
    pass

# ==============================================================================
# MAIN GAME LOOP
# ==============================================================================

def game_loop():
    global game_time, call_queue
    generate_calls()

    while True:
        game_time += 1
        if len(call_queue) > 1 and random.randint(1,4) == 1: call_queue.pop(random.randint(0, len(call_queue)-1))
        if len(call_queue) < 3 and random.randint(1,3) == 1: generate_calls()

        if player.get('vehicle_issue') and random.randint(1, 10) == 1:
            clear_screen(); print_header("Mechanical Failure")
            print_text("Your tire pressure light suddenly comes on. You missed a slow leak and have to go out of service.")
            player['dispatch_reputation'] -= 2; print_text("Dispatch Reputation decreased by 2.")
            input("\nPress Enter to continue..."); player['vehicle_issue'] = False

        clear_screen()
        print_header(f"On Duty - Unit {player['unit_number']} - Turn: {game_time}")
        print("--- PENDING CALLS ---")
        if not call_queue: print("The board is clear. Good work.")
        else:
            sorted_calls = sorted(call_queue, key=lambda x: x['priority'])
            for call in sorted_calls: print(f"{call['id']}: PRI: {call['priority']} | TYPE: {call['type']:<20} | WAIT: {call['waiting']}m")
        print("---------------------")

        print("\nWhat do you want to do?")
        print("  'take [call #]' | 'lookup [call #]' | 'proactive' | 'sheet' | 'quit'")
        
        choice = get_input().split()
        if not choice: continue
        action = choice[0]

        if action == "take":
            if len(choice) < 2 or not choice[1].isdigit(): print_text("Please specify which call number to take."); continue
            call_id = int(choice[1])
            call_to_handle = next((c for c in call_queue if c['id'] == call_id), None)
            if call_to_handle:
                call_queue = [c for c in call_queue if c['id'] != call_id]
                # ROUTER
                if call_to_handle['type'] == 'Noise Complaint': handle_noise_complaint(call_to_handle)
                elif call_to_handle['type'] == 'Suspicious Person': handle_suspicious_person(call_to_handle)
                elif call_to_handle['type'] == 'Shoplifting': handle_shoplifting_call(call_to_handle)
                else: handle_generic_call(call_to_handle)
            else: print_text("Invalid call number.")
        
        elif action == "lookup":
            if len(choice) < 2 or not choice[1].isdigit(): print_text("Please specify a call number."); continue
            call_id = int(choice[1])
            call = next((c for c in call_queue if c['id'] == call_id), None)
            if call:
                print_header(f"Details for Call #{call_id}"); print_text(f"TYPE: {call['type']}"); print_text(f"ADDRESS: {call['address']}"); print_text("Initial report: No further details available at this time."); input("\nPress Enter...")
            else: print_text("Invalid call number.")
        elif action == "proactive": handle_proactive_choice()
        elif action == "sheet":
            clear_screen(); print_header("Officer File")
            for stat, value in player.items(): print(f"{stat.replace('_', ' ').title()}: {value}")
            input("\nPress Enter...")
        elif action == "quit": print_text("Ending your shift. Thanks for playing!"); break
        else: print_text("Invalid command.")

# ==============================================================================
# START THE GAME
# ==============================================================================

if __name__ == "__main__":
    character_creation()
    pre_shift_routine()
    game_loop()
