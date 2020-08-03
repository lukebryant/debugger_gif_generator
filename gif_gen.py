from dataclasses import dataclass
from datetime import datetime, timedelta
from PIL import Image, ImageDraw
from random import randint


images = []

width = 1200
color_1 = (255, 255, 255)
color_2 = (255, 0, 0)
step = 8

bar_height = 40
bar_bottom_pos = (width / 2) - (bar_height / 2)
bar_top_pos = bar_bottom_pos + bar_height

line_y_pos = bar_top_pos + bar_height / 2
window_width = timedelta(days=5)


@dataclass
class Session(object):
    start: datetime
    end: datetime


def draw_session(session: Session, draw):
    x0 = datetime_to_pos(session.start)
    x1 = datetime_to_pos(session.end)
    y0 = bar_bottom_pos
    y1 = bar_top_pos
    draw.rectangle([(x0, y0), (x1, y1)], fill=color_2, outline=color_2)


def draw_window_ending_at_session(session: Session, draw):
    x0 = datetime_to_pos(session.start - window_width)
    x1 = datetime_to_pos(session.start)
    y0 = line_y_pos
    y1 = line_y_pos
    draw.line([(x0, y0), (x1, y1)], fill=color_2, width=10)


def datetime_to_pos(date_time: datetime) -> float:
    return width / (total_time / (date_time - first_start))


sessions = []
first_start = datetime.now()
end = first_start
for s in range(10):
    start = end + timedelta(hours=randint(10, 48))
    end = start + timedelta(hours=randint(6, 12))
    sessions.append(Session(start, end))

total_time = end - first_start

sessions_image = Image.new('RGB', (width, width), color_1)
base_draw = ImageDraw.Draw(sessions_image)

for session in sessions:
    draw_session(session, base_draw)

base_draw.arc([(50, 50), (1000, 50)], 30, 0, fill=color_2, width=10)

for session in sessions[4:]:
    next_image = sessions_image.copy()
    draw = ImageDraw.Draw(next_image)
    draw_window_ending_at_session(session, draw)
    images.append(next_image)


images[0].save('sessions.gif', save_all=True, append_images=images[1:],
    optimize=False, duration=500, loop=0)
