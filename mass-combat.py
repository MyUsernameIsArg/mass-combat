import streamlit as st
import pandas as pd
import random

st.title("⚔️ D&D Group Combat Roller")

# --- Basic Inputs organized by Attacker/Defender ---
col_attack, col_defense = st.columns(2)

with col_attack:
    st.subheader("Attackers")
    num_attackers = st.number_input("Number of attackers:", min_value=1, value=5)
    attack_dc = st.number_input("Minimum roll attackers need (DC):", min_value=1, value=18)
    atk_adv = st.checkbox("Attackers roll with Advantage")
    atk_disadv = st.checkbox("Attackers roll with Disadvantage")
    if atk_adv and atk_disadv:
        st.warning("Advantage and Disadvantage cancel each other. Normal roll will be used.")
        atk_adv = atk_disadv = False
    attack_roll_mod_basic = st.number_input("Attacker Roll Modifier:", value=0)
    attack_damage_mod_basic = st.number_input("Attacker Damage Modifier:", value=0)
    attack_die_basic = st.number_input("Attacker Die:", min_value=2, value=10)

with col_defense:
    st.subheader("Defenders")
    num_defenders = st.number_input("Number of defenders:", min_value=1, value=5)
    defense_dc = st.number_input("Minimum roll defenders need (DC):", min_value=1, value=18)
    def_adv = st.checkbox("Defenders roll with Advantage")
    def_disadv = st.checkbox("Defenders roll with Disadvantage")
    if def_adv and def_disadv:
        st.warning("Advantage and Disadvantage cancel each other. Normal roll will be used.")
        def_adv = def_disadv = False
    defense_roll_mod_basic = st.number_input("Defender Roll Modifier:", value=0)
    defense_block_mod_basic = st.number_input("Defender Block Modifier:", value=0)
    defense_die_basic = st.number_input("Defender Die:", min_value=2, value=10)

# --- Other general options ---
rounds = st.number_input("Number of rounds to simulate:", min_value=1, value=1)
detailed_mode = st.checkbox("Show detailed rolls for each round", value=False)

# --- Advanced Mode ---
st.subheader("Advanced Options")
advanced_mode = st.checkbox("Enable Advanced Mode: Individual modifiers & dice")

modifier_options = list(range(-3, 11))
damage_block_options = list(range(-5, 11))
die_options = [4,6,8,10,12,20]

if advanced_mode:
    attack_roll_mods, attack_damage_mods, attack_dice = [], [], []
    defense_roll_mods, defense_block_mods, defense_dice = [], [], []

    group_size = 5  # Number of units per collapsible section

    col_attack_adv, col_defense_adv = st.columns(2)

    # --- Attackers ---
    with col_attack_adv:
        st.markdown("### Attackers Advanced")
        for start in range(0, num_attackers, group_size):
            end = min(start + group_size, num_attackers)
            with st.expander(f"Attacker {start+1}–{end}"):
                for i in range(start, end):
                    st.markdown(f"**Attacker {i+1}**")
                    cols = st.columns(3)
                    roll_mod = cols[0].selectbox("Roll Modifier", modifier_options, index=3, key=f"atk_roll_{i}")
                    die = cols[1].selectbox("Die", die_options, index=3, key=f"atk_die_{i}")
                    dmg_mod = cols[2].selectbox("Damage Modifier", damage_block_options, index=5, key=f"atk_dmg_{i}")
                    attack_roll_mods.append(roll_mod)
                    attack_dice.append(die)
                    attack_damage_mods.append(dmg_mod)

    # --- Defenders ---
    with col_defense_adv:
        st.markdown("### Defenders Advanced")
        for start in range(0, num_defenders, group_size):
            end = min(start + group_size, num_defenders)
            with st.expander(f"Defender {start+1}–{end}"):
                for i in range(start, end):
                    st.markdown(f"**Defender {i+1}**")
                    cols = st.columns(3)
                    roll_mod = cols[0].selectbox("Roll Modifier", modifier_options, index=3, key=f"def_roll_{i}")
                    die = cols[1].selectbox("Die", die_options, index=3, key=f"def_die_{i}")
                    blk_mod = cols[2].selectbox("Block Modifier", damage_block_options, index=5, key=f"def_blk_{i}")
                    defense_roll_mods.append(roll_mod)
                    defense_dice.append(die)
                    defense_block_mods.append(blk_mod)
