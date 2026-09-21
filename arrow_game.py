import pygame
import sys
import math

pygame.init()

# 窗口设置
WIDTH = 480
HEIGHT = 580

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("一箭又一箭")

clock = pygame.time.Clock()

# 字体
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc"
]

font_path = None

for path in FONT_PATHS:
    try:
        pygame.font.Font(path, 16)
        font_path = path
        break
    except:
        pass

if font_path:
    FONT_SMALL = pygame.font.Font(font_path, 15)
    FONT_NORMAL = pygame.font.Font(font_path, 18)
    FONT_BIG = pygame.font.Font(font_path, 28)
    FONT_TITLE = pygame.font.Font(font_path, 36)
else:
    FONT_SMALL = pygame.font.SysFont("arial", 15)
    FONT_NORMAL = pygame.font.SysFont("arial", 18)
    FONT_BIG = pygame.font.SysFont("arial", 28)
    FONT_TITLE = pygame.font.SysFont("arial", 36)


# 颜色
COLOR_BG = (245, 246, 250)
COLOR_CELL = (255, 255, 255)

COLOR_ARROW = (52, 120, 246)
COLOR_ERROR = (235, 87, 87)
COLOR_SUCCESS = (46, 184, 114)

COLOR_HINT = (245, 180, 45)

COLOR_WHITE = (255, 255, 255)
COLOR_TEXT = (45, 55, 72)

COLOR_BUTTON = (90, 105, 130)
COLOR_BUTTON_HOVER = (60, 75, 100)

COLOR_GRID = (218, 224, 233)

# 棋盘
ROWS = 5
COLS = 5

CELL_SIZE = 60

BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE

BOARD_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_Y = 135


# 关卡数据
LEVELS = [
    {
        "mistakes": 3,
        "arrows": [
            ([(0, 1)], "U"),
            ([(1, 1)], "U"),
            ([(2, 1)], "U"),

            ([(0, 3)], "U"),
            ([(1, 3)], "U"),
            ([(2, 3)], "L"),

            ([(1, 4)], "R"),
            ([(3, 0)], "L"),
            ([(4, 2)], "D"),
        ]
    },

    {
        "mistakes": 3,
        "arrows": [
            ([(0, 0)], "U"),
            ([(1, 0)], "U"),
            ([(2, 0)], "U"),

            ([(1, 4)], "D"),
            ([(2, 4)], "D"),
            ([(3, 4)], "D"),

            ([(4, 1)], "R"),
            ([(4, 2)], "R"),
            ([(4, 3)], "R"),

            ([(0, 2)], "L"),
            ([(0, 3)], "L"),

            ([(2, 2)], "D"),
            ([(3, 2)], "D"),
        ]
    },

    {
        "mistakes": 3,
        "arrows": [
            ([(0, 0)], "R"),
            ([(0, 1)], "R"),
            ([(0, 2)], "R"),
            ([(0, 3)], "R"),
            ([(0, 4)], "U"),

            ([(1, 0)], "U"),
            ([(2, 0)], "U"),
            ([(3, 0)], "U"),

            ([(1, 2)], "D"),
            ([(2, 2)], "D"),
            ([(3, 2)], "D"),

            ([(2, 1)], "R"),

            ([(4, 1)], "L"),
            ([(4, 2)], "L"),
            ([(4, 3)], "L"),
        ]
    }
]


# 绘制箭头
def draw_custom_arrow(
        surface,
        cell_rect,
        direction,
        color,
        shake_offset=0,
        flying_offset=(0, 0)
):
    cx, cy = cell_rect.center

    cx += shake_offset
    cx += flying_offset[0]
    cy += flying_offset[1]

    w = cell_rect.width * 0.55
    h = cell_rect.height * 0.55

    raw_points = [
        (0, -h / 2),
        (w / 2, 0),
        (w / 4, 0),
        (w / 4, h / 2),
        (-w / 4, h / 2),
        (-w / 4, 0),
        (-w / 2, 0)
    ]

    transformed_points = []

    for px, py in raw_points:

        if direction == "U":
            rx, ry = px, py

        elif direction == "D":
            rx, ry = -px, -py

        elif direction == "L":
            rx, ry = py, -px

        elif direction == "R":
            rx, ry = -py, px

        else:
            rx, ry = px, py

        transformed_points.append(
            (cx + rx, cy + ry)
        )

    pygame.draw.polygon(
        surface,
        color,
        transformed_points
    )


