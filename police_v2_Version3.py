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
# UI & HELPER FUNCTIONS (Mobile-Friendly)
# ==============================================================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title):
    print(f"\n{'='*40}\n {title.upper().center(38)} \n{'='*40}")

def print_text(text, delay=0.5):
    print(textwrap.fill(text, width=60))
    time.sleep(delay)

def get_input(prompt="> "):
    try:
        return input(prompt).strip().lower()
    except EOFError:
        return ""

def print_menu(options):
    for idx, opt in enumerate(options, 1):
        print(f"{idx}. {opt}")

def mobile_help():
    clear_screen()
    print_header("HELP & COMMANDS")
    print_text("To play, tap choices by typing commands below. You can:")
    print_text("- take [call_id]: Respond to a call.")
    print_text("- lookup [call_id]: Read call details.")
    print_text("- proactive: Engage in proactive patrol.")
    print_text("- sheet: View your officer and reputation.")
    print_text("- help: View this help menu.")
    print_text("- quit: End your shift.")
    input("\nPress Enter to return to duty...")

# ==============================================================================
# CHARACTER CREATION
# ==============================================================================

def display_creation_screen(stats, points):
    clear_screen()
    print_header("Create Officer")
    print(f"Points to spend: {points}")
    print("Stats start at 5, max 30.\n" + "-"*30)
    for stat, value in stats.items():
        display_name = stat.replace("_", " ").title()
        print(f"{display_name}: {value}")
    print("-"*30)
    print("Commands:")
    print_menu([
        "+ [stat] [amount]    (e.g. + strength 3)",
        "- [stat] [amount]    (e.g. - stamina 2)",
        "randomize           (auto-assign points)",
        "done                (finish when points=0)"
    ])

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
        if points == 0: print("\nType 'done' to begin your first shift.")
        choice = get_input()
        if choice == "help":
            mobile_help()
            continue
        parts = choice.split()
        if not parts:
            continue
        action = parts[0]
        if action == "done" and points == 0:
            break
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
                print_text("Specify a stat.")
                continue
            amount = 1
            stat_parts = parts[1:]
            if parts[-1].isdigit():
                try:
                    amount = int(parts[-1])
                    stat_parts = parts[1:-1]
                except ValueError:
                    pass
            stat_name = "_".join(stat_parts).lower()
            if stat_name not in stats:
                print_text(f"Invalid stat: {stat_name}")
                continue
            if action == '+':
                if points < amount:
                    print_text(f"You only have {points} points.")
                elif stats[stat_name] + amount > 30:
                    print_text(f"{stat_name.title()} can't go above 30.")
                else:
                    stats[stat_name] += amount
                    points -= amount
            elif action == '-':
                if stats[stat_name] - amount < 5:
                    print_text(f"{stat_name.title()} can't drop below 5.")
                else:
                    stats[stat_name] -= amount
                    points += amount
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
    print_header("Officer Created")
    print_text("Welcome to the Department, rookie. Time to hit the streets!")
    input("\nPress Enter to continue to Roll Call...")

# ==============================================================================
# SKILL CHECKS
# ==============================================================================

def skill_check(skill_name):
    skill_key = skill_name.lower().replace(" ", "_")
    if skill_key not in player:
        return False
    roll = random.randint(1, 100)
    rookie_bonus = 30
    effective_skill = player[skill_key] + rookie_bonus
    print_text(f"Rolling {skill_name}: {player[skill_key]} + {rookie_bonus} vs {roll}")
    return roll <= effective_skill

# ==============================================================================
# PRE-SHIFT & END-OF-SHIFT ROUTINES
# ==============================================================================

def pre_shift_routine():
    global player
    clear_screen(); print_header("Roll Call")
    player['vehicle_issue'] = False
    event = random.choice(["bolo", "chew_out", "policy_update", "quick_roll_call"])
    player["unit_number"] = f"1-ADAM-{random.randint(10, 99)}"
    print_text(f"Sergeant: 'Rookie, you're in {player['unit_number']} today.'")
    if event == "bolo":
        print_text("BOLO for a stolen sedan. Might be important.")
    elif event == "chew_out":
        print_text("Sergeant chews out the squad for a previous mistake.")
    else:
        print_text("Quick, quiet roll call.")
    input("\nPress Enter for vehicle inspection...")
    clear_screen(); print_header("Vehicle Inspection")
    print_text("You walk around your unit, checking for issues.")
    if not skill_check("Perception"):
        print_text("Looks fine. What could go wrong?")
        if random.randint(1, 4) == 1:
            player['vehicle_issue'] = True
            print_text("Missed a slow tire leak. Could be a problem later.", 0)
    else:
        print_text("You spot a new dent; you log it and save trouble with fleet.")
        player['squad_reputation'] += 1
    print_text("Logged in and 10-8 (in service).")
    input("\nPress Enter to start your shift...")

