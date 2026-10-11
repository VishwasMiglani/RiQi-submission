# Qiskit Fall Fest 2026 — Project Submission Template
**IIIT Kottayam Quantum Hackathon (24-Hour Sprint)**

> ⚠️ **CRITICAL INSTRUCTIONS FOR PARTICIPANTS:**
> 1. **Do NOT rename or delete the section headings** below. The automated AI evaluation and filtering system relies on this exact Markdown structure to parse and grade your project.
> 2. Replace all placeholder text enclosed in `[brackets]` with your project's details.
> 3. **Commit History Audit:** All project commits must be timestamped strictly within the 24-hour hackathon window (between **October 10, 2026 at 7:05 PM** and **October 11, 2026 at 7:05 PM**). Commits observed outside this window will result in **immediate disqualification**.
> 4. Ensure all Jupyter Notebooks have their cells **run and outputs displayed** before pushing.
> 5. Starter resources and reference guides are located in the [`references/`](./references/) folder.
> 6. **Tech Stack Flexibility:** You are free to use any external frameworks/technologies (e.g., Streamlit, React, Pygame, FastAPI, NetworkX) for your frontend, app logic, or classical baselines. However, **Qiskit MUST power the quantum core** of your project.
> 7. **Full Event Guide & Rules:** For full schedule details, track inspirations, submission steps, and grading focus areas, refer to [`HACKATHON_GUIDE.md`](./HACKATHON_GUIDE.md).

---

# RiQi — The Quantum Forensics Lab

## Project Metadata

* **Project Title:** RiQi — The Quantum Forensics Lab
* **Team Name:** RiQi
* **Chosen Track:** Track 1: Quantum Games & Interactive Puzzles
* **Video Presentation Link:** 'https://drive.google.com/drive/folders/1bjVEFvaTWyYe5s7xLzZgAaEQqxnxi3n1?usp=sharing'
* **Live Demo Timestamp in Video:** `[05:30]`

### Team Members (Max 4 members)
| Name | Email | GitHub Username |
| :--- | :--- | :--- |
| Vishwas Miglani | `vishwasmiglani.connect@gmail.com` | `@VishwasMiglani` |

---

## 1. Project Overview & Motivation

* **Summary (3–4 sentences):**
  RiQi is an interactive quantum forensics laboratory game (featuring the PHASE//TRACE investigation protocol) where players act as quantum investigators characterising a suspect single-qubit component. The intercepted module contains an unknown hidden operation—either the Identity gate ($I$) or a Phase-Flip gate ($Z$). Players design probing protocols (selecting computational vs. Hadamard interference probes) to gather measurement evidence, calculate information gain, and deduce the component's true internal state.

* **Why this problem / game?**
  Most introductory quantum games rely on simple superposition or classical random number generators without illustrating *why* quantum mechanics enables unique observation techniques. RiQi turns **Quantum Process Tomography** and **Hadamard Interference** into core gameplay mechanics. It demonstrates why phase anomalies are invisible under computational-basis inspection ($Z|0\rangle = |0\rangle$) and highlights how quantum basis transformations convert phase shifts into observable population states ($|+\rangle \rightarrow |-\rangle$).

---

## 2. Quantum Architecture & Mechanics

* **Core Quantum Principles Used:**
  Superposition (Hadamard $H$ gate), Quantum Phase ($Z$ gate), Phase-to-Population Conversion (Interference via $H \cdot Z \cdot H = X$), and Statevector Probability Calculations vs. Finite-Shot Measurement Collapse (`StatevectorSampler`).

* **How the Quantum Circuit is Integrated:**
  Qiskit dynamically constructs and executes 1-qubit probing circuits based on player inputs:
  1. **Experiment A (Computational Probe):** $|0\rangle \rightarrow [U] \rightarrow \text{Measure}$
     - Returns outcome `0` with probability 1.0 for both $I$ and $Z$ (0 bits mutual information).
  2. **Experiment B (Interference Probe):** $|0\rangle \rightarrow [H] \rightarrow [U] \rightarrow [H] \rightarrow \text{Measure}$
     - Returns outcome `0` with probability 1.0 for $I$, and outcome `1` with probability 1.0 for $Z$ (1.0 bit mutual information).

* **Circuit Details:**
  * **Number of Qubits:** 1 Qubit (Modular 1-qubit process characterization)
  * **Key Gates Used:** Hadamard ($H$), Pauli-Z ($Z$), Identity ($I$), Measurement
  * **Primitives Used:** `qiskit.primitives.StatevectorSampler` and `qiskit.quantum_info.Statevector`
  * **Other Technologies Used:** Streamlit (Scientific Instrument Console UI), Matplotlib (Scientific dual-series histogram with ideal vs observed frequencies), Python `unittest` framework

```python
# Core Qiskit circuit construction in src/quantum_engine.py
def create_circuit(hidden_gate: str, experiment_choice: str, add_measurement: bool = True) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1 if add_measurement else 0)

    if experiment_choice == "A":
        # Computational-basis probe: |0> -> U -> Measure
        if hidden_gate == "Z":
            qc.z(0)
        else:
            qc.id(0)
    elif experiment_choice == "B":
        # Interference probe: |0> -> H -> U -> H -> Measure
        qc.h(0)
        if hidden_gate == "Z":
            qc.z(0)
        else:
            qc.id(0)
        qc.h(0)

    if add_measurement:
        qc.measure(0, 0)
    return qc
```

---

## 3. Repository Structure & How to Run

### Project Structure
```text
├── README.md               # Project documentation (this file)
├── HACKATHON_GUIDE.md      # Hackathon guidelines & rules
├── requirements.txt        # Python dependencies (Qiskit 2.x, Streamlit, Matplotlib)
├── test_quantum_engine.py  # Unit test suite verifying quantum logic & secrecy
├── src/                    # Source code scripts & application
│   ├── quantum_engine.py   # Core Qiskit circuit & sampling engine
│   ├── classical_baseline.py # Information theory & classical comparison benchmark
│   └── app.py              # Streamlit interactive laboratory UI
├── notebooks/              # Executed Jupyter notebooks
│   └── solution.ipynb      # Main runnable notebook with pre-rendered outputs
└── references/             # Hackathon reference guides (Track 1 & Track 2)
```

### Installation & Execution Instructions

> 💡 **Environment Recommendation:** We recommend using a fresh Python virtual environment:
> ```bash
> python -m venv venv
> source venv/bin/activate    # On Windows: venv\Scripts\activate
> pip install -r requirements.txt
> ```

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VishwasMiglani/RiQi-submission.git
   cd RiQi-submission
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the project / demo:**
   ```bash
   # Run the interactive Streamlit laboratory app:
   streamlit run src/app.py

   # Run the automated unit test suite:
   python -m unittest test_quantum_engine.py

   # Run the classical vs quantum information theory benchmark:
   python src/classical_baseline.py

   # Open the pre-rendered Jupyter Notebook:
   jupyter notebook notebooks/solution.ipynb
   ```

---

## 4. Implementation Walkthrough & Live Demo

* **Walkthrough of Gameplay / Optimization Pipeline:**
  1. **Case Briefing:** A new case assigns a secret gate $U \in \{I, Z\}$ randomly without displaying it to the player.
  2. **Probe Selection:** The player selects Experiment A (Computational) or Experiment B (Interference) and chooses shot count presets ($N \in \{1, 16, 64, 256\}$).
  3. **Obfuscated Investigation:** The engine builds a player-facing schematic (`U_suspect`) preventing gate leakage during investigation.
  4. **Histogram & Physics Analysis:** Theoretical probabilities $P(0), P(1)$ and sampled frequencies $N(0), N(1)$ are rendered alongside a physical explanation.
  5. **Verdict Submission & Audit:** The player submits their diagnosis. If the player used Experiment A only, the app issues a **Scientific Rigor Warning** highlighting that Exp A provided 0 bits of evidence (50% blind guess). If Experiment B was used, the quantum phase interference is validated and scored.

* **Key Screenshots / Terminal Output:**
  ```text
  === PHASE//TRACE CLASSICAL VS QUANTUM BASELINE BENCHMARK ===
  Shot Count: 1000

  [Experiment A: Computational-Basis Probe]
    Gate I Counts: {'0': 1000, '1': 0}
    Gate Z Counts: {'0': 1000, '1': 0}
    Information Gain: 0.0 bits (ZERO DISTINGUISHING POWER)

  [Experiment B: Interference Probe]
    Gate I Counts: {'0': 1000, '1': 0}
    Gate Z Counts: {'0': 0, '1': 1000}
    Information Gain: 1.0 bits (100% DEFINITIVE DISCRIMINATION)
  ```

---

## 5. Classical vs. Quantum Comparison

* **Classical Baseline / Counterpart:**
  The classical baseline ([`src/classical_baseline.py`](./src/classical_baseline.py)) calculates Shannon Mutual Information $I(\text{Secret}; \text{Outcome}) = H(\text{Outcome}) - H(\text{Outcome} | \text{Secret})$ across both probing protocols under $N=1000$ shots.

* **Comparative Analysis:**
  - **Computational Probing (Exp A):** Yields $I(\text{Secret}; \text{Outcome}) = 0.0\text{ bits}$. Because $Z|0\rangle = |0\rangle$, computational measurements cannot distinguish $I$ from $Z$. Running additional shots does not increase information gain.
  - **Quantum Interference Probing (Exp B):** Yields $I(\text{Secret}; \text{Outcome}) = 1.0\text{ bit}$. Applying Hadamard gates transforms relative phase shifts into observable population states ($I \rightarrow |0\rangle, Z \rightarrow |1\rangle$), enabling 100% definitive gate identification.

---

## 6. Performance, Results & Limitations

* **Key Results & Observations:**
  - Verified 100% ideal discrimination in Experiment B ($P(|0\rangle) = 1.0$ for $I$, $P(|1\rangle) = 1.0$ for $Z$).
  - Verified exact zero discrimination in Experiment A ($P(|0\rangle) = 1.0$ for both gates).
  - All 11 unit tests in `test_quantum_engine.py` passed in $0.18\text{s}$.

* **Critical Reflection on Limitations:**
  - **No Unphysical Quantum Speedup Claim:** Single-qubit circuits are easily simulated classically. RiQi demonstrates basis change and phase interference principles rather than exponential quantum advantage.
  - **NISQ Noise Sensitivity:** On real quantum hardware, single-qubit gate infidelity, readout error, and phase damping ($T_2$ relaxation) degrade the 100% ideal outcome in Experiment B to $\sim 95\% - 99\%$ fidelity.
  - **Future Scope:** Expanding RiQi to 2-qubit entangling gates ($CNOT$, $CZ$) and full 16-parameter Pauli Quantum Process Tomography.

---

## 7. References & Acknowledgments

* **Official Template & Event:** [Qiskit Fall Fest 2026 Hackathon Template (IIIT Kottayam)](https://github.com/Shanwis/Qiskit-Fall-Fest-2026-IIITKottayam-Hackathon-Template).
* **IBM Qiskit SDK Documentation:** [Qiskit Circuits & Primitives Guide](https://docs.quantum.ibm.com/guides).
* **Quantum Information Theory:** Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*. Cambridge University Press. (Chapter 8: Quantum Process Characterization).
* **AI Assistance Disclosure:** Developed with AI pair-programming assistance for code structuring, Streamlit CSS styling, and unit test coverage in accordance with event rules.