# Arrow 类
class Arrow:

    def __init__(self, row, col, direction):

        self.row = row
        self.col = col
        self.direction = direction

        self.removed = False

        # 错误抖动
        self.shaking = False
        self.shake_timer = 0
        self.shake_duration = 350

        # 飞出动画
        self.flying = False
        self.fly_timer = 0
        self.fly_duration = 400

        # 提示动画
        self.hint = False
        self.hint_timer = 0

    def start_shake(self):

        self.shaking = True
        self.shake_timer = 0

    def start_flying(self):

        self.flying = True
        self.fly_timer = 0

    def start_hint(self):

        self.hint = True
        self.hint_timer = 0

    def update(self, dt):

        if self.shaking:

            self.shake_timer += dt

            if self.shake_timer >= self.shake_duration:

                self.shaking = False
                self.shake_timer = 0

        if self.flying:

            self.fly_timer += dt

            if self.fly_timer >= self.fly_duration:

                self.removed = True

        if self.hint:

            self.hint_timer += dt

            if self.hint_timer >= 1800:

                self.hint = False
                self.hint_timer = 0

    def get_shake_offset(self):

        if not self.shaking:
            return 0

        progress = (
            self.shake_timer /
            self.shake_duration
        )

        strength = 7 * (1 - progress)

        return math.sin(
            progress * math.pi * 6
        ) * strength

    def get_fly_offset(self):

        if not self.flying:
            return 0, 0

        progress = min(
            self.fly_timer /
            self.fly_duration,
            1
        )

        progress = progress * progress

        distance = 420 * progress

        if self.direction == "U":
            return 0, -distance

        elif self.direction == "D":
            return 0, distance

        elif self.direction == "L":
            return -distance, 0

        elif self.direction == "R":
            return distance, 0

        return 0, 0

    def draw(self, surface):

        if self.removed:
            return

        cell_rect = pygame.Rect(
            BOARD_X + self.col * CELL_SIZE + 3,
            BOARD_Y + self.row * CELL_SIZE + 3,
            CELL_SIZE - 6,
            CELL_SIZE - 6
        )

        if self.flying:

            color = COLOR_SUCCESS

        elif self.shaking:

            color = COLOR_ERROR

        elif self.hint:

            # 提示时闪烁
            flash = (
                math.sin(
                    self.hint_timer / 100 * math.pi
                ) + 1
            ) / 2

            if flash > 0.5:
                color = COLOR_HINT
            else:
                color = COLOR_ARROW

        else:

            color = COLOR_ARROW

        shake_offset = self.get_shake_offset()
        fly_offset = self.get_fly_offset()

        draw_custom_arrow(
            surface,
            cell_rect,
            self.direction,
            color,
            shake_offset,
            fly_offset
        )


