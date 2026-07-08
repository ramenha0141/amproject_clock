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
    animationSpeed,
    color,
    colorMode,
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

# 時刻(時)ごとの空の色 (Minecraftの昼夜サイクルを参考)。
# 末尾の 24.0 は先頭 0.0 と同色にしてループを滑らかにつなぐ。
SKY_KEYFRAMES = [
    (0.0, "#0A1133"),  # 深夜: 濃い藍色の夜空
    (5.0, "#27305C"),  # 夜明け前: 空が白み始める
    (6.5, "#FF7B3D"),  # 日の出: オレンジの朝焼け
    (8.0, "#7FB0FF"),  # 朝
    (12.0, "#78A7FF"),  # 正午: Minecraftの昼空の青
    (16.0, "#78A7FF"),  # 午後
    (18.0, "#FB6A2B"),  # 日の入り: 夕焼けのオレンジ
    (19.5, "#3A2A5C"),  # 薄暮: 紫がかった空
    (21.0, "#0F1840"),  # 夜
    (24.0, "#0A1133"),  # 深夜 (0:00へループ)
]

DEFAULT_HOUR_COLOR = "#000000"
ACTIVE_HOUR_COLOR = "#FB2B37"

TIMER_COLOR = "#FF0000"
TIMER_BACKGROUND_COLOR_SETTING = "#FFCCCC"
TIMER_BACKGROUND_COLOR_SET = "#CCCCFF"

# ガチャモード用の色定義
GACHA_TEXT_COLOR = "#FF0000"


def mouse_pos_to_minute():
    return (30 - atan2(mouse.X - CENTER, mouse.Y - CENTER) / pi * 30) % 60


@animation(True)
def draw():
    global count

    count = (count + 1) % 100

    key_pressed()
    mouse_pressed()
    draw_background()
    draw_dials()
    draw_timer()
    draw_hands()
    draw_scales()
    draw_gacha_interface()  # ガチャ機能の描画処理


@keyPressed
def key_pressed():
    global current_mode, timer_value, gaming_mode, gacha_n, gacha_m, gacha_result_prob

    if keyboard.key == "t":
        if current_mode == "normal":
            if timer_value is not None:
                timer_value = None
            else:
                current_mode = "set_timer"
        elif current_mode == "set_timer":
            current_mode = "normal"
    elif keyboard.key == "g":
        gaming_mode = not gaming_mode

    # 「k」キーでのガチャモード切り替え・解除
    elif keyboard.key == "k":
        # ガチャモードのどの状態(選択中・結果表示中)であっても通常に戻す
        if current_mode in ["gacha_n", "gacha_m", "gacha_result"]:
            current_mode = "normal"
            gacha_n = None
            gacha_m = None
            gacha_result_prob = None
        else:
            # 通常モードから新しくガチャモードを開始
            current_mode = "gacha_n"
            gacha_n = None
            gacha_m = None
            gacha_result_prob = None


@mousePressed
def mouse_pressed():
    global current_mode, timer_value, gacha_n, gacha_m, gacha_result_prob

    if mouse.pressButton == "left":
        if current_mode == "set_timer":
            current_mode = "normal"
            timer_value = int(mouse_pos_to_minute() + 0.5) % 60

        # 確率 n の決定
        elif current_mode == "gacha_n":
            raw_min = mouse_pos_to_minute()
            if raw_min > 59.9:
                raw_min = 59.9
            gacha_n = round(raw_min * 0.1, 2)
            current_mode = "gacha_m"  # 続けてmの選択（連動プレビュー）モードへ

        # 回数 m の決定と結果の確定
        elif current_mode == "gacha_m":
            raw_min = mouse_pos_to_minute()
            if raw_min > 59.5:
                raw_min = 59.5
            gacha_m = int(raw_min * 2)
            current_mode = "gacha_result"  # 結果確定画面モードへ

            # 確定時の確率計算
            if gacha_n > 0 and gacha_m > 0:
                gacha_result_prob = 1 - (1 - gacha_n / 100) ** gacha_m
            else:
                gacha_result_prob = 0.0


def lerp_color(c1, c2, t):
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return "#" + format(r, "02x") + format(g, "02x") + format(b, "02x")


