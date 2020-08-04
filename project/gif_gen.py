import sys
from datetime import datetime, timedelta
from random import randint

import ipdb
from PIL import Image, ImageDraw

from rolling_period import (
    RollingPeriodRuleSettings,
    Session,
    get_session_rolling_hours_rule_status
)

images = []

width = 1200
color_1 = (255, 255, 255)
color_2 = (255, 0, 0)
color_3 = (255, 0, 255)
blue = (0, 0, 255)
step = 8

bar_height = 40
bar_bottom_pos = (width / 2) - (bar_height / 2)
bar_top_pos = bar_bottom_pos + bar_height

line_y_pos = bar_top_pos + bar_height / 2
window_width = timedelta(days=5)


def draw_session(session: Session, draw, color=color_2):
    x0 = datetime_to_pos(session.start_datetime)
    x1 = datetime_to_pos(session.end_datetime)
    y0 = bar_bottom_pos
    y1 = bar_top_pos
    draw.rectangle([(x0, y0), (x1, y1)], fill=color, outline=color)


def draw_window_ending_at(dt: datetime, draw):
    x0 = datetime_to_pos(dt - window_width)
    x1 = datetime_to_pos(dt)
    y0 = line_y_pos
    y1 = line_y_pos
    draw.line([(x0, y0), (x1, y1)], fill=color_2, width=10)


def datetime_to_pos(date_time: datetime) -> float:
    return width / (total_time / (date_time - first_start_datetime))


sessions = []
first_start_datetime = datetime.now()
end_datetime = first_start_datetime


for i in range(10):
    start_datetime = end_datetime + timedelta(hours=randint(10, 48))
    end_datetime = start_datetime + timedelta(hours=randint(6, 12))
    sessions.append(Session(i, start_datetime, end_datetime))

total_time = end_datetime - first_start_datetime

sessions_image = Image.new('RGB', (width, width), color_1)
base_draw = ImageDraw.Draw(sessions_image)

period_end_boundary = None


def trace_lines(frame, event, arg):
    lo = frame.f_locals
    if 'i' in lo:
        global i
        if i == lo['i']:
            return
        i = lo['i']
        next_image = Image.new('RGB', (width, width), color_1)
        draw = ImageDraw.Draw(next_image)
        for session in lo['sorted_sessions']:
            if session == lo['test_session']:
                draw_session(session, draw, color=color_3)
            elif 'sessions_in_window' in lo and session in lo['sessions_in_window']:
                draw_session(session, draw, color=blue)
            else:
                draw_session(session, draw)
        draw_window_ending_at(lo['period_end_boundary'], draw)
        draw.text([300,300], str(lo['max_hours_in_period']), fill=blue)
        images.append(next_image)


def trace_calls(frame, event, arg):
    if frame.f_code.co_name == "get_session_rolling_hours_rule_status":
        return trace_lines
    return

sys.settrace(trace_calls)

result = get_session_rolling_hours_rule_status(
    RollingPeriodRuleSettings(30, timedelta(days=5)),
    sessions[3],
    sessions)


images[0].save('sessions.gif', save_all=True, append_images=images[1:],
               optimize=False, duration=2000, loop=0)
