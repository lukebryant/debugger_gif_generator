from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Set


@dataclass
class RollingPeriodRuleSettings(object):
    hours_threshold: float
    rolling_period_size: timedelta


@dataclass
class RollingHoursRuleStatus(object):
    is_broken: bool
    max_worked_hours: float


@dataclass(frozen=True)
class Session(object):
    id: int
    start_datetime: datetime
    end_datetime: datetime

    def duration_hours(self):
        return (self.end_datetime - self.start_datetime).total_seconds() / 3600


def get_session_rolling_hours_rule_status(
    rolling_period_rule_settings: RollingPeriodRuleSettings,
    test_session: Session,
    sorted_sessions: List[Session],
) -> RollingHoursRuleStatus:
    """
        Naive in that we only consider sessions that *start* within some rolling
        window, to avoid weird edge cases. I believe a similar and performance
        equivalent approach could be used to do this strictly. I.e. dealing
        with partial sessions on the boundaries of the window.
    """
    hours_threshold = rolling_period_rule_settings.hours_threshold
    rolling_period_size = rolling_period_rule_settings.rolling_period_size

    period_start_boundary = test_session.start_datetime - rolling_period_size
    period_end_boundary = test_session.start_datetime

    hours_in_period = test_session.duration_hours()
    max_hours_in_period = hours_in_period
    earliest_session_in_window_i = 0
    sessions_in_window: Set[Session] = set()
    for i, session in enumerate(sorted_sessions):
        hours_in_period += session.duration_hours()
        sessions_in_window.add(session)
        if session.start_datetime > period_end_boundary:
            period_start_boundary = session.start_datetime - rolling_period_size
            # Remove hours from sessions that are no longer in the window
            for j, cutoff_session in enumerate(
                    sorted_sessions[earliest_session_in_window_i:]):
                if cutoff_session.start_datetime < period_start_boundary:
                    hours_in_period -= cutoff_session.duration_hours()
                    print(f'removing session with id: {cutoff_session.id}')
                    sessions_in_window.remove(cutoff_session)
                else:
                    earliest_session_in_window_i = earliest_session_in_window_i + j
                    print(f'earliest_session_in_window_i: {earliest_session_in_window_i}')
                    period_end_boundary = (
                        cutoff_session.start_datetime + rolling_period_size)
                    break
        max_hours_in_period = max(hours_in_period, max_hours_in_period)
    return RollingHoursRuleStatus(
        is_broken=max_hours_in_period > hours_threshold,
        max_worked_hours=max_hours_in_period)