# Game 类
class Game:

    def __init__(self):

        self.level_index = 0

        self.state = "START"

        self.arrows = []

        self.mistakes_left = 0

        # 当前关卡时间
        self.level_time = 0

        # 历史最佳时间
        self.best_times = [None] * len(LEVELS)

        # 撤销记录
        self.history = []

        # 提示次数
        self.hints_used = 0

        # 本关错误次数
        self.mistakes_used = 0

        # 当前星级
        self.stars = 0

        self.load_level(0)

    # 加载关卡
    def load_level(self, index):

        self.level_index = index

        level = LEVELS[index]

        self.mistakes_left = level["mistakes"]

        self.level_time = 0

        self.history = []

        self.hints_used = 0

        self.mistakes_used = 0

        self.stars = 0

        self.arrows = []

        for position, direction in level["arrows"]:

            row, col = position[0]

            arrow = Arrow(
                row,
                col,
                direction
            )

            self.arrows.append(arrow)

    # 重新开始
    def restart(self):

        self.load_level(
            self.level_index
        )

        self.state = "PLAYING"

    # 当前没有被删除的箭头
    def active_arrows(self):

        return [
            arrow
            for arrow in self.arrows
            if not arrow.removed
        ]

    # 找某个位置的箭头
    def arrow_at(self, row, col):

        for arrow in self.active_arrows():

            if (
                arrow.row == row
                and arrow.col == col
            ):
                return arrow

        return None

    # 判断箭头能不能飞
    def can_fly(self, arrow):

        row = arrow.row
        col = arrow.col

        if arrow.direction == "R":

            for c in range(
                col + 1,
                COLS
            ):

                target = self.arrow_at(
                    row,
                    c
                )

                if (
                    target is not None
                    and not target.flying
                ):
                    return False

        elif arrow.direction == "L":

            for c in range(
                col - 1,
                -1,
                -1
            ):

                target = self.arrow_at(
                    row,
                    c
                )

                if (
                    target is not None
                    and not target.flying
                ):
                    return False

        elif arrow.direction == "U":

            for r in range(
                row - 1,
                -1,
                -1
            ):

                target = self.arrow_at(
                    r,
                    col
                )

                if (
                    target is not None
                    and not target.flying
                ):
                    return False

        elif arrow.direction == "D":

            for r in range(
                row + 1,
                ROWS
            ):

                target = self.arrow_at(
                    r,
                    col
                )

                if (
                    target is not None
                    and not target.flying
                ):
                    return False

        return True

    # 点击箭头
    def click_arrow(self, mouse_pos):

        if self.state != "PLAYING":
            return

        mx, my = mouse_pos

        if not (
            BOARD_X <= mx <=
            BOARD_X + BOARD_WIDTH
            and
            BOARD_Y <= my <=
            BOARD_Y + BOARD_HEIGHT
        ):
            return

        col = int(
            (mx - BOARD_X) /
            CELL_SIZE
        )

        row = int(
            (my - BOARD_Y) /
            CELL_SIZE
        )

        if (
            row < 0
            or row >= ROWS
            or col < 0
            or col >= COLS
        ):
            return

        arrow = self.arrow_at(
            row,
            col
        )

        if arrow is None:
            return

        if (
            arrow.flying
            or arrow.shaking
        ):
            return

        if self.can_fly(arrow):

            # 保存撤销记录
            self.history.append(
                (
                    arrow.row,
                    arrow.col,
                    arrow.direction
                )
            )

            arrow.start_flying()

        else:

            arrow.start_shake()

            self.mistakes_left -= 1

            self.mistakes_used += 1

            if self.mistakes_left <= 0:

                self.state = "FAILED"

    # 撤销
    def undo(self):

        if self.state != "PLAYING":
            return

        if len(self.history) == 0:
            return

        row, col, direction = (
            self.history.pop()
        )

        # 找到已经飞出的箭头
        for arrow in self.arrows:

            if (
                arrow.row == row
                and arrow.col == col
                and arrow.direction == direction
                and arrow.removed
            ):

                arrow.removed = False
                arrow.flying = False
                arrow.fly_timer = 0

                break

            elif (
                arrow.row == row
                and arrow.col == col
                and arrow.direction == direction
                and arrow.flying
            ):

                arrow.flying = False
                arrow.fly_timer = 0

                break

    # 提示
    def give_hint(self):

        if self.state != "PLAYING":
            return

        possible = []

        for arrow in self.active_arrows():

            if (
                not arrow.flying
                and not arrow.shaking
                and self.can_fly(arrow)
            ):

                possible.append(arrow)

        if len(possible) == 0:
            return

        # 选择第一个可以飞出的箭头
        arrow = possible[0]

        arrow.start_hint()

        self.hints_used += 1

    # 计算星级
    def calculate_stars(self):
        # 时间
        time_score = self.level_time
        # 错误
        mistakes = self.mistakes_used
        # 提示
        hints = self.hints_used
        if (
            time_score <= 15
            and mistakes == 0
            and hints == 0
        ):
            return 3

        elif (
            time_score <= 30
            and mistakes <= 1
            and hints <= 1
        ):

            return 2

        else:

            return 1

    # 更新
    def update(self, dt):

        for arrow in self.arrows:

            arrow.update(dt)

        if self.state != "PLAYING":
            return

        # 计时
        self.level_time += dt / 1000

        active = self.active_arrows()

        if len(active) == 0:

            self.stars = (
                self.calculate_stars()
            )

            # 保存最佳时间
            old_best = (
                self.best_times[
                    self.level_index
                ]
            )

            if (
                old_best is None
                or self.level_time < old_best
            ):

                self.best_times[
                    self.level_index
                ] = self.level_time

            if (
                self.level_index
                == len(LEVELS) - 1
            ):

                self.state = "ALL_COMPLETE"

            else:

                self.state = "LEVEL_COMPLETE"

    # 绘制棋盘
    def draw_board(self, surface):

        board_rect = pygame.Rect(
            BOARD_X - 6,
            BOARD_Y - 6,
            BOARD_WIDTH + 12,
            BOARD_HEIGHT + 12
        )

        pygame.draw.rect(
            surface,
            COLOR_GRID,
            board_rect,
            border_radius=10
        )

        for row in range(ROWS):

            for col in range(COLS):

                rect = pygame.Rect(
                    BOARD_X
                    + col * CELL_SIZE
                    + 3,

                    BOARD_Y
                    + row * CELL_SIZE
                    + 3,

                    CELL_SIZE - 6,
                    CELL_SIZE - 6
                )

                pygame.draw.rect(
                    surface,
                    COLOR_CELL,
                    rect,
                    border_radius=7
                )

        for arrow in self.arrows:

            arrow.draw(surface)

    # 绘制按钮
    def draw_button(
            self,
            surface,
            rect,
            text
    ):

        mouse_pos = pygame.mouse.get_pos()

        color = (
            COLOR_BUTTON_HOVER
            if rect.collidepoint(mouse_pos)
            else COLOR_BUTTON
        )

        pygame.draw.rect(
            surface,
            color,
            rect,
            border_radius=8
        )

        label = FONT_NORMAL.render(
            text,
            True,
            COLOR_WHITE
        )

        surface.blit(
            label,
            label.get_rect(
                center=rect.center
            )
        )

    # 星星
    def draw_stars(
            self,
            surface,
            stars,
            y
    ):

        text = ""

        for i in range(3):

            if i < stars:
                text += "★"
            else:
                text += "☆"

        label = FONT_BIG.render(
            text,
            True,
            COLOR_HINT
        )

        surface.blit(
            label,
            label.get_rect(
                center=(WIDTH // 2, y)
            )
        )

    # 开始界面
    def draw_start(self, surface):

        surface.fill(COLOR_BG)

        title = FONT_TITLE.render(
            "一箭又一箭",
            True,
            COLOR_TEXT
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 120)
            )
        )

        text = FONT_NORMAL.render(
            "点击箭头，让它飞出棋盘",
            True,
            COLOR_TEXT
        )

        surface.blit(
            text,
            text.get_rect(
                center=(WIDTH // 2, 185)
            )
        )

        text2 = FONT_SMALL.render(
            "箭头前方没有其他箭头才能飞出",
            True,
            COLOR_TEXT
        )

        surface.blit(
            text2,
            text2.get_rect(
                center=(WIDTH // 2, 220)
            )
        )

        text3 = FONT_SMALL.render(
            "共三关",
            True,
            COLOR_TEXT
        )

        surface.blit(
            text3,
            text3.get_rect(
                center=(WIDTH // 2, 250)
            )
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 300, 160, 48
            ),
            "开始游戏"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 365, 160, 48
            ),
            "选择关卡"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 430, 160, 48
            ),
            "退出游戏"
        )

    # 关卡选择
    def draw_level_select(
            self,
            surface
    ):

        surface.fill(COLOR_BG)

        title = FONT_TITLE.render(
            "选择关卡",
            True,
            COLOR_TEXT
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 100)
            )
        )

        for i in range(len(LEVELS)):

            rect = pygame.Rect(
                100 + i * 95,
                200,
                80,
                55
            )

            self.draw_button(
                surface,
                rect,
                f"第{i + 1}关"
            )

            best = self.best_times[i]

            if best is None:

                best_text = "未挑战"

            else:

                best_text = (
                    f"{best:.1f}s"
                )

            label = FONT_SMALL.render(
                best_text,
                True,
                COLOR_TEXT
            )

            surface.blit(
                label,
                label.get_rect(
                    center=(
                        rect.centerx,
                        rect.bottom + 22
                    )
                )
            )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 390, 160, 48
            ),
            "返回"
        )

    # 游戏界面
    def draw_game(self, surface):

        surface.fill(COLOR_BG)

        title = FONT_BIG.render(
            "一箭又一箭",
            True,
            COLOR_TEXT
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 30)
            )
        )

        level_text = FONT_NORMAL.render(
            f"第 {self.level_index + 1} 关",
            True,
            COLOR_TEXT
        )

        surface.blit(
            level_text,
            (15, 65)
        )

        remaining = len(
            self.active_arrows()
        )

        arrow_text = FONT_SMALL.render(
            f"剩余：{remaining}",
            True,
            COLOR_TEXT
        )

        surface.blit(
            arrow_text,
            (135, 68)
        )

        mistake_text = FONT_SMALL.render(
            f"错误：{self.mistakes_left}",
            True,
            COLOR_ERROR
        )

        surface.blit(
            mistake_text,
            (235, 68)
        )

        time_text = FONT_SMALL.render(
            f"时间：{self.level_time:.1f}s",
            True,
            COLOR_TEXT
        )

        surface.blit(
            time_text,
            (330, 68)
        )

        self.draw_board(surface)

        # 第一排按钮
        self.draw_button(
            surface,
            pygame.Rect(
                35, 475, 90, 40
            ),
            "提示"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                135, 475, 90, 40
            ),
            "撤销"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                235, 475, 95, 40
            ),
            "重新开始"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                340, 475, 95, 40
            ),
            "退出"
        )

        info = FONT_SMALL.render(
            f"已使用提示：{self.hints_used}",
            True,
            COLOR_TEXT
        )

        surface.blit(
            info,
            info.get_rect(
                center=(WIDTH // 2, 545)
            )
        )

    # 关卡完成
    def draw_level_complete(
            self,
            surface
    ):

        surface.fill(COLOR_BG)

        title = FONT_TITLE.render(
            "恭喜通关！",
            True,
            COLOR_SUCCESS
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 115)
            )
        )

        text = FONT_NORMAL.render(
            f"第 {self.level_index + 1} 关完成",
            True,
            COLOR_TEXT
        )

        surface.blit(
            text,
            text.get_rect(
                center=(WIDTH // 2, 175)
            )
        )

        time_text = FONT_NORMAL.render(
            f"本关用时：{self.level_time:.1f} 秒",
            True,
            COLOR_TEXT
        )

        surface.blit(
            time_text,
            time_text.get_rect(
                center=(WIDTH // 2, 215)
            )
        )

        self.draw_stars(
            surface,
            self.stars,
            265
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 315, 160, 45
            ),
            "下一关"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 375, 160, 45
            ),
            "重新挑战"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 435, 160, 45
            ),
            "退出游戏"
        )

    # 全部完成
    def draw_all_complete(
            self,
            surface
    ):

        surface.fill(COLOR_BG)

        title = FONT_TITLE.render(
            "全部通关！",
            True,
            COLOR_SUCCESS
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 110)
            )
        )

        text = FONT_BIG.render(
            "你完成了所有关卡",
            True,
            COLOR_TEXT
        )

        surface.blit(
            text,
            text.get_rect(
                center=(WIDTH // 2, 170)
            )
        )

        total_stars = sum(
            3 if t is not None else 0
            for t in self.best_times
        )

        star_text = FONT_NORMAL.render(
            "全部关卡完成！",
            True,
            COLOR_HINT
        )

        surface.blit(
            star_text,
            star_text.get_rect(
                center=(WIDTH // 2, 220)
            )
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 300, 160, 48
            ),
            "重新开始"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 365, 160, 48
            ),
            "选择关卡"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 430, 160, 48
            ),
            "退出游戏"
        )

    # 失败界面
    def draw_failed(
            self,
            surface
    ):

        surface.fill(COLOR_BG)

        title = FONT_TITLE.render(
            "挑战失败",
            True,
            COLOR_ERROR
        )

        surface.blit(
            title,
            title.get_rect(
                center=(WIDTH // 2, 150)
            )
        )

        text = FONT_NORMAL.render(
            "错误次数已经用完",
            True,
            COLOR_TEXT
        )

        surface.blit(
            text,
            text.get_rect(
                center=(WIDTH // 2, 215)
            )
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 310, 160, 48
            ),
            "重新挑战"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 375, 160, 48
            ),
            "选择关卡"
        )

        self.draw_button(
            surface,
            pygame.Rect(
                160, 440, 160, 48
            ),
            "退出游戏"
        )

    # 绘制
    def draw(self, surface):

        if self.state == "START":

            self.draw_start(surface)

        elif self.state == "LEVEL_SELECT":

            self.draw_level_select(surface)

        elif self.state == "PLAYING":

            self.draw_game(surface)

        elif self.state == "LEVEL_COMPLETE":

            self.draw_level_complete(
                surface
            )

        elif self.state == "ALL_COMPLETE":

            self.draw_all_complete(
                surface
            )

        elif self.state == "FAILED":

            self.draw_failed(surface)