def end_of_shift_summary(old_rep):
    print_header("End of Shift")
    print_text("Back at the station, logging off the computer.")
    print("\n--- REPUTATION CHANGES ---")
    squad_change = player['squad_reputation'] - old_rep['squad']
    dispatch_change = player['dispatch_reputation'] - old_rep['dispatch']
    investigative_change = player['investigative_reputation'] - old_rep['investigative']
    print(f"Squad Rep: {player['squad_reputation']} ({squad_change:+})")
    print(f"Dispatch Rep: {player['dispatch_reputation']} ({dispatch_change:+})")
    print(f"Investigative Rep: {player['investigative_reputation']} ({investigative_change:+})")
    print("--------------------\n")
    if squad_change > 3:
        print_text("Squad is impressed with your work today.")
    elif squad_change < -3:
        print_text("You hear grumbling in the locker room. Watch your back.")
    if dispatch_change > 2:
        print_text("Dispatch likes your work. Fewer bullshit calls next shift.")
    if investigative_change > 4:
        print_text("Detectives nod at you. You're getting noticed.")
    player['current_day'] += 1

# ==============================================================================
# CALL DATABASE (TO BE PASTED MANUALLY)
# ==============================================================================

CALL_DATABASE = {
    # Paste all call categories and calls here
}

CRITICAL_CALL_TYPES = [
    "Officer Needs Assistance", "Homicide", "Kidnapping", "Bomb Threat"
]

# ==============================================================================
# MISSION & ACTION HANDLERS
# ==============================================================================

def display_call_slip(call):
    clear_screen()
    print_header(f"CALL SLIP: {call['type']}")
    print_text(f"ID: {call['id']}\nPRIORITY: {call['priority']}\nADDRESS: {call['address']}\nSUMMARY: {call['summary']}")
    input("\nPress Enter to proceed...")

def clear_call_menu(outcomes):
    global shift_time_remaining
    print_header("Clear Call")
    for i, outcome in enumerate(outcomes):
        print(f"{i+1}: {outcome['desc']} ({outcome['time_cost']} mins)")
    print(f"{len(outcomes)+1}: Ride the call... (90 mins)")
    while True:
        choice = get_input()
        if choice == "help":
            mobile_help()
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(outcomes) + 1:
            if int(choice) - 1 < len(outcomes):
                selected = outcomes[int(choice) - 1]
                shift_time_remaining -= selected['time_cost']
                end_call(selected['message'], **selected.get('rep_changes', {}))
            else:
                shift_time_remaining -= 90
                end_call("You take extra time on the report, burning the clock. The squad won't like that.", squad_reputation=-3, dispatch_reputation=-2)
            return

def end_call(message, **kwargs):
    print_header("Call Concluded")
    print_text(message)
    for rep, change in kwargs.items():
        if rep in player:
            player[rep] += change
            print_text(f"{rep.replace('_', ' ').title()} changed by {change:+}")
    input("\nPress Enter to return to service...")

