import sys
from dataclasses import dataclass
from datetime import timedelta

from session.models import Session


def sample(a, b):
    x = a + b
    y = x * 2
    print('Sample: ' + str(y))


def trace_calls(frame, event, arg):
    if frame.f_code.co_name == "sample":
        print(frame.f_code)

        return trace_lines

    return


def trace_lines(frame, event, arg):
    print(frame.f_lineno)
    print(frame.f_locals)


sys.settrace(trace_calls)

sample(3, 2)
