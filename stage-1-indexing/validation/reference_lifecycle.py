"""Pure decision oracle for execution.md; not a queue or concurrency proof."""
from collections.abc import Iterable

STATES = {'PLANNED', 'RUNNING', 'PAUSED', 'FAILED', 'SUCCEEDED'}
INTENTS = {'HOLD', 'RUN', 'PAUSE'}
WORK_STATES = {'PENDING', 'RUNNING', 'FAILED', 'SUCCEEDED'}


def dataset_state(work: Iterable[str], intents: Iterable[str], *,
                  completion_verified: bool, ever_attempted: bool) -> str:
    work, intents = tuple(work), tuple(intents)
    if not set(work) <= WORK_STATES or not set(intents) <= INTENTS:
        raise ValueError('unknown work state or run intent')
    if completion_verified:
        if any(s != 'SUCCEEDED' for s in work):
            raise ValueError('completion cannot verify unfinished work')
        return 'SUCCEEDED'
    if 'RUNNING' in work:
        return 'RUNNING'
    if 'FAILED' in work:
        return 'FAILED'
    if 'RUN' in intents:
        return 'RUNNING'
    return 'PAUSED' if ever_attempted else 'PLANNED'


def run_state(intent: str, selected_states: Iterable[str]) -> str:
    selected_states = tuple(selected_states)
    if intent not in INTENTS or len(selected_states) != 3 or not set(selected_states) <= STATES:
        raise ValueError('a run requires a valid intent and three dataset states')
    if all(s == 'SUCCEEDED' for s in selected_states):
        return 'SUCCEEDED'
    if intent == 'PAUSE':
        return 'PAUSED'
    if intent == 'HOLD':
        return 'PLANNED'
    return 'FAILED' if 'FAILED' in selected_states else 'RUNNING'


def can_claim(*, state: str, launching_intent: str, work_state: str,
              demand: bool, prerequisites: bool, due: bool, resources: bool,
              plan_frozen: bool, component: str) -> bool:
    if state not in STATES or launching_intent not in INTENTS or work_state not in WORK_STATES:
        raise ValueError('unknown admission state')
    if component not in {'text_metadata', 'extract', 'resolve', 'name_flags', 'semgrep_flags'}:
        raise ValueError('unknown work component')
    return (state != 'SUCCEEDED' and launching_intent == 'RUN'
            and work_state == 'PENDING' and demand and prerequisites and due
            and resources and (plan_frozen or component == 'text_metadata'))


def lease_valid(*, state: str, work_state: str, token: str, current_token: str,
                generation: int, current_generation: int, now: float, expires: float) -> bool:
    return (state != 'SUCCEEDED' and work_state == 'RUNNING'
            and token == current_token and generation == current_generation
            and expires > now)