def handle_generic_call(call):
    display_call_slip(call)
    print_text("You arrive and assess the scene.")
    if random.randint(1, 10) == 1:
        print_text("Arrived: Unfounded. Nothing here.")
        clear_call_menu([{"desc": "Clear as unfounded.", "time_cost": 15, "message": "Dispatch appreciates quick turnaround.", "rep_changes": {"dispatch_reputation": 1}}])
        return
    print_menu([
        "Investigate scene (Perception)",
        "Talk to involved parties (De-escalation)",
        "Take command (Command Presence)"
    ])
    choice = get_input()
    if choice == "help":
        mobile_help()
        return handle_generic_call(call)
    if choice == '1':
        if skill_check("Perception"):
            print_text("You notice something critical!")
            if random.randint(1, 4) == 1:
                print_text(f"It was just {call['unfounded']}.")
                clear_call_menu([{"desc": "Report as unfounded.", "time_cost": 20, "message": "Good work clearing a bogus call.", "rep_changes": {"dispatch_reputation": 2, "investigative_reputation": 1}}])
            else:
                print_text(f"The hidden detail: {call['twist']}")
                clear_call_menu([{"desc": "Make arrest/report.", "time_cost": 60, "message": "Successful resolution and solid report.", "rep_changes": {"investigative_reputation": 3, "squad_reputation": 1}}])
        else:
            print_text("Nothing unusual found. Routine report.")
            clear_call_menu([{"desc": "File routine report.", "time_cost": 25, "message": "Handled as standard call.", "rep_changes": {"dispatch_reputation": 1}}])
    elif choice == '2':
        if skill_check("De-escalation"):
            print_text("You calm everyone down.")
            clear_call_menu([{"desc": "De-escalate and clear.", "time_cost": 30, "message": "Resolved without incident.", "rep_changes": {"dispatch_reputation": 1, "squad_reputation": 1}}])
        else:
            print_text("Tension increases. You struggle to maintain control.")
            clear_call_menu([{"desc": "Back off and let cool down.", "time_cost": 20, "message": "Situation fizzles out, but you look ineffective.", "rep_changes": {"squad_reputation": -1}}])
    elif choice == '3':
        if skill_check("Command Presence"):
            print_text("Your authority settles the scene.")
            clear_call_menu([{"desc": "Take control and clear.", "time_cost": 25, "message": "Swift, textbook resolution.", "rep_changes": {"squad_reputation": 2}}])
        else:
            print_text("They ignore you, see you as a rookie.")
            clear_call_menu([{"desc": "Call for supervisor.", "time_cost": 45, "message": "Supervisor needed. Not a good look.", "rep_changes": {"squad_reputation": -3, "dispatch_reputation": -1}}])
    else:
        print_text("You hesitate. Situation resolves itself.")
        clear_call_menu([{"desc": "Clear the call.", "time_cost": 15, "message": "No significant action.", "rep_changes": {"squad_reputation": -1}}])

def handle_proactive_patrol():
    global shift_time_remaining
    print_text("You go hunting for trouble...")
    shift_time_remaining -= 45
    event_roll = random.randint(1, 10)
    if event_roll <= 3:
        end_call("Quiet hour on patrol. City is peaceful.")
    elif event_roll <= 6:
        print_text("You spot a suspicious car.")
        if skill_check("Law Knowledge"):
            end_call("Plates come back stolen. Vehicle recovered!", investigative_reputation=3, dispatch_reputation=1)
        else:
            end_call("You botch the plate number and miss a stolen car.", investigative_reputation=-1)
    elif event_roll <= 9:
        print_text("Hand-to-hand drug deal spotted.")
        if skill_check("Strength"):
            end_call("You catch the dealer after a chase! Great bust.", investigative_reputation=5, squad_reputation=1)
        else:
            end_call("Dealer escapes into alley. Damn.", investigative_reputation=-2, squad_reputation=-1)
    else:
        print_text("Witness a felony stop that turns into a shootout!")
        if skill_check("Marksmanship"):
            end_call("You win the gunfight. Hero status!", investigative_reputation=15, squad_reputation=5)
        else:
            end_call("Shots go wide, suspect escapes. IA will investigate.", investigative_reputation=-5, squad_reputation=-3)

def handle_critical_incident():
    global shift_time_remaining
    call_type = random.choice(CRITICAL_CALL_TYPES)
    clear_screen(); print_header(f"!!! CRITICAL INCIDENT - {call_type.upper()} !!!")
    print_text("Radio: All other traffic stops. Dispatcher sounds urgent.")
    print_text(f"{player['unit_number']}, you're closest. Respond CODE 3!")
    time_cost = random.randint(150, 240)
    shift_time_remaining -= time_cost
    input("\nPress Enter to acknowledge and respond...")
    print_text("Hours of adrenaline and chaos. Scene secured.")
    if call_type == "Officer Needs Assistance":
        end_call("You saved a fellow officer from ambush. Hero!", squad_reputation=15, investigative_reputation=5)
    elif call_type == "Homicide":
        end_call("First on scene at a homicide. Evidence preserved.", investigative_reputation=10, squad_reputation=2)
    else:
        end_call("Handled duties admirably in a critical situation.", squad_reputation=5, investigative_reputation=10)

def check_for_random_events():
    global shift_time_remaining
    if player['vehicle_issue'] and random.randint(1, 30) == 1:
        print_header("!!! MECHANICAL FAILURE !!!")
        print_text("Your tire blows out on the highway. Delay!")
        shift_time_remaining -= 60
        player['squad_reputation'] -= 2
        player['vehicle_issue'] = False
        input("\nPress Enter after the delay...")
        return True
    return False

