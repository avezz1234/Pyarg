from time import sleep
import math
import random
#i didnt really comment this because it's VERY self explanatory lol
characterstats = {
    "Tank":     {"Health": 150, "Damage": 20, "Speed": 5,  "Weapon": "Club"},
    "Bandit":   {"Health": 100, "Damage": 30, "Speed": 15, "Weapon": "Dagger"},
    "Archer":   {"Health": 80,  "Damage": 25, "Speed": 10, "Weapon": "Bow"},
    "Canoneer": {"Health": 90,  "Damage": 50, "Speed": 5,  "Weapon": "Cannon"}
}

classdesc = {
    "Tank":     "You have picked Tank; Slow but durable. High health, low damage.",
    "Bandit":   "You have picked Bandit; Fast but fragile. Low health, high damage.",
    "Archer":   "You have picked Archer; Balanced. Moderate health and damage.",
    "Canoneer": "You have picked Canoneer; Slow but powerful. High damage, low health."
}

items = {
    "Poison Dagger": {"damage": 15, "effect": "poison",    "desc": "Poisons enemies for 5dmg/turn for 3 turns."},
    "Iron Sword":    {"damage": 25, "effect": None,         "desc": "Reliable extra damage."},
    "Frost Bow":     {"damage": 20, "effect": "slow",       "desc": "Slows enemies, making them skip every other attack."},
    "Cursed Club":   {"damage": 30, "effect": "recoil",     "desc": "Hits hard but you take 5 recoil damage per swing."},
    "Vampiric Fang": {"damage": 18, "effect": "lifesteal",  "desc": "Steals 50% of damage dealt back as HP."}
}

# base stats for enemies, scaled up per level
enemy_pool = {
    "Wolf":         {"hp": 100, "dmg": 10, "xp": 50,  "drop": "Poison Dagger"},
    "Zombie":       {"hp": 80,  "dmg": 15, "xp": 40,  "drop": "Iron Sword"},
    "Bandit":       {"hp": 90,  "dmg": 20, "xp": 60,  "drop": "Cursed Club"},
    "Giant Spider": {"hp": 70,  "dmg": 12, "xp": 45,  "drop": "Vampiric Fang"},
    "Forest Troll": {"hp": 130, "dmg": 25, "xp": 80,  "drop": "Frost Bow"},
    "Dark Wraith":  {"hp": 110, "dmg": 30, "xp": 90,  "drop": None}
}

player = {
    "name": "", "class": "", "level": 1, "xp": 0, "xp_next": 100,
    "hp": 0, "max_hp": 0, "damage": 0, "speed": 0,
    "weapon": "", "inventory": [], "equipped_item": None
}

def init_player(classquery, namequery):
    stats = characterstats[classquery]
    player.update({
        "name": namequery, "class": classquery,
        "hp": stats["Health"], "max_hp": stats["Health"],
        "damage": stats["Damage"], "speed": stats["Speed"],
        "weapon": stats["Weapon"]
    })

def level_up():
    player["level"] += 1
    old_hp  = player["max_hp"]
    old_dmg = player["damage"]
    old_spd = player["speed"]
    player["max_hp"]  = math.floor(old_hp  * 1.2)
    player["damage"]  = math.floor(old_dmg * 1.2)
    player["speed"]   = math.floor(old_spd * 1.2)
    player["hp"]      = player["max_hp"]
    print(f"\n*** LEVEL UP! You are now level {player['level']}! ***")
    print(f"  HP:     {old_hp} -> {player['max_hp']}")
    print(f"  Damage: {old_dmg} -> {player['damage']}")
    print(f"  Speed:  {old_spd} -> {player['speed']}")

def gain_xp(amount):
    player["xp"] += amount
    print(f"\n+{amount} XP ({player['xp']}/{player['xp_next']})")
    while player["xp"] >= player["xp_next"]:
        player["xp"] -= player["xp_next"]
        player["xp_next"] = math.floor(player["xp_next"] * 1.5)
        level_up()

def scale_enemy(name):
    base = enemy_pool[name]
    # enemies scale at 10% per level vs player's 20% — they fall behind over time
    scale = 1 + (player["level"] - 1) * 0.10
    return {
        "name": name,
        "hp":   math.floor(base["hp"]  * scale),
        "dmg":  math.floor(base["dmg"] * scale),
        "xp":   math.floor(base["xp"]  * scale),
        "drop": base["drop"]
    }

def random_encounter():
    enemy_name = random.choice(list(enemy_pool.keys()))
    e = scale_enemy(enemy_name)
    print(f"\nA {e['name']} appears! (HP: {e['hp']} | DMG: {e['dmg']})")
    action = input("1. Fight\n2. Flee\n> ").strip()
    if action == "1":
        combat(e["name"], e["hp"], e["dmg"], e["xp"], e["drop"])
    else:
        print("You back away slowly and avoid the fight.")

def show_inventory():
    print("\n--- Inventory ---")
    if not player["inventory"]:
        print("Empty.")
    else:
        for i, item in enumerate(player["inventory"], 1):
            equipped = " (equipped)" if item == player["equipped_item"] else ""
            print(f"{i}. {item}{equipped} — {items[item]['desc']}")
    print(f"Equipped: {player['equipped_item'] or 'None'}")
    choice = input("Enter item number to equip, or Enter to close: ").strip()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(player["inventory"]):
            player["equipped_item"] = player["inventory"][idx]
            print(f"Equipped {player['equipped_item']}!")
        else:
            print("Invalid slot.")

def combat(enemy_name, enemy_hp, enemy_dmg, xp_reward, drop=None):
    ranged = player["class"] in ["Archer", "Canoneer"]
    turn = 0
    poison_turns = 0
    slow_turns = 0

    while player["hp"] > 0 and enemy_hp > 0:
        turn += 1

        if poison_turns > 0:
            enemy_hp -= 5
            poison_turns -= 1
            print(f"Poison deals 5 damage to {enemy_name}! ({poison_turns} turns left)")
            if enemy_hp <= 0:
                break

        print(f"\n[Turn {turn}] Your HP: {player['hp']}/{player['max_hp']} | {enemy_name} HP: {enemy_hp}")
        print(f"1. Use {player['weapon']} (+{player['damage']} dmg)")
        print(f"2. Use item ({'nothing equipped' if not player['equipped_item'] else player['equipped_item'] + ' +' + str(items[player['equipped_item']]['damage']) + ' dmg'})")
        print("3. Punch (5 dmg)")
        print("4. Flee")
        print("5. Inventory")

        if ranged and turn % 2 == 0:
            print("You reload...")
            if slow_turns > 0:
                slow_turns -= 1
                print(f"{enemy_name} is slowed and skips their attack!")
            else:
                player["hp"] -= enemy_dmg
                print(f"{enemy_name} hits you for {enemy_dmg}!")
            continue

        action = input("> ").strip()

        if action == "5":
            show_inventory()
            continue
        elif action == "1":
            enemy_hp -= player["damage"]
            print(f"You swing your {player['weapon']} for {player['damage']} damage!")
        elif action == "2":
            if not player["equipped_item"]:
                print("Nothing equipped.")
                continue
            it = player["equipped_item"]
            dmg = items[it]["damage"]
            enemy_hp -= dmg
            print(f"You use {it} for {dmg} damage!")
            effect = items[it]["effect"]
            if effect == "poison":
                poison_turns = 3
                print(f"{enemy_name} is poisoned for 3 turns!")
            elif effect == "slow":
                slow_turns = 3
                print(f"{enemy_name} is slowed for 3 turns!")
            elif effect == "lifesteal":
                heal = dmg // 2
                player["hp"] = min(player["hp"] + heal, player["max_hp"])
                print(f"You lifesteal {heal} HP!")
            elif effect == "recoil":
                player["hp"] -= 5
                print("The cursed club recoils — you take 5 damage!")
        elif action == "3":
            enemy_hp -= 5
            print("You punch for 5 damage.")
        elif action == "4":
            print("You flee!")
            return "ran"
        else:
            print("Invalid input.")
            continue

        if enemy_hp <= 0:
            break

        if slow_turns > 0:
            slow_turns -= 1
            print(f"{enemy_name} is slowed and skips their attack!")
        else:
            player["hp"] -= enemy_dmg
            print(f"{enemy_name} hits you for {enemy_dmg}!")

    if player["hp"] <= 0:
        print("You died.")
        return "dead"
    else:
        print(f"\nYou defeated the {enemy_name}!")
        gain_xp(xp_reward)
        if drop and random.random() < 0.6:  # 60% drop chance
            print(f"The {enemy_name} dropped: {drop}!")
            player["inventory"].append(drop)
            if input(f"Equip {drop}? (y/n): ").strip().lower() == "y":
                player["equipped_item"] = drop
        return "won"

def prompt_with_inventory(prompt_text):
    # wraps any input prompt so inventory is always accessible
    while True:
        action = input(prompt_text + "\n5. Inventory\n> ").strip()
        if action == "5":
            show_inventory()
        else:
            return action

# --- intro ---
namequery = input("Welcome to generic RPG. What is your name? ")
print(f"Welcome, {namequery}, to the world of generic RPG. Please select a class.")

while True:
    classquery = input("Select a class: Tank, Bandit, Archer, Canoneer. (class + 'info' for stats) ").strip().title()
    if classquery.endswith("Info"):
        className = classquery.replace("Info", "").strip()
        if className in characterstats:
            for stat, value in characterstats[className].items():
                print(f"{stat}: {value}")
        else:
            print("Invalid class.")
    elif classquery in characterstats:
        print(classdesc[classquery])
        break
    else:
        print("Invalid input.")

init_player(classquery, namequery)

# --- gameplay ---
sleep(2)
print("\nYou wake up in a dark forest, with no memory of how you got there.")
print("Surrounded by trees, you have nothing but your weapon and your wit.")

options1 = prompt_with_inventory("Which sense do you use?\n1. Sight\n2. Hearing\n3. Smell")

events = {
    "1": f"A dark ring of trees surrounds you. You break through with your {characterstats[classquery]['Weapon']}. Pale moonlight floods in — a lone wolf prowls in the shadows.",
    "2": "You hear something. A voice. It sounds just. Like. You.",
    "3": "Something reeks. Rotting flesh. A zombie shambles toward you."
}

event1options = {
    "1": "1. Fight the wolf\n2. Run away\n3. Try to tame the wolf\n4. Do nothing",
    "2": "1. Follow the sound\n2. Ignore it\n3. Search for the source\n4. Do nothing",
    "3": "1. Fight the zombie\n2. Run away\n3. Try to reason with it\n4. Do nothing"
}

if options1 not in events:
    print("Invalid choice.")
else:
    print(f"\n{events[options1]}")
    action = prompt_with_inventory(event1options[options1])

    if options1 == "1":
        if action == "1":
            e = scale_enemy("Wolf")
            combat(e["name"], e["hp"], e["dmg"], e["xp"], e["drop"])
        elif action == "2":
            print("You run. The wolf gives chase but you lose it in the trees.")
        elif action == "3":
            print("You hold out your hand. The wolf sniffs it... and sits. You have a wolf now.")
        elif action == "4":
            print("You do nothing. The wolf loses interest and walks away.")

    elif options1 == "2":
        if action == "1":
            print("You follow the sound. It leads you to a mirror standing alone in the dirt.")
        elif action == "2":
            print("You ignore it. The sound fades. You feel uneasy.")
        elif action == "3":
            print("You search. You find nothing. The sound stops.")
        elif action == "4":
            print("You do nothing. The sound gets louder, then cuts out.")

    elif options1 == "3":
        if action == "1":
            e = scale_enemy("Zombie")
            combat(e["name"], e["hp"], e["dmg"], e["xp"], e["drop"])
        elif action == "2":
            print("You run. It's slow. You escape easily.")
        elif action == "3":
            print("You try to talk to it. It bites you.")
        elif action == "4":
            print("You do nothing. It gets closer.")

    # --- roaming encounters after story event ---
    print("\nYou press deeper into the forest...")
    while True:
        sleep(1)
        # chance of encounter increases slightly each loop
        if random.random() < 0.65:
            random_encounter()
        else:
            print("\nThe forest is quiet for now...")
        
        if player["hp"] <= 0:
            print("\nGame over.")
            break

        next_action = prompt_with_inventory("\nWhat do you do?\n1. Keep moving\n2. Rest (restore 20 HP)\n3. Check stats")
        if next_action == "1":
            print("You push forward into the darkness.")
        elif next_action == "2":
            heal = min(20, player["max_hp"] - player["hp"])
            player["hp"] += heal
            print(f"You rest and recover {heal} HP. ({player['hp']}/{player['max_hp']})")
        elif next_action == "3":
            print(f"\n--- {player['name']} | Level {player['level']} {player['class']} ---")
            print(f"HP: {player['hp']}/{player['max_hp']} | Damage: {player['damage']} | Speed: {player['speed']}")
            print(f"XP: {player['xp']}/{player['xp_next']} | Weapon: {player['weapon']}")
            print(f"Equipped item: {player['equipped_item'] or 'None'}")