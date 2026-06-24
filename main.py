# type: ignore

from citam_pydraw import (
    Arc,
    Date,
    Ellipse,
    KeyBoard,
    Line,
    Mouse,
    Music,
    Rectangle,
    Text,
    Window,
    animation,
    keyPressed,
    mousePressed,
)
from math import atan2, pi, sin, cos

CLOCK_RADIUS = 300
CLOCK_SIZE = CLOCK_RADIUS * 2
WINDOW_SIZE = CLOCK_SIZE + 100
CENTER = int(WINDOW_SIZE / 2)

HOUR_HAND_LENGTH = CLOCK_RADIUS * 0.4
HOUR_HAND_THICKNESS = 8
MINUTE_HAND_LENGTH = CLOCK_RADIUS * 0.7
MINUTE_HAND_THICKNESS = 4
SECOND_HAND_LENGTH = CLOCK_RADIUS * 0.85
SECOND_HAND_THICKNESS = 2

SCALE_START = (WINDOW_SIZE - CLOCK_SIZE) / 2
SCALE_END = SCALE_START + (CENTER - SCALE_START) / 25
FONT_SIZE = int(WINDOW_SIZE * 0.05)
DIAL_LOCATION = SCALE_START + (CENTER - SCALE_START) / 6

CLOCK_COLOR = "#FFFFFF"
SUNRISE_COLOR = "#FB702B"
NIGHT_COLOR = "#160764"
NOON_COLOR = "#2BA4FB"

DEFAULT_HOUR_COLOR = "#000000"
ACTIVE_HOUR_COLOR = "#FB2B37"

TIMER_COLOR = "#FF0000"
TIMER_BACKGROUND_COLOR_SETTING = "#FFCCCC"
TIMER_BACKGROUND_COLOR_SET = "#CCCCFF"


@animation(True)
def draw():
    key_pressed()
    mouse_pressed()
    draw_background()
    draw_dials()
    draw_timer()
    draw_hands()
    draw_scales()


@keyPressed
def key_pressed():
    global current_mode, timer_value

    assert keyboard is not None

    if keyboard.key == "t":
        if current_mode == "normal":
            if timer_value is not None:
                timer_value = None
            else:
                current_mode = "set_timer"
        elif current_mode == "set_timer":
            current_mode = "normal"


@mousePressed
def mouse_pressed():
    global current_mode, timer_value

    if mouse.pressButton == "left" and current_mode == "set_timer":
        current_mode = "normal"
        timer_value = int(30 - atan2(mouse.X - CENTER, mouse.Y - CENTER) / pi * 30)


def draw_background():
    hour = date.hour + date.minute / 60

    if 4.5 <= hour < 7:
        Rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE).fill(SUNRISE_COLOR)
    elif 7 <= hour < 17:
        Rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE).fill(NOON_COLOR)
    elif 17 <= hour < 20:
        Rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE).fill(SUNRISE_COLOR)
    elif 20 <= hour < 24 or 0 <= hour < 4.5:
        Rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE).fill(NIGHT_COLOR)


def draw_dials():
    Ellipse(CENTER, CENTER, CLOCK_SIZE, CLOCK_SIZE).fill(CLOCK_COLOR)

    for i in range(0, 12):
        text = "12" if i == 0 else str(i)
        fill_color = ACTIVE_HOUR_COLOR if (date.hour % 12) == i else DEFAULT_HOUR_COLOR

        Text(text, CENTER, DIAL_LOCATION).fill(fill_color).font(
            "", FONT_SIZE
        ).setRotationCenter(CENTER, CENTER).rotate(int((360 / 12) * i))


def draw_scales():
    for i in range(1, 61):
        if (i % 5) == 0:
            scale = Line(CENTER, SCALE_START, CENTER, SCALE_END * 1.1, 2)
        else:
            scale = Line(CENTER, SCALE_START, CENTER, SCALE_END, 1)
        scale.setRotationCenter(CENTER, CENTER)
        scale.rotate(int((360 / 60) * i))


def draw_hands():
    # 時針
    # Line(
    #    CENTER, CENTER, CENTER, CENTER - HOUR_HAND_LENGTH, HOUR_HAND_THICKNESS
    # ).setRotationCenter(CENTER, CENTER).rotate(
    #    (date.hour + date.minute / 60) / 12 * 360
    # )
    # 分針
    Line(
        CENTER, CENTER, CENTER, CENTER - MINUTE_HAND_LENGTH, MINUTE_HAND_THICKNESS
    ).setRotationCenter(CENTER, CENTER).rotate(
        (date.minute + date.second / 60) / 60 * 360
    )
    # 秒針
    Line(
        CENTER, CENTER, CENTER, CENTER - SECOND_HAND_LENGTH, SECOND_HAND_THICKNESS
    ).setRotationCenter(CENTER, CENTER).rotate(
        (date.second + date.milli_second / 1000) / 60 * 360
    ).fill("#f00")


def draw_timer():
    global timer_value

    assert mouse is not None

    if date.minute == timer_value:
        timer_value = None
        timer_sound.play()

    current_degree = int((date.minute + date.second / 60) / 60 * 360)

    if current_mode == "set_timer":
        target_degree = int(
            int(30 - atan2(mouse.X - CENTER, mouse.Y - CENTER) / pi * 30) / 60 * 360
        )

        Arc(
            CENTER,
            CENTER,
            CLOCK_SIZE * 0.75,
            CLOCK_SIZE * 0.75,
            90 - current_degree,
            -(target_degree - current_degree + 360),
        ).fill(TIMER_BACKGROUND_COLOR_SETTING).noOutline()
    elif timer_value is not None:
        target_degree = int(timer_value / 60 * 360)

        Arc(
            CENTER,
            CENTER,
            CLOCK_SIZE * 0.75,
            CLOCK_SIZE * 0.75,
            90 - current_degree,
            -(target_degree - current_degree + 360),
        ).fill(TIMER_BACKGROUND_COLOR_SET).noOutline()

        Text(
            f"{(timer_value - date.minute + 60) % 60}分",
            cos((target_degree - 90) / 180 * pi) * CLOCK_RADIUS * 0.65 + CENTER,
            sin((target_degree - 90) / 180 * pi) * CLOCK_RADIUS * 0.65 + CENTER,
        ).font("", 24).fill(TIMER_COLOR)


if __name__ == "__main__":
    window = (
        Window(WINDOW_SIZE, WINDOW_SIZE)
        .title("デジタルアナログ時計")
        .background(CLOCK_COLOR)
    )

    date = Date()
    keyboard = KeyBoard()
    mouse = Mouse()

    current_mode = "normal"
    timer_value = None

    timer_sound = Music("./timer.mp3")

    draw()
    window.show()
