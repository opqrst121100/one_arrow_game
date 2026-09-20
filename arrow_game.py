import pygame
import sys
import math

pygame.init()

# 窗口设置（调小窗口尺寸）
WIDTH = 480
HEIGHT = 560
screen = pygame.display.set_mode((WIDTH, HEIGHT))  # 默认带标题栏，可随意拖动窗口
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
    FONT_BIG = pygame.font.Font(font_path, 30)
    FONT_TITLE = pygame.font.Font(font_path, 38)
else:
    FONT_SMALL = pygame.font.SysFont("arial", 15)
    FONT_NORMAL = pygame.font.SysFont("arial", 18)
    FONT_BIG = pygame.font.SysFont("arial", 30)
    FONT_TITLE = pygame.font.SysFont("arial", 38)

# 颜色
COLOR_BG = (245, 246, 250)           # 柔和暖白，淡灰背景
COLOR_CELL = (255, 255, 255)         # 纯白棋盘方格
COLOR_ARROW = (52, 120, 246)          # 经典蓝色箭头
COLOR_ERROR = (235, 87, 87)          # 错误提示红
COLOR_SUCCESS = (46, 184, 114)       # 飞出成功绿
COLOR_WHITE = (255, 255, 255)        # 按钮纯白文字
COLOR_TEXT = (45, 55, 72)            # 深灰深蓝主文字
COLOR_BUTTON = (90, 105, 130)        # 按钮默认颜色
COLOR_BUTTON_HOVER = (60, 75, 100)  # 按钮悬停颜色
COLOR_GRID = (218, 224, 233)         # 棋盘网格边框底色

# 棋盘 5×5
ROWS = 5
COLS = 5
CELL_SIZE = 60                       # 格子大小调整为 60
BOARD_WIDTH = COLS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE
BOARD_X = (WIDTH - BOARD_WIDTH) // 2
BOARD_Y = 130

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


# 箭头绘制
def draw_custom_arrow(surface, cell_rect, direction, color, shake_offset=0, flying_offset=(0, 0)):
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
        transformed_points.append((cx + rx, cy + ry))
    pygame.draw.polygon(surface, color, transformed_points)


# Arrow 类
class Arrow:
    def __init__(self, row, col, direction):
        self.row = row
        self.col = col
        self.direction = direction
        self.removed = False
        self.shaking = False
        self.shake_timer = 0
        self.shake_duration = 350
        self.flying = False
        self.fly_timer = 0
        self.fly_duration = 400

    def start_shake(self):
        self.shaking = True
        self.shake_timer = 0

    def start_flying(self):
        self.flying = True
        self.fly_timer = 0

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

    def get_shake_offset(self):
        if not self.shaking:
            return 0
        progress = self.shake_timer / self.shake_duration
        strength = 7 * (1 - progress)
        return math.sin(progress * math.pi * 6) * strength

    def get_fly_offset(self):
        if not self.flying:
            return 0, 0
        progress = min(self.fly_timer / self.fly_duration, 1)
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
        else:
            color = COLOR_ARROW
        shake_offset = self.get_shake_offset()
        fly_offset = self.get_fly_offset()
        draw_custom_arrow(surface, cell_rect, self.direction, color, shake_offset, fly_offset)


