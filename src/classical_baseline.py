"""
PHASE//TRACE — Classical Baseline & Information Analysis

This module compares computational-basis classical probing against quantum interference
probing, measuring the information gain (in bits) obtained from each experiment.

Scientific Context:
1. Computational-Basis Probing (Exp A):
   - Probes using Z-basis measurements only.
   - For both Identity (I) and Phase-Flip (Z), Z|0⟩ = |0⟩.
   - Outcome distribution P(0) = 1.0, P(1) = 0.0 for both gates.
   - Shannon Mutual Information I(Secret; Outcome) = 0.0 bits.
   - Conclusion: Exp A carries zero diagnostic information regardless of shot count.

2. Quantum Interference Probing (Exp B):
   - Probes using Hadamard basis transformations: |0⟩ -> H -> U -> H -> Measure.
   - For Identity (I): Outcome '0' with P(0) = 1.0.
   - For Phase-Flip (Z): Outcome '1' with P(1) = 1.0.
   - Shannon Mutual Information I(Secret; Outcome) = 1.0 bit.
   - Conclusion: Exp B uniquely and deterministically identifies the secret gate.

3. Classical Simulation vs Physical Measurement:
   - A classical computer running Qiskit easily simulates 1-qubit statevectors.
   - The distinction is not computational speedup, but rather basis rotation:
     classical bit-level inspection only sees 0 vs 1 population, whereas quantum
     interference enables phase-to-population translation.
"""

from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

from quantum_engine import run_forensics_experiment


@dataclass
class BaselineComparisonResult:
    """Contains comparative metrics between Exp A and Exp B across both hidden gates."""
    exp_A_I_counts: Dict[str, int]
    exp_A_Z_counts: Dict[str, int]
    exp_B_I_counts: Dict[str, int]
    exp_B_Z_counts: Dict[str, int]
    exp_A_info_gain_bits: float
    exp_B_info_gain_bits: float
    shots: int


def calculate_mutual_information(p_I_0: float, p_Z_0: float) -> float:
    """Calculates Shannon Mutual Information I(Secret; Measurement) in bits.
    
    Assumes equal prior probability P(Secret = I) = P(Secret = Z) = 0.5.
    
    Args:
        p_I_0: Probability of measuring '0' given hidden gate is I.
        p_Z_0: Probability of measuring '0' given hidden gate is Z.

    Returns:
        Mutual information in bits [0.0, 1.0].
    """
    # Joint probabilities P(Secret, Outcome)
    p_I = 0.5
    p_Z = 0.5
    
    p_0_given_I = p_I_0
    p_1_given_I = 1.0 - p_I_0
    
    p_0_given_Z = p_Z_0
    p_1_given_Z = 1.0 - p_Z_0
    
    # Marginal probability of outcome '0' and '1'
    p_out_0 = p_I * p_0_given_I + p_Z * p_0_given_Z
    p_out_1 = p_I * p_1_given_I + p_Z * p_1_given_Z

    # Shannon Entropy H(Outcome)
    h_out = 0.0
    for p in [p_out_0, p_out_1]:
        if p > 1e-12:
            h_out -= p * np.log2(p)

    # Conditional Entropy H(Outcome | Secret)
    h_cond_I = 0.0
    for p in [p_0_given_I, p_1_given_I]:
        if p > 1e-12:
            h_cond_I -= p * np.log2(p)

    h_cond_Z = 0.0
    for p in [p_0_given_Z, p_1_given_Z]:
        if p > 1e-12:
            h_cond_Z -= p * np.log2(p)

    h_cond = p_I * h_cond_I + p_Z * h_cond_Z

    # Mutual Information I(Secret; Outcome) = H(Outcome) - H(Outcome | Secret)
    mi = max(0.0, h_out - h_cond)
    return float(np.round(mi, 4))


def run_classical_baseline_benchmark(shots: int = 1000) -> BaselineComparisonResult:
    """Runs a complete experimental benchmark comparing Exp A and Exp B across both gates.

    Args:
        shots: Number of finite-shot sampling runs.

    Returns:
        BaselineComparisonResult containing counts and calculated information gain.
    """
    # Exp A on both gates
    res_A_I = run_forensics_experiment("I", "A", shots=shots)
    res_A_Z = run_forensics_experiment("Z", "A", shots=shots)

    # Exp B on both gates
    res_B_I = run_forensics_experiment("I", "B", shots=shots)
    res_B_Z = run_forensics_experiment("Z", "B", shots=shots)

    # Calculate information gain in bits
    mi_A = calculate_mutual_information(
        res_A_I.ideal_probabilities["0"], res_A_Z.ideal_probabilities["0"]
    )
    mi_B = calculate_mutual_information(
        res_B_I.ideal_probabilities["0"], res_B_Z.ideal_probabilities["0"]
    )

    return BaselineComparisonResult(
        exp_A_I_counts=res_A_I.counts,
        exp_A_Z_counts=res_A_Z.counts,
        exp_B_I_counts=res_B_I.counts,
        exp_B_Z_counts=res_B_Z.counts,
        exp_A_info_gain_bits=mi_A,
        exp_B_info_gain_bits=mi_B,
        shots=shots,
    )


if __name__ == "__main__":
    benchmark = run_classical_baseline_benchmark(1000)
    print("=== PHASE//TRACE CLASSICAL VS QUANTUM BASELINE BENCHMARK ===")
    print(f"Shot Count: {benchmark.shots}")
    print("\n[Experiment A: Computational-Basis Probe]")
    print(f"  Gate I Counts: {benchmark.exp_A_I_counts}")
    print(f"  Gate Z Counts: {benchmark.exp_A_Z_counts}")
    print(f"  Information Gain: {benchmark.exp_A_info_gain_bits} bits (ZERO DISTINGUISHING POWER)")
    
    print("\n[Experiment B: Interference Probe]")
    print(f"  Gate I Counts: {benchmark.exp_B_I_counts}")
    print(f"  Gate Z Counts: {benchmark.exp_B_Z_counts}")
    print(f"  Information Gain: {benchmark.exp_B_info_gain_bits} bits (100% DEFINITIVE DISCRIMINATION)")