# ==============================================================================
# MAIN GAME LOGIC
# ==============================================================================

def generate_calls():
    global call_queue, call_id_counter
    if not call_queue:
        num_calls = random.randint(6, 10)
        all_call_types = list(CALL_DATABASE.keys())
        standard_call_types = [t for t in all_call_types if t not in CRITICAL_CALL_TYPES]
        high_priority_call_types = [
            "Assault In Progress", "Robbery/Burglary In Progress", "Shooting/Stabbing",
            "Violent Domestic", "Carjacking In Progress"
        ]
        for _ in range(num_calls):
            priority_roll = random.randint(1, 8)
            if priority_roll == 1:
                call_type = random.choice(high_priority_call_types)
                priority = "HIGH"
            else:
                call_type = random.choice(standard_call_types)
                priority = random.randint(1, 5)
            call_details = random.choice(CALL_DATABASE[call_type])
            new_call = {
                'id': call_id_counter,
                'type': call_type,
                'priority': priority,
                'address': f"{random.randint(100, 9999)} {random.choice(['Main St', 'Oak Ave', 'Pine Ln', 'Maple Ct', 'Park Blvd', 'Cedar St'])}",
                'summary': call_details['summary'],
                'twist': call_details['twist'],
                'unfounded': call_details['unfounded']
            }
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
    print_text("A gritty, realistic, text-based police RPG for mobile.\nType 'help' any time for commands.")
    input("\nPress Enter to begin...")
    character_creation()
    while True:
        start_new_shift()
        old_rep = {
            'squad': player['squad_reputation'],
            'dispatch': player['dispatch_reputation'],
            'investigative': player['investigative_reputation']
        }
        while shift_time_remaining > 0:
            generate_calls()
            if check_for_random_events(): continue
            if random.randint(1, 35) == 1: handle_critical_incident(); continue
            clear_screen()
            hours, minutes = divmod(shift_time_remaining, 60)
            current_date = START_DATE + timedelta(days=player['current_day'] - 1)
            date_str = current_date.strftime("%A, %B %d, %Y")
            print_header(f"ON DUTY - UNIT {player['unit_number']} - {date_str}")
            print(f"Time Left: {hours:02d}h {minutes:02d}m".center(40))
            print("--- CAD ---")
            def sort_key(call):
                p = call['priority']
                if isinstance(p, str): return (0, p)
                return (1, -p)
            call_queue.sort(key=sort_key)
            for call in call_queue:
                print(f"ID: {call['id']:<3} | PRI: {str(call['priority']):<5} | TYPE: {call['type']:<26}")
            print("--------------------------------")
            print_menu([
                "take [id] | lookup [id]",
                "proactive | sheet | help | quit"
            ])
            choice_input = get_input().split()
            if not choice_input: continue
            action = choice_input[0]
            if action == "help":
                mobile_help()
            elif action == "take":
                if len(choice_input) < 2 or not choice_input[1].isdigit():
                    print_text("Specify a valid call ID.")
                    continue
                call_id = int(choice_input[1])
                call_to_handle = next((c for c in call_queue if c['id'] == call_id), None)
                if call_to_handle:
                    call_queue = [c for c in call_queue if c['id'] != call_id]
                    handle_generic_call(call_to_handle)
                else:
                    print_text("Call ID not found.")
            elif action == "lookup":
                if len(choice_input) < 2 or not choice_input[1].isdigit():
                    print_text("Lookup which call ID?")
                    continue
                call_id = int(choice_input[1])
                call = next((c for c in call_queue if c['id'] == call_id), None)
                if call: display_call_slip(call)
                else: print_text("Invalid call ID.")
            elif action == "proactive":
                handle_proactive_patrol()
            elif action == "sheet":
                clear_screen(); print_header("Officer Sheet")
                for key, value in player.items():
                    print(f"{key.replace('_', ' ').title():<18}: {value}")
                input("\nPress Enter to return...")
            elif action == "quit":
                shift_time_remaining = 0
            else:
                print_text("Invalid command.")
        end_of_shift_summary(old_rep)
        print("\nStart next shift? (y/n)")
        if get_input() != 'y':
            print_text("Thanks for playing! Stay safe out there.")
            break

if __name__ == "__main__":
    main()