#!/usr/bin/env python3
"""
疯狂的鸽子游戏单元测试
"""

import os
import sys

# 设置虚拟显示和音频驱动
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()
pygame.display.set_mode((480, 800))

import unittest
from pigeon_pop import (
    Pigeon, Corn, Bug, Game,
    STATE_MENU, STATE_PLAYING, STATE_WIN, STATE_LOSE, STATE_LEVEL_SELECT
)


class TestPigeon(unittest.TestCase):
    """测试鸽子类"""

    def test_pigeon_creation(self):
        """测试鸽子创建"""
        p = Pigeon(100, 200)
        self.assertEqual(p.x, 100)
        self.assertEqual(p.y, 200)
        self.assertFalse(p.pecking)

    def test_pigeon_movement(self):
        """测试鸽子移动"""
        p = Pigeon(100, 100)
        p.move_to(200, 200)
        self.assertEqual(p.target_x, 170)  # 200 - 30 adjustment
        self.assertEqual(p.target_y, 180)  # 200 - 20 adjustment

    def test_pigeon_peck(self):
        """测试鸽子啄食"""
        p = Pigeon(100, 100)
        self.assertFalse(p.pecking)
        p.peck()
        self.assertTrue(p.pecking)

    def test_pigeon_update(self):
        """测试鸽子更新"""
        p = Pigeon(100, 100)
        p.move_to(200, 200)
        initial_dance = p.dance_timer
        p.update()
        self.assertGreater(p.dance_timer, initial_dance)


class TestCorn(unittest.TestCase):
    """测试玉米棒类"""

    def test_corn_creation(self):
        """测试玉米棒创建"""
        c = Corn(100, 150, 8, 4)
        self.assertEqual(len(c.kernels), 32)  # 8 * 4 = 32

    def test_bad_kernels(self):
        """测试坏玉米粒设置"""
        c = Corn(100, 150, 8, 4)
        c.set_bad_kernels(5)
        bad_count = sum(1 for k in c.kernels if k['bad'])
        self.assertEqual(bad_count, 5)

    def test_worm_kernels(self):
        """测试虫子玉米粒设置"""
        c = Corn(100, 150, 8, 4)
        c.set_bad_kernels(5)
        c.set_worm_kernels(3)
        worm_count = sum(1 for k in c.kernels if k['has_worm'])
        self.assertEqual(worm_count, 3)

    def test_remaining_good_kernels(self):
        """测试剩余好玉米粒计数"""
        c = Corn(100, 150, 8, 4)
        c.set_bad_kernels(5)
        self.assertEqual(c.get_remaining_good_kernels(), 27)  # 32 - 5
        self.assertEqual(c.get_total_good_kernels(), 27)

    def test_check_peck(self):
        """测试啄食检测"""
        c = Corn(100, 150, 8, 4)
        kernel = c.kernels[0]
        kx, ky = kernel['x'] + 9, kernel['y'] + 9
        found = c.check_peck(kx, ky)
        self.assertEqual(found, kernel)

    def test_check_peck_miss(self):
        """测试啄食未命中"""
        c = Corn(100, 150, 8, 4)
        found = c.check_peck(0, 0)
        self.assertIsNone(found)

    def test_eaten_kernel_not_found(self):
        """测试已吃的玉米粒不会再被检测到"""
        c = Corn(100, 150, 8, 4)
        kernel = c.kernels[0]
        kernel['eaten'] = True
        kx, ky = kernel['x'] + 9, kernel['y'] + 9
        found = c.check_peck(kx, ky)
        self.assertIsNone(found)


class TestBug(unittest.TestCase):
    """测试虫子类"""

    def test_bug_creation(self):
        """测试虫子创建"""
        b = Bug(200, 300, 'bee')
        self.assertEqual(b.bug_type, 'bee')
        self.assertTrue(b.alive)

    def test_bug_types(self):
        """测试不同类型虫子"""
        for bug_type in ['fly', 'bee', 'mosquito']:
            b = Bug(100, 100, bug_type)
            self.assertEqual(b.bug_type, bug_type)

    def test_bug_collision(self):
        """测试虫子碰撞检测"""
        b = Bug(100, 100, 'fly')
        self.assertTrue(b.check_collision(105, 105))  # 在范围内
        self.assertFalse(b.check_collision(200, 200))  # 不在范围内


