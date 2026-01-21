#!/usr/bin/env python3
"""
疯狂的鸽子 (Pigeon Pop) - 百分百复刻版
一款以鸽子为主角的休闲闯关游戏

游戏规则:
1. 点击屏幕控制鸽子啄食黄色玉米粒
2. 避开黑色的坏玉米粒，碰到就失败
3. 吃掉所有黄色玉米粒即可过关
4. 可以吃虫子来增加虫子收集数量
5. 根据完成时间获得星星评级
"""

import pygame
import random
import math
import sys
import os

# 初始化 pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    # 没有音频设备时跳过音频初始化
    pass

# 屏幕设置
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 215, 0)
DARK_YELLOW = (204, 172, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GREEN = (34, 139, 34)
LIGHT_GREEN = (144, 238, 144)
GRAY = (128, 128, 128)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
LIGHT_BLUE = (135, 206, 235)
CORN_GREEN = (107, 142, 35)
BAD_CORN_COLOR = (40, 40, 40)

# 游戏状态
STATE_MENU = 0
STATE_PLAYING = 1
STATE_WIN = 2
STATE_LOSE = 3
STATE_LEVEL_SELECT = 4


class Pigeon:
    """鸽子类 - 玩家控制的角色"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 80
        self.target_x = x
        self.target_y = y
        self.speed = 15
        self.pecking = False
        self.peck_timer = 0
        self.peck_duration = 15
        self.dance_timer = 0
        self.dance_phase = 0
        self.body_color = (180, 180, 180)  # 灰色鸽子
        self.head_color = (150, 200, 150)  # 绿色脖子

    def draw(self, screen):
        """绘制鸽子"""
        # 跳舞动画偏移
        dance_offset_y = math.sin(self.dance_timer * 0.1) * 3
        dance_offset_x = math.sin(self.dance_timer * 0.15) * 2

        x = self.x + dance_offset_x
        y = self.y + dance_offset_y

        # 身体（椭圆形）
        body_rect = pygame.Rect(x - 25, y - 10, 50, 35)
        pygame.draw.ellipse(screen, self.body_color, body_rect)
        pygame.draw.ellipse(screen, DARK_GRAY, body_rect, 2)

        # 翅膀
        wing_offset = math.sin(self.dance_timer * 0.2) * 5
        # 左翅膀
        wing_points = [
            (x - 20, y),
            (x - 35, y - 10 + wing_offset),
            (x - 30, y + 10),
        ]
        pygame.draw.polygon(screen, (160, 160, 160), wing_points)
        pygame.draw.polygon(screen, DARK_GRAY, wing_points, 2)

        # 右翅膀
        wing_points = [
            (x + 20, y),
            (x + 35, y - 10 - wing_offset),
            (x + 30, y + 10),
        ]
        pygame.draw.polygon(screen, (160, 160, 160), wing_points)
        pygame.draw.polygon(screen, DARK_GRAY, wing_points, 2)

        # 尾巴
        tail_points = [
            (x - 25, y + 5),
            (x - 45, y + 15),
            (x - 40, y + 5),
            (x - 50, y + 10),
            (x - 35, y),
        ]
        pygame.draw.polygon(screen, (140, 140, 140), tail_points)
        pygame.draw.polygon(screen, DARK_GRAY, tail_points, 2)

        # 脖子（彩虹色）
        neck_rect = pygame.Rect(x + 15, y - 20, 18, 25)
        pygame.draw.ellipse(screen, self.head_color, neck_rect)

        # 头
        head_x = x + 25
        head_y = y - 30

        if self.pecking:
            # 啄食动作 - 头向前伸
            head_x += 15
            head_y += 10

        pygame.draw.circle(screen, self.body_color, (int(head_x), int(head_y)), 15)
        pygame.draw.circle(screen, DARK_GRAY, (int(head_x), int(head_y)), 15, 2)

        # 眼睛
        eye_x = head_x + 5
        eye_y = head_y - 3
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 5)
        pygame.draw.circle(screen, BLACK, (int(eye_x), int(eye_y)), 3)
        pygame.draw.circle(screen, WHITE, (int(eye_x - 1), int(eye_y - 1)), 1)

        # 嘴巴（喙）
        beak_x = head_x + 12
        beak_y = head_y + 2
        if self.pecking:
            beak_x += 5
        beak_points = [
            (beak_x, beak_y - 3),
            (beak_x + 12, beak_y),
            (beak_x, beak_y + 3),
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        pygame.draw.polygon(screen, DARK_BROWN, beak_points, 1)

        # 脚
        foot_y = y + 25
        # 左脚
        pygame.draw.line(screen, ORANGE, (x - 10, y + 15), (x - 10, foot_y), 3)
        pygame.draw.line(screen, ORANGE, (x - 10, foot_y), (x - 18, foot_y + 5), 2)
        pygame.draw.line(screen, ORANGE, (x - 10, foot_y), (x - 5, foot_y + 5), 2)
        # 右脚
        pygame.draw.line(screen, ORANGE, (x + 10, y + 15), (x + 10, foot_y), 3)
        pygame.draw.line(screen, ORANGE, (x + 10, foot_y), (x + 2, foot_y + 5), 2)
        pygame.draw.line(screen, ORANGE, (x + 10, foot_y), (x + 15, foot_y + 5), 2)

    def update(self):
        """更新鸽子状态"""
        # 移动到目标位置
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 5:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        # 啄食动画
        if self.pecking:
            self.peck_timer += 1
            if self.peck_timer >= self.peck_duration:
                self.pecking = False
                self.peck_timer = 0

        # 跳舞动画
        self.dance_timer += 1

    def move_to(self, x, y):
        """设置目标位置"""
        self.target_x = x - 30  # 调整使嘴巴对准目标
        self.target_y = y - 20

    def peck(self):
        """执行啄食动作"""
        self.pecking = True
        self.peck_timer = 0

    def get_beak_pos(self):
        """获取嘴巴位置（用于碰撞检测）"""
        head_x = self.x + 25
        head_y = self.y - 30
        if self.pecking:
            head_x += 15
            head_y += 10
        return (head_x + 15, head_y)


class Corn:
    """玉米棒类"""

    def __init__(self, x, y, rows=8, cols=4):
        self.x = x
        self.y = y
        self.rows = rows
        self.cols = cols
        self.kernels = []  # 玉米粒列表
        self.kernel_size = 18
        self.generate_kernels()

    def generate_kernels(self):
        """生成玉米粒"""
        self.kernels = []
        for row in range(self.rows):
            for col in range(self.cols):
                # 交错排列
                offset_x = (row % 2) * (self.kernel_size // 2)
                kx = self.x + col * self.kernel_size + offset_x
                ky = self.y + row * (self.kernel_size - 2)

                kernel = {
                    'x': kx,
                    'y': ky,
                    'eaten': False,
                    'bad': False,
                    'has_worm': False,
                    'worm_timer': 0,
                }
                self.kernels.append(kernel)

    def set_bad_kernels(self, count):
        """设置坏玉米粒数量"""
        good_kernels = [k for k in self.kernels if not k['bad']]
        random.shuffle(good_kernels)
        for i in range(min(count, len(good_kernels))):
            good_kernels[i]['bad'] = True

    def set_worm_kernels(self, count):
        """在坏玉米上设置虫子"""
        bad_kernels = [k for k in self.kernels if k['bad'] and not k['eaten']]
        random.shuffle(bad_kernels)
        for i in range(min(count, len(bad_kernels))):
            bad_kernels[i]['has_worm'] = True

    def draw(self, screen):
        """绘制玉米棒"""
        # 绘制玉米芯
        core_rect = pygame.Rect(self.x - 5, self.y - 10,
                                self.cols * self.kernel_size + 10,
                                self.rows * (self.kernel_size - 2) + 20)
        pygame.draw.ellipse(screen, CORN_GREEN, core_rect)

        # 绘制玉米叶子
        leaf_points = [
            (self.x - 10, self.y + self.rows * (self.kernel_size - 2)),
            (self.x - 30, self.y + self.rows * (self.kernel_size - 2) + 40),
            (self.x + 10, self.y + self.rows * (self.kernel_size - 2) + 20),
        ]
        pygame.draw.polygon(screen, GREEN, leaf_points)

        leaf_points2 = [
            (self.x + self.cols * self.kernel_size + 10, self.y + self.rows * (self.kernel_size - 2)),
            (self.x + self.cols * self.kernel_size + 30, self.y + self.rows * (self.kernel_size - 2) + 40),
            (self.x + self.cols * self.kernel_size - 10, self.y + self.rows * (self.kernel_size - 2) + 20),
        ]
        pygame.draw.polygon(screen, GREEN, leaf_points2)

        # 绘制玉米粒
        for kernel in self.kernels:
            if not kernel['eaten']:
                self.draw_kernel(screen, kernel)

    def draw_kernel(self, screen, kernel):
        """绘制单个玉米粒"""
        x, y = kernel['x'], kernel['y']
        size = self.kernel_size

        if kernel['bad']:
            # 坏玉米粒 - 黑色
            color = BAD_CORN_COLOR
            highlight = (60, 60, 60)
        else:
            # 好玉米粒 - 黄色
            color = YELLOW
            highlight = (255, 255, 150)

        # 绘制玉米粒（圆角矩形效果）
        rect = pygame.Rect(x, y, size - 2, size - 2)
        pygame.draw.ellipse(screen, color, rect)

        # 高光
        highlight_rect = pygame.Rect(x + 2, y + 2, size // 3, size // 3)
        pygame.draw.ellipse(screen, highlight, highlight_rect)

        # 如果有虫子
        if kernel['has_worm'] and kernel['bad']:
            self.draw_worm(screen, x + size // 2, y + size // 2)

    def draw_worm(self, screen, x, y):
        """绘制虫子"""
        # 简单的虫子形状
        worm_color = (150, 200, 100)
        pygame.draw.ellipse(screen, worm_color, (x - 8, y - 3, 16, 6))
        pygame.draw.circle(screen, (100, 150, 50), (x + 6, y), 3)
        # 眼睛
        pygame.draw.circle(screen, BLACK, (x + 7, y - 1), 1)

    def check_peck(self, peck_x, peck_y):
        """检查啄食位置，返回被啄的玉米粒"""
        for kernel in self.kernels:
            if kernel['eaten']:
                continue
            kx, ky = kernel['x'], kernel['y']
            # 检查点击是否在玉米粒范围内
            if (kx <= peck_x <= kx + self.kernel_size and
                ky <= peck_y <= ky + self.kernel_size):
                return kernel
        return None

    def get_remaining_good_kernels(self):
        """获取剩余的好玉米粒数量"""
        return sum(1 for k in self.kernels if not k['eaten'] and not k['bad'])

    def get_total_good_kernels(self):
        """获取总共的好玉米粒数量"""
        return sum(1 for k in self.kernels if not k['bad'])


class Bug:
    """虫子/害虫类（飞行的）"""

    def __init__(self, x, y, bug_type='fly'):
        self.x = x
        self.y = y
        self.bug_type = bug_type  # 'fly', 'bee', 'mosquito'
        self.speed = 2
        self.direction = random.uniform(0, 2 * math.pi)
        self.alive = True
        self.wing_timer = 0

    def update(self):
        """更新虫子位置"""
        self.wing_timer += 1
        # 随机改变方向
        if random.random() < 0.02:
            self.direction += random.uniform(-0.5, 0.5)

        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed

        # 边界反弹
        if self.x < 50 or self.x > SCREEN_WIDTH - 50:
            self.direction = math.pi - self.direction
        if self.y < 100 or self.y > SCREEN_HEIGHT - 200:
            self.direction = -self.direction

    def draw(self, screen):
        """绘制虫子"""
        if not self.alive:
            return

        wing_offset = math.sin(self.wing_timer * 0.5) * 5

        if self.bug_type == 'fly':
            # 苍蝇
            pygame.draw.ellipse(screen, (50, 50, 50), (self.x - 6, self.y - 4, 12, 8))
            pygame.draw.circle(screen, (40, 40, 40), (int(self.x + 5), int(self.y)), 4)
            # 翅膀
            pygame.draw.ellipse(screen, (200, 200, 200, 128),
                              (self.x - 10, self.y - 8 + wing_offset, 8, 12))
            pygame.draw.ellipse(screen, (200, 200, 200, 128),
                              (self.x + 2, self.y - 8 - wing_offset, 8, 12))
        elif self.bug_type == 'bee':
            # 蜜蜂
            pygame.draw.ellipse(screen, YELLOW, (self.x - 8, self.y - 5, 16, 10))
            # 条纹
            pygame.draw.line(screen, BLACK, (self.x - 4, self.y - 5), (self.x - 4, self.y + 5), 2)
            pygame.draw.line(screen, BLACK, (self.x + 2, self.y - 5), (self.x + 2, self.y + 5), 2)
            # 翅膀
            pygame.draw.ellipse(screen, (255, 255, 255, 128),
                              (self.x - 6, self.y - 12 + wing_offset, 6, 10))
            pygame.draw.ellipse(screen, (255, 255, 255, 128),
                              (self.x, self.y - 12 - wing_offset, 6, 10))
        elif self.bug_type == 'mosquito':
            # 蚊子
            pygame.draw.ellipse(screen, (80, 60, 60), (self.x - 4, self.y - 2, 8, 4))
            pygame.draw.line(screen, (80, 60, 60), (self.x + 4, self.y), (self.x + 10, self.y), 1)
            # 翅膀
            pygame.draw.ellipse(screen, (180, 180, 180, 128),
                              (self.x - 6, self.y - 6 + wing_offset, 5, 8))
            pygame.draw.ellipse(screen, (180, 180, 180, 128),
                              (self.x + 1, self.y - 6 - wing_offset, 5, 8))

    def check_collision(self, x, y, radius=20):
        """检查与指定位置的碰撞"""
        dist = math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
        return dist < radius


class Game:
    """游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("疯狂的鸽子 - Pigeon Pop")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # 尝试加载中文字体
        try:
            self.chinese_font = pygame.font.Font("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 24)
            self.chinese_font_big = pygame.font.Font("/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 48)
        except:
            try:
                self.chinese_font = pygame.font.Font("/usr/share/fonts/truetype/arphic/uming.ttc", 24)
                self.chinese_font_big = pygame.font.Font("/usr/share/fonts/truetype/arphic/uming.ttc", 48)
            except:
                self.chinese_font = self.font
                self.chinese_font_big = self.big_font

        self.state = STATE_MENU
        self.current_level = 1
        self.total_worms = 0  # 总虫子收集数
        self.level_worms = 0  # 当前关卡虫子
        self.level_time = 0
        self.level_start_time = 0
        self.stars = 0

        # 关卡配置
        self.levels = self.create_levels()

        self.reset_level()

    def create_levels(self):
        """创建关卡配置"""
        levels = []
        for i in range(1, 201):  # 200个关卡
            level = {
                'bad_kernels': min(2 + i // 5, 15),  # 坏玉米逐渐增加
                'worm_kernels': min(1 + i // 10, 5),  # 虫子数量
                'bugs': [],  # 飞行虫子
                'time_3star': 10 + i * 2,  # 3星时间
                'time_2star': 20 + i * 3,  # 2星时间
                'corn_rows': min(6 + i // 20, 12),  # 玉米行数
                'corn_cols': min(4 + i // 30, 6),  # 玉米列数
            }

            # 添加特殊关卡元素
            if i >= 8:
                level['bugs'].append('bee')
            if i >= 15:
                level['bugs'].append('fly')
            if i >= 25:
                level['bugs'].append('mosquito')

            levels.append(level)
        return levels

    def reset_level(self):
        """重置当前关卡"""
        level_config = self.levels[self.current_level - 1]

        # 创建鸽子
        self.pigeon = Pigeon(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200)

        # 创建玉米
        corn_x = (SCREEN_WIDTH - level_config['corn_cols'] * 18) // 2
        corn_y = 150
        self.corn = Corn(corn_x, corn_y, level_config['corn_rows'], level_config['corn_cols'])
        self.corn.set_bad_kernels(level_config['bad_kernels'])
        self.corn.set_worm_kernels(level_config['worm_kernels'])

        # 创建飞行虫子
        self.bugs = []
        for bug_type in level_config['bugs']:
            bug = Bug(random.randint(100, SCREEN_WIDTH - 100),
                     random.randint(200, 400), bug_type)
            self.bugs.append(bug)

        self.level_worms = 0
        self.level_start_time = pygame.time.get_ticks()
        self.level_time = 0
        self.stars = 0

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_MENU
                    else:
                        return False
                elif event.key == pygame.K_r:
                    if self.state in [STATE_WIN, STATE_LOSE]:
                        self.reset_level()
                        self.state = STATE_PLAYING
                elif event.key == pygame.K_SPACE:
                    if self.state == STATE_WIN:
                        self.current_level = min(self.current_level + 1, 200)
                        self.reset_level()
                        self.state = STATE_PLAYING
        return True

    def handle_click(self, pos):
        """处理点击事件"""
        x, y = pos

        if self.state == STATE_MENU:
            # 开始游戏按钮区域
            if 140 < x < 340 and 350 < y < 420:
                self.reset_level()
                self.state = STATE_PLAYING
            # 选关按钮区域
            elif 140 < x < 340 and 450 < y < 520:
                self.state = STATE_LEVEL_SELECT

        elif self.state == STATE_LEVEL_SELECT:
            # 关卡选择
            # 返回按钮
            if 20 < x < 100 and 20 < y < 60:
                self.state = STATE_MENU
                return

            # 关卡按钮
            for i in range(20):  # 显示20个关卡
                row = i // 5
                col = i % 5
                btn_x = 40 + col * 85
                btn_y = 100 + row * 85
                if btn_x < x < btn_x + 70 and btn_y < y < btn_y + 70:
                    self.current_level = i + 1
                    self.reset_level()
                    self.state = STATE_PLAYING
                    return

        elif self.state == STATE_PLAYING:
            # 移动鸽子并啄食
            self.pigeon.move_to(x, y)
            self.pigeon.peck()

            # 延迟检查啄食（等鸽子移动到位）
            # 这里简化处理，直接检查点击位置
            beak_x, beak_y = x, y

            # 检查是否啄到玉米
            kernel = self.corn.check_peck(beak_x, beak_y)
            if kernel:
                if kernel['bad']:
                    if kernel['has_worm']:
                        # 吃到虫子
                        kernel['has_worm'] = False
                        self.level_worms += 1
                        self.total_worms += 1
                    else:
                        # 啄到坏玉米，游戏失败
                        self.state = STATE_LOSE
                else:
                    # 吃掉好玉米
                    kernel['eaten'] = True

                    # 检查是否吃完所有好玉米
                    if self.corn.get_remaining_good_kernels() == 0:
                        self.calculate_stars()
                        self.state = STATE_WIN

            # 检查是否啄到飞行虫子
            for bug in self.bugs:
                if bug.alive and bug.check_collision(beak_x, beak_y):
                    bug.alive = False
                    if bug.bug_type == 'bee':
                        # 蜜蜂会增加虫子
                        self.level_worms += 5
                        self.total_worms += 5
                    else:
                        self.level_worms += 1
                        self.total_worms += 1

        elif self.state == STATE_WIN:
            # 下一关按钮
            if 140 < x < 340 and 500 < y < 570:
                self.current_level = min(self.current_level + 1, 200)
                self.reset_level()
                self.state = STATE_PLAYING
            # 重玩按钮
            elif 140 < x < 340 and 590 < y < 660:
                self.reset_level()
                self.state = STATE_PLAYING

        elif self.state == STATE_LOSE:
            # 重试按钮
            if 140 < x < 340 and 450 < y < 520:
                self.reset_level()
                self.state = STATE_PLAYING
            # 返回菜单按钮
            elif 140 < x < 340 and 540 < y < 610:
                self.state = STATE_MENU

    def calculate_stars(self):
        """计算星星评级"""
        level_config = self.levels[self.current_level - 1]
        elapsed = (pygame.time.get_ticks() - self.level_start_time) / 1000

        if elapsed <= level_config['time_3star']:
            self.stars = 3
        elif elapsed <= level_config['time_2star']:
            self.stars = 2
        else:
            self.stars = 1

    def update(self):
        """更新游戏状态"""
        if self.state == STATE_PLAYING:
            self.pigeon.update()
            self.level_time = (pygame.time.get_ticks() - self.level_start_time) / 1000

            for bug in self.bugs:
                if bug.alive:
                    bug.update()

    def draw(self):
        """绘制游戏画面"""
        # 背景
        self.screen.fill(LIGHT_BLUE)

        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_LEVEL_SELECT:
            self.draw_level_select()
        elif self.state == STATE_PLAYING:
            self.draw_game()
        elif self.state == STATE_WIN:
            self.draw_win()
        elif self.state == STATE_LOSE:
            self.draw_lose()

        pygame.display.flip()

    def draw_menu(self):
        """绘制主菜单"""
        # 标题
        title = self.chinese_font_big.render("疯狂的鸽子", True, DARK_BROWN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # 副标题
        subtitle = self.chinese_font.render("Pigeon Pop", True, BROWN)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)

        # 绘制一只跳舞的鸽子
        demo_pigeon = Pigeon(SCREEN_WIDTH // 2, 300)
        demo_pigeon.dance_timer = pygame.time.get_ticks() // 16
        demo_pigeon.draw(self.screen)

        # 开始按钮
        pygame.draw.rect(self.screen, GREEN, (140, 350, 200, 70), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (140, 350, 200, 70), 3, border_radius=10)
        start_text = self.chinese_font.render("开始游戏", True, WHITE)
        start_rect = start_text.get_rect(center=(240, 385))
        self.screen.blit(start_text, start_rect)

        # 选关按钮
        pygame.draw.rect(self.screen, ORANGE, (140, 450, 200, 70), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (140, 450, 200, 70), 3, border_radius=10)
        select_text = self.chinese_font.render("选择关卡", True, WHITE)
        select_rect = select_text.get_rect(center=(240, 485))
        self.screen.blit(select_text, select_rect)

        # 虫子数量
        worm_text = self.chinese_font.render(f"虫子: {self.total_worms}", True, DARK_BROWN)
        self.screen.blit(worm_text, (20, 20))

    def draw_level_select(self):
        """绘制关卡选择"""
        # 标题
        title = self.chinese_font_big.render("选择关卡", True, DARK_BROWN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # 返回按钮
        pygame.draw.rect(self.screen, GRAY, (20, 20, 80, 40), border_radius=5)
        back_text = self.chinese_font.render("返回", True, WHITE)
        self.screen.blit(back_text, (35, 25))

        # 关卡按钮
        for i in range(20):
            row = i // 5
            col = i % 5
            btn_x = 40 + col * 85
            btn_y = 100 + row * 85

            color = GREEN if i < self.current_level else GRAY
            pygame.draw.rect(self.screen, color, (btn_x, btn_y, 70, 70), border_radius=10)
            pygame.draw.rect(self.screen, DARK_GRAY, (btn_x, btn_y, 70, 70), 2, border_radius=10)

            level_text = self.font.render(str(i + 1), True, WHITE)
            level_rect = level_text.get_rect(center=(btn_x + 35, btn_y + 35))
            self.screen.blit(level_text, level_rect)

    def draw_game(self):
        """绘制游戏画面"""
        # 玉米
        self.corn.draw(self.screen)

        # 飞行虫子
        for bug in self.bugs:
            bug.draw(self.screen)

        # 鸽子
        self.pigeon.draw(self.screen)

        # UI
        # 关卡信息
        level_text = self.chinese_font.render(f"关卡 {self.current_level}", True, DARK_BROWN)
        self.screen.blit(level_text, (20, 20))

        # 时间
        time_text = self.chinese_font.render(f"时间: {self.level_time:.1f}s", True, DARK_BROWN)
        self.screen.blit(time_text, (20, 50))

        # 虫子
        worm_text = self.chinese_font.render(f"虫子: {self.level_worms}", True, DARK_BROWN)
        self.screen.blit(worm_text, (20, 80))

        # 剩余玉米
        remaining = self.corn.get_remaining_good_kernels()
        total = self.corn.get_total_good_kernels()
        corn_text = self.chinese_font.render(f"玉米: {remaining}/{total}", True, DARK_BROWN)
        self.screen.blit(corn_text, (SCREEN_WIDTH - 120, 20))

    def draw_win(self):
        """绘制胜利画面"""
        # 背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(WHITE)
        self.screen.blit(overlay, (0, 0))

        # 胜利文字
        win_text = self.chinese_font_big.render("过关!", True, GREEN)
        win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(win_text, win_rect)

        # 星星
        star_y = 250
        for i in range(3):
            star_x = SCREEN_WIDTH // 2 - 60 + i * 60
            color = YELLOW if i < self.stars else GRAY
            self.draw_star(star_x, star_y, 25, color)

        # 时间
        time_text = self.chinese_font.render(f"用时: {self.level_time:.1f}秒", True, DARK_BROWN)
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(time_text, time_rect)

        # 虫子
        worm_text = self.chinese_font.render(f"收集虫子: {self.level_worms}", True, DARK_BROWN)
        worm_rect = worm_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(worm_text, worm_rect)

        # 跳舞的鸽子
        dance_pigeon = Pigeon(SCREEN_WIDTH // 2, 450)
        dance_pigeon.dance_timer = pygame.time.get_ticks() // 10
        dance_pigeon.draw(self.screen)

        # 下一关按钮
        pygame.draw.rect(self.screen, GREEN, (140, 500, 200, 70), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (140, 500, 200, 70), 3, border_radius=10)
        next_text = self.chinese_font.render("下一关", True, WHITE)
        next_rect = next_text.get_rect(center=(240, 535))
        self.screen.blit(next_text, next_rect)

        # 重玩按钮
        pygame.draw.rect(self.screen, ORANGE, (140, 590, 200, 70), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (140, 590, 200, 70), 3, border_radius=10)
        replay_text = self.chinese_font.render("重玩", True, WHITE)
        replay_rect = replay_text.get_rect(center=(240, 625))
        self.screen.blit(replay_text, replay_rect)

    def draw_lose(self):
        """绘制失败画面"""
        # 背景遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((50, 50, 50))
        self.screen.blit(overlay, (0, 0))

        # 失败文字
        lose_text = self.chinese_font_big.render("失败!", True, RED)
        lose_rect = lose_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(lose_text, lose_rect)

        # 提示
        hint_text = self.chinese_font.render("啄到了坏玉米!", True, WHITE)
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(hint_text, hint_rect)

        # 悲伤的鸽子
        sad_pigeon = Pigeon(SCREEN_WIDTH // 2, 380)
        sad_pigeon.draw(self.screen)

        # 重试按钮
        pygame.draw.rect(self.screen, GREEN, (140, 450, 200, 70), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (140, 450, 200, 70), 3, border_radius=10)
        retry_text = self.chinese_font.render("重试", True, WHITE)
        retry_rect = retry_text.get_rect(center=(240, 485))
        self.screen.blit(retry_text, retry_rect)

        # 返回菜单按钮
        pygame.draw.rect(self.screen, GRAY, (140, 540, 200, 70), border_radius=10)
        pygame.draw.rect(self.screen, DARK_GRAY, (140, 540, 200, 70), 3, border_radius=10)
        menu_text = self.chinese_font.render("返回菜单", True, WHITE)
        menu_rect = menu_text.get_rect(center=(240, 575))
        self.screen.blit(menu_text, menu_rect)

    def draw_star(self, x, y, size, color):
        """绘制星星"""
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            if i % 2 == 0:
                r = size
            else:
                r = size * 0.4
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            points.append((px, py))
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, DARK_GRAY, points, 2)

    def run(self):
        """游戏主循环"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    """主函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
