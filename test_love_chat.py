#!/usr/bin/env python3
"""
心动物语 (Love Chat) 游戏测试
"""

import unittest
import os
import sys
import json

# 设置虚拟显示驱动以便在无图形界面环境中运行测试
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
pygame.init()

from love_chat import (
    Girl, CuteGirl, CoolGirl, GentleGirl, EnergeticGirl, MysteriousGirl,
    Dialogue, DialogueChoice, DialogueManager,
    AdManager, SaveManager, Game,
    AFFECTION_STRANGER, AFFECTION_ACQUAINTANCE, AFFECTION_FRIEND,
    AFFECTION_CLOSE, AFFECTION_LOVER,
    ENDING_BAD, ENDING_NORMAL, ENDING_GOOD, ENDING_PERFECT,
    create_cute_girl_dialogues, create_cool_girl_dialogues, create_gentle_girl_dialogues
)


class TestGirl(unittest.TestCase):
    """测试角色类"""

    def setUp(self):
        """设置测试环境"""
        self.girl = CuteGirl()

    def test_girl_creation(self):
        """测试角色创建"""
        self.assertEqual(self.girl.name, "小樱")
        self.assertEqual(self.girl.girl_type, "cute")
        self.assertEqual(self.girl.affection, 0)
        self.assertTrue(self.girl.unlocked)

    def test_affection_levels(self):
        """测试好感度等级"""
        # 陌生人
        self.girl.affection = 0
        self.assertEqual(self.girl.get_affection_level(), AFFECTION_STRANGER)
        self.assertEqual(self.girl.get_affection_title(), "陌生人")

        # 认识
        self.girl.affection = 20
        self.assertEqual(self.girl.get_affection_level(), AFFECTION_ACQUAINTANCE)
        self.assertEqual(self.girl.get_affection_title(), "认识")

        # 朋友
        self.girl.affection = 40
        self.assertEqual(self.girl.get_affection_level(), AFFECTION_FRIEND)
        self.assertEqual(self.girl.get_affection_title(), "朋友")

        # 亲密
        self.girl.affection = 60
        self.assertEqual(self.girl.get_affection_level(), AFFECTION_CLOSE)
        self.assertEqual(self.girl.get_affection_title(), "亲密")

        # 恋人
        self.girl.affection = 80
        self.assertEqual(self.girl.get_affection_level(), AFFECTION_LOVER)
        self.assertEqual(self.girl.get_affection_title(), "恋人")

    def test_add_affection(self):
        """测试好感度增减"""
        self.girl.affection = 50

        # 正常增加
        self.girl.add_affection(10)
        self.assertEqual(self.girl.affection, 60)

        # 正常减少
        self.girl.add_affection(-20)
        self.assertEqual(self.girl.affection, 40)

        # 上限测试
        self.girl.affection = 95
        self.girl.add_affection(20)
        self.assertEqual(self.girl.affection, 100)

        # 下限测试
        self.girl.affection = 5
        self.girl.add_affection(-20)
        self.assertEqual(self.girl.affection, 0)


class TestAllGirls(unittest.TestCase):
    """测试所有角色类型"""

    def test_cute_girl(self):
        """测试可爱型女孩"""
        girl = CuteGirl()
        self.assertEqual(girl.name, "小樱")
        self.assertEqual(girl.girl_type, "cute")
        self.assertTrue(girl.unlocked)

    def test_cool_girl(self):
        """测试高冷型女孩"""
        girl = CoolGirl()
        self.assertEqual(girl.name, "冰凝")
        self.assertEqual(girl.girl_type, "cool")
        self.assertTrue(girl.unlocked)

    def test_gentle_girl(self):
        """测试温柔型女孩"""
        girl = GentleGirl()
        self.assertEqual(girl.name, "雨薇")
        self.assertEqual(girl.girl_type, "gentle")
        self.assertTrue(girl.unlocked)

    def test_energetic_girl(self):
        """测试元气型女孩"""
        girl = EnergeticGirl()
        self.assertEqual(girl.name, "晴子")
        self.assertEqual(girl.girl_type, "energetic")
        self.assertFalse(girl.unlocked)  # 默认锁定

    def test_mysterious_girl(self):
        """测试神秘型女孩"""
        girl = MysteriousGirl()
        self.assertEqual(girl.name, "月华")
        self.assertEqual(girl.girl_type, "mysterious")
        self.assertFalse(girl.unlocked)  # 默认锁定


