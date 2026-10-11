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
from app import (
    start_new_case,
    init_session_state,
    generate_case_incident,
    build_obfuscated_player_circuit,
    INCIDENT_SCENARIOS,
)


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

    def test_case_initialization_and_narrative(self):
        """Verify initial session state creation and narrative metadata generation."""
        state = {}
        init_session_state(state)

        # Cumulative counters initialized
        self.assertEqual(state["total_cases"], 0)
        self.assertEqual(state["cases_solved"], 0)

        # Case-specific fields initialized
        self.assertTrue(state["case_id"].startswith("CASE-"))
        self.assertIn("source", state["case_incident"])
        self.assertIn("ref", state["case_incident"])
        self.assertIn("context", state["case_incident"])
        self.assertTrue(state["case_incident"]["ref"].startswith("REF-"))

        # Secret gate chosen independently from valid set {I, Z}
        self.assertIn(state["secret_gate"], {"I", "Z"})

        # Budget and empty evidence
        self.assertEqual(state["evidence_budget"], 3)
        self.assertEqual(len(state["probes_run"]), 0)
        self.assertFalse(state["verdict_submitted"])
        self.assertIsNone(state["user_diagnosis"])
        self.assertIsNone(state["verdict_result"])

    def test_new_case_lifecycle_and_state_reset(self):
        """Verify that starting a new case resets case state while preserving cumulative score."""
        state = {}
        init_session_state(state)

        # Simulate executing 2 probes
        res1 = run_forensics_experiment("I", "A", shots=64)
        res2 = run_forensics_experiment("I", "B", shots=64)
        state["probes_run"].extend([res1, res2])
        self.assertEqual(len(state["probes_run"]), 2)

        # Simulate diagnosis submission and correct verdict
        state["verdict_submitted"] = True
        state["user_diagnosis"] = state["secret_gate"]
        state["total_cases"] += 1
        state["cases_solved"] += 1

        prev_case_id = state["case_id"]

        # Trigger new case
        start_new_case(state)

        # New case must have distinct ID
        self.assertNotEqual(state["case_id"], prev_case_id)
        self.assertTrue(state["case_id"].startswith("CASE-"))

        # Narrative metadata generated
        self.assertIn("source", state["case_incident"])
        self.assertIn("ref", state["case_incident"])
        self.assertIn("context", state["case_incident"])

        # Secret gate selected
        self.assertIn(state["secret_gate"], {"I", "Z"})

        # Case-specific state strictly reset
        self.assertEqual(state["evidence_budget"], 3)
        self.assertEqual(len(state["probes_run"]), 0, "Old evidence must not carry into new case")
        self.assertFalse(state["verdict_submitted"], "Verdict submitted state must reset to False")
        self.assertIsNone(state["user_diagnosis"], "Previous verdict must be cleared")
        self.assertIsNone(state["verdict_result"], "Previous verdict feedback must be cleared")

        # Cumulative score preserved across cases
        self.assertEqual(state["total_cases"], 1, "Cumulative total_cases must persist across cases")
        self.assertEqual(state["cases_solved"], 1, "Cumulative cases_solved must persist across cases")

    def test_case_independence_and_secrecy(self):
        """Verify secret gate is independently selected and not leaked in narrative context."""
        state = {}
        init_session_state(state)

        selected_gates = set()
        for _ in range(60):
            start_new_case(state)
            selected_gates.add(state["secret_gate"])
            incident = state["case_incident"]

            # Ensure narrative never reveals secret gate identity
            context_lower = incident["context"].lower()
            ref_lower = incident["ref"].lower()
            source_lower = incident["source"].lower()

            # The narrative context must not state the secret gate
            self.assertNotIn(f"is gate {state['secret_gate'].lower()}", context_lower)
            self.assertNotIn(f"is {state['secret_gate'].lower()}", ref_lower)

        # Both I and Z should be sampled over 60 trials
        self.assertEqual(selected_gates, {"I", "Z"}, "Secret gate must be independently selected from both options")

    def test_probe_budget_enforcement(self):
        """Verify that probe budget limit (3 probes) is enforced."""
        state = {}
        init_session_state(state)
        self.assertEqual(state["evidence_budget"], 3)

        # Run 3 probes
        for _ in range(3):
            remaining = state["evidence_budget"] - len(state["probes_run"])
            self.assertGreater(remaining, 0)
            res = run_forensics_experiment(state["secret_gate"], "A", shots=64)
            state["probes_run"].append(res)

        # Budget exhausted
        remaining = state["evidence_budget"] - len(state["probes_run"])
        self.assertEqual(remaining, 0)
        self.assertEqual(len(state["probes_run"]), 3)


if __name__ == "__main__":
    unittest.main()
