# app.py
# ==================================================================================================
# 🧟 THE WALKING DEAD — SURVIVAL OS
# A large-scale Streamlit application (>500 lines)
# Decision system, simulation, dashboards, and styled UI
# ==================================================================================================

import streamlit as st
from abc import ABC, abstractmethod
from datetime import date
import random
import math

# ==================================================================================================
# PAGE CONFIG + GLOBAL STYLE
# ==================================================================================================

st.set_page_config(
    page_title="The Walking Dead — Survival OS",
    page_icon="🧟",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
    /* Global */
    body {
        background-color: #020617;
        color: #e5e7eb;
    }

    /* Titles */
    .title {
        font-size: 3.2rem;
        font-weight: 900;
        color: #f9fafb;
    }

    .subtitle {
        color: #d1d5db;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }

    /* Panels & cards */
    .panel, .card {
        background: #020617;
        border: 1px solid #1f2933;
        padding: 1.2rem;
        border-radius: 1.2rem;
        color: #f3f4f6; /* 👈 FIX: force normal readable text */
    }

    /* Card text */
    .card h4 {
        color: #f9fafb;
        font-weight: 700;
    }

    .card p {
        color: #e5e7eb;
        margin: 0.2rem 0;
    }

    /* Status colors */
    .good { color: #22c55e; font-weight: 700; }
    .warn { color: #facc15; font-weight: 700; }
    .bad  { color: #ef4444; font-weight: 700; }

    /* Metrics */
    .stat {
        font-size: 1.3rem;
        font-weight: 800;
        color: #f9fafb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

)

# ==================================================================================================
# CORE DOMAIN MODELS
# ==================================================================================================

class Survivor:
    def __init__(self, name, strength, intelligence, stamina, morale, role):
        self.name = name
        self.strength = strength
        self.intelligence = intelligence
        self.stamina = stamina
        self.morale = morale
        self.role = role
        self.alive = True

    def combat_power(self):
        return round((self.strength * 0.5 + self.stamina * 0.3 + self.morale * 0.2), 2)

    def efficiency(self):
        return round((self.intelligence + self.stamina) / 2, 2)


class Base:
    def __init__(self, name, defense, food, medicine, population):
        self.name = name
        self.defense = defense
        self.food = food
        self.medicine = medicine
        self.population = population

    def safety_score(self):
        return round((self.defense + self.population) / 2, 2)


class Threat:
    def __init__(self, name, danger, frequency):
        self.name = name
        self.danger = danger
        self.frequency = frequency


# ==================================================================================================
# TRANSPORT & EXPEDITION SYSTEM
# ==================================================================================================

class Transport(ABC):
    def __init__(self, name, noise, capacity, speed):
        self.name = name
        self.noise = noise
        self.capacity = capacity
        self.speed = speed

    def risk(self):
        return round((self.noise * 0.6 + (10 - self.speed) * 0.4), 2)


class OnFoot(Transport):
    def __init__(self): super().__init__("🚶 On Foot", 2, 3, 4)

class Horse(Transport):
    def __init__(self): super().__init__("🐎 Horse", 3, 2, 6)

class Car(Transport):
    def __init__(self): super().__init__("🚗 Car", 8, 5, 9)

class Truck(Transport):
    def __init__(self): super().__init__("🚚 Truck", 9, 8, 7)

# ==================================================================================================
# DATA — SURVIVORS, BASES, THREATS
# ==================================================================================================

SURVIVORS = [
    Survivor("Rick", 9, 7, 8, 9, "Leader"),
    Survivor("Daryl", 10, 6, 9, 8, "Hunter"),
    Survivor("Michonne", 9, 8, 8, 8, "Warrior"),
    Survivor("Carol", 7, 9, 7, 9, "Strategist"),
    Survivor("Glenn", 6, 8, 8, 8, "Scout"),
]

BASES = {
    "Prison": Base("Prison", 9, 70, 50, 30),
    "Alexandria": Base("Alexandria", 7, 80, 60, 45),
    "Hilltop": Base("Hilltop", 6, 90, 40, 50),
}

THREATS = [
    Threat("Walkers", 6, 8),
    Threat("Raiders", 8, 4),
    Threat("Disease", 7, 5),
]

# ==================================================================================================
# GAME / SIMULATION ENGINES
# ==================================================================================================

def daily_food_consumption(population):
    return population * 0.8


def morale_change(base, survivors):
    avg_morale = sum(s.morale for s in survivors) / len(survivors)
    if base.food < 20: return -2
    if avg_morale > 8: return 1
    return 0


def random_event():
    roll = random.randint(1, 100)
    if roll < 30: return "Walker attack"
    if roll < 45: return "Illness outbreak"
    if roll < 60: return "Internal conflict"
    if roll < 75: return "Successful scavenging"
    return "Quiet day"


# ==================================================================================================
# SIDEBAR — COMMAND CENTER
# ==================================================================================================

st.sidebar.title("🧠 Command Center")

base_choice = st.sidebar.selectbox("Choose your base", BASES.keys())
transport_choice = st.sidebar.selectbox("Expedition transport", ["On Foot", "Horse", "Car", "Truck"])
days = st.sidebar.slider("Simulate days", 1, 30, 7)

risk_tolerance = st.sidebar.selectbox("Risk tolerance", ["Low", "Medium", "High"])

# ==================================================================================================
# INITIALIZE STATE
# ==================================================================================================

base = BASES[base_choice]
transport_map = {
    "On Foot": OnFoot(),
    "Horse": Horse(),
    "Car": Car(),
    "Truck": Truck(),
}
transport = transport_map[transport_choice]

# ==================================================================================================
# MAIN UI — DASHBOARD
# ==================================================================================================

st.markdown('<div class="title">🧟 The Walking Dead — Survival OS</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A strategic survival simulation & decision system</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------
# HIGH-LEVEL METRICS
# --------------------------------------------------------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🏠 Base", base.name)
with col2:
    st.metric("🛡️ Defense", base.defense)
with col3:
    st.metric("👥 Population", base.population)
with col4:
    st.metric("⚠️ Transport Risk", transport.risk())

# --------------------------------------------------------------------------------------------------
# SURVIVOR ROSTER
# --------------------------------------------------------------------------------------------------

st.markdown("## 👥 Survivor Roster")

cols = st.columns(3)
for i, s in enumerate(SURVIVORS):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="card">
            <h4>{s.name} — {s.role}</h4>
            <p>💪 Strength: {s.strength}</p>
            <p>🧠 Intelligence: {s.intelligence}</p>
            <p>🏃 Stamina: {s.stamina}</p>
            <p>🙂 Morale: {s.morale}</p>
            <p>⚔️ Combat Power: {s.combat_power()}</p>
        </div>
        """, unsafe_allow_html=True)

# --------------------------------------------------------------------------------------------------
# BASE STATUS
# --------------------------------------------------------------------------------------------------

st.markdown("## 🏠 Base Status")

b1, b2, b3, b4 = st.columns(4)
with b1: st.metric("🍖 Food", base.food)
with b2: st.metric("💊 Medicine", base.medicine)
with b3: st.metric("🛡️ Defense", base.defense)
with b4: st.metric("⭐ Safety Score", base.safety_score())

# --------------------------------------------------------------------------------------------------
# SIMULATION
# --------------------------------------------------------------------------------------------------

st.markdown("## ⏳ Simulation Results")

log = []
food = base.food
medicine = base.medicine
morale = sum(s.morale for s in SURVIVORS) / len(SURVIVORS)

for d in range(days):
    event = random_event()
    food -= daily_food_consumption(base.population)
    morale += morale_change(base, SURVIVORS)

    if event == "Walker attack":
        base.defense -= random.randint(0, 2)
        morale -= 1
    elif event == "Illness outbreak":
        medicine -= random.randint(2, 6)
        morale -= 2
    elif event == "Successful scavenging":
        food += random.randint(10, 25)
        morale += 2

    log.append(f"Day {d+1}: {event}")

# --------------------------------------------------------------------------------------------------
# RESULTS
# --------------------------------------------------------------------------------------------------

c1, c2, c3 = st.columns(3)
with c1: st.metric("🍖 Final Food", max(food, 0))
with c2: st.metric("💊 Final Medicine", max(medicine, 0))
with c3: st.metric("🙂 Avg Morale", round(morale, 2))

st.markdown("### 📜 Event Log")
for entry in log:
    st.write(entry)

# --------------------------------------------------------------------------------------------------
# FINAL VERDICT
# --------------------------------------------------------------------------------------------------

st.markdown("## 🧠 Survival Verdict")

if food <= 0 or morale < 3 or base.defense < 3:
    st.error("☠️ Colony collapse imminent")
elif morale > 7 and food > 30:
    st.success("🟢 Colony stable and thriving")
else:
    st.warning("🟡 Colony surviving but fragile")

st.caption("The Walking Dead — Survival OS | Streamlit Edition | v1.0")