class TestDialogue(unittest.TestCase):
    """测试对话系统"""

    def setUp(self):
        """设置测试环境"""
        self.choice1 = DialogueChoice(
            text="选项1",
            affection_change=10,
            response="回应1",
            next_dialogue_id="next_1",
            emotion="happy"
        )
        self.choice2 = DialogueChoice(
            text="选项2",
            affection_change=-5,
            response="回应2",
            next_dialogue_id="next_2",
            emotion="sad"
        )
        self.dialogue = Dialogue(
            dialogue_id="test_dialogue",
            girl_text="测试对话文本",
            choices=[self.choice1, self.choice2],
            emotion="normal",
            chapter=1
        )

    def test_dialogue_choice_creation(self):
        """测试对话选项创建"""
        self.assertEqual(self.choice1.text, "选项1")
        self.assertEqual(self.choice1.affection_change, 10)
        self.assertEqual(self.choice1.response, "回应1")
        self.assertEqual(self.choice1.next_dialogue_id, "next_1")
        self.assertEqual(self.choice1.emotion, "happy")

    def test_dialogue_creation(self):
        """测试对话创建"""
        self.assertEqual(self.dialogue.dialogue_id, "test_dialogue")
        self.assertEqual(self.dialogue.girl_text, "测试对话文本")
        self.assertEqual(len(self.dialogue.choices), 2)
        self.assertEqual(self.dialogue.emotion, "normal")
        self.assertEqual(self.dialogue.chapter, 1)


class TestDialogueManager(unittest.TestCase):
    """测试对话管理器"""

    def setUp(self):
        """设置测试环境"""
        self.manager = DialogueManager()
        self.dialogue1 = Dialogue(
            "dialogue_1",
            "文本1",
            [DialogueChoice("选项", 5, "回应", "dialogue_2")],
            chapter=1
        )
        self.dialogue2 = Dialogue(
            "dialogue_2",
            "文本2",
            [DialogueChoice("选项", 5, "回应")],
            chapter=1
        )

    def test_add_and_get_dialogue(self):
        """测试添加和获取对话"""
        self.manager.add_dialogue(self.dialogue1)
        self.manager.add_dialogue(self.dialogue2)

        retrieved = self.manager.get_dialogue("dialogue_1")
        self.assertEqual(retrieved.girl_text, "文本1")

        retrieved2 = self.manager.get_dialogue("dialogue_2")
        self.assertEqual(retrieved2.girl_text, "文本2")

    def test_get_nonexistent_dialogue(self):
        """测试获取不存在的对话"""
        result = self.manager.get_dialogue("nonexistent")
        self.assertIsNone(result)

    def test_current_dialogue(self):
        """测试当前对话管理"""
        self.manager.add_dialogue(self.dialogue1)
        self.manager.set_current_dialogue("dialogue_1")

        current = self.manager.get_current_dialogue()
        self.assertEqual(current.dialogue_id, "dialogue_1")


class TestCuteGirlDialogues(unittest.TestCase):
    """测试可爱女孩对话内容"""

    def setUp(self):
        """设置测试环境"""
        self.dialogues = create_cute_girl_dialogues()

    def test_chapter1_start_exists(self):
        """测试第一章起始对话存在"""
        dialogue = self.dialogues.get_dialogue("cute_ch1_start")
        self.assertIsNotNone(dialogue)
        self.assertEqual(dialogue.chapter, 1)

    def test_chapter1_has_choices(self):
        """测试第一章有选项"""
        dialogue = self.dialogues.get_dialogue("cute_ch1_start")
        self.assertGreater(len(dialogue.choices), 0)

    def test_all_chapters_exist(self):
        """测试所有章节存在"""
        ch1 = self.dialogues.get_dialogue("cute_ch1_start")
        ch2 = self.dialogues.get_dialogue("cute_ch2_start")
        ch3 = self.dialogues.get_dialogue("cute_ch3_start")

        self.assertIsNotNone(ch1)
        self.assertIsNotNone(ch2)
        self.assertIsNotNone(ch3)

    def test_endings_exist(self):
        """测试结局存在"""
        good = self.dialogues.get_dialogue("cute_good_ending")
        normal = self.dialogues.get_dialogue("cute_normal_ending")
        bad = self.dialogues.get_dialogue("cute_bad_ending")

        self.assertIsNotNone(good)
        self.assertIsNotNone(normal)
        self.assertIsNotNone(bad)


