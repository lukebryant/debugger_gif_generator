import sys
from datetime import datetime, timedelta
from functools import partial
from random import randint
from typing import Dict

import ipdb
from PIL import Image, ImageDraw, ImageFont

from rolling_period import (
    RollingPeriodRuleSettings,
    Session,
    get_session_rolling_hours_rule_status
)

images = []

width = 1200
black = (0, 0, 0)
translucent_black = (128, 128, 128, 128)
white = (255, 255, 255)
red = (255, 0, 0)
purple = (255, 0, 255)
blue = (0, 0, 255)
step = 8
font = ImageFont.truetype("./Roboto-Regular.ttf", 20)


bar_height = 40
bar_bottom_pos = (width / 2) - (bar_height / 2)
bar_top_pos = bar_bottom_pos + bar_height
bottom_bar_label_pos = bar_bottom_pos - 30
top_bar_label_pos = bar_top_pos + 10

line_y_pos = bar_bottom_pos - 70
window_width = timedelta(days=5)


def draw_session(session: Session, draw, max_hours_in_period=0, color=red):
    x0 = datetime_to_pos(session.start_datetime)
    x1 = datetime_to_pos(session.end_datetime)
    y0 = bar_bottom_pos
    y1 = bar_top_pos
    draw.rectangle([(x0, y0), (x1, y1)], fill=color, outline=color)
    top_text_pos = (x0, top_bar_label_pos)
    bottom_text_pos = (x0, bottom_bar_label_pos)
    draw.text(top_text_pos, str(session.duration_hours()),
              font=font, fill=black)
    draw.text(bottom_text_pos, str(max_hours_in_period), font=font, fill=black)


def draw_window_ending_at(dt: datetime, draw, hours_in_window=0):
    x0 = datetime_to_pos(dt - window_width)
    x1 = datetime_to_pos(dt)
    y0 = line_y_pos
    y1 = line_y_pos
    draw.text((x0 + (x1 - x0) / 2, line_y_pos - 30), str(hours_in_window),
              font=font, fill=black)
    draw.line([(x0, y0), (x1, y1)], fill=black, width=6)
    draw.line([(x0, y0 - 2), (x0, y0 + 10)], fill=black, width=6)
    draw.line([(x1, y1 - 2), (x1, y1 + 10)], fill=black, width=6)


def datetime_to_pos(date_time: datetime) -> float:
    return width / (total_time / (date_time - first_start_datetime))


sessions = []
first_start_datetime = datetime.now()
end_datetime = first_start_datetime


for i in range(10):
    start_datetime = end_datetime + timedelta(hours=randint(10, 24))
    end_datetime = start_datetime + timedelta(hours=randint(5, 8))
    sessions.append(Session(i, start_datetime, end_datetime))

total_time = end_datetime - first_start_datetime


def draw_date_lines(start: datetime, end: datetime):
    start_of_day = datetime(
        year=start.year,
        month=start.month,
        day=start.day + 1, hour=0, second=0)
    base_image = Image.new('RGBA', (width, width), white)
    i = 0
    while(start_of_day < end_datetime):
        draw = ImageDraw.Draw(base_image)
        x = datetime_to_pos(start_of_day)
        y0 = width / 3
        y1 = 2 * width / 3
        # show text for every other day because we don't have space for all
        if i % 2 == 0:
            draw.text((x, y1 + 60), str(start_of_day.date()), font=font,
                fill=black)
            y1 += 50
        draw.line([(x, y0), (x, y1)],
            fill=translucent_black, width=1)
        start_of_day += timedelta(days=1)
        i += 1
    return base_image


base_image = draw_date_lines(first_start_datetime, end_datetime)


def trace_lines(previous_i, frame, event, arg):
    lo = frame.f_locals
    if 'i' in lo:
        global i
        if i == lo['i']:
            return
        i = lo['i']
        draw_next_image(lo)
    return partial(trace_lines, i)


def draw_next_image(lo: Dict):  # lo means locals
    next_image = base_image.copy()
    draw = ImageDraw.Draw(next_image)
    for session in lo['sorted_sessions']:
        if session in lo['sessions_in_window']:
            style_kwargs = {'color': blue}
        else:
            style_kwargs = {}
        draw_session(
            session,
            draw,
            lo['max_hours_in_period_for_sessions_dict'][session.id],
            **style_kwargs)
    draw_window_ending_at(
        lo['period_end_boundary'],
        draw,
        lo['hours_in_period'])
    draw.multiline_text(
        [20, 20],
        str('\n'.join([k + ': ' + str(v) for k, v in lo.items()])),
        fill=blue,
        font=font)
    images.append(next_image)


def trace_calls(frame, event, arg):
    if frame.f_code.co_name == "get_session_rolling_hours_rule_status":
        return partial(trace_lines, None)
    return


sys.settrace(trace_calls)

result = get_session_rolling_hours_rule_status(
    RollingPeriodRuleSettings(30, timedelta(days=5)),
    sessions)


images[0].save('sessions.gif', save_all=True, append_images=images[1:],
               optimize=False, duration=2000, loop=0)
