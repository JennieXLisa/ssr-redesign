import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference_lifecycle import can_claim, dataset_state, lease_valid, run_state


class LifecycleTests(unittest.TestCase):
    def test_shared_pause_does_not_stop_another_run(self):
        state = dataset_state(['PENDING'], ['PAUSE', 'RUN'], completion_verified=False, ever_attempted=True)
        self.assertEqual(state, 'RUNNING')
        self.assertEqual(run_state('PAUSE', [state] * 3), 'PAUSED')
        self.assertEqual(run_state('RUN', [state] * 3), 'RUNNING')

    def test_drain_then_pause_or_success(self):
        self.assertEqual(dataset_state(['RUNNING'], ['PAUSE'], completion_verified=False, ever_attempted=True), 'RUNNING')
        self.assertEqual(dataset_state(['PENDING'], ['PAUSE'], completion_verified=False, ever_attempted=True), 'PAUSED')
        self.assertEqual(dataset_state(['SUCCEEDED'], ['PAUSE'], completion_verified=True, ever_attempted=True), 'SUCCEEDED')
        self.assertEqual(run_state('PAUSE', ['SUCCEEDED'] * 3), 'SUCCEEDED')

    def test_empty_plan_needs_actual_audit(self):
        self.assertEqual(dataset_state([], ['RUN'], completion_verified=False, ever_attempted=False), 'RUNNING')
        self.assertEqual(dataset_state([], ['HOLD'], completion_verified=True, ever_attempted=False), 'SUCCEEDED')
        with self.assertRaises(ValueError):
            dataset_state(['FAILED'], ['RUN'], completion_verified=True, ever_attempted=True)

    def test_admission_truth_table(self):
        for state, intent, work in itertools.product(
                ['PLANNED', 'RUNNING', 'PAUSED', 'FAILED', 'SUCCEEDED'],
                ['HOLD', 'RUN', 'PAUSE'], ['PENDING', 'RUNNING', 'FAILED', 'SUCCEEDED']):
            args = dict(state=state, launching_intent=intent, work_state=work,
                        demand=True, prerequisites=True, due=True, resources=True,
                        plan_frozen=True, component='extract')
            expected = state != 'SUCCEEDED' and intent == 'RUN' and work == 'PENDING'
            self.assertEqual(can_claim(**args), expected)
            for guard in ['demand', 'prerequisites', 'due', 'resources', 'plan_frozen']:
                self.assertFalse(can_claim(**{**args, guard: False}))

    def test_metadata_bootstrap_is_only_unfrozen_admission(self):
        args = dict(state='PLANNED', launching_intent='RUN', work_state='PENDING',
                    demand=True, prerequisites=True, due=True, resources=True, plan_frozen=False)
        self.assertTrue(can_claim(**args, component='text_metadata'))
        self.assertFalse(can_claim(**args, component='resolve'))

    def test_fencing_and_paused_publication(self):
        args = dict(state='PAUSED', work_state='RUNNING', token='a', current_token='a',
                    generation=3, current_generation=3, now=100, expires=120)
        self.assertTrue(lease_valid(**args))
        for change in [{'state': 'SUCCEEDED'}, {'work_state': 'SUCCEEDED'}, {'token': 'old'},
                       {'generation': 2}, {'now': 120}, {'now': 121}]:
            self.assertFalse(lease_valid(**{**args, **change}))

    def test_failed_components_do_not_cancel_other_demand(self):
        self.assertEqual(dataset_state(['FAILED', 'PENDING'], ['RUN'], completion_verified=False, ever_attempted=True), 'FAILED')
        self.assertEqual(run_state('RUN', ['SUCCEEDED', 'FAILED', 'RUNNING']), 'FAILED')
        self.assertEqual(run_state('PAUSE', ['SUCCEEDED', 'FAILED', 'RUNNING']), 'PAUSED')


if __name__ == '__main__':
    unittest.main()