class TestCoolGirlDialogues(unittest.TestCase):
    """测试高冷女孩对话内容"""

    def setUp(self):
        """设置测试环境"""
        self.dialogues = create_cool_girl_dialogues()

    def test_chapter1_start_exists(self):
        """测试第一章起始对话存在"""
        dialogue = self.dialogues.get_dialogue("cool_ch1_start")
        self.assertIsNotNone(dialogue)

    def test_all_chapters_exist(self):
        """测试所有章节存在"""
        ch1 = self.dialogues.get_dialogue("cool_ch1_start")
        ch2 = self.dialogues.get_dialogue("cool_ch2_start")
        ch3 = self.dialogues.get_dialogue("cool_ch3_start")

        self.assertIsNotNone(ch1)
        self.assertIsNotNone(ch2)
        self.assertIsNotNone(ch3)


class TestGentleGirlDialogues(unittest.TestCase):
    """测试温柔女孩对话内容"""

    def setUp(self):
        """设置测试环境"""
        self.dialogues = create_gentle_girl_dialogues()

    def test_chapter1_start_exists(self):
        """测试第一章起始对话存在"""
        dialogue = self.dialogues.get_dialogue("gentle_ch1_start")
        self.assertIsNotNone(dialogue)

    def test_all_chapters_exist(self):
        """测试所有章节存在"""
        ch1 = self.dialogues.get_dialogue("gentle_ch1_start")
        ch2 = self.dialogues.get_dialogue("gentle_ch2_start")
        ch3 = self.dialogues.get_dialogue("gentle_ch3_start")

        self.assertIsNotNone(ch1)
        self.assertIsNotNone(ch2)
        self.assertIsNotNone(ch3)


class TestAdManager(unittest.TestCase):
    """测试广告管理器"""

    def setUp(self):
        """设置测试环境"""
        self.ad_manager = AdManager()

    def test_initial_state(self):
        """测试初始状态"""
        self.assertTrue(self.ad_manager.ad_ready)
        self.assertEqual(self.ad_manager.ad_cooldown, 0)
        self.assertEqual(self.ad_manager.ads_watched, 0)

    def test_is_ad_ready(self):
        """测试广告就绪状态"""
        self.assertTrue(self.ad_manager.is_ad_ready())

        # 设置冷却
        self.ad_manager.ad_cooldown = 30
        self.assertFalse(self.ad_manager.is_ad_ready())

    def test_show_ad(self):
        """测试显示广告"""
        result = self.ad_manager.show_ad()
        self.assertTrue(result)
        self.assertEqual(self.ad_manager.ads_watched, 1)
        self.assertGreater(self.ad_manager.ad_cooldown, 0)

        # 冷却中不能再看
        result2 = self.ad_manager.show_ad()
        self.assertFalse(result2)

    def test_get_reward(self):
        """测试获取奖励"""
        hint_reward = self.ad_manager.get_reward("hint")
        self.assertIn("提示", hint_reward)
        self.assertEqual(self.ad_manager.rewards["hint"], 1)

        affection_reward = self.ad_manager.get_reward("affection")
        self.assertIn("好感度", affection_reward)
        self.assertEqual(self.ad_manager.rewards["affection"], 5)

        unlock_reward = self.ad_manager.get_reward("unlock")
        self.assertIn("解锁", unlock_reward)
        self.assertEqual(self.ad_manager.rewards["unlock"], 1)


class TestSaveManager(unittest.TestCase):
    """测试存档管理器"""

    def setUp(self):
        """设置测试环境"""
        self.save_manager = SaveManager()
        self.save_manager.save_file = "test_save.json"

    def tearDown(self):
        """清理测试文件"""
        if os.path.exists("test_save.json"):
            os.remove("test_save.json")

    def test_save_and_load(self):
        """测试保存和加载"""
        test_data = {
            "girls": {
                "cute": {"affection": 50, "chapter": 1, "unlocked": True}
            },
            "total_play_time": 100,
        }

        # 保存
        result = self.save_manager.save(test_data)
        self.assertTrue(result)

        # 加载
        loaded = self.save_manager.load()
        self.assertEqual(loaded["girls"]["cute"]["affection"], 50)
        self.assertEqual(loaded["girls"]["cute"]["chapter"], 1)

    def test_load_nonexistent(self):
        """测试加载不存在的文件"""
        self.save_manager.save_file = "nonexistent.json"
        loaded = self.save_manager.load()
        self.assertIsNotNone(loaded)  # 应返回默认数据


