"""
Unit and integration tests for PHASE//TRACE Quantum Forensics Engine & App Logic.
"""

import unittest
import numpy as np

# Adjust path import if needed
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from quantum_engine import (
    run_forensics_experiment,
    create_circuit,
    calculate_ideal_probabilities,
    sample_circuit,
    normalize_hidden_gate,
    normalize_experiment_choice,
    validate_shots,
    ExperimentResult,
)
from classical_baseline import run_classical_baseline_benchmark
from app import start_new_case, build_obfuscated_player_circuit


class TestQuantumEngineAndApp(unittest.TestCase):

    def test_input_validation(self):
        """Test parameter normalization and error handling for invalid inputs."""
        # Valid gate normalization
        self.assertEqual(normalize_hidden_gate("i"), "I")
        self.assertEqual(normalize_hidden_gate("Z"), "Z")

        # Invalid gate
        with self.assertRaises(ValueError):
            normalize_hidden_gate("X")
        with self.assertRaises(ValueError):
            normalize_hidden_gate("123")

        # Valid experiment normalization
        self.assertEqual(normalize_experiment_choice("a"), "A")
        self.assertEqual(normalize_experiment_choice("computational"), "A")
        self.assertEqual(normalize_experiment_choice("b"), "B")
        self.assertEqual(normalize_experiment_choice("interference"), "B")

        # Invalid experiment
        with self.assertRaises(ValueError):
            normalize_experiment_choice("C")

        # Shots validation
        self.assertEqual(validate_shots(500), 500)
        with self.assertRaises(ValueError):
            validate_shots(0)
        with self.assertRaises(ValueError):
            validate_shots(-10)

    def test_all_gates_and_experiments(self):
        """Test all 4 combinations of hidden gates {I, Z} and experiments {A, B}."""
        # Exp A with Gate I
        res_A_I = run_forensics_experiment("I", "A", shots=100)
        self.assertEqual(res_A_I.ideal_probabilities, {"0": 1.0, "1": 0.0})
        self.assertEqual(res_A_I.counts.get("0", 0), 100)

        # Exp A with Gate Z
        res_A_Z = run_forensics_experiment("Z", "A", shots=100)
        self.assertEqual(res_A_Z.ideal_probabilities, {"0": 1.0, "1": 0.0})
        self.assertEqual(res_A_Z.counts.get("0", 0), 100)

        # Exp B with Gate I
        res_B_I = run_forensics_experiment("I", "B", shots=100)
        self.assertEqual(res_B_I.ideal_probabilities, {"0": 1.0, "1": 0.0})
        self.assertEqual(res_B_I.counts.get("0", 0), 100)

        # Exp B with Gate Z
        res_B_Z = run_forensics_experiment("Z", "B", shots=100)
        self.assertEqual(res_B_Z.ideal_probabilities, {"0": 0.0, "1": 1.0})
        self.assertEqual(res_B_Z.counts.get("1", 0), 100)

    def test_experiment_A_indistinguishability(self):
        """Verify that Experiment A cannot distinguish I from Z (both yield P(0)=1.0)."""
        res_I = run_forensics_experiment("I", "A", shots=1000)
        res_Z = run_forensics_experiment("Z", "A", shots=1000)

        # Ideal probabilities must be identical
        self.assertEqual(res_I.ideal_probabilities, {"0": 1.0, "1": 0.0})
        self.assertEqual(res_Z.ideal_probabilities, {"0": 1.0, "1": 0.0})

        # Observed counts for 1000 shots should both be 100% '0'
        self.assertEqual(res_I.counts.get("0", 0), 1000)
        self.assertEqual(res_Z.counts.get("0", 0), 1000)

    def test_experiment_B_distinguishability(self):
        """Verify that Experiment B distinguishes I from Z in ideal simulator."""
        res_I = run_forensics_experiment("I", "B", shots=1000)
        res_Z = run_forensics_experiment("Z", "B", shots=1000)

        # Ideal probabilities: U=I -> P('0')=1.0, P('1')=0.0
        self.assertEqual(res_I.ideal_probabilities, {"0": 1.0, "1": 0.0})
        self.assertEqual(res_I.counts.get("0", 0), 1000)

        # Ideal probabilities: U=Z -> P('0')=0.0, P('1')=1.0
        self.assertEqual(res_Z.ideal_probabilities, {"0": 0.0, "1": 1.0})
        self.assertEqual(res_Z.counts.get("1", 0), 1000)

    def test_circuit_structure(self):
        """Verify quantum circuit gate depth and instruction count."""
        qc_A = create_circuit("Z", "A", add_measurement=True)
        qc_B = create_circuit("Z", "B", add_measurement=True)

        self.assertEqual(qc_A.num_qubits, 1)
        self.assertEqual(qc_B.num_qubits, 1)

        # Experiment B must contain 2 Hadamard gates
        op_names_B = [op.operation.name for op in qc_B.data]
        self.assertIn("h", op_names_B)
        self.assertEqual(op_names_B.count("h"), 2)

    def test_player_view_secrecy(self):
        """Verify that player-facing obfuscated circuits do not leak secret gate info."""
        qc_obf_A = build_obfuscated_player_circuit("A")
        qc_obf_B = build_obfuscated_player_circuit("B")

        draw_str_A = str(qc_obf_A.draw(output="text"))
        draw_str_B = str(qc_obf_B.draw(output="text"))

        # Check that secret gate 'Z' is not leaked in player circuit schematic
        self.assertNotIn("[ z ]", draw_str_A.lower())
        self.assertNotIn("[ z ]", draw_str_B.lower())

    def test_classical_baseline_benchmark(self):
        """Verify information theory calculations in classical baseline."""
        bm = run_classical_baseline_benchmark(shots=500)
        self.assertEqual(bm.exp_A_info_gain_bits, 0.0)
        self.assertEqual(bm.exp_B_info_gain_bits, 1.0)


if __name__ == "__main__":
    unittest.main()
