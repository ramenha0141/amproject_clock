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
from math import atan2, pi, sin, cos, hypot, radians

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

ALARM_INTERVAL = 25
ALARM_COLOR = "#37B92E"

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

BALL_SIZE = int(CLOCK_SIZE * 0.025)
BALL_SPEED = 2
BALL_COLOR = "#111111"

# パドル(弧): 軸周りのレール上をマウス角度で公転。面は外向き。
PADDLE_RADIUS = CLOCK_RADIUS * 0.2
PADDLE_HALF_DEG = 33
PADDLE_THICKNESS = 12
PADDLE_COLOR = "#1E7A1E"
PADDLE_MAX_DEFLECT_DEG = 60  # パドル端に当てた時の最大偏向角(度)

WALL_RADIUS = CLOCK_RADIUS - BALL_SIZE / 2

# ブロック: 同心3重リング（各リング同数＝外側ほど弧が幅広）／弧で描画
BLOCK_RING_FACTORS = [0.55, 0.70, 0.85]
BLOCK_COUNT_PER_RING = 12
BLOCK_THICKNESS = 24
BLOCK_ANGLE_FILL = 0.82
BLOCK_HALF_DEG = (360 / BLOCK_COUNT_PER_RING) / 2 * BLOCK_ANGLE_FILL

BLOCKS = []  # 各要素: (r, bcx, bcy, half_ang_rad, tk_start, tk_extent)
for ring_radius_factor in BLOCK_RING_FACTORS:
    ring_radius = CLOCK_RADIUS * ring_radius_factor
    for k in range(BLOCK_COUNT_PER_RING):
        center_degree = k * (360 / BLOCK_COUNT_PER_RING)
        rad = radians(center_degree)
        bcx, bcy = sin(rad), -cos(rad)
        tk_center = 90 - center_degree
        BLOCKS.append(
            (
                ring_radius,
                bcx,
                bcy,
                radians(BLOCK_HALF_DEG),
                tk_center - BLOCK_HALF_DEG,
                2 * BLOCK_HALF_DEG,
            )
        )
BLOCK_COUNT = len(BLOCKS)
ALL_BLOCKS_MASK = (1 << BLOCK_COUNT) - 1


def mouse_pos_to_minute():
    return int(30 - atan2(mouse.X - CENTER, mouse.Y - CENTER) / pi * 30 + 0.5)


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
    draw_block()
    draw_alarm()


@keyPressed
def key_pressed():
    global current_mode, timer_value, gaming_mode, alarm_mode, alarm_start

    if keyboard.key == "t":
        if current_mode == "set_timer":
            current_mode = "normal"
        else:
            if timer_value is not None:
                timer_value = None
            else:
                current_mode = "set_timer"
    elif keyboard.key == "g":
        gaming_mode = not gaming_mode
    elif keyboard.key == "b":
        if current_mode == "block":
            current_mode = "normal"
        else:
            current_mode = "block"
            reset_block()
    elif keyboard.key == "a":
        alarm_mode = not alarm_mode
        alarm_start = date.minute


@mousePressed
def mouse_pressed():
    global current_mode, timer_value

    if mouse.pressButton == "left" and current_mode == "set_timer":
        current_mode = "normal"
        timer_value = mouse_pos_to_minute()


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
    for i in range(0, 60):
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


def reset_block():
    global ball_x, ball_y, ball_vx, ball_vy, block_state

    ball_x = CENTER
    ball_y = CENTER
    launch_degree = 30  # 時計規約(0 = 真上)
    ball_vx = sin(radians(launch_degree)) * BALL_SPEED
    ball_vy = -cos(radians(launch_degree)) * BALL_SPEED
    block_state = 0