# 创建游戏
game = Game()

running = True


# 主循环
while running:

    dt = clock.tick(60)

    for event in pygame.event.get():

        # 关闭窗口
        if event.type == pygame.QUIT:

            running = False

        # 鼠标点击
        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:
                continue

            mouse_pos = event.pos

            # 开始界面
            if game.state == "START":

                start_button = pygame.Rect(
                    160, 300, 160, 48
                )

                select_button = pygame.Rect(
                    160, 365, 160, 48
                )

                exit_button = pygame.Rect(
                    160, 430, 160, 48
                )

                if start_button.collidepoint(
                    mouse_pos
                ):

                    game.restart()

                elif select_button.collidepoint(
                    mouse_pos
                ):

                    game.state = "LEVEL_SELECT"

                elif exit_button.collidepoint(
                    mouse_pos
                ):

                    running = False

            # 关卡选择
            elif game.state == "LEVEL_SELECT":

                for i in range(
                    len(LEVELS)
                ):

                    rect = pygame.Rect(
                        100 + i * 95,
                        200,
                        80,
                        55
                    )

                    if rect.collidepoint(
                        mouse_pos
                    ):

                        game.load_level(i)

                        game.state = "PLAYING"

                back_button = pygame.Rect(
                    160, 390, 160, 48
                )

                if back_button.collidepoint(
                    mouse_pos
                ):

                    game.state = "START"

            # 游戏中
            elif game.state == "PLAYING":

                hint_button = pygame.Rect(
                    35, 475, 90, 40
                )

                undo_button = pygame.Rect(
                    135, 475, 90, 40
                )

                restart_button = pygame.Rect(
                    235, 475, 95, 40
                )

                exit_button = pygame.Rect(
                    340, 475, 95, 40
                )

                if hint_button.collidepoint(
                    mouse_pos
                ):

                    game.give_hint()

                elif undo_button.collidepoint(
                    mouse_pos
                ):

                    game.undo()

                elif restart_button.collidepoint(
                    mouse_pos
                ):

                    game.restart()

                elif exit_button.collidepoint(
                    mouse_pos
                ):

                    running = False

                else:

                    game.click_arrow(
                        mouse_pos
                    )

            # 普通关卡完成
            elif game.state == "LEVEL_COMPLETE":

                next_button = pygame.Rect(
                    160, 315, 160, 45
                )

                restart_button = pygame.Rect(
                    160, 375, 160, 45
                )

                exit_button = pygame.Rect(
                    160, 435, 160, 45
                )

                if next_button.collidepoint(
                    mouse_pos
                ):

                    game.load_level(
                        game.level_index + 1
                    )

                    game.state = "PLAYING"

                elif restart_button.collidepoint(
                    mouse_pos
                ):

                    game.restart()

                elif exit_button.collidepoint(
                    mouse_pos
                ):

                    running = False

            # 全部完成
            elif game.state == "ALL_COMPLETE":

                restart_button = pygame.Rect(
                    160, 300, 160, 48
                )

                select_button = pygame.Rect(
                    160, 365, 160, 48
                )

                exit_button = pygame.Rect(
                    160, 430, 160, 48
                )

                if restart_button.collidepoint(
                    mouse_pos
                ):

                    game.load_level(0)

                    game.state = "PLAYING"

                elif select_button.collidepoint(
                    mouse_pos
                ):

                    game.state = "LEVEL_SELECT"

                elif exit_button.collidepoint(
                    mouse_pos
                ):

                    running = False

            # 失败
            elif game.state == "FAILED":

                restart_button = pygame.Rect(
                    160, 310, 160, 48
                )

                select_button = pygame.Rect(
                    160, 375, 160, 48
                )

                exit_button = pygame.Rect(
                    160, 440, 160, 48
                )

                if restart_button.collidepoint(
                    mouse_pos
                ):

                    game.restart()

                elif select_button.collidepoint(
                    mouse_pos
                ):

                    game.state = "LEVEL_SELECT"

                elif exit_button.collidepoint(
                    mouse_pos
                ):

                    running = False

    # 更新游戏
    game.update(dt)

    # 绘制
    game.draw(screen)

    pygame.display.flip()


pygame.quit()
sys.exit()