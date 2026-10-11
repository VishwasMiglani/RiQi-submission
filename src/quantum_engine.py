"""
PHASE//TRACE — Quantum Forensics Engine

This module provides the core quantum mechanics engine for PHASE//TRACE, a quantum
forensics lab puzzle created for Qiskit Fall Fest 2026 (IIIT Kottayam).

Scientific Concept:
The player investigates an unknown/hidden one-qubit operation U ∈ {I, Z}.
- Experiment A (Computational-basis probe):
    |0⟩ -> [ U ] -> Measure
    For both U=I and U=Z, Z|0⟩ = |0⟩ (up to phase). Ideal outcome: '0' with probability 1.0.
    Conclusion: Cannot distinguish I from Z in the computational basis.
- Experiment B (Interference probe):
    |0⟩ -> [ H ] -> [ U ] -> [ H ] -> Measure
    For U=I: H * I * H |0⟩ = H * H |0⟩ = |0⟩. Ideal outcome: '0' with probability 1.0.
    For U=Z: H * Z * H |0⟩ = X |0⟩ = |1⟩. Ideal outcome: '1' with probability 1.0.
    Conclusion: Interference transforms relative phase shifts into observable population differences.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Any
import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector
from qiskit.primitives import StatevectorSampler


VALID_GATES = {"I": "Identity Gate (No-op)", "Z": "Pauli-Z Phase-Flip Gate"}

VALID_EXPERIMENTS = {
    "A": "Experiment A: Computational-Basis Probe (|0⟩ -> U -> Measure)",
    "B": "Experiment B: Interference Probe (|0⟩ -> H -> U -> H -> Measure)",
}

EXPLANATIONS = {
    "A": (
        "Experiment A (Computational-Basis Probe):\n"
        "Prepares state |0⟩, applies the hidden gate U, and measures directly in the Z-basis.\n"
        "Since Z|0⟩ = |0⟩, both Identity (I) and Phase-Flip (Z) leave the computational state |0⟩ invariant.\n"
        "Result: Both I and Z produce outcome '0' with probability 1.0.\n"
        "Conclusion: Computational-basis measurement CANNOT distinguish I from Z!"
    ),
    "B": (
        "Experiment B (Interference Probe):\n"
        "Prepares state |0⟩, applies Hadamard H to create equal superposition |+⟩ = (|0⟩+|1⟩)/√2,\n"
        "applies hidden gate U, applies Hadamard H again, and measures in the Z-basis.\n"
        "- If U = I: H * I * H |0⟩ = |0⟩ (Outcome '0' with probability 1.0).\n"
        "- If U = Z: H * Z * H |0⟩ = X |0⟩ = |1⟩ (Outcome '1' with probability 1.0).\n"
        "Conclusion: The second Hadamard gate creates quantum interference, mapping the phase shift "
        "induced by Z into distinguishable computational states (|0⟩ vs |1⟩)!"
    ),
}


@dataclass
class ExperimentResult:
    """Encapsulates the complete result of a quantum forensics experiment.

    Attributes:
        experiment_choice: String identifier for the experiment ('A' or 'B').
        experiment_name: Human-readable description of the experiment probe.
        circuit: The constructed Qiskit QuantumCircuit (with measurement).
        ideal_probabilities: Theoretical statevector probability distribution {'0': p0, '1': p1}.
        counts: Finite-shot observed measurement counts (e.g., {'0': 1000, '1': 0}).
        shots: Total number of execution shots performed.
        explanation: Beginner-friendly explanation of why the probe produces this outcome.
    """
    experiment_choice: str
    experiment_name: str
    circuit: QuantumCircuit
    ideal_probabilities: Dict[str, float]
    counts: Dict[str, int]
    shots: int
    explanation: str


def normalize_hidden_gate(hidden_gate: str) -> str:
    """Validates and normalizes the hidden gate identifier."""
    if not isinstance(hidden_gate, str):
        raise ValueError(f"hidden_gate must be a string, got {type(hidden_gate).__name__}.")
    gate = hidden_gate.strip().upper()
    if gate not in VALID_GATES:
        valid_str = ", ".join(sorted(VALID_GATES.keys()))
        raise ValueError(f"Invalid hidden_gate '{hidden_gate}'. Supported gates are: {valid_str}.")
    return gate


def normalize_experiment_choice(experiment_choice: str) -> str:
    """Validates and normalizes the experiment choice identifier."""
    if not isinstance(experiment_choice, str):
        raise ValueError(f"experiment_choice must be a string, got {type(experiment_choice).__name__}.")
    exp = experiment_choice.strip().upper()
    if exp in {"A", "COMPUTATIONAL", "COMPUTATIONAL-BASIS", "COMPUTATIONAL_BASIS"}:
        return "A"
    if exp in {"B", "INTERFERENCE", "INTERFERENCE-PROBE", "INTERFERENCE_PROBE"}:
        return "B"
    raise ValueError(
        f"Invalid experiment_choice '{experiment_choice}'. "
        "Must be 'A' (Computational-basis probe) or 'B' (Interference probe)."
    )


def validate_shots(shots: int) -> int:
    """Validates shot count parameter."""
    if not isinstance(shots, int) or isinstance(shots, bool):
        raise ValueError(f"shots must be an integer, got {type(shots).__name__}.")
    if shots <= 0:
        raise ValueError(f"shots must be a positive integer (> 0), got {shots}.")
    return shots


def create_circuit(
    hidden_gate: str, experiment_choice: str, add_measurement: bool = True
) -> QuantumCircuit:
    """Constructs the Qiskit QuantumCircuit for a given hidden gate and experiment probe.

    Args:
        hidden_gate: 'I' or 'Z'.
        experiment_choice: 'A' or 'B'.
        add_measurement: If True, appends explicit measurement to a classical register.

    Returns:
        Qiskit QuantumCircuit.
    """
    gate = normalize_hidden_gate(hidden_gate)
    exp = normalize_experiment_choice(experiment_choice)

    if add_measurement:
        qc = QuantumCircuit(1, 1, name=f"PHASE_TRACE_Exp_{exp}")
    else:
        qc = QuantumCircuit(1, name=f"PHASE_TRACE_Exp_{exp}_Statevector")

    # Qubit starts in default state |0⟩

    if exp == "A":
        # Computational-basis probe: |0⟩ -> U -> Measure
        if gate == "Z":
            qc.z(0)
        else:
            qc.id(0)
    elif exp == "B":
        # Interference probe: |0⟩ -> H -> U -> H -> Measure
        qc.h(0)
        if gate == "Z":
            qc.z(0)
        else:
            qc.id(0)
        qc.h(0)

    if add_measurement:
        qc.measure(0, 0)

    return qc


def calculate_ideal_probabilities(circuit_without_meas: QuantumCircuit) -> Dict[str, float]:
    """Calculates exact theoretical statevector probabilities before measurement.

    Args:
        circuit_without_meas: QuantumCircuit without measurement gates.

    Returns:
        Dictionary mapping bitstrings '0' and '1' to exact probabilities.
    """
    sv = Statevector.from_instruction(circuit_without_meas)
    probs = sv.probabilities_dict()

    # Ensure both '0' and '1' exist in dictionary formatted cleanly
    p0 = float(np.round(probs.get("0", 0.0), 6))
    p1 = float(np.round(probs.get("1", 0.0), 6))
    return {"0": p0, "1": p1}


def sample_circuit(circuit_with_meas: QuantumCircuit, shots: int) -> Dict[str, int]:
    """Executes measurement sampling using Qiskit's StatevectorSampler.

    Args:
        circuit_with_meas: QuantumCircuit containing measurement gates.
        shots: Number of execution shots.

    Returns:
        Dictionary mapping bitstrings '0' and '1' to observed counts.
    """
    shots = validate_shots(shots)
    sampler = StatevectorSampler()
    job = sampler.run([circuit_with_meas], shots=shots)
    pub_result = job.result()[0]

    # Extract classical bit counts from PrimitiveResult
    data = pub_result.data
    raw_counts = None
    if hasattr(data, "c"):
        raw_counts = data.c.get_counts()
    elif hasattr(data, "meas"):
        raw_counts = data.meas.get_counts()
    else:
        # Fallback for dynamic register names
        for attr in dir(data):
            if not attr.startswith("_"):
                val = getattr(data, attr)
                if hasattr(val, "get_counts"):
                    raw_counts = val.get_counts()
                    break

    if raw_counts is None:
        raise RuntimeError("Failed to extract measurement counts from StatevectorSampler result.")

    counts = {"0": 0, "1": 0}
    for bitstr, cnt in raw_counts.items():
        # Sanitize bitstring format
        clean_bitstr = str(bitstr).strip()
        counts[clean_bitstr] = int(cnt)

    return counts


def run_forensics_experiment(
    hidden_gate: str, experiment_choice: str, shots: int = 1000
) -> ExperimentResult:
    """Main interface for executing a PHASE//TRACE forensics probe.

    Args:
        hidden_gate: The secret gate under investigation ('I' or 'Z').
        experiment_choice: The player's experiment choice ('A' or 'B').
        shots: Number of finite-shot measurement samples (default: 1000).

    Returns:
        ExperimentResult object containing circuit, ideal probabilities,
        observed counts, shot count, and beginner-friendly explanation.
    """
    gate = normalize_hidden_gate(hidden_gate)
    exp = normalize_experiment_choice(experiment_choice)
    shots = validate_shots(shots)

    # Build statevector circuit (no measurement) for theoretical probabilities
    qc_sv = create_circuit(gate, exp, add_measurement=False)
    ideal_probs = calculate_ideal_probabilities(qc_sv)

    # Build measurement circuit for sampling
    qc_meas = create_circuit(gate, exp, add_measurement=True)
    counts = sample_circuit(qc_meas, shots=shots)

    return ExperimentResult(
        experiment_choice=exp,
        experiment_name=VALID_EXPERIMENTS[exp],
        circuit=qc_meas,
        ideal_probabilities=ideal_probs,
        counts=counts,
        shots=shots,
        explanation=EXPLANATIONS[exp],
    )