def draw_block():
    global ball_x, ball_y, ball_vx, ball_vy, block_state

    if current_mode != "block":
        return

    # (A) ボールの位置更新
    ball_x += ball_vx
    ball_y += ball_vy

    # (B) 外周の壁で反射
    dx, dy = ball_x - CENTER, ball_y - CENTER
    dist = hypot(dx, dy)
    if dist > WALL_RADIUS and dist > 0:
        nx, ny = dx / dist, dy / dist
        dot = ball_vx * nx + ball_vy * ny
        if dot > 0:
            ball_vx -= 2 * dot * nx
            ball_vy -= 2 * dot * ny
        ball_x = CENTER + nx * WALL_RADIUS
        ball_y = CENTER + ny * WALL_RADIUS

    # (C) ブロックとの当たり判定・破壊(極座標/弧)
    dx, dy = ball_x - CENTER, ball_y - CENTER
    dist = hypot(dx, dy)
    if dist > 0:
        bux, buy = dx / dist, dy / dist  # ボールの半径方向単位ベクトル
        for i in range(BLOCK_COUNT):
            if block_state & (1 << i):
                continue
            r, bcx, bcy, half_ang, _, _ = BLOCKS[i]
            ang = atan2(bcx * buy - bcy * bux, bcx * bux + bcy * buy)
            pen_r = (BLOCK_THICKNESS / 2 + BALL_SIZE / 2) - abs(dist - r)
            pen_t = (half_ang * r + BALL_SIZE / 2) - abs(ang) * r
            if pen_r > 0 and pen_t > 0:
                block_state |= 1 << i
                if pen_r <= pen_t:
                    sign = 1 if dist >= r else -1
                    nx, ny, pen = bux * sign, buy * sign, pen_r
                else:
                    sign = 1 if ang >= 0 else -1
                    nx, ny, pen = -buy * sign, bux * sign, pen_t
                dot = ball_vx * nx + ball_vy * ny
                if dot < 0:
                    ball_vx -= 2 * dot * nx
                    ball_vy -= 2 * dot * ny
                ball_x += nx * pen
                ball_y += ny * pen
                break

    # (D) 全ブロック破壊なら再出現(エンドレス)
    if block_state == ALL_BLOCKS_MASK:
        block_state = 0

    # (E) 弧パドル(軸周りを公転)で反射 — 当たり位置に応じて反射角を変える
    mouse_degree = mouse_pos_to_minute() * 6
    prad = radians(mouse_degree)
    pdx, pdy = sin(prad), -cos(prad)  # パドル中心の半径方向(外向き)
    dx, dy = ball_x - CENTER, ball_y - CENTER
    dist = hypot(dx, dy)
    if dist > 0:
        bux, buy = dx / dist, dy / dist  # ボールの半径方向(外向き)
        band = BALL_SIZE / 2 + PADDLE_THICKNESS / 2
        half_rad = radians(PADDLE_HALF_DEG)
        ang = atan2(pdx * buy - pdy * bux, pdx * bux + pdy * buy)
        if abs(dist - PADDLE_RADIUS) < band and abs(ang) < half_rad:
            dot = ball_vx * bux + ball_vy * buy
            if dot < 0:
                speed = hypot(ball_vx, ball_vy)
                deflect = (ang / half_rad) * radians(PADDLE_MAX_DEFLECT_DEG)
                nx = bux * cos(deflect) - buy * sin(deflect)
                ny = bux * sin(deflect) + buy * cos(deflect)
                ball_vx = nx * speed
                ball_vy = ny * speed
            ball_x = CENTER + bux * (PADDLE_RADIUS + band)
            ball_y = CENTER + buy * (PADDLE_RADIUS + band)

    # (F) 描画
    for i in range(BLOCK_COUNT):
        if block_state & (1 << i):
            continue
        r, _, _, _, tk_start, tk_extent = BLOCKS[i]
        Arc(CENTER, CENTER, r * 2, r * 2, tk_start, tk_extent).outlineStyle(
            "arc"
        ).outlineWidth(BLOCK_THICKNESS).outlineFill(
            color(int(i / BLOCK_COUNT * 100), 80, 90)
        )

    tk_center = 90 - mouse_degree
    Arc(
        CENTER,
        CENTER,
        PADDLE_RADIUS * 2,
        PADDLE_RADIUS * 2,
        tk_center - PADDLE_HALF_DEG,
        2 * PADDLE_HALF_DEG,
    ).outlineStyle("arc").outlineWidth(PADDLE_THICKNESS).outlineFill(PADDLE_COLOR)

    Ellipse(ball_x, ball_y, BALL_SIZE, BALL_SIZE).fill(BALL_COLOR)

def draw_alarm():
    global alarm_set, alarm_start
    if alarm_mode:
        alarm_set = (alarm_start + ALARM_INTERVAL) % 60
        scale = (
            Line(CENTER, SCALE_START, CENTER, SCALE_END * 1.2, 2)
            .fill(ALARM_COLOR)
            .lineWeight(5)
        )
        scale.setRotationCenter(CENTER, CENTER)
        scale.rotate(int((360 / 60) * alarm_set))
        if date.minute == alarm_set:
            alarm_sound.play()
            alarm_start = alarm_set


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
    alarm_sound = Music("./timer.mp3")

    current_mode = "normal"
    timer_value = None
    gaming_mode = False
    alarm_mode = False
    alarm_start = 0
    alarm_set = 0
    count = 0

    draw()
    window.show()