# Game 类
class Game:
    def __init__(self):
        self.level_index = 0
        self.state = "START"
        self.arrows = []
        self.mistakes_left = 0
        self.load_level(0)

    def load_level(self, index):
        self.level_index = index
        level = LEVELS[index]
        self.mistakes_left = level["mistakes"]
        self.arrows = []
        for position, direction in level["arrows"]:
            row, col = position[0]
            arrow = Arrow(row, col, direction)
            self.arrows.append(arrow)

    def restart(self):
        self.load_level(self.level_index)
        self.state = "PLAYING"

    def active_arrows(self):
        return [arrow for arrow in self.arrows if not arrow.removed]

    def arrow_at(self, row, col):
        for arrow in self.active_arrows():
            if arrow.row == row and arrow.col == col:
                return arrow
        return None

    def can_fly(self, arrow):
        row = arrow.row
        col = arrow.col
        if arrow.direction == "R":
            for c in range(col + 1, COLS):
                target = self.arrow_at(row, c)
                if target is not None and not target.flying:
                    return False
        elif arrow.direction == "L":
            for c in range(col - 1, -1, -1):
                target = self.arrow_at(row, c)
                if target is not None and not target.flying:
                    return False
        elif arrow.direction == "U":
            for r in range(row - 1, -1, -1):
                target = self.arrow_at(r, col)
                if target is not None and not target.flying:
                    return False
        elif arrow.direction == "D":
            for r in range(row + 1, ROWS):
                target = self.arrow_at(r, col)
                if target is not None and not target.flying:
                    return False
        return True

    def click_arrow(self, mouse_pos):
        if self.state != "PLAYING":
            return
        mx, my = mouse_pos
        if not (BOARD_X <= mx <= BOARD_X + BOARD_WIDTH and BOARD_Y <= my <= BOARD_Y + BOARD_HEIGHT):
            return
        col = int((mx - BOARD_X) / CELL_SIZE)
        row = int((my - BOARD_Y) / CELL_SIZE)
        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            return
        arrow = self.arrow_at(row, col)
        if arrow is None:
            return
        if arrow.flying or arrow.shaking:
            return

        if self.can_fly(arrow):
            arrow.start_flying()
        else:
            arrow.start_shake()
            self.mistakes_left -= 1
            if self.mistakes_left <= 0:
                self.state = "FAILED"

    def update(self, dt):
        for arrow in self.arrows:
            arrow.update(dt)
        if self.state != "PLAYING":
            return
        active = self.active_arrows()
        if len(active) == 0:
            if self.level_index == len(LEVELS) - 1:
                self.state = "ALL_COMPLETE"
            else:
                self.state = "LEVEL_COMPLETE"

    def draw_board(self, surface):
        board_rect = pygame.Rect(BOARD_X - 6, BOARD_Y - 6, BOARD_WIDTH + 12, BOARD_HEIGHT + 12)
        pygame.draw.rect(surface, COLOR_GRID, board_rect, border_radius=10)
        for row in range(ROWS):
            for col in range(COLS):
                rect = pygame.Rect(
                    BOARD_X + col * CELL_SIZE + 3,
                    BOARD_Y + row * CELL_SIZE + 3,
                    CELL_SIZE - 6,
                    CELL_SIZE - 6
                )
                pygame.draw.rect(surface, COLOR_CELL, rect, border_radius=7)
        for arrow in self.arrows:
            arrow.draw(surface)

    def draw_game(self, surface):
        surface.fill(COLOR_BG)
        title = FONT_BIG.render("一箭又一箭", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 35)))
        level_text = FONT_NORMAL.render(f"第 {self.level_index + 1} 关", True, COLOR_TEXT)
        surface.blit(level_text, (20, 80))
        remaining = len(self.active_arrows())
        arrow_text = FONT_NORMAL.render(f"剩余箭头数：{remaining}", True, COLOR_TEXT)
        surface.blit(arrow_text, (180, 80))
        mistake_text = FONT_NORMAL.render(f"剩余错误次数：{self.mistakes_left}", True, COLOR_TEXT)
        surface.blit(mistake_text, (340, 80))
        self.draw_board(surface)
        self.draw_button(surface, pygame.Rect(140, 470, 95, 42), "重新开始")
        self.draw_button(surface, pygame.Rect(245, 470, 95, 42), "退出游戏")

    def draw_button(self, surface, rect, text):
        mouse_pos = pygame.mouse.get_pos()
        color = COLOR_BUTTON_HOVER if rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(surface, color, rect, border_radius=8)
        label = FONT_NORMAL.render(text, True, COLOR_WHITE)
        surface.blit(label, label.get_rect(center=rect.center))

    def draw_start(self, surface):
        surface.fill(COLOR_BG)
        title = FONT_TITLE.render("一箭又一箭", True, COLOR_TEXT)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 140)))
        text = FONT_NORMAL.render("点击箭头，让它飞出棋盘", True, COLOR_TEXT)
        surface.blit(text, text.get_rect(center=(WIDTH // 2, 210)))
        text2 = FONT_SMALL.render("箭头前方没有其他箭头才能飞出", True, COLOR_TEXT)
        surface.blit(text2, text2.get_rect(center=(WIDTH // 2, 245)))
        text3 = FONT_SMALL.render("共 3 关", True, COLOR_TEXT)
        surface.blit(text3, text3.get_rect(center=(WIDTH // 2, 275)))
        self.draw_button(surface, pygame.Rect(160, 340, 160, 48), "开始游戏")
        self.draw_button(surface, pygame.Rect(160, 405, 160, 48), "退出游戏")

    def draw_level_complete(self, surface):
        surface.fill(COLOR_BG)
        title = FONT_TITLE.render("恭喜通关！", True, COLOR_SUCCESS)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 160)))
        text = FONT_NORMAL.render(f"第 {self.level_index + 1} 关完成", True, COLOR_TEXT)
        surface.blit(text, text.get_rect(center=(WIDTH // 2, 230)))
        self.draw_button(surface, pygame.Rect(160, 310, 160, 45), "下一关")
        self.draw_button(surface, pygame.Rect(160, 370, 160, 45), "重新挑战")
        self.draw_button(surface, pygame.Rect(160, 430, 160, 45), "退出游戏")

    def draw_all_complete(self, surface):
        surface.fill(COLOR_BG)
        title = FONT_TITLE.render("全部通关！", True, COLOR_SUCCESS)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 160)))
        text = FONT_BIG.render("你完成了所有关卡", True, COLOR_TEXT)
        surface.blit(text, text.get_rect(center=(WIDTH // 2, 230)))
        self.draw_button(surface, pygame.Rect(160, 330, 160, 48), "重新开始")
        self.draw_button(surface, pygame.Rect(160, 395, 160, 48), "退出游戏")

    def draw_failed(self, surface):
        surface.fill(COLOR_BG)
        title = FONT_TITLE.render("挑战失败", True, COLOR_ERROR)
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 160)))
        text = FONT_NORMAL.render("剩余次数已经用完", True, COLOR_TEXT)
        surface.blit(text, text.get_rect(center=(WIDTH // 2, 230)))
        self.draw_button(surface, pygame.Rect(160, 330, 160, 48), "重新挑战")
        self.draw_button(surface, pygame.Rect(160, 395, 160, 48), "退出游戏")

    def draw(self, surface):
        if self.state == "START":
            self.draw_start(surface)
        elif self.state == "PLAYING":
            self.draw_game(surface)
        elif self.state == "LEVEL_COMPLETE":
            self.draw_level_complete(surface)
        elif self.state == "ALL_COMPLETE":
            self.draw_all_complete(surface)
        elif self.state == "FAILED":
            self.draw_failed(surface)


game = Game()
running = True
while running:
    dt = clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button != 1:
                continue
            mouse_pos = event.pos
            if game.state == "START":
                start_btn = pygame.Rect(160, 340, 160, 48)
                exit_btn = pygame.Rect(160, 405, 160, 48)
                if start_btn.collidepoint(mouse_pos):
                    game.restart()
                elif exit_btn.collidepoint(mouse_pos):
                    running = False

            elif game.state == "PLAYING":
                restart_button = pygame.Rect(140, 470, 95, 42)
                exit_button = pygame.Rect(245, 470, 95, 42)
                if restart_button.collidepoint(mouse_pos):
                    game.restart()
                elif exit_button.collidepoint(mouse_pos):
                    running = False
                else:
                    game.click_arrow(mouse_pos)

            elif game.state == "LEVEL_COMPLETE":
                next_button = pygame.Rect(160, 310, 160, 45)
                restart_button = pygame.Rect(160, 370, 160, 45)
                exit_button = pygame.Rect(160, 430, 160, 45)
                if next_button.collidepoint(mouse_pos):
                    game.load_level(game.level_index + 1)
                    game.state = "PLAYING"
                elif restart_button.collidepoint(mouse_pos):
                    game.restart()
                elif exit_button.collidepoint(mouse_pos):
                    running = False

            elif game.state == "ALL_COMPLETE":
                restart_button = pygame.Rect(160, 330, 160, 48)
                exit_button = pygame.Rect(160, 395, 160, 48)
                if restart_button.collidepoint(mouse_pos):
                    game.load_level(0)
                    game.state = "PLAYING"
                elif exit_button.collidepoint(mouse_pos):
                    running = False

            elif game.state == "FAILED":
                restart_button = pygame.Rect(160, 330, 160, 48)
                exit_button = pygame.Rect(160, 395, 160, 48)
                if restart_button.collidepoint(mouse_pos):
                    game.restart()
                elif exit_button.collidepoint(mouse_pos):
                    running = False

    game.update(dt)
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