else:
    # Basic mode: use same values for all
    attack_roll_mods = [attack_roll_mod_basic]*num_attackers
    attack_damage_mods = [attack_damage_mod_basic]*num_attackers
    attack_dice = [attack_die_basic]*num_attackers

    defense_roll_mods = [defense_roll_mod_basic]*num_defenders
    defense_block_mods = [defense_block_mod_basic]*num_defenders
    defense_dice = [defense_die_basic]*num_defenders

# --- Dice Rolling Functions ---
def roll_die(adv=False, disadv=False):
    roll1 = random.randint(1, 20)
    roll2 = random.randint(1, 20)
    if adv:
        return max(roll1, roll2), (roll1, roll2)
    elif disadv:
        return min(roll1, roll2), (roll1, roll2)
    else:
        return roll1, (roll1,)

def roll_attackers(num_attackers, attack_dc, attack_dice, roll_mods, dmg_mods, adv=False, disadv=False):
    total_damage = 0
    attack_rolls = []
    damage_rolls = []
    for i in range(num_attackers):
        roll, rolls = roll_die(adv=adv, disadv=disadv)
        total_roll = roll + roll_mods[i]
        attack_rolls.append((rolls, total_roll))
        if total_roll >= attack_dc:
            dmg = max(0, random.randint(1, attack_dice[i]) + dmg_mods[i])
            damage_rolls.append(dmg)
            total_damage += dmg
    return total_damage, attack_rolls, damage_rolls

def roll_defenders(num_defenders, defense_dc, defense_dice, roll_mods, blk_mods, adv=False, disadv=False):
    total_block = 0
    defense_rolls = []
    block_rolls = []
    for i in range(num_defenders):
        roll, rolls = roll_die(adv=adv, disadv=disadv)
        total_roll = roll + roll_mods[i]
        defense_rolls.append((rolls, total_roll))
        if total_roll >= defense_dc:
            blk = max(0, random.randint(1, defense_dice[i]) + blk_mods[i])
            block_rolls.append(blk)
            total_block += blk
    return total_block, defense_rolls, block_rolls

# --- Run a single round ---
def run_round():
    damage, atk_rolls, dmg_rolls = roll_attackers(
        num_attackers, attack_dc, attack_dice, attack_roll_mods, attack_damage_mods,
        adv=atk_adv, disadv=atk_disadv
    )
    block, def_rolls, blk_rolls = roll_defenders(
        num_defenders, defense_dc, defense_dice, defense_roll_mods, defense_block_mods,
        adv=def_adv, disadv=def_disadv
    )
    return damage, block, atk_rolls, dmg_rolls, def_rolls, blk_rolls

# --- Run multiple rounds ---
def run_combat():
    results = []
    for r in range(1, rounds+1):
        damage, block, atk_rolls, dmg_rolls, def_rolls, blk_rolls = run_round()
        results.append({
            "Round": r,
            "Total Damage": damage,
            "Total Block": block,
            "Attacker Rolls": atk_rolls if detailed_mode else None,
            "Damage Rolls": dmg_rolls if detailed_mode else None,
            "Defender Rolls": def_rolls if detailed_mode else None,
            "Block Rolls": blk_rolls if detailed_mode else None
        })
    df = pd.DataFrame(results)
    st.dataframe(df)
    st.write("**Cumulative Totals:**")
    st.write("Total Damage:", df["Total Damage"].sum())
    st.write("Total Block:", df["Total Block"].sum())

# --- Button to run combat ---
if st.button("Roll Combat!"):
    run_combat()