def sky_color(hour):
    for i in range(len(SKY_KEYFRAMES) - 1):
        t0, c0 = SKY_KEYFRAMES[i]
        t1, c1 = SKY_KEYFRAMES[i + 1]
        if t0 <= hour < t1:
            return lerp_color(c0, c1, (hour - t0) / (t1 - t0))
    return SKY_KEYFRAMES[-1][1]


def draw_background():
    if gaming_mode:
        Rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE).fill(color(count, 100, 100))
    else:
        hour = date.hour + date.minute / 60 + date.second / 3600
        Rectangle(0, 0, WINDOW_SIZE, WINDOW_SIZE).fill(sky_color(hour))


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

    if date.minute == timer_value:
        timer_value = None
        timer_sound.play()

    current_degree = int((date.minute + date.second / 60) / 60 * 360)

    if current_mode == "set_timer":
        target_minute = mouse_pos_to_minute()
        target_degree = target_minute * 6

        Arc(
            CENTER,
            CENTER,
            CLOCK_SIZE * 0.75,
            CLOCK_SIZE * 0.75,
            90 - current_degree,
            -(target_degree - current_degree + 360),
        ).fill(TIMER_BACKGROUND_COLOR_SETTING).noOutline()

        Text(
            f"{(target_minute - date.minute + 60) % 60}分",
            cos((target_degree - 90) / 180 * pi) * CLOCK_RADIUS * 0.65 + CENTER,
            sin((target_degree - 90) / 180 * pi) * CLOCK_RADIUS * 0.65 + CENTER,
        ).font("", 24).fill(TIMER_COLOR)
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


def draw_gacha_interface():
    current_mouse_min = mouse_pos_to_minute()

    str_n = "n"
    str_m = "m"
    prob_to_display = None  # 画面に表示する当たる確率のパーセンテージ

    # 1. 確率nの選択中
    if current_mode == "gacha_n":
        preview_min = current_mouse_min if current_mouse_min <= 59.9 else 59.9
        str_n = f"{round(preview_min * 0.1, 2):.2f}"

    # 2. 回数mの選択中（ここを「同時に出て連動して動く」ように大改造しました）
    elif current_mode == "gacha_m":
        str_n = f"{gacha_n:.2f}"

        # マウスの位置からリアルタイムに回数「m」を計算
        preview_min = current_mouse_min if current_mouse_min <= 59.5 else 59.5
        current_m = int(preview_min * 2)
        str_m = f"{current_m}"

        # 【重要】クリック前でも、マウスの回数変化に連動して確率をリアルタイム計算する
        if gacha_n > 0 and current_m > 0:
            prob_to_display = (1 - (1 - gacha_n / 100) ** current_m) * 100
        else:
            prob_to_display = 0.0

    # 3. クリックして結果が確定した後（gacha_result）
    elif current_mode == "gacha_result":
        str_n = f"{gacha_n:.2f}"
        str_m = f"{gacha_m}"
        if gacha_result_prob is not None:
            prob_to_display = gacha_result_prob * 100

    # ガチャモード稼働中なら、いつでも「n％の確率を m回する」をリアルタイム描写
    if current_mode in ["gacha_n", "gacha_m", "gacha_result"]:
        display_text = f"{str_n}％の確率を {str_m}回する"
        Text(display_text, CENTER + 15, CENTER).font("", FONT_SIZE).fill(
            GACHA_TEXT_COLOR
        )

    # 回数選択中（連動中）、または結果確定後のどちらでも下の行に「当たる確率」を数字で出す
    if prob_to_display is not None:
        result_text = f"当たる確率: {round(prob_to_display, 2):.2f}%"
        Text(result_text, CENTER + 60, CENTER + FONT_SIZE + 10).font(
            "", FONT_SIZE
        ).fill(GACHA_TEXT_COLOR)


if __name__ == "__main__":
    window = (
        Window(WINDOW_SIZE, WINDOW_SIZE)
        .title("デジタルアナログ時計")
        .background(CLOCK_COLOR)
    )
    animationSpeed(100)
    colorMode("HSV")

    date = Date()
    keyboard = KeyBoard()
    mouse = Mouse()
    timer_sound = Music("./timer.mp3")

    current_mode = "normal"
    timer_value = None
    gaming_mode = False
    count = 0

    gacha_n = None
    gacha_m = None
    gacha_result_prob = None

    draw()
    window.show()