class TestGame(unittest.TestCase):
    """测试游戏类"""

    def setUp(self):
        """测试前初始化"""
        self.game = Game()

    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.game.state, STATE_MENU)
        self.assertEqual(self.game.current_level, 1)

    def test_start_game(self):
        """测试开始游戏"""
        self.game.handle_click((240, 385))  # 点击开始按钮
        self.assertEqual(self.game.state, STATE_PLAYING)

    def test_level_select(self):
        """测试关卡选择"""
        self.game.handle_click((240, 485))  # 点击选关按钮
        self.assertEqual(self.game.state, STATE_LEVEL_SELECT)

    def test_eat_good_kernel(self):
        """测试吃好玉米粒"""
        self.game.state = STATE_PLAYING
        self.game.reset_level()

        initial_count = self.game.corn.get_remaining_good_kernels()

        # 找一个好玉米粒
        for k in self.game.corn.kernels:
            if not k['bad']:
                kx = k['x'] + 9
                ky = k['y'] + 9
                self.game.handle_click((kx, ky))
                break

        self.assertEqual(
            self.game.corn.get_remaining_good_kernels(),
            initial_count - 1
        )

    def test_eat_bad_kernel_loses(self):
        """测试吃坏玉米粒会失败"""
        self.game.state = STATE_PLAYING
        self.game.reset_level()

        # 找一个没有虫子的坏玉米粒
        for k in self.game.corn.kernels:
            if k['bad'] and not k['has_worm']:
                kx = k['x'] + 9
                ky = k['y'] + 9
                self.game.handle_click((kx, ky))
                break

        self.assertEqual(self.game.state, STATE_LOSE)

    def test_eat_worm_on_bad_kernel(self):
        """测试吃坏玉米上的虫子"""
        self.game.state = STATE_PLAYING
        self.game.reset_level()

        initial_worms = self.game.level_worms

        # 找一个有虫子的坏玉米粒
        for k in self.game.corn.kernels:
            if k['bad'] and k['has_worm']:
                kx = k['x'] + 9
                ky = k['y'] + 9
                self.game.handle_click((kx, ky))
                self.assertEqual(self.game.level_worms, initial_worms + 1)
                self.assertFalse(k['has_worm'])
                self.assertNotEqual(self.game.state, STATE_LOSE)
                break

    def test_win_game(self):
        """测试通关"""
        self.game.state = STATE_PLAYING
        self.game.reset_level()

        # 吃掉所有好玉米粒
        for k in self.game.corn.kernels:
            if not k['bad']:
                k['eaten'] = True

        # 重置一个好玉米来触发胜利检测
        self.game.corn.kernels[0]['bad'] = False
        self.game.corn.kernels[0]['eaten'] = False

        kx = self.game.corn.kernels[0]['x'] + 9
        ky = self.game.corn.kernels[0]['y'] + 9
        self.game.handle_click((kx, ky))

        self.assertEqual(self.game.state, STATE_WIN)
        self.assertGreater(self.game.stars, 0)

    def test_levels_configuration(self):
        """测试关卡配置"""
        self.assertEqual(len(self.game.levels), 200)

        # 测试难度递增
        self.assertLess(
            self.game.levels[0]['bad_kernels'],
            self.game.levels[50]['bad_kernels']
        )

        # 测试虫子出现
        self.assertEqual(self.game.levels[0]['bugs'], [])
        self.assertIn('bee', self.game.levels[10]['bugs'])

    def test_reset_level(self):
        """测试重置关卡"""
        self.game.state = STATE_PLAYING
        self.game.level_worms = 10

        self.game.reset_level()

        self.assertEqual(self.game.level_worms, 0)
        self.assertIsNotNone(self.game.pigeon)
        self.assertIsNotNone(self.game.corn)


class TestStarRating(unittest.TestCase):
    """测试星星评级"""

    def test_three_stars(self):
        """测试三星评级"""
        g = Game()
        g.current_level = 1
        g.level_start_time = pygame.time.get_ticks()
        # 快速完成 (0秒)
        g.calculate_stars()
        self.assertEqual(g.stars, 3)

    def test_calculate_stars_called(self):
        """测试胜利时计算星星"""
        g = Game()
        g.state = STATE_PLAYING
        g.reset_level()

        # 快速吃完所有好玉米
        for k in g.corn.kernels:
            if not k['bad']:
                k['eaten'] = True

        # 留一个来触发胜利
        g.corn.kernels[0]['bad'] = False
        g.corn.kernels[0]['eaten'] = False

        kx = g.corn.kernels[0]['x'] + 9
        ky = g.corn.kernels[0]['y'] + 9
        g.handle_click((kx, ky))

        self.assertGreater(g.stars, 0)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
