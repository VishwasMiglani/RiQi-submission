"""
RiQi — The Quantum Forensics Lab (Streamlit App)

Qiskit Fall Fest 2026 | IIIT Kottayam — Track 1: Quantum Games & Interactive Puzzles
Protocol: PHASE//TRACE
Author: Senior Quantum Engineer & Scientific Software Designer
"""

import random
from typing import Dict, Any, List
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# Import tested Qiskit quantum engine
from quantum_engine import (
    run_forensics_experiment,
    create_circuit,
    ExperimentResult,
    VALID_EXPERIMENTS,
)
from qiskit import QuantumCircuit

# --- DESIGN SYSTEM: SCIENTIFIC INSTRUMENT CONSOLE ---
LAB_CSS = """
<style>
    /* Global Workspace Background & Typography */
    .stApp, .stMain {
        background-color: #F3F1EB !important;
        color: #202832 !important;
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Hide Streamlit Toolbar, Deploy Button, and Status Decoration */
    header[data-testid="stHeader"],
    .stAppHeader,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    .stDeployButton {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    /* Container Grid & Spacing Scale (4, 8, 12, 16, 20, 24, 32 px) */
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1060px !important;
    }

    /* Editorial Typography Scale */
    h1, h2, h3, h4, h5, h6 {
        color: #202832 !important;
        font-weight: 600 !important;
        letter-spacing: -0.015em !important;
        margin-top: 0 !important;
    }

    .stMarkdown, p, span, label {
        color: #202832;
        font-size: 0.90rem;
        line-height: 1.55;
    }

    /* Instrument Header Panel */
    .instrument-header {
        border-bottom: 1px solid #D6D7D2;
        padding-bottom: 14px;
        margin-bottom: 16px;
    }

    .header-top-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
    }

    .instrument-id-cluster {
        display: flex;
        align-items: baseline;
        gap: 10px;
        flex-wrap: wrap;
    }

    .apparatus-name {
        font-size: 1.55rem;
        font-weight: 700;
        color: #202832;
        letter-spacing: -0.03em;
        line-height: 1;
    }

    .apparatus-model {
        font-size: 0.78rem;
        font-weight: 600;
        color: #66717C;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .protocol-badge {
        font-family: 'IBM Plex Mono', 'JetBrains Mono', Consolas, monospace;
        font-size: 0.74rem;
        font-weight: 600;
        color: #416A83;
        background-color: #EAE8E1;
        border: 1px solid #D6D7D2;
        border-radius: 2px;
        padding: 2px 7px;
        letter-spacing: 0.04em;
    }

    .case-meta-cluster {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .system-status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.74rem;
        font-weight: 600;
        color: #2A7B4C;
        letter-spacing: 0.05em;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #2A7B4C;
        display: inline-block;
    }

    .case-ref-box {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        font-weight: 700;
        color: #202832;
        background-color: #FFFFFF;
        border: 1px solid #D6D7D2;
        border-left: 3px solid #C45132;
        border-radius: 2px;
        padding: 3px 9px;
    }

    /* Telemetry Horizontal Strip: 4 Equal Grid Columns */
    .telemetry-bar {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        align-items: center;
        background-color: #FFFFFF;
        border: 1px solid #D6D7D2;
        border-radius: 2px;
        padding: 10px 18px;
        margin-bottom: 20px;
    }

    .telemetry-cell {
        display: flex;
        flex-direction: column;
        gap: 2px;
        border-right: 1px solid #EAE8E1;
        padding-right: 8px;
    }

    .telemetry-cell:last-child {
        border-right: none;
        padding-right: 0;
    }

    .telemetry-key {
        font-size: 0.68rem;
        font-weight: 700;
        color: #66717C;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    .telemetry-val {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.94rem;
        font-weight: 700;
        color: #202832;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .telemetry-sub {
        font-size: 0.70rem;
        font-weight: 500;
        color: #66717C;
    }

    .pulse-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    /* General Console Panel */
    .console-panel {
        background-color: #FFFFFF;
        border: 1px solid #D6D7D2;
        border-radius: 2px;
        padding: 14px 18px;
        margin-bottom: 20px;
    }

    .panel-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #EAE8E1;
        padding-bottom: 8px;
        margin-bottom: 12px;
    }

    .panel-section-label {
        font-size: 0.76rem;
        font-weight: 700;
        color: #66717C;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    .incident-ref-tag {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        color: #416A83;
        background-color: #F3F1EB;
        border: 1px solid #D6D7D2;
        border-radius: 2px;
        padding: 2px 8px;
    }

    .dispatch-meta-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
        gap: 12px;
        margin-bottom: 12px;
        background-color: #F8F7F3;
        border: 1px solid #EAE8E1;
        border-radius: 2px;
        padding: 10px 14px;
    }

    .meta-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
    }

    .meta-item-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #66717C;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .meta-item-value {
        font-size: 0.86rem;
        font-weight: 600;
        color: #202832;
    }

    .dispatch-narrative {
        font-size: 0.88rem;
        line-height: 1.55;
        color: #202832;
        margin-bottom: 4px;
    }

    .candidate-tag {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 2px;
        display: inline-block;
    }

    .tag-id {
        background-color: rgba(65, 106, 131, 0.10);
        color: #416A83;
        border: 1px solid #416A83;
    }

    .tag-phase {
        background-color: rgba(196, 81, 50, 0.10);
        color: #C45132;
        border: 1px solid #C45132;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        background-color: transparent !important;
        border-bottom: 1px solid #D6D7D2 !important;
        padding: 0 !important;
        gap: 20px !important;
        margin-bottom: 20px !important;
    }

    button[data-baseweb="tab"] {
        background-color: transparent !important;
        color: #66717C !important;
        border-radius: 0 !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
        padding: 10px 4px !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        transition: color 0.12s ease !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: transparent !important;
        color: #202832 !important;
        border-bottom: 2px solid #C45132 !important;
    }

    /* Form Controls: Radio Group Options Only (NOT Section Label) */
    .stWidgetLabel label, label[data-testid="stWidgetLabel"] {
        color: #202832 !important;
        font-weight: 700 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        margin-bottom: 6px !important;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 10px !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #FFFFFF !important;
        border: 1px solid #D6D7D2 !important;
        border-radius: 2px !important;
        padding: 12px 16px !important;
        color: #202832 !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: border-color 0.12s ease, background-color 0.12s ease !important;
        cursor: pointer !important;
        width: 100% !important;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #C45132 !important;
        background-color: #FAF9F6 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border-color: #D6D7D2 !important;
        color: #202832 !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.86rem !important;
    }

    /* Buttons: Primary & Secondary */
    .stButton > button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #C45132 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        letter-spacing: 0.04em !important;
        text-transform: uppercase !important;
        border: none !important;
        border-radius: 2px !important;
        padding: 10px 22px !important;
        transition: background-color 0.12s ease !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="primary"]:hover, button[data-testid="baseButton-primary"]:hover {
        background-color: #A83E23 !important;
        color: #FFFFFF !important;
    }

    .stButton > button[kind="primary"]:disabled, button[data-testid="baseButton-primary"]:disabled {
        background-color: #D6D7D2 !important;
        color: #8A94A0 !important;
        cursor: not-allowed !important;
    }

    .stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"], .stButton > button {
        background-color: #FFFFFF !important;
        color: #202832 !important;
        border: 1px solid #D6D7D2 !important;
        border-radius: 2px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        padding: 8px 18px !important;
        transition: all 0.12s ease !important;
    }

    .stButton > button[kind="secondary"]:hover, button[data-testid="baseButton-secondary"]:hover, .stButton > button:hover {
        background-color: #EAE8E1 !important;
        border-color: #202832 !important;
        color: #202832 !important;
    }

    /* Integrated Circuit Terminal Display */
    div[data-testid="stCodeBlock"] {
        background-color: #1E2530 !important;
        border: 1px solid #2B3545 !important;
        border-radius: 2px !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stCodeBlock"] pre,
    div[data-testid="stCodeBlock"] code {
        background-color: #1E2530 !important;
        color: #E2E8F0 !important;
        font-family: 'IBM Plex Mono', 'JetBrains Mono', Consolas, monospace !important;
        font-size: 0.83rem !important;
        padding: 12px 14px !important;
        margin: 0 !important;
        border: none !important;
    }

    /* Diagnostic Verdict Panels */
    .verdict-banner-success {
        background-color: rgba(42, 123, 76, 0.08);
        border: 1px solid #2A7B4C;
        border-left: 4px solid #2A7B4C;
        border-radius: 2px;
        padding: 16px 20px;
        margin-top: 16px;
        color: #202832;
    }

    .verdict-banner-error {
        background-color: rgba(197, 48, 48, 0.08);
        border: 1px solid #C53030;
        border-left: 4px solid #C53030;
        border-radius: 2px;
        padding: 16px 20px;
        margin-top: 16px;
        color: #202832;
    }

    .rigor-box-valid {
        background-color: #FFFFFF;
        border: 1px solid #D6D7D2;
        border-left: 3px solid #2A7B4C;
        border-radius: 2px;
        padding: 14px 18px;
        margin-top: 14px;
        color: #202832;
    }

    .rigor-box-warning {
        background-color: #FFFFFF;
        border: 1px solid #D6D7D2;
        border-left: 3px solid #B86B14;
        border-radius: 2px;
        padding: 14px 18px;
        margin-top: 14px;
        color: #202832;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #EAE8E1 !important;
        border-right: 1px solid #D6D7D2 !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""

# --- INCIDENT SCENARIOS & CASE NARRATIVES ---
INCIDENT_SCENARIOS = [
    {
        "source": "Superconducting Qubit Bus (Sector 4-A)",
        "ref": "REF-401-CRYO",
        "context": "An intercepted transceiver component from the cryogenic readout bus exhibited anomalous phase dispersion during multi-channel calibration.",
    },
    {
        "source": "Optical Quantum Repeater (Node 07-C)",
        "ref": "REF-712-PHOTON",
        "context": "Network intrusion monitors flagged a quarantined repeater station following an unscheduled firmware reconfiguration on the pulse-shaping stage.",
    },
    {
        "source": "Trapped-Ion Co-Processor (Rack 12-F)",
        "ref": "REF-128-ION",
        "context": "Parity checks on an isolated memory zone detected state anomalies after an unverified laser stabilization cycle.",
    },
    {
        "source": "Transmon Routing Manifold (Bay 09)",
        "ref": "REF-935-DRIVE",
        "context": "Hardware telemetry identified an unauthorized microwave control block inserted into the high-coherence single-qubit drive path.",
    },
    {
        "source": "Cryogenic Buffer Storage (Unit 03-D)",
        "ref": "REF-340-MEM",
        "context": "A suspect storage cell quarantined during routine maintenance exhibits unexplained phase behavior under continuous drive.",
    },
    {
        "source": "Dilution Stage Line 3 (15 mK Stage)",
        "ref": "REF-819-THERM",
        "context": "Spectral diagnostics isolated a suspect physical gate module operating on the cryogenic input-output signal path.",
    },
]


def generate_case_incident() -> Dict[str, str]:
    """Generates a case-specific incident narrative detail with a unique reference code."""
    base = random.choice(INCIDENT_SCENARIOS)
    serial = random.randint(100, 999)
    prefix = base["ref"].split("-")[2] if len(base["ref"].split("-")) > 2 else "MOD"
    return {
        "source": base["source"],
        "ref": f"REF-{serial}-{prefix}",
        "context": base["context"],
    }


# --- SESSION STATE MANAGEMENT ---
def init_session_state(state=None):
    """Initializes global and case-specific session state."""
    if state is None:
        state = st.session_state

    if isinstance(state, dict):
        if "total_cases" not in state:
            state["total_cases"] = 0
        if "cases_solved" not in state:
            state["cases_solved"] = 0
        if "case_id" not in state or state.get("reset_needed", False):
            start_new_case(state)
    else:
        if "total_cases" not in state:
            state.total_cases = 0
        if "cases_solved" not in state:
            state.cases_solved = 0
        if "case_id" not in state or getattr(state, "reset_needed", False):
            start_new_case(state)


def start_new_case(state=None):
    """Starts a new case, selecting a hidden operation randomly and resetting all per-case state."""
    if state is None:
        state = st.session_state

    current_id = state.get("case_id") if isinstance(state, dict) else getattr(state, "case_id", None)
    new_id = f"CASE-{random.randint(1000, 9999)}"
    while new_id == current_id:
        new_id = f"CASE-{random.randint(1000, 9999)}"

    incident = generate_case_incident()
    secret_gate = random.choice(["I", "Z"])

    if isinstance(state, dict):
        state["case_id"] = new_id
        state["case_incident"] = incident
        state["secret_gate"] = secret_gate
        state["evidence_budget"] = 3  # Max 3 probes allowed per case
        state["probes_run"] = []      # Fresh empty evidence history
        state["verdict_submitted"] = False
        state["user_diagnosis"] = None
        state["verdict_result"] = None
        state["reset_needed"] = False
    else:
        state.case_id = new_id
        state.case_incident = incident
        state.secret_gate = secret_gate
        state.evidence_budget = 3  # Max 3 probes allowed per case
        state.probes_run = []      # Fresh empty evidence history
        state.verdict_submitted = False
        state.user_diagnosis = None
        state.verdict_result = None
        state.reset_needed = False

    return state


# --- HELPER FUNCTIONS FOR OBFUSCATED CIRCUIT VISUALIZATION ---
def build_obfuscated_player_circuit(experiment_choice: str) -> QuantumCircuit:
    """Builds a player-facing circuit diagram obscuring the secret gate as 'U_suspect'.

    This guarantees 0% secret gate leakage in the player's probe view.
    """
    exp = experiment_choice.upper()
    qc = QuantumCircuit(1, 1, name=f"Probe_Exp_{exp}")
    if exp == "A":
        # Computational probe: |0⟩ -> U_suspect -> Measure
        qc.barrier(label="Prep |0⟩")
        qc.rz(0.0, 0)  # Visualization alignment
        qc.barrier(label="U_suspect")
        qc.measure(0, 0)
    elif exp == "B":
        # Interference probe: |0⟩ -> H -> U_suspect -> H -> Measure
        qc.h(0)
        qc.barrier(label="U_suspect")
        qc.h(0)
        qc.measure(0, 0)
    return qc


def render_histogram(ideal_probs: Dict[str, float], counts: Dict[str, int], shots: int):
    """Renders a clean scientific matplotlib histogram comparing ideal vs observed outcomes."""
    fig, ax = plt.subplots(figsize=(5.4, 2.7), facecolor="#FFFFFF")
    ax.set_facecolor("#F8F7F3")

    states = ["|0⟩", "|1⟩"]
    x = np.arange(len(states))
    width = 0.30

    ideal_vals = [ideal_probs.get("0", 0.0), ideal_probs.get("1", 0.0)]
    observed_freqs = [counts.get("0", 0) / shots, counts.get("1", 0) / shots]

    rects1 = ax.bar(
        x - width / 2,
        ideal_vals,
        width,
        label="Theoretical Ideal P(|x⟩)",
        color="#416A83",
        alpha=0.92,
        edgecolor="#2F4F63",
        linewidth=1.0,
    )
    rects2 = ax.bar(
        x + width / 2,
        observed_freqs,
        width,
        label=f"Observed Sample (N = {shots})",
        color="#C45132",
        alpha=0.92,
        edgecolor="#9C361E",
        linewidth=1.0,
    )

    ax.set_ylabel("Probability / Frequency", color="#66717C", fontsize=8.5, fontweight="600")
    ax.set_title("TOMOGRAPHY OUTCOME DISTRIBUTION", color="#202832", fontsize=9.0, fontweight="700", pad=10, loc="left")
    ax.set_xticks(x)
    ax.set_xticklabels(states, color="#202832", fontsize=9.5, fontweight="700")
    ax.set_ylim(0, 1.20)
    ax.tick_params(colors="#66717C", labelsize=8)

    # Gridlines & Spines
    ax.grid(axis="y", linestyle="--", alpha=0.5, color="#D6D7D2")
    for spine in ax.spines.values():
        spine.set_color("#D6D7D2")
        spine.set_linewidth(1.0)

    # Legend
    legend = ax.legend(facecolor="#FFFFFF", edgecolor="#D6D7D2", fontsize=7.5, loc="upper right", framealpha=0.95)
    for text in legend.get_texts():
        text.set_color("#202832")
        text.set_fontweight("500")

    # Add precision numerical callouts above each bar
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(
            f"{h:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color="#416A83",
            fontsize=8,
            fontweight="700",
        )
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(
            f"{h:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 2),
            textcoords="offset points",
            ha="center",
            va="bottom",
            color="#C45132",
            fontsize=8,
            fontweight="700",
        )

    plt.tight_layout()
    return fig


def main():
    # --- PAGE CONFIGURATION & THEME ---
    st.set_page_config(
        page_title="RiQi — Quantum Forensics Lab",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(LAB_CSS, unsafe_allow_html=True)

    # --- SESSION STATE INITIALIZATION ---
    init_session_state()

    # --- INSTRUMENT HEADER IDENTIFICATION PANEL ---
    st.markdown(
        f"""
        <div class="instrument-header">
            <div class="header-top-bar">
                <div class="instrument-id-cluster">
                    <span class="apparatus-name">RiQi</span>
                    <span class="apparatus-model">QF-1002 // QUANTUM FORENSICS LAB</span>
                    <span class="protocol-badge">PROTOCOL: PHASE//TRACE</span>
                </div>
                <div class="case-meta-cluster">
                    <span class="system-status-indicator"><span class="status-dot"></span>SYS READY</span>
                    <span class="case-ref-box">{st.session_state.case_id}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- TELEMETRY HORIZONTAL STRIP ---
    remaining_probes = st.session_state.evidence_budget - len(st.session_state.probes_run)
    acc = (st.session_state.cases_solved / st.session_state.total_cases * 100) if st.session_state.total_cases > 0 else 0.0
    status_txt = "CASE RESOLVED" if st.session_state.verdict_submitted else "ACTIVE INTERROGATION"
    status_col = "#2A7B4C" if st.session_state.verdict_submitted else "#C45132"
    budget_color = "#202832" if remaining_probes > 1 else ("#C45132" if remaining_probes == 1 else "#C53030")

    st.markdown(
        f"""
        <div class="telemetry-bar">
            <div class="telemetry-cell">
                <span class="telemetry-key">INVESTIGATOR RECORD</span>
                <span class="telemetry-val">{st.session_state.cases_solved} <span class="telemetry-sub">SOLVED</span></span>
            </div>
            <div class="telemetry-cell">
                <span class="telemetry-key">FIDELITY RATING</span>
                <span class="telemetry-val">{acc:.0f}% <span class="telemetry-sub">ACCURACY</span></span>
            </div>
            <div class="telemetry-cell">
                <span class="telemetry-key">PROBE BUDGET</span>
                <span class="telemetry-val" style="color: {budget_color};">{remaining_probes} / {st.session_state.evidence_budget} <span class="telemetry-sub">REMAINING</span></span>
            </div>
            <div class="telemetry-cell">
                <span class="telemetry-key">DIAGNOSIS STATUS</span>
                <span class="telemetry-val" style="color: {status_col};"><span class="pulse-dot" style="background-color: {status_col};"></span>{status_txt}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- SIDEBAR CONTROL PANEL ---
    with st.sidebar:
        st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #66717C; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 8px;'>INVESTIGATION CONTROL</div>", unsafe_allow_html=True)
        if st.button("INITIALIZE NEW CASE", use_container_width=True, type="secondary"):
            start_new_case()
            st.rerun()

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
        with st.expander("LABORATORY MANUAL & THEORY", expanded=False):
            st.markdown(
                r"""
                **OBJECTIVE & PREMISE:**
                An intercepted single-qubit component executes an unknown unitary operation $U \in \{I, Z\}$:
                - **Identity ($I$):** Zero phase alteration ($I|0\rangle = |0\rangle, I|1\rangle = |1\rangle$).
                - **Phase-Flip ($Z$):** $\pi$-phase flip on $|1\rangle$ ($Z|0\rangle = |0\rangle, Z|1\rangle = -|1\rangle$).

                ---
                **PROBING PROTOCOLS:**
                1. **Protocol A (Computational Basis):**
                   $|0\rangle \rightarrow [U] \rightarrow \text{Measure } Z$
                   *Result:* Because $|0\rangle$ is an eigenstate of $Z$ with eigenvalue $+1$, both $I$ and $Z$ yield outcome `0` with probability $1.0$.
                   *Mutual Information Gain:* **$0.0\text{ bits}$** (Completely blind to phase).

                2. **Protocol B (Hadamard Interference):**
                   $|0\rangle \xrightarrow{H} |+\rangle \rightarrow [U] \xrightarrow{H} \text{Measure } Z$
                   *Result:*
                   - For $U = I$: $H \cdot I \cdot |+\rangle = |0\rangle$ (Outcome `0` with probability $1.0$).
                   - For $U = Z$: $H \cdot Z \cdot |+\rangle = H |-\rangle = |1\rangle$ (Outcome `1` with probability $1.0$).
                   *Mutual Information Gain:* **$1.0\text{ bit}$** (Definitive mathematical proof).

                *Simulation: Qiskit `StatevectorSampler` computes finite-shot projection collapse.*
                """
            )

    # --- INCIDENT BRIEFING & DISPATCH ---
    incident = st.session_state.get(
        "case_incident",
        {
            "source": "Superconducting Qubit Bus (Sector 4-A)",
            "ref": "REF-401-CRYO",
            "context": "An intercepted transceiver component from the cryogenic readout bus exhibited anomalous phase dispersion during multi-channel calibration.",
        },
    )

    st.markdown(
        f"""
        <div class="console-panel">
            <div class="panel-header-row">
                <span class="panel-section-label">01 // INCIDENT DISPATCH & ANOMALY TELEMETRY</span>
                <span class="incident-ref-tag">{incident['ref']}</span>
            </div>
            <div class="dispatch-meta-grid">
                <div class="meta-item">
                    <span class="meta-item-label">TARGET HARDWARE INTERCEPT</span>
                    <span class="meta-item-value">{incident['source']}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-item-label">HYPOTHESIZED UNITARY SET</span>
                    <span class="meta-item-value">
                        <span class="candidate-tag tag-id">I : IDENTITY</span>
                        <span style="color: #66717C; margin: 0 4px;">OR</span>
                        <span class="candidate-tag tag-phase">Z : PHASE-FLIP</span>
                    </span>
                </div>
            </div>
            <div class="dispatch-narrative">
                {incident['context']} Diagnostic telemetry confirms the component applies either
                <b>Identity (I)</b> or a <b>Phase-Flip (Z)</b>.
                Design probing protocols to gather measurement evidence and diagnose the component's true operation before state decoherence.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- MAIN WORKSPACE TABS ---
    tab1, tab2, tab3 = st.tabs(["01. Experiment Station", "02. Evidence Log", "03. Diagnostic Verdict"])

    # --- TAB 1: EXPERIMENT STATION ---
    with tab1:
        st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #66717C; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 8px;'>02 // PROTOCOL CONFIGURATION & EXECUTION</div>", unsafe_allow_html=True)

        col_exp, col_shots = st.columns([2.7, 1.0])
        with col_exp:
            exp_choice = st.radio(
                "Select Interrogation Protocol:",
                options=["A", "B"],
                key=f"exp_{st.session_state.case_id}",
                format_func=lambda x: (
                    "Protocol A — Computational Probe (|0⟩ → U → Measure) [0.0 bits info // Inconclusive]"
                    if x == "A"
                    else "Protocol B — Interference Probe (|0⟩ → H → U → H → Measure) [1.0 bit info // Definitive]"
                ),
                disabled=st.session_state.verdict_submitted or remaining_probes <= 0,
                help="Protocol A inspects computational basis. Protocol B uses Hadamard interference to reveal phase.",
            )

        with col_shots:
            shot_count = st.selectbox(
                "Sample Count (N Shots):",
                options=[1, 16, 64, 256],
                index=3,
                key=f"shots_{st.session_state.case_id}",
                disabled=st.session_state.verdict_submitted or remaining_probes <= 0,
                help="Total projective measurements executed via Qiskit StatevectorSampler.",
            )

        run_disabled = st.session_state.verdict_submitted or remaining_probes <= 0
        btn_label = f"EXECUTE QUANTUM PROBE [{shot_count} SHOTS]" if not run_disabled else ("PROBE BUDGET DEPLETED" if remaining_probes <= 0 else "CASE CLOSED")
        if st.button(btn_label, use_container_width=True, disabled=run_disabled, type="primary"):
            res: ExperimentResult = run_forensics_experiment(
                hidden_gate=st.session_state.secret_gate,
                experiment_choice=exp_choice,
                shots=shot_count,
            )
            st.session_state.probes_run.append(res)
            st.rerun()

        # Latest Probe Results
        if st.session_state.probes_run:
            latest_res: ExperimentResult = st.session_state.probes_run[-1]
            st.markdown("<div style='border-bottom: 1px solid #D6D7D2; margin: 24px 0 20px 0;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #66717C; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 12px;'>03 // TOMOGRAPHY MEASUREMENT REPORT & ANALYSIS</div>", unsafe_allow_html=True)

            # Top Row: Balanced Circuit Terminal on Left, Matplotlib Histogram on Right
            col_circuit, col_chart = st.columns([1, 1])
            with col_circuit:
                st.markdown("<div style='font-size: 0.74rem; font-weight: 700; color: #66717C; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 6px;'>BLACK-BOX CIRCUIT TOPOLOGY (PLAYER VIEW)</div>", unsafe_allow_html=True)
                obf_qc = build_obfuscated_player_circuit(latest_res.experiment_choice)
                st.code(obf_qc.draw(output="text"), language="text")

            with col_chart:
                fig = render_histogram(latest_res.ideal_probabilities, latest_res.counts, latest_res.shots)
                st.pyplot(fig)

            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)

            # Bottom Row: Statistical Breakdown Table on Left, Physical Interpretation Memo on Right
            col_table, col_memo = st.columns([1, 1])
            with col_table:
                p0_obs = latest_res.counts.get("0", 0) / latest_res.shots
                p1_obs = latest_res.counts.get("1", 0) / latest_res.shots
                st.markdown(
                    f"""
                    <div style="background-color: #FFFFFF; border: 1px solid #D6D7D2; border-radius: 2px; padding: 14px 18px; min-height: 120px;">
                        <div style="font-size: 0.72rem; font-weight: 700; color: #66717C; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 8px;">STATISTICAL OUTCOME BREAKDOWN</div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.84rem; color: #202832;">
                            <thead>
                                <tr style="border-bottom: 1px solid #EAE8E1; text-align: left; font-size: 0.72rem; color: #66717C; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em;">
                                    <th style="padding: 4px 6px;">METRIC</th>
                                    <th style="padding: 4px 6px; text-align: right;">STATE |0⟩</th>
                                    <th style="padding: 4px 6px; text-align: right;">STATE |1⟩</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 1px solid #F3F1EB;">
                                    <td style="padding: 6px; font-weight: 500;">Theoretical Ideal P(|x⟩)</td>
                                    <td style="padding: 6px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #416A83;">{latest_res.ideal_probabilities['0']:.2f}</td>
                                    <td style="padding: 6px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #416A83;">{latest_res.ideal_probabilities['1']:.2f}</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #F3F1EB;">
                                    <td style="padding: 6px; font-weight: 500;">Observed Freq (k/N)</td>
                                    <td style="padding: 6px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #C45132;">{p0_obs:.2f}</td>
                                    <td style="padding: 6px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #C45132;">{p1_obs:.2f}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 6px; font-weight: 500;">Sampled Counts ({latest_res.shots} shots)</td>
                                    <td style="padding: 6px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #202832;">{latest_res.counts.get('0', 0)}</td>
                                    <td style="padding: 6px; text-align: right; font-family: 'IBM Plex Mono', monospace; font-weight: 700; color: #202832;">{latest_res.counts.get('1', 0)}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_memo:
                st.markdown(
                    f"""
                    <div style="background-color: #FFFFFF; border: 1px solid #D6D7D2; border-left: 3px solid #416A83; border-radius: 2px; padding: 14px 18px; min-height: 120px;">
                        <div style="color: #416A83; font-weight: 700; font-size: 0.74rem; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 6px;">PHYSICAL TOMOGRAPHY INTERPRETATION</div>
                        <div style="color: #202832; font-size: 0.88rem; line-height: 1.55;">{latest_res.explanation}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- TAB 2: EVIDENCE LOG ---
    with tab2:
        st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #66717C; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 12px;'>CHRONOLOGICAL LABORATORY RECORD</div>", unsafe_allow_html=True)
        if not st.session_state.probes_run:
            st.info("NO PROBES EXECUTED YET FOR THIS CASE // DEPLOY EXPERIMENT PROTOCOL A OR B IN TAB 1 TO COMMENCE TOMOGRAPHY DATA COLLECTION.")
        else:
            for idx, res in enumerate(reversed(st.session_state.probes_run), 1):
                probe_num = len(st.session_state.probes_run) - idx + 1
                exp_label = "PROTOCOL A // COMPUTATIONAL" if res.experiment_choice == "A" else "PROTOCOL B // INTERFERENCE"
                with st.expander(f"RECORD ENTRY #{probe_num:02d} — {exp_label} [N = {res.shots} SHOTS]", expanded=(idx == 1)):
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.markdown(
                            f"""
                            <div style="font-size: 0.84rem; line-height: 1.6; color: #202832;">
                                <div><strong>Protocol:</strong> {res.experiment_name}</div>
                                <div><strong>Ideal Probabilities:</strong> <code>|0⟩: {res.ideal_probabilities['0']:.2f}</code>, <code>|1⟩: {res.ideal_probabilities['1']:.2f}</code></div>
                                <div><strong>Observed Counts:</strong> <code>|0⟩: {res.counts.get('0', 0)}</code>, <code>|1⟩: {res.counts.get('1', 0)}</code></div>
                                <div style="margin-top: 8px; color: #66717C; font-size: 0.82rem;">{res.explanation}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    with c2:
                        fig = render_histogram(res.ideal_probabilities, res.counts, res.shots)
                        st.pyplot(fig)

    # --- TAB 3: DIAGNOSIS ---
    with tab3:
        st.markdown("<div style='font-size: 0.76rem; font-weight: 700; color: #66717C; letter-spacing: 0.07em; text-transform: uppercase; margin-bottom: 8px;'>04 // DIAGNOSTIC HYPOTHESIS & VERDICT SUBMISSION</div>", unsafe_allow_html=True)
        st.write("Synthesize experimental measurement evidence to deduce the true unitary matrix implemented by the suspect component:")

        diag_choice = st.radio(
            "Select Diagnosed Unitary Operation:",
            options=["I", "Z"],
            key=f"diag_{st.session_state.case_id}",
            format_func=lambda x: (
                "Gate I — Identity Matrix (U = I, zero phase alteration)"
                if x == "I"
                else "Gate Z — Pauli Phase-Flip Matrix (U = Z, π relative phase rotation on |1⟩)"
            ),
            disabled=st.session_state.verdict_submitted,
        )

        if st.button("SUBMIT FORENSIC DIAGNOSIS", use_container_width=True, disabled=st.session_state.verdict_submitted, type="primary"):
            st.session_state.verdict_submitted = True
            st.session_state.user_diagnosis = diag_choice
            st.session_state.total_cases += 1

            is_correct = (diag_choice == st.session_state.secret_gate)
            if is_correct:
                st.session_state.cases_solved += 1
            st.rerun()

        # Verdict Post-Submission Breakdown
        if st.session_state.verdict_submitted:
            is_correct = (st.session_state.user_diagnosis == st.session_state.secret_gate)
            ran_exp_b = any(res.experiment_choice == "B" for res in st.session_state.probes_run)

            if is_correct:
                st.markdown(
                    f"""
                    <div class="verdict-banner-success">
                        <div style="font-weight: 700; color: #2A7B4C; font-size: 0.88rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">DIAGNOSIS CONFIRMED // ACCURATE PROCESS IDENTIFICATION</div>
                        <p style="margin-bottom: 0; font-size: 0.88rem;">You accurately identified the suspect black-box component as <b>Gate {st.session_state.secret_gate}</b> based on experimental evidence.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="verdict-banner-error">
                        <div style="font-weight: 700; color: #C53030; font-size: 0.88rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">DIAGNOSIS REJECTED // PROCESS MISIDENTIFICATION</div>
                        <p style="margin-bottom: 0; font-size: 0.88rem;">You diagnosed <b>Gate {st.session_state.user_diagnosis}</b>, but physical characterization proves the true operation was <b>Gate {st.session_state.secret_gate}</b>.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if not ran_exp_b:
                st.markdown(
                    r"""
                    <div class="rigor-box-warning">
                        <div style="font-weight: 700; color: #B86B14; font-size: 0.80rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">SCIENTIFIC RIGOR AUDIT // INSUFFICIENT EVIDENCE (BLIND GUESS DETECTED)</div>
                        <p style="font-size: 0.86rem; margin-bottom: 0; line-height: 1.55;">
                            Diagnosis was submitted without deploying <b>Protocol B (Hadamard Interference Probe)</b>.<br>
                            Under Protocol A, both Identity ($I$) and Phase-Flip ($Z$) yield outcome <code>0</code> with probability 1.0 ($Z|0\rangle = |0\rangle$).
                            Protocol A produces <b>0.0 bits of mutual information</b>. Your diagnosis was a 50/50 blind guess rather than empirical quantum proof.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    r"""
                    <div class="rigor-box-valid">
                        <div style="font-weight: 700; color: #2A7B4C; font-size: 0.80rem; letter-spacing: 0.05em; text-transform: uppercase; margin-bottom: 4px;">SCIENTIFIC RIGOR AUDIT // VALIDATED (EMPIRICAL QUANTUM PROOF)</div>
                        <p style="font-size: 0.86rem; margin-bottom: 0; line-height: 1.55;">
                            You applied <b>Protocol B (Hadamard Interference Probe)</b>.
                            Applying basis transformations before and after the hidden gate ($H \cdot Z \cdot H = X$) mapped the unobservable $\pi$ relative phase shift into orthogonal population states (<code>I → |0⟩</code>, <code>Z → |1⟩</code>), yielding <b>1.0 bit of mutual information</b> and decisive proof!
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='margin-top: 18px; font-size: 0.74rem; font-weight: 700; color: #66717C; letter-spacing: 0.05em; text-transform: uppercase;'>DECLASSIFIED HARDWARE ARCHITECTURE (INTERNAL GATES REVEALED):</div>", unsafe_allow_html=True)
            real_qc = create_circuit(st.session_state.secret_gate, "B", add_measurement=True)
            st.code(real_qc.draw(output="text"), language="text")

            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            if st.button("INITIALIZE NEXT CASE", use_container_width=True, type="secondary"):
                start_new_case()
                st.rerun()


if __name__ == "__main__":
    main()
