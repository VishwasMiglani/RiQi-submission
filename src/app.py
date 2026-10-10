"""
PHASE//TRACE — The Quantum Forensics Lab (Streamlit App)

Qiskit Fall Fest 2026 | IIIT Kottayam — Track 1: Quantum Games & Interactive Puzzles
Author: Senior Quantum Engineer & Hackathon Technical Lead
"""

import random
import uuid
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

# --- PAGE CONFIGURATION & DARK LABORATORY THEME ---
st.set_page_config(
    page_title="PHASE//TRACE — Quantum Forensics Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Dark Charcoal/Navy Lab Theme with Cyan & Violet Accents
LAB_CSS = """
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0B0F19;
        color: #E6EDF3;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Header Container */
    .lab-header {
        background: linear-gradient(135deg, #161B22 0%, #0D1117 100%);
        border: 1px solid #30363D;
        border-left: 5px solid #00F2FE;
        border-radius: 8px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 242, 254, 0.05);
    }
    .lab-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        background: linear-gradient(90deg, #00F2FE 0%, #9D4EDD 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .lab-subtitle {
        color: #8B949E;
        font-size: 0.95rem;
        margin-top: 4px;
    }

    /* Cards & Containers */
    .evidence-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 18px 20px;
        margin-bottom: 16px;
    }
    .evidence-card-header {
        color: #00F2FE;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Verdict Panel Styling */
    .verdict-success {
        background: rgba(0, 242, 254, 0.08);
        border: 2px solid #00F2FE;
        border-radius: 8px;
        padding: 20px;
        color: #E6EDF3;
    }
    .verdict-failure {
        background: rgba(255, 75, 75, 0.08);
        border: 2px solid #FF4B4B;
        border-radius: 8px;
        padding: 20px;
        color: #E6EDF3;
    }

    /* Badges & Metrics */
    .metric-badge {
        background-color: #21262D;
        border: 1px solid #30363D;
        border-radius: 6px;
        padding: 12px 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #00F2FE;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #8B949E;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Hide standard Streamlit header/footer noise */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(LAB_CSS, unsafe_allow_html=True)


# --- SESSION STATE INITIALIZATION ---
def init_session_state():
    """Initializes global and case-specific session state."""
    if "total_cases" not in st.session_state:
        st.session_state.total_cases = 0
    if "cases_solved" not in st.session_state:
        st.session_state.cases_solved = 0
    if "case_id" not in st.session_state or st.session_state.get("reset_needed", False):
        start_new_case()


def start_new_case():
    """Starts a new case, selecting a hidden operation randomly and resetting probe log."""
    st.session_state.case_id = f"CASE-{random.randint(1000, 9999)}"
    # Secret operation selected independently of player choices
    st.session_state.secret_gate = random.choice(["I", "Z"])
    st.session_state.evidence_budget = 3  # Max 3 probes allowed per case
    st.session_state.probes_run = []      # History of executed probes
    st.session_state.verdict_submitted = False
    st.session_state.user_diagnosis = None
    st.session_state.verdict_result = None
    st.session_state.reset_needed = False


init_session_state()


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
        qc.rz(0.0, 0) # Placeholder visualization block
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
    """Renders a high-contrast dark-mode matplotlib histogram comparing ideal vs observed outcomes."""
    fig, ax = plt.subplots(figsize=(6, 3.2), facecolor="#161B22")
    ax.set_facecolor("#0D1117")

    states = ["|0⟩", "|1⟩"]
    x = np.arange(len(states))
    width = 0.35

    ideal_vals = [ideal_probs.get("0", 0.0), ideal_probs.get("1", 0.0)]
    observed_freqs = [counts.get("0", 0) / shots, counts.get("1", 0) / shots]

    rects1 = ax.bar(x - width / 2, ideal_vals, width, label="Theoretical Ideal", color="#9D4EDD", alpha=0.85)
    rects2 = ax.bar(x + width / 2, observed_freqs, width, label=f"Observed ({shots} shots)", color="#00F2FE", alpha=0.85)

    ax.set_ylabel("Probability / Frequency", color="#E6EDF3", fontsize=9)
    ax.set_title("Measurement Outcome Distribution", color="#E6EDF3", fontsize=11, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(states, color="#E6EDF3", fontsize=10)
    ax.set_ylim(0, 1.15)
    ax.tick_params(colors="#E6EDF3", labelsize=8)

    # Gridlines
    ax.grid(axis="y", linestyle="--", alpha=0.2, color="#8B949E")
    for spine in ax.spines.values():
        spine.set_color("#30363D")

    # Legend
    legend = ax.legend(facecolor="#161B22", edgecolor="#30363D", fontsize=8)
    for text in legend.get_texts():
        text.set_color("#E6EDF3")

    # Add value annotations over bars
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    color="#D8B4F8", fontsize=7)
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.2f}", xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    color="#80F7FE", fontsize=7)

    plt.tight_layout()
    return fig


# --- HEADER & SIDEBAR SCOREBOARD ---
st.markdown(
    f"""
    <div class="lab-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="lab-title">PHASE//TRACE</h1>
                <div class="lab-subtitle">Quantum Forensics Laboratory — Interactive Quantum Process Characterization</div>
            </div>
            <div style="text-align: right;">
                <span style="background: #21262D; border: 1px solid #30363D; color: #00F2FE; font-size: 0.85rem; padding: 6px 12px; border-radius: 20px; font-weight: 600;">
                    {st.session_state.case_id}
                </span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Control Panel & Lab Manual
with st.sidebar:
    st.markdown("### 📊 Forensics Scoreboard")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="metric-badge">
                <div class="metric-value">{st.session_state.cases_solved}</div>
                <div class="metric-label">Cases Solved</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        acc = (st.session_state.cases_solved / st.session_state.total_cases * 100) if st.session_state.total_cases > 0 else 0.0
        st.markdown(
            f"""
            <div class="metric-badge">
                <div class="metric-value">{acc:.0f}%</div>
                <div class="metric-label">Accuracy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🛠️ Case Actions")
    if st.button("🔄 Start New Case", use_container_width=True, type="secondary"):
        start_new_case()
        st.rerun()

    st.markdown("---")
    with st.expander("📖 Laboratory Manual & Tutorial", expanded=False):
        st.markdown(
            r"""
            **Case Objective:**  
            An unknown quantum module has been intercepted. The module applies a secret one-qubit gate $U \in \{I, Z\}$:
            - **Gate $I$ (Identity):** Leaves quantum state completely unchanged.
            - **Gate $Z$ (Phase-Flip):** Flips the phase of $|1\\rangle$ ($Z|1\\rangle = -|1\\rangle$), but leaves $|0\\rangle$ unchanged ($Z|0\\rangle = |0\\rangle$).

            **Available Probes:**
            1. **Experiment A (Computational Basis):**  
               $|0\\rangle \\rightarrow [U] \\rightarrow \\text{Measure}$  
               *Result:* Both $I$ and $Z$ produce outcome `0` with 100% probability. Exp A **cannot** distinguish $I$ from $Z$.
            2. **Experiment B (Interference Probe):**  
               $|0\\rangle \\rightarrow [H] \\rightarrow [U] \\rightarrow [H] \\rightarrow \\text{Measure}$  
               *Result:*  
               - If $U = I$: Returns outcome `0` with 100% probability.  
               - If $U = Z$: Returns outcome `1` with 100% probability.  

            *Note: Theoretical simulation is computed via Qiskit Statevector; finite-shot sampling models realistic measurement counts.*
            """
        )

# --- MAIN LABORATORY WORKSPACE ---

# Case Briefing Banner
remaining_probes = st.session_state.evidence_budget - len(st.session_state.probes_run)
st.markdown(
    f"""
    <div class="evidence-card">
        <div class="evidence-card-header">📂 Incident Briefing: {st.session_state.case_id}</div>
        <p style="color: #C9D1D9; font-size: 0.95rem; margin-bottom: 8px;">
            An anomalous single-qubit quantum component has been flagged. Preliminary logs indicate the component applies either 
            <b>Identity (I)</b> or a <b>Phase-Flip (Z)</b>. You must design and execute quantum probing experiments to deduce 
            the component's true internal gate.
        </p>
        <div style="font-size: 0.85rem; color: #8B949E;">
            <b>Remaining Probe Budget:</b> <span style="color: {'#00F2FE' if remaining_probes > 0 else '#FF4B4B'}; font-weight: bold;">{remaining_probes} / {st.session_state.evidence_budget} probes</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tabs: 1. Experiment Station, 2. Evidence Log & Analysis, 3. Diagnostic Verdict
tab1, tab2, tab3 = st.tabs(["🔬 1. Quantum Experiment Station", "📋 2. Evidence Log", "⚖️ 3. Diagnostic Verdict"])

# --- TAB 1: EXPERIMENT STATION ---
with tab1:
    st.markdown("#### Experiment Probe Selection")
    
    col_exp, col_shots = st.columns([2, 1])
    with col_exp:
        exp_choice = st.radio(
            "Select Probing Protocol:",
            options=["A", "B"],
            format_func=lambda x: (
                "Experiment A — Computational-Basis Probe (|0⟩ → U → Measure)"
                if x == "A"
                else "Experiment B — Interference Probe (|0⟩ → H → U → H → Measure)"
            ),
            disabled=st.session_state.verdict_submitted or remaining_probes <= 0,
            help="Exp A measures computational state; Exp B uses Hadamard interference to observe phase.",
        )
    
    with col_shots:
        shot_count = st.selectbox(
            "Shot Count (Shots):",
            options=[1, 16, 64, 256],
            index=3,
            disabled=st.session_state.verdict_submitted or remaining_probes <= 0,
            help="Select the number of quantum execution shots for finite-shot measurement sampling.",
        )

    run_disabled = st.session_state.verdict_submitted or remaining_probes <= 0
    if st.button("🚀 Execute Quantum Probe", use_container_width=True, disabled=run_disabled, type="primary"):
        # Execute tested Qiskit engine
        res: ExperimentResult = run_forensics_experiment(
            hidden_gate=st.session_state.secret_gate,
            experiment_choice=exp_choice,
            shots=shot_count,
        )
        st.session_state.probes_run.append(res)
        st.rerun()

    # Display latest probe result if available
    if st.session_state.probes_run:
        latest_res: ExperimentResult = st.session_state.probes_run[-1]
        st.markdown("---")
        st.markdown("#### Latest Probe Output & Measurement Analysis")

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown("**Circuit Schematic (Player View):**")
            # Render obfuscated circuit schematic so secret gate is NEVER leaked in UI
            obf_qc = build_obfuscated_player_circuit(latest_res.experiment_choice)
            st.code(obf_qc.draw(output="text"), language="text")

            st.markdown(
                f"""
                <div style="background-color: #161B22; border-left: 3px solid #00F2FE; padding: 12px; border-radius: 4px; font-size: 0.88rem; color: #C9D1D9;">
                    <b>Probabilistic Breakdown:</b><br>
                    • Ideal Theoretical: P(|0⟩) = <code>{latest_res.ideal_probabilities['0']:.2f}</code>, P(|1⟩) = <code>{latest_res.ideal_probabilities['1']:.2f}</code><br>
                    • Observed Counts ({latest_res.shots} shots): |0⟩ = <code>{latest_res.counts.get('0', 0)}</code>, |1⟩ = <code>{latest_res.counts.get('1', 0)}</code>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_right:
            # Render histogram
            fig = render_histogram(latest_res.ideal_probabilities, latest_res.counts, latest_res.shots)
            st.pyplot(fig)

        st.markdown(
            f"""
            <div class="evidence-card" style="border-left: 4px solid #9D4EDD;">
                <div style="color: #9D4EDD; font-weight: 600; margin-bottom: 6px;">💡 Physical Analysis:</div>
                <div style="color: #C9D1D9; font-size: 0.9rem;">{latest_res.explanation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- TAB 2: EVIDENCE LOG ---
with tab2:
    st.markdown("#### Chronological Probe History")
    if not st.session_state.probes_run:
        st.info("No probes have been executed for this case yet. Go to Tab 1 to run an experiment.")
    else:
        for idx, res in enumerate(st.session_state.probes_run, 1):
            with st.expander(f"Probe #{idx}: {res.experiment_name} ({res.shots} shots)", expanded=(idx == len(st.session_state.probes_run))):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.write("**Ideal Probabilities:**", res.ideal_probabilities)
                    st.write("**Observed Counts:**", res.counts)
                with c2:
                    fig = render_histogram(res.ideal_probabilities, res.counts, res.shots)
                    st.pyplot(fig)
                st.caption(res.explanation)

# --- TAB 3: DIAGNOSTIC VERDICT ---
with tab3:
    st.markdown("#### Submit Final Case Diagnosis")
    st.write("Based on the experimental evidence gathered, identify the secret gate inside the component:")

    diag_choice = st.radio(
        "Select Suspected Gate:",
        options=["I", "Z"],
        format_func=lambda x: f"Gate {x} — Identity (No phase flip)" if x == "I" else f"Gate {x} — Phase-Flip (Z gate)",
        disabled=st.session_state.verdict_submitted,
    )

    if st.button("⚖️ Submit Verdict", use_container_width=True, disabled=st.session_state.verdict_submitted, type="primary"):
        st.session_state.verdict_submitted = True
        st.session_state.user_diagnosis = diag_choice
        st.session_state.total_cases += 1
        
        is_correct = (diag_choice == st.session_state.secret_gate)
        if is_correct:
            st.session_state.cases_solved += 1
        st.rerun()

    # If verdict has been submitted, display comprehensive analysis
    if st.session_state.verdict_submitted:
        is_correct = (st.session_state.user_diagnosis == st.session_state.secret_gate)
        ran_exp_b = any(res.experiment_choice == "B" for res in st.session_state.probes_run)
        
        st.markdown("---")
        if is_correct:
            st.markdown(
                f"""
                <div class="verdict-success">
                    <h3 style="color: #00F2FE; margin-top: 0;">🎉 CORRECT DIAGNOSIS!</h3>
                    <p>You correctly identified the hidden operation as <b>Gate {st.session_state.secret_gate}</b>.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
                <div class="verdict-failure">
                    <h3 style="color: #FF4B4B; margin-top: 0;">❌ INCORRECT DIAGNOSIS</h3>
                    <p>Your diagnosis was <b>Gate {st.session_state.user_diagnosis}</b>, but the actual hidden operation was <b>Gate {st.session_state.secret_gate}</b>.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 🔬 Scientific Rigor Audit & Forensic Breakdown")
        
        if not ran_exp_b:
            st.warning(
                "⚠️ **Scientific Rigor Warning (Blind Guess Detection):**\n\n"
                "You submitted your verdict without running **Experiment B (Interference Probe)**.\n\n"
                "In Experiment A, both Identity (I) and Phase-Flip (Z) produce outcome `0` with probability 1.0. "
                "Therefore, Experiment A provides **0 bits of distinguishing information**. "
                "Running additional shots on Experiment A does NOT help—statistical precision cannot create information where none exists! "
                "Your diagnosis relied on a 50/50 blind guess rather than quantum evidence."
            )
        else:
            st.success(
                "✅ **Quantum Evidence Validated:**\n\n"
                "You successfully utilized **Experiment B (Interference Probe)**. By applying Hadamard gates before and after "
                "the hidden gate, you mapped the relative phase shift induced by $Z$ into observable population differences "
                "($I \\rightarrow |0\\rangle$, $Z \\rightarrow |1\\rangle$), producing definitive quantum evidence for your verdict!"
            )

        st.markdown("#### Revealed Quantum Circuit Architecture")
        real_qc = create_circuit(st.session_state.secret_gate, "B", add_measurement=True)
        st.code(real_qc.draw(output="text"), language="text")

        if st.button("▶️ Play Next Case", use_container_width=True, type="secondary"):
            start_new_case()
            st.rerun()
