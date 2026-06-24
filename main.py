from citam_pydraw import Date, Ellipse, Line, Text, Window, animation

CLOCK_RADIUS = 300
CLOCK_SIZE = CLOCK_RADIUS * 2
WINDOW_SIZE = CLOCK_SIZE + 100
CENTER = int(WINDOW_SIZE / 2)

HOUR_HAND_LENGTH = CLOCK_RADIUS * 0.4
HOUR_HAND_THICKNESS = 8
MINUTE_HAND_LENGTH = CLOCK_RADIUS * 0.6
MINUTE_HAND_THICKNESS = 4
SECOND_HAND_LENGTH = CLOCK_RADIUS * 0.85
SECOND_HAND_THICKNESS = 2

SCALE_START = (WINDOW_SIZE - CLOCK_SIZE) / 2
SCALE_END = SCALE_START + (CENTER - SCALE_START) / 25
FONT_SIZE = int(CLOCK_RADIUS / 7)
DIAL_LOCATION = SCALE_START + (CENTER - SCALE_START) / 6

DEFAULT_HOUR_COLOR = "#000000"
ACTIVE_HOUR_COLOR = "#FB2B37"


@animation(True)
def draw():
    draw_hands()
    draw_dials()
    draw_scales()


def draw_dials():
    Ellipse(CENTER, CENTER, CLOCK_SIZE, CLOCK_SIZE).noFill()

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
    Line(
        CENTER, CENTER, CENTER, CENTER - HOUR_HAND_LENGTH, HOUR_HAND_THICKNESS
    ).setRotationCenter(CENTER, CENTER).rotate(
        (date.hour + date.minute / 60) / 12 * 360  # pyright: ignore
    )
    # 分針
    Line(
        CENTER, CENTER, CENTER, CENTER - MINUTE_HAND_LENGTH, MINUTE_HAND_THICKNESS
    ).setRotationCenter(CENTER, CENTER).rotate(
        (date.minute + date.second / 60) / 60 * 360  # pyright: ignore
    )
    # 秒針
    Line(
        CENTER, CENTER, CENTER, CENTER - SECOND_HAND_LENGTH, SECOND_HAND_THICKNESS
    ).setRotationCenter(CENTER, CENTER).rotate(
        (date.second + date.milli_second / 1000) / 60 * 360  # pyright: ignore
    ).fill("#f00")


if __name__ == "__main__":
    window = (
        Window(WINDOW_SIZE, WINDOW_SIZE)
        .title("デジタルアナログ時計")
        .background("#fff")
    )

    date = Date()

    draw()
    window.show()