class TestGame(unittest.TestCase):
    """测试游戏主类"""

    def setUp(self):
        """设置测试环境"""
        # 设置虚拟显示
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.display.set_mode((480, 800))
        self.game = Game()

    def tearDown(self):
        """清理"""
        if os.path.exists("love_chat_save.json"):
            os.remove("love_chat_save.json")

    def test_game_initialization(self):
        """测试游戏初始化"""
        self.assertIsNotNone(self.game.screen)
        self.assertEqual(len(self.game.girls), 5)
        self.assertIsNotNone(self.game.ad_manager)
        self.assertIsNotNone(self.game.save_manager)

    def test_girls_exist(self):
        """测试所有角色存在"""
        self.assertIn("cute", self.game.girls)
        self.assertIn("cool", self.game.girls)
        self.assertIn("gentle", self.game.girls)
        self.assertIn("energetic", self.game.girls)
        self.assertIn("mysterious", self.game.girls)

    def test_dialogue_managers_exist(self):
        """测试对话管理器存在"""
        self.assertIn("cute", self.game.dialogue_managers)
        self.assertIn("cool", self.game.dialogue_managers)
        self.assertIn("gentle", self.game.dialogue_managers)

    def test_initial_state(self):
        """测试初始状态"""
        from love_chat import STATE_MENU
        self.assertEqual(self.game.state, STATE_MENU)

    def test_unlocked_girls(self):
        """测试解锁状态"""
        self.assertTrue(self.game.girls["cute"].unlocked)
        self.assertTrue(self.game.girls["cool"].unlocked)
        self.assertTrue(self.game.girls["gentle"].unlocked)
        self.assertFalse(self.game.girls["energetic"].unlocked)
        self.assertFalse(self.game.girls["mysterious"].unlocked)


class TestAffectionSystem(unittest.TestCase):
    """测试好感度系统"""

    def test_affection_boundaries(self):
        """测试好感度边界"""
        girl = CuteGirl()

        # 测试等级边界
        test_cases = [
            (0, AFFECTION_STRANGER),
            (19, AFFECTION_STRANGER),
            (20, AFFECTION_ACQUAINTANCE),
            (39, AFFECTION_ACQUAINTANCE),
            (40, AFFECTION_FRIEND),
            (59, AFFECTION_FRIEND),
            (60, AFFECTION_CLOSE),
            (79, AFFECTION_CLOSE),
            (80, AFFECTION_LOVER),
            (100, AFFECTION_LOVER),
        ]

        for affection, expected_level in test_cases:
            girl.affection = affection
            self.assertEqual(
                girl.get_affection_level(),
                expected_level,
                f"Affection {affection} should be level {expected_level}"
            )


class TestEndingSystem(unittest.TestCase):
    """测试结局系统"""

    def test_ending_determination(self):
        """测试结局判定"""
        # 根据好感度判定结局
        test_cases = [
            (90, ENDING_PERFECT),  # 80+ -> 完美结局
            (70, ENDING_GOOD),     # 60-79 -> 好结局
            (50, ENDING_NORMAL),   # 40-59 -> 普通结局
            (20, ENDING_BAD),      # <40 -> 坏结局
        ]

        for affection, expected_ending in test_cases:
            if affection >= 80:
                ending = ENDING_PERFECT
            elif affection >= 60:
                ending = ENDING_GOOD
            elif affection >= 40:
                ending = ENDING_NORMAL
            else:
                ending = ENDING_BAD

            self.assertEqual(
                ending,
                expected_ending,
                f"Affection {affection} should give ending {expected_ending}"
            )


class TestDialogueFlow(unittest.TestCase):
    """测试对话流程"""

    def test_cute_girl_dialogue_flow(self):
        """测试可爱女孩对话流程"""
        dialogues = create_cute_girl_dialogues()
        girl = CuteGirl()

        # 模拟选择最佳选项
        dialogues.set_current_dialogue("cute_ch1_start")
        current = dialogues.get_current_dialogue()

        self.assertIsNotNone(current)
        self.assertEqual(current.chapter, 1)

        # 选择第二个选项（好感度+10）
        choice = current.choices[1]
        girl.add_affection(choice.affection_change)

        self.assertEqual(girl.affection, 10)
        self.assertEqual(choice.next_dialogue_id, "cute_ch1_intro")

    def test_dialogue_chain(self):
        """测试对话链"""
        dialogues = create_cute_girl_dialogues()

        # 验证对话链接完整性
        visited = set()
        queue = ["cute_ch1_start"]

        while queue:
            dialogue_id = queue.pop(0)
            if dialogue_id in visited or dialogue_id is None:
                continue

            visited.add(dialogue_id)
            dialogue = dialogues.get_dialogue(dialogue_id)

            if dialogue:
                for choice in dialogue.choices:
                    if choice.next_dialogue_id:
                        queue.append(choice.next_dialogue_id)

        # 应该访问了多个对话节点
        self.assertGreater(len(visited), 3)


if __name__ == "__main__":
    unittest.main()
