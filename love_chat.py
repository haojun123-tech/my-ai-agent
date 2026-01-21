#!/usr/bin/env python3
"""
心动物语 (Love Chat) - 回合制美女恋爱对话游戏

游戏特色:
1. 多种类型美女角色可选
2. 回合制对话系统，每次选择影响好感度
3. 多结局系统
4. 广告奖励机制（观看广告获取道具/提示）

目标用户: 面向需要情感寄托的单身男性
商业模式: 免费+广告

作者: AI助手
"""

import pygame
import random
import math
import sys
import os
import json
from datetime import datetime

# 初始化 pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass

# 屏幕设置
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
LIGHT_PINK = (255, 218, 233)
DEEP_PINK = (255, 105, 180)
RED = (255, 99, 71)
GOLD = (255, 215, 0)
PURPLE = (186, 85, 211)
LIGHT_PURPLE = (221, 160, 221)
BLUE = (100, 149, 237)
LIGHT_BLUE = (173, 216, 230)
GREEN = (144, 238, 144)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
CREAM = (255, 253, 208)
BROWN = (139, 69, 19)

# 游戏状态
STATE_MENU = 0
STATE_GIRL_SELECT = 1
STATE_CHATTING = 2
STATE_ENDING = 3
STATE_GALLERY = 4
STATE_AD_WATCHING = 5

# 好感度等级
AFFECTION_STRANGER = 0      # 陌生人 0-19
AFFECTION_ACQUAINTANCE = 1  # 认识 20-39
AFFECTION_FRIEND = 2        # 朋友 40-59
AFFECTION_CLOSE = 3         # 亲密 60-79
AFFECTION_LOVER = 4         # 恋人 80-100

# 结局类型
ENDING_BAD = 0      # 坏结局
ENDING_NORMAL = 1   # 普通结局
ENDING_GOOD = 2     # 好结局
ENDING_PERFECT = 3  # 完美结局


class Girl:
    """美女角色基类"""

    def __init__(self, name, girl_type, description, personality):
        self.name = name
        self.girl_type = girl_type  # 类型: cute, cool, gentle, energetic, mysterious
        self.description = description
        self.personality = personality
        self.affection = 0  # 好感度 0-100
        self.current_chapter = 0
        self.unlocked = False
        self.endings_achieved = []

        # 外观属性
        self.hair_color = BLACK
        self.skin_color = (255, 224, 189)
        self.eye_color = BLACK
        self.dress_color = PINK
        self.accessory_color = GOLD

    def get_affection_level(self):
        """获取好感度等级"""
        if self.affection < 20:
            return AFFECTION_STRANGER
        elif self.affection < 40:
            return AFFECTION_ACQUAINTANCE
        elif self.affection < 60:
            return AFFECTION_FRIEND
        elif self.affection < 80:
            return AFFECTION_CLOSE
        else:
            return AFFECTION_LOVER

    def get_affection_title(self):
        """获取好感度称号"""
        level = self.get_affection_level()
        titles = ["陌生人", "认识", "朋友", "亲密", "恋人"]
        return titles[level]

    def add_affection(self, amount):
        """增加好感度"""
        self.affection = max(0, min(100, self.affection + amount))

    def draw(self, screen, x, y, scale=1.0, emotion="normal"):
        """绘制角色立绘"""
        # 基础位置
        center_x = x
        center_y = y

        # 根据缩放调整
        body_height = int(200 * scale)
        head_size = int(60 * scale)

        # 绘制身体（简化的卡通风格）
        # 裙子/衣服
        dress_points = [
            (center_x - int(40*scale), center_y - int(20*scale)),
            (center_x + int(40*scale), center_y - int(20*scale)),
            (center_x + int(50*scale), center_y + int(80*scale)),
            (center_x - int(50*scale), center_y + int(80*scale)),
        ]
        pygame.draw.polygon(screen, self.dress_color, dress_points)
        pygame.draw.polygon(screen, tuple(max(0, c-30) for c in self.dress_color), dress_points, 2)

        # 脖子
        pygame.draw.rect(screen, self.skin_color,
                        (center_x - int(10*scale), center_y - int(40*scale),
                         int(20*scale), int(25*scale)))

        # 头部
        head_y = center_y - int(80*scale)
        pygame.draw.circle(screen, self.skin_color, (center_x, head_y), head_size)

        # 头发
        self._draw_hair(screen, center_x, head_y, head_size, scale)

        # 眼睛
        eye_y = head_y + int(5*scale)
        eye_offset = int(20*scale)
        eye_size = int(12*scale)

        # 眼白
        pygame.draw.ellipse(screen, WHITE,
                           (center_x - eye_offset - eye_size, eye_y - int(8*scale),
                            eye_size*2, int(16*scale)))
        pygame.draw.ellipse(screen, WHITE,
                           (center_x + eye_offset - eye_size, eye_y - int(8*scale),
                            eye_size*2, int(16*scale)))

        # 瞳孔
        pupil_size = int(8*scale)
        pygame.draw.circle(screen, self.eye_color, (center_x - eye_offset, eye_y), pupil_size)
        pygame.draw.circle(screen, self.eye_color, (center_x + eye_offset, eye_y), pupil_size)

        # 高光
        highlight_size = int(3*scale)
        pygame.draw.circle(screen, WHITE,
                          (center_x - eye_offset + int(2*scale), eye_y - int(2*scale)), highlight_size)
        pygame.draw.circle(screen, WHITE,
                          (center_x + eye_offset + int(2*scale), eye_y - int(2*scale)), highlight_size)

        # 表情（根据emotion参数）
        self._draw_expression(screen, center_x, head_y, scale, emotion)

        # 腮红
        blush_color = (255, 200, 200, 128)
        pygame.draw.circle(screen, (255, 200, 200),
                          (center_x - int(30*scale), head_y + int(15*scale)), int(10*scale))
        pygame.draw.circle(screen, (255, 200, 200),
                          (center_x + int(30*scale), head_y + int(15*scale)), int(10*scale))

    def _draw_hair(self, screen, x, y, head_size, scale):
        """绘制头发 - 子类可重写"""
        # 默认长发
        hair_width = int(head_size * 1.3)

        # 头顶
        pygame.draw.arc(screen, self.hair_color,
                       (x - hair_width, y - head_size - int(10*scale),
                        hair_width*2, head_size*2),
                       3.14, 0, int(20*scale))

        # 刘海
        for i in range(-3, 4):
            offset = i * int(10*scale)
            pygame.draw.ellipse(screen, self.hair_color,
                              (x + offset - int(8*scale), y - head_size + int(5*scale),
                               int(16*scale), int(30*scale)))

        # 两侧长发
        left_hair = [
            (x - hair_width + int(10*scale), y - int(20*scale)),
            (x - hair_width - int(5*scale), y + int(100*scale)),
            (x - hair_width + int(20*scale), y + int(90*scale)),
            (x - int(head_size*0.7), y),
        ]
        pygame.draw.polygon(screen, self.hair_color, left_hair)

        right_hair = [
            (x + hair_width - int(10*scale), y - int(20*scale)),
            (x + hair_width + int(5*scale), y + int(100*scale)),
            (x + hair_width - int(20*scale), y + int(90*scale)),
            (x + int(head_size*0.7), y),
        ]
        pygame.draw.polygon(screen, self.hair_color, right_hair)

    def _draw_expression(self, screen, x, y, scale, emotion):
        """绘制表情"""
        mouth_y = y + int(25*scale)

        if emotion == "happy":
            # 开心的笑容
            pygame.draw.arc(screen, DEEP_PINK,
                           (x - int(15*scale), mouth_y - int(5*scale),
                            int(30*scale), int(15*scale)),
                           3.14, 0, int(3*scale))
        elif emotion == "shy":
            # 害羞
            pygame.draw.arc(screen, DEEP_PINK,
                           (x - int(10*scale), mouth_y,
                            int(20*scale), int(10*scale)),
                           3.14, 0, int(2*scale))
            # 加深腮红效果（会在draw方法中重复绘制）
        elif emotion == "sad":
            # 难过
            pygame.draw.arc(screen, DEEP_PINK,
                           (x - int(10*scale), mouth_y + int(5*scale),
                            int(20*scale), int(10*scale)),
                           0, 3.14, int(2*scale))
        elif emotion == "angry":
            # 生气
            pygame.draw.line(screen, DEEP_PINK,
                            (x - int(10*scale), mouth_y),
                            (x + int(10*scale), mouth_y), int(3*scale))
            # 怒眉
            pygame.draw.line(screen, self.hair_color,
                            (x - int(30*scale), y - int(15*scale)),
                            (x - int(15*scale), y - int(10*scale)), int(3*scale))
            pygame.draw.line(screen, self.hair_color,
                            (x + int(30*scale), y - int(15*scale)),
                            (x + int(15*scale), y - int(10*scale)), int(3*scale))
        elif emotion == "surprise":
            # 惊讶
            pygame.draw.circle(screen, DEEP_PINK, (x, mouth_y + int(5*scale)), int(8*scale))
            pygame.draw.circle(screen, (255, 200, 200), (x, mouth_y + int(5*scale)), int(5*scale))
        else:
            # 普通表情
            pygame.draw.arc(screen, DEEP_PINK,
                           (x - int(8*scale), mouth_y,
                            int(16*scale), int(8*scale)),
                           3.14, 0, int(2*scale))


class CuteGirl(Girl):
    """可爱型女孩"""

    def __init__(self):
        super().__init__(
            name="小樱",
            girl_type="cute",
            description="活泼可爱的邻家女孩，喜欢二次元和可爱的东西",
            personality="天真、活泼、有点小迷糊"
        )
        self.hair_color = (139, 69, 19)  # 棕色头发
        self.eye_color = (139, 90, 43)   # 棕色眼睛
        self.dress_color = PINK
        self.unlocked = True  # 默认解锁


class CoolGirl(Girl):
    """高冷型女孩"""

    def __init__(self):
        super().__init__(
            name="冰凝",
            girl_type="cool",
            description="外表高冷的学生会长，内心其实很温柔",
            personality="冷静、理性、外冷内热"
        )
        self.hair_color = (20, 20, 40)   # 深黑色头发
        self.eye_color = (70, 130, 180)  # 钢蓝色眼睛
        self.dress_color = LIGHT_BLUE
        self.unlocked = True


class GentleGirl(Girl):
    """温柔型女孩"""

    def __init__(self):
        super().__init__(
            name="雨薇",
            girl_type="gentle",
            description="温柔体贴的图书馆管理员，喜欢阅读和下厨",
            personality="温柔、善解人意、有母性光环"
        )
        self.hair_color = (50, 30, 20)   # 深棕色头发
        self.eye_color = (34, 139, 34)   # 绿色眼睛
        self.dress_color = LIGHT_PURPLE
        self.unlocked = True


class EnergeticGirl(Girl):
    """元气型女孩"""

    def __init__(self):
        super().__init__(
            name="晴子",
            girl_type="energetic",
            description="运动系阳光女孩，校篮球队的王牌",
            personality="开朗、直率、充满活力"
        )
        self.hair_color = (255, 140, 0)  # 橙色头发
        self.eye_color = (255, 165, 0)   # 橙色眼睛
        self.dress_color = ORANGE


class MysteriousGirl(Girl):
    """神秘型女孩"""

    def __init__(self):
        super().__init__(
            name="月华",
            girl_type="mysterious",
            description="神秘的转学生，似乎隐藏着什么秘密",
            personality="神秘、优雅、若即若离"
        )
        self.hair_color = (75, 0, 130)   # 紫色头发
        self.eye_color = (148, 0, 211)   # 紫色眼睛
        self.dress_color = PURPLE


class DialogueChoice:
    """对话选项"""

    def __init__(self, text, affection_change, response, next_dialogue_id=None,
                 emotion="normal", special_effect=None):
        self.text = text
        self.affection_change = affection_change  # 好感度变化
        self.response = response  # 女孩的回应
        self.next_dialogue_id = next_dialogue_id
        self.emotion = emotion  # 回应时的表情
        self.special_effect = special_effect  # 特殊效果（如解锁CG）


class Dialogue:
    """对话节点"""

    def __init__(self, dialogue_id, girl_text, choices, emotion="normal",
                 background=None, chapter=0):
        self.dialogue_id = dialogue_id
        self.girl_text = girl_text  # 女孩说的话
        self.choices = choices  # 玩家选项列表
        self.emotion = emotion  # 女孩的表情
        self.background = background  # 背景场景
        self.chapter = chapter


class DialogueManager:
    """对话管理器"""

    def __init__(self):
        self.dialogues = {}
        self.current_dialogue_id = None

    def add_dialogue(self, dialogue):
        """添加对话"""
        self.dialogues[dialogue.dialogue_id] = dialogue

    def get_dialogue(self, dialogue_id):
        """获取对话"""
        return self.dialogues.get(dialogue_id)

    def set_current_dialogue(self, dialogue_id):
        """设置当前对话"""
        self.current_dialogue_id = dialogue_id

    def get_current_dialogue(self):
        """获取当前对话"""
        return self.dialogues.get(self.current_dialogue_id)


def create_cute_girl_dialogues():
    """创建可爱女孩的对话内容"""
    dialogues = DialogueManager()

    # 第一章：初次相遇
    dialogues.add_dialogue(Dialogue(
        "cute_ch1_start",
        "啊！不好意思，我没看路撞到你了...你、你没事吧？",
        [
            DialogueChoice(
                "没事，你也小心点",
                5,
                "嘿嘿，谢谢你~我叫小樱，你呢？",
                "cute_ch1_intro",
                "happy"
            ),
            DialogueChoice(
                "没关系，是我挡路了",
                10,
                "哇，你人真好！我叫小樱~❤",
                "cute_ch1_intro",
                "happy"
            ),
            DialogueChoice(
                "走路不看路啊？",
                -5,
                "呜...对不起嘛...",
                "cute_ch1_intro",
                "sad"
            ),
        ],
        emotion="surprise",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch1_intro",
        "你是新来的吗？我之前好像没见过你诶~",
        [
            DialogueChoice(
                "是的，今天刚转学过来",
                5,
                "哇！那我来带你参观学校吧！",
                "cute_ch1_tour",
                "happy"
            ),
            DialogueChoice(
                "我一直在这里上学啊",
                0,
                "诶？！真的吗...那为什么我没注意到呢...",
                "cute_ch1_tour",
                "surprise"
            ),
            DialogueChoice(
                "你管得着吗？",
                -10,
                "呜...我只是想和你交朋友嘛...",
                "cute_ch1_tour",
                "sad"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch1_tour",
        "这里是学校的花园，我最喜欢在这里发呆了~你平时喜欢做什么？",
        [
            DialogueChoice(
                "我喜欢打游戏",
                15,
                "哇！我也是！你玩什么游戏？我们可以一起玩！",
                "cute_ch1_end",
                "happy"
            ),
            DialogueChoice(
                "看书吧",
                5,
                "看书也不错~虽然我看两页就会睡着...",
                "cute_ch1_end",
                "shy"
            ),
            DialogueChoice(
                "没什么特别的爱好",
                0,
                "这样啊...那要不要试试和我一起玩？",
                "cute_ch1_end",
                "normal"
            ),
        ],
        emotion="happy",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch1_end",
        "今天和你聊天很开心~明天也能见到你吗？",
        [
            DialogueChoice(
                "当然，我很期待",
                15,
                "太好了！那我们明天见！(开心地跑走了)",
                None,
                "happy"
            ),
            DialogueChoice(
                "如果有缘的话",
                5,
                "嘿嘿，那我们一定会再见的~",
                None,
                "shy"
            ),
            DialogueChoice(
                "再说吧",
                -5,
                "哦...好吧...(有点失落地走了)",
                None,
                "sad"
            ),
        ],
        emotion="shy",
        chapter=1
    ))

    # 第二章：逐渐熟悉
    dialogues.add_dialogue(Dialogue(
        "cute_ch2_start",
        "你来啦！我等你好久了~今天要不要一起去吃冰淇淋？",
        [
            DialogueChoice(
                "好啊，我请客",
                15,
                "真的吗？！你最好了！❤",
                "cute_ch2_icecream",
                "happy"
            ),
            DialogueChoice(
                "可以，AA吧",
                5,
                "好~那走吧走吧！",
                "cute_ch2_icecream",
                "happy"
            ),
            DialogueChoice(
                "今天有事，改天吧",
                -5,
                "这样啊...那下次一定要陪我哦！",
                None,
                "sad"
            ),
        ],
        emotion="happy",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch2_icecream",
        "你喜欢什么口味的冰淇淋？我最喜欢草莓味的！",
        [
            DialogueChoice(
                "我也喜欢草莓味",
                10,
                "哇！我们好有默契！太开心了~",
                "cute_ch2_chat",
                "happy"
            ),
            DialogueChoice(
                "巧克力味",
                5,
                "巧克力也好吃！要尝尝我的吗？",
                "cute_ch2_chat",
                "happy"
            ),
            DialogueChoice(
                "随便，都行",
                0,
                "那我帮你选一个吧~相信我的眼光！",
                "cute_ch2_chat",
                "normal"
            ),
        ],
        emotion="happy",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch2_chat",
        "嘿嘿...和你在一起总是很开心...你觉得我怎么样？",
        [
            DialogueChoice(
                "你很可爱",
                20,
                "(脸红)可、可爱吗...谢谢...",
                "cute_ch2_end",
                "shy"
            ),
            DialogueChoice(
                "你是个好朋友",
                5,
                "朋友...嗯，朋友也很好！",
                "cute_ch2_end",
                "normal"
            ),
            DialogueChoice(
                "还行吧",
                -5,
                "只是还行吗...哼！",
                "cute_ch2_end",
                "angry"
            ),
        ],
        emotion="shy",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch2_end",
        "今天的冰淇淋好好吃~下次我们去游乐园吧！",
        [
            DialogueChoice(
                "好啊，我来安排",
                15,
                "耶！一言为定！❤",
                None,
                "happy"
            ),
            DialogueChoice(
                "有时间再说",
                0,
                "好~那你一定要记得哦！",
                None,
                "normal"
            ),
        ],
        emotion="happy",
        chapter=2
    ))

    # 第三章：心意相通
    dialogues.add_dialogue(Dialogue(
        "cute_ch3_start",
        "那个...我有话想对你说...你、你能听我说吗？",
        [
            DialogueChoice(
                "当然，我听着",
                10,
                "(深呼吸)我...我好像...喜欢上你了...",
                "cute_ch3_confession",
                "shy"
            ),
            DialogueChoice(
                "怎么了？出什么事了？",
                5,
                "没、没出事！我只是...想告诉你一件事...",
                "cute_ch3_confession",
                "shy"
            ),
        ],
        emotion="shy",
        chapter=3
    ))

    dialogues.add_dialogue(Dialogue(
        "cute_ch3_confession",
        "我知道这很突然...但是和你在一起的时候，我真的很幸福...你、你愿意和我交往吗？",
        [
            DialogueChoice(
                "我也喜欢你",
                30,
                "真、真的吗？！太好了！我好开心！❤❤❤",
                "cute_good_ending",
                "happy"
            ),
            DialogueChoice(
                "让我考虑一下",
                0,
                "嗯...好的...那我等你的答复...",
                "cute_normal_ending",
                "sad"
            ),
            DialogueChoice(
                "抱歉，我们还是做朋友吧",
                -20,
                "这样啊...我明白了...谢谢你一直以来对我的照顾...",
                "cute_bad_ending",
                "sad"
            ),
        ],
        emotion="shy",
        chapter=3
    ))

    # 好结局
    dialogues.add_dialogue(Dialogue(
        "cute_good_ending",
        "从今天起，你就是我的男朋友了！要一直对我好哦~❤",
        [
            DialogueChoice(
                "我会的，一直都会",
                20,
                "嘿嘿~我最喜欢你了！",
                None,
                "happy"
            ),
        ],
        emotion="happy",
        chapter=3
    ))

    # 普通结局
    dialogues.add_dialogue(Dialogue(
        "cute_normal_ending",
        "那...我会一直等你的...不管多久...",
        [
            DialogueChoice(
                "谢谢你的心意",
                5,
                "嗯...你慢慢想...",
                None,
                "sad"
            ),
        ],
        emotion="sad",
        chapter=3
    ))

    # 坏结局
    dialogues.add_dialogue(Dialogue(
        "cute_bad_ending",
        "我...我知道了...那我们还能做朋友吗？",
        [
            DialogueChoice(
                "当然可以",
                5,
                "那就好...至少我们还是朋友...",
                None,
                "sad"
            ),
            DialogueChoice(
                "以后少联系吧",
                -10,
                "(流泪)好...再见...",
                None,
                "sad"
            ),
        ],
        emotion="sad",
        chapter=3
    ))

    return dialogues


def create_cool_girl_dialogues():
    """创建高冷女孩的对话内容"""
    dialogues = DialogueManager()

    # 第一章：图书馆相遇
    dialogues.add_dialogue(Dialogue(
        "cool_ch1_start",
        "这个位置有人了。请另找座位。",
        [
            DialogueChoice(
                "不好意思，我换个位置",
                5,
                "...算了，你坐吧，我要走了。",
                "cool_ch1_leave",
                "normal"
            ),
            DialogueChoice(
                "图书馆是公共场所吧？",
                10,
                "(挑眉)...有点意思。坐吧。",
                "cool_ch1_stay",
                "surprise"
            ),
            DialogueChoice(
                "你谁啊？凭什么赶我走",
                -10,
                "学生会长。有问题？",
                "cool_ch1_stay",
                "angry"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch1_leave",
        "(看着你离开的背影)...有点奇怪的人。",
        [
            DialogueChoice(
                "(转身)你说什么？",
                5,
                "没什么。走吧。",
                None,
                "normal"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch1_stay",
        "你在看什么书？...《人间失格》？品味不错。",
        [
            DialogueChoice(
                "你也喜欢太宰治？",
                15,
                "(微微一笑)不讨厌。",
                "cool_ch1_chat",
                "happy"
            ),
            DialogueChoice(
                "随便看看而已",
                5,
                "是吗...那还挺巧的。",
                "cool_ch1_chat",
                "normal"
            ),
            DialogueChoice(
                "关你什么事",
                -10,
                "...真是没礼貌。",
                None,
                "angry"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch1_chat",
        "我叫冰凝。是这所学校的学生会长。你呢？",
        [
            DialogueChoice(
                "(自我介绍)",
                10,
                "记住了。希望以后不要给学生会添麻烦。",
                "cool_ch1_end",
                "normal"
            ),
            DialogueChoice(
                "你为什么要知道？",
                5,
                "(轻笑)有意思。那就算了。",
                "cool_ch1_end",
                "happy"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch1_end",
        "图书馆快关门了。...下次再见。",
        [
            DialogueChoice(
                "明天还会来吗？",
                10,
                "(停顿)...也许吧。",
                None,
                "shy"
            ),
            DialogueChoice(
                "再见",
                5,
                "嗯。",
                None,
                "normal"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    # 第二章：意外的温柔
    dialogues.add_dialogue(Dialogue(
        "cool_ch2_start",
        "你怎么在这里？...是来找我的吗？",
        [
            DialogueChoice(
                "想来看看你",
                15,
                "(微微脸红)...随你便。",
                "cool_ch2_chat",
                "shy"
            ),
            DialogueChoice(
                "只是路过",
                5,
                "是吗...那你可以走了。",
                "cool_ch2_chat",
                "normal"
            ),
            DialogueChoice(
                "有事找学生会",
                0,
                "什么事？说。",
                "cool_ch2_chat",
                "normal"
            ),
        ],
        emotion="normal",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch2_chat",
        "...今天没什么事。要不要去天台透透气？",
        [
            DialogueChoice(
                "好啊，一起去",
                15,
                "别想太多，只是刚好无聊而已。",
                "cool_ch2_rooftop",
                "shy"
            ),
            DialogueChoice(
                "你主动约我？太阳打西边出来了",
                10,
                "...你很烦。来不来？",
                "cool_ch2_rooftop",
                "angry"
            ),
        ],
        emotion="normal",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch2_rooftop",
        "(看着远方)...其实当学生会长，也挺累的。",
        [
            DialogueChoice(
                "辛苦你了",
                20,
                "...(轻声)谢谢。",
                "cool_ch2_end",
                "shy"
            ),
            DialogueChoice(
                "那为什么还要当？",
                10,
                "...有些事，必须要有人做。",
                "cool_ch2_end",
                "normal"
            ),
            DialogueChoice(
                "那就别当啊",
                -5,
                "你不懂。",
                "cool_ch2_end",
                "angry"
            ),
        ],
        emotion="sad",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch2_end",
        "今天...谢谢你陪我。以后...可以经常来吗？",
        [
            DialogueChoice(
                "只要你需要，我就来",
                20,
                "(难得地笑了)...嗯。",
                None,
                "happy"
            ),
            DialogueChoice(
                "有空就来",
                10,
                "...好。",
                None,
                "normal"
            ),
        ],
        emotion="shy",
        chapter=2
    ))

    # 第三章：冰雪消融
    dialogues.add_dialogue(Dialogue(
        "cool_ch3_start",
        "我有话要对你说...不准笑。",
        [
            DialogueChoice(
                "我不会笑的，你说",
                10,
                "(深呼吸)我...可能...对你有点感觉...",
                "cool_ch3_confession",
                "shy"
            ),
            DialogueChoice(
                "什么事这么严肃？",
                5,
                "闭嘴，听我说完。",
                "cool_ch3_confession",
                "angry"
            ),
        ],
        emotion="shy",
        chapter=3
    ))

    dialogues.add_dialogue(Dialogue(
        "cool_ch3_confession",
        "我从来没有这样过...你是第一个让我觉得...可以依靠的人。你...愿意和我在一起吗？",
        [
            DialogueChoice(
                "我也喜欢你，愿意",
                30,
                "(眼眶微红)...终于等到你说这句话了。",
                "cool_good_ending",
                "happy"
            ),
            DialogueChoice(
                "我需要时间",
                0,
                "...我明白。我等你。",
                "cool_normal_ending",
                "sad"
            ),
            DialogueChoice(
                "抱歉，我做不到",
                -20,
                "...我知道了。请回吧。",
                "cool_bad_ending",
                "sad"
            ),
        ],
        emotion="shy",
        chapter=3
    ))

    # 好结局
    dialogues.add_dialogue(Dialogue(
        "cool_good_ending",
        "从今以后...你要对我负责。这是命令。",
        [
            DialogueChoice(
                "遵命，我的公主",
                20,
                "(微笑)...白痴。",
                None,
                "happy"
            ),
        ],
        emotion="happy",
        chapter=3
    ))

    # 普通结局
    dialogues.add_dialogue(Dialogue(
        "cool_normal_ending",
        "我会在老地方等你...不管多久。",
        [
            DialogueChoice(
                "我会给你答复的",
                5,
                "嗯...去吧。",
                None,
                "sad"
            ),
        ],
        emotion="sad",
        chapter=3
    ))

    # 坏结局
    dialogues.add_dialogue(Dialogue(
        "cool_bad_ending",
        "...果然是我自作多情。以后...不用来找我了。",
        [
            DialogueChoice(
                "对不起",
                0,
                "不用道歉。走吧。",
                None,
                "sad"
            ),
        ],
        emotion="sad",
        chapter=3
    ))

    return dialogues


def create_gentle_girl_dialogues():
    """创建温柔女孩的对话内容"""
    dialogues = DialogueManager()

    # 第一章：图书馆的邂逅
    dialogues.add_dialogue(Dialogue(
        "gentle_ch1_start",
        "你好，需要帮忙找什么书吗？",
        [
            DialogueChoice(
                "请问有关于烹饪的书吗？",
                10,
                "(眼睛一亮)你也喜欢做饭吗？这边请~",
                "gentle_ch1_cooking",
                "happy"
            ),
            DialogueChoice(
                "随便看看",
                5,
                "好的，有需要随时叫我~",
                "gentle_ch1_browse",
                "normal"
            ),
            DialogueChoice(
                "不用，我自己找",
                0,
                "好的，那你慢慢看~",
                "gentle_ch1_browse",
                "normal"
            ),
        ],
        emotion="happy",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "gentle_ch1_cooking",
        "我叫雨薇，是这里的图书管理员。平时我很喜欢下厨呢~你呢？",
        [
            DialogueChoice(
                "我也很喜欢做饭",
                15,
                "真的吗？那有机会我们可以交流一下食谱~",
                "gentle_ch1_end",
                "happy"
            ),
            DialogueChoice(
                "我只会吃，不会做",
                10,
                "(笑)那以后我做给你吃吧~",
                "gentle_ch1_end",
                "happy"
            ),
            DialogueChoice(
                "还好吧",
                5,
                "做饭其实很有趣的，可以治愈心情呢~",
                "gentle_ch1_end",
                "normal"
            ),
        ],
        emotion="happy",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "gentle_ch1_browse",
        "(整理书架)这位同学，你看起来有心事呢~",
        [
            DialogueChoice(
                "你怎么看出来的？",
                10,
                "(温柔地笑)我比较擅长观察人~要聊聊吗？",
                "gentle_ch1_end",
                "happy"
            ),
            DialogueChoice(
                "没有啊",
                5,
                "是吗？那可能是我多想了~",
                "gentle_ch1_end",
                "normal"
            ),
        ],
        emotion="normal",
        chapter=1
    ))

    dialogues.add_dialogue(Dialogue(
        "gentle_ch1_end",
        "图书馆快关门了呢~下次再来吧，我会在这里等你的~",
        [
            DialogueChoice(
                "明天一定来",
                15,
                "(开心)那我等你~路上小心哦~",
                None,
                "happy"
            ),
            DialogueChoice(
                "有空就来",
                5,
                "好~期待再见到你~",
                None,
                "normal"
            ),
        ],
        emotion="happy",
        chapter=1
    ))

    # 第二章：温暖的便当
    dialogues.add_dialogue(Dialogue(
        "gentle_ch2_start",
        "你来了~我今天带了自己做的便当，要一起吃吗？",
        [
            DialogueChoice(
                "太好了，谢谢你！",
                15,
                "(开心地打开便当)希望合你口味~",
                "gentle_ch2_lunch",
                "happy"
            ),
            DialogueChoice(
                "会不会太麻烦你了？",
                10,
                "不会呀~我做饭的时候就想到你了~",
                "gentle_ch2_lunch",
                "shy"
            ),
            DialogueChoice(
                "我已经吃过了",
                -5,
                "这样啊...那我留到明天再给你吧...",
                None,
                "sad"
            ),
        ],
        emotion="happy",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "gentle_ch2_lunch",
        "好吃吗？我放了你上次说喜欢的食材~",
        [
            DialogueChoice(
                "超级好吃！你记得我说的话",
                20,
                "(脸红)你说的话我都记得呢~",
                "gentle_ch2_end",
                "shy"
            ),
            DialogueChoice(
                "很好吃，谢谢",
                10,
                "喜欢就好~以后我经常做给你~",
                "gentle_ch2_end",
                "happy"
            ),
            DialogueChoice(
                "还可以",
                0,
                "是吗...那下次我改进一下...",
                "gentle_ch2_end",
                "sad"
            ),
        ],
        emotion="happy",
        chapter=2
    ))

    dialogues.add_dialogue(Dialogue(
        "gentle_ch2_end",
        "(收拾便当盒)能照顾你，我很开心~下次...我们去公园野餐吧？",
        [
            DialogueChoice(
                "好啊，我很期待",
                15,
                "(温柔地笑)那就这么说定了~",
                None,
                "happy"
            ),
            DialogueChoice(
                "看天气吧",
                5,
                "嗯~我会选一个好天气的~",
                None,
                "normal"
            ),
        ],
        emotion="happy",
        chapter=2
    ))

    # 第三章：温柔的告白
    dialogues.add_dialogue(Dialogue(
        "gentle_ch3_start",
        "今天...有些话想对你说...你能听我说完吗？",
        [
            DialogueChoice(
                "当然，你说",
                10,
                "(深吸一口气)其实我...一直很喜欢你...",
                "gentle_ch3_confession",
                "shy"
            ),
            DialogueChoice(
                "怎么了？",
                5,
                "我想告诉你...一件重要的事...",
                "gentle_ch3_confession",
                "shy"
            ),
        ],
        emotion="shy",
        chapter=3
    ))

    dialogues.add_dialogue(Dialogue(
        "gentle_ch3_confession",
        "照顾你、为你做饭、看着你开心...这已经成为我生活中最重要的事了。你愿意...让我一直陪在你身边吗？",
        [
            DialogueChoice(
                "我也喜欢你，愿意",
                30,
                "(眼眶湿润)太好了...我会一直好好照顾你的...",
                "gentle_good_ending",
                "happy"
            ),
            DialogueChoice(
                "让我想想",
                0,
                "嗯...不管结果如何，我都会继续照顾你的...",
                "gentle_normal_ending",
                "sad"
            ),
            DialogueChoice(
                "对不起，我把你当姐姐",
                -20,
                "(强忍泪水)...我明白了...谢谢你告诉我...",
                "gentle_bad_ending",
                "sad"
            ),
        ],
        emotion="shy",
        chapter=3
    ))

    # 好结局
    dialogues.add_dialogue(Dialogue(
        "gentle_good_ending",
        "从今以后，让我来守护你吧~我会做你最喜欢的饭菜，每天等你回家~",
        [
            DialogueChoice(
                "我也会好好珍惜你",
                20,
                "(幸福地笑)我们要一直在一起哦~",
                None,
                "happy"
            ),
        ],
        emotion="happy",
        chapter=3
    ))

    # 普通结局
    dialogues.add_dialogue(Dialogue(
        "gentle_normal_ending",
        "我会等你的...你是我最重要的人...",
        [
            DialogueChoice(
                "谢谢你",
                5,
                "不用谢~我会一直在这里的~",
                None,
                "sad"
            ),
        ],
        emotion="sad",
        chapter=3
    ))

    # 坏结局
    dialogues.add_dialogue(Dialogue(
        "gentle_bad_ending",
        "能遇见你，是我最幸福的事...以后...要好好照顾自己...",
        [
            DialogueChoice(
                "对不起",
                0,
                "(微笑)不用道歉...这是我自己的心意...",
                None,
                "sad"
            ),
        ],
        emotion="sad",
        chapter=3
    ))

    return dialogues


class AdManager:
    """广告管理器"""

    def __init__(self):
        self.ad_ready = True
        self.ad_cooldown = 0
        self.ads_watched = 0
        self.rewards = {
            "hint": 0,      # 提示道具
            "affection": 0,  # 好感度加成
            "unlock": 0,    # 解锁券
        }

    def is_ad_ready(self):
        """检查广告是否准备好"""
        return self.ad_ready and self.ad_cooldown <= 0

    def show_ad(self):
        """显示广告（模拟）"""
        if self.is_ad_ready():
            self.ad_cooldown = 30  # 30秒冷却
            self.ads_watched += 1
            return True
        return False

    def get_reward(self, reward_type):
        """获取广告奖励"""
        if reward_type == "hint":
            self.rewards["hint"] += 1
            return "获得提示道具 x1"
        elif reward_type == "affection":
            self.rewards["affection"] += 5
            return "获得好感度加成 +5"
        elif reward_type == "unlock":
            self.rewards["unlock"] += 1
            return "获得解锁券 x1"
        return ""

    def update(self):
        """更新冷却时间"""
        if self.ad_cooldown > 0:
            self.ad_cooldown -= 1/60  # 假设60FPS


class SaveManager:
    """存档管理器"""

    def __init__(self):
        self.save_file = "love_chat_save.json"
        self.data = {
            "girls": {},
            "total_play_time": 0,
            "achievements": [],
            "ads_watched": 0,
        }

    def save(self, game_data):
        """保存游戏"""
        self.data.update(game_data)
        try:
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def load(self):
        """加载存档"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            return self.data
        except Exception:
            return self.data


class Game:
    """游戏主类"""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("心动物语 - Love Chat")
        self.clock = pygame.time.Clock()
        self.running = True

        # 初始化字体
        self.init_fonts()

        # 游戏状态
        self.state = STATE_MENU
        self.selected_girl = None
        self.current_dialogue = None
        self.showing_response = False
        self.response_text = ""
        self.response_emotion = "normal"

        # 初始化角色
        self.girls = {
            "cute": CuteGirl(),
            "cool": CoolGirl(),
            "gentle": GentleGirl(),
            "energetic": EnergeticGirl(),
            "mysterious": MysteriousGirl(),
        }

        # 对话管理器
        self.dialogue_managers = {
            "cute": create_cute_girl_dialogues(),
            "cool": create_cool_girl_dialogues(),
            "gentle": create_gentle_girl_dialogues(),
        }

        # 广告和存档
        self.ad_manager = AdManager()
        self.save_manager = SaveManager()

        # 加载存档
        self.load_game()

        # UI状态
        self.scroll_offset = 0
        self.text_animation_index = 0
        self.text_animation_timer = 0
        self.choice_hover = -1

        # 动画
        self.heart_particles = []
        self.background_animation = 0

    def init_fonts(self):
        """初始化字体"""
        font_paths = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            None  # pygame 默认字体
        ]

        self.font_large = None
        self.font_medium = None
        self.font_small = None

        for path in font_paths:
            try:
                if path:
                    self.font_large = pygame.font.Font(path, 32)
                    self.font_medium = pygame.font.Font(path, 24)
                    self.font_small = pygame.font.Font(path, 18)
                else:
                    self.font_large = pygame.font.Font(None, 32)
                    self.font_medium = pygame.font.Font(None, 24)
                    self.font_small = pygame.font.Font(None, 18)
                break
            except Exception:
                continue

    def load_game(self):
        """加载游戏存档"""
        data = self.save_manager.load()
        for girl_type, girl_data in data.get("girls", {}).items():
            if girl_type in self.girls:
                self.girls[girl_type].affection = girl_data.get("affection", 0)
                self.girls[girl_type].current_chapter = girl_data.get("chapter", 0)
                self.girls[girl_type].unlocked = girl_data.get("unlocked", False)

    def save_game(self):
        """保存游戏"""
        girls_data = {}
        for girl_type, girl in self.girls.items():
            girls_data[girl_type] = {
                "affection": girl.affection,
                "chapter": girl.current_chapter,
                "unlocked": girl.unlocked,
            }
        self.save_manager.save({"girls": girls_data})

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game()
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self.handle_hover(event.pos)

    def handle_click(self, pos):
        """处理点击"""
        x, y = pos

        if self.state == STATE_MENU:
            self.handle_menu_click(x, y)
        elif self.state == STATE_GIRL_SELECT:
            self.handle_girl_select_click(x, y)
        elif self.state == STATE_CHATTING:
            self.handle_chat_click(x, y)
        elif self.state == STATE_ENDING:
            self.handle_ending_click(x, y)

    def handle_hover(self, pos):
        """处理鼠标悬停"""
        x, y = pos

        if self.state == STATE_CHATTING and not self.showing_response:
            # 检查选项悬停
            if self.current_dialogue:
                choices = self.current_dialogue.choices
                start_y = 550
                for i, choice in enumerate(choices):
                    choice_rect = pygame.Rect(40, start_y + i * 70, SCREEN_WIDTH - 80, 60)
                    if choice_rect.collidepoint(x, y):
                        self.choice_hover = i
                        return
            self.choice_hover = -1

    def handle_menu_click(self, x, y):
        """处理主菜单点击"""
        # 开始游戏按钮
        if 140 <= x <= 340 and 400 <= y <= 460:
            self.state = STATE_GIRL_SELECT
        # 继续游戏按钮
        elif 140 <= x <= 340 and 480 <= y <= 540:
            self.state = STATE_GIRL_SELECT
        # 看广告获取奖励
        elif 140 <= x <= 340 and 560 <= y <= 620:
            if self.ad_manager.is_ad_ready():
                self.state = STATE_AD_WATCHING

    def handle_girl_select_click(self, x, y):
        """处理角色选择点击"""
        # 返回按钮
        if 20 <= x <= 100 and 20 <= y <= 60:
            self.state = STATE_MENU
            return

        # 角色卡片
        girl_types = ["cute", "cool", "gentle", "energetic", "mysterious"]
        start_y = 100
        for i, girl_type in enumerate(girl_types):
            row = i // 2
            col = i % 2
            card_x = 30 + col * 220
            card_y = start_y + row * 200

            if card_x <= x <= card_x + 200 and card_y <= y <= card_y + 180:
                girl = self.girls[girl_type]
                if girl.unlocked:
                    self.selected_girl = girl
                    self.start_chat(girl_type)
                    return

    def start_chat(self, girl_type):
        """开始对话"""
        if girl_type in self.dialogue_managers:
            dm = self.dialogue_managers[girl_type]
            chapter = self.selected_girl.current_chapter

            # 根据章节选择起始对话
            start_ids = {
                0: f"{girl_type}_ch1_start",
                1: f"{girl_type}_ch2_start",
                2: f"{girl_type}_ch3_start",
            }

            start_id = start_ids.get(chapter, f"{girl_type}_ch1_start")
            dm.set_current_dialogue(start_id)
            self.current_dialogue = dm.get_current_dialogue()
            self.state = STATE_CHATTING
            self.showing_response = False
            self.text_animation_index = 0

    def handle_chat_click(self, x, y):
        """处理对话点击"""
        # 返回按钮
        if 20 <= x <= 100 and 20 <= y <= 60:
            self.save_game()
            self.state = STATE_GIRL_SELECT
            return

        if self.showing_response:
            # 点击继续
            self.showing_response = False
            if self.current_dialogue:
                # 获取下一个对话
                girl_type = self.selected_girl.girl_type
                dm = self.dialogue_managers.get(girl_type)
                if dm:
                    next_dialogue = dm.get_current_dialogue()
                    if next_dialogue:
                        self.current_dialogue = next_dialogue
                        self.text_animation_index = 0
                    else:
                        # 章节结束
                        self.check_ending()
            return

        # 选择对话选项
        if self.current_dialogue:
            choices = self.current_dialogue.choices
            start_y = 550
            for i, choice in enumerate(choices):
                choice_rect = pygame.Rect(40, start_y + i * 70, SCREEN_WIDTH - 80, 60)
                if choice_rect.collidepoint(x, y):
                    self.select_choice(i)
                    return

    def select_choice(self, index):
        """选择对话选项"""
        if self.current_dialogue and index < len(self.current_dialogue.choices):
            choice = self.current_dialogue.choices[index]

            # 更新好感度
            self.selected_girl.add_affection(choice.affection_change)

            # 显示回应
            self.showing_response = True
            self.response_text = choice.response
            self.response_emotion = choice.emotion
            self.text_animation_index = 0

            # 添加心形特效
            if choice.affection_change > 10:
                self.add_heart_particles(5)
            elif choice.affection_change > 0:
                self.add_heart_particles(2)

            # 设置下一个对话
            if choice.next_dialogue_id:
                girl_type = self.selected_girl.girl_type
                dm = self.dialogue_managers.get(girl_type)
                if dm:
                    dm.set_current_dialogue(choice.next_dialogue_id)
            else:
                # 对话结束，检查结局
                girl_type = self.selected_girl.girl_type
                dm = self.dialogue_managers.get(girl_type)
                if dm:
                    dm.set_current_dialogue(None)

    def check_ending(self):
        """检查结局"""
        affection = self.selected_girl.affection
        chapter = self.selected_girl.current_chapter

        if chapter >= 2:  # 第三章结束
            if affection >= 80:
                ending = ENDING_PERFECT
            elif affection >= 60:
                ending = ENDING_GOOD
            elif affection >= 40:
                ending = ENDING_NORMAL
            else:
                ending = ENDING_BAD

            self.selected_girl.endings_achieved.append(ending)
            self.state = STATE_ENDING
        else:
            # 进入下一章
            self.selected_girl.current_chapter += 1
            self.save_game()
            self.state = STATE_GIRL_SELECT

    def handle_ending_click(self, x, y):
        """处理结局界面点击"""
        # 返回选择界面
        if 140 <= x <= 340 and 650 <= y <= 710:
            self.save_game()
            self.state = STATE_GIRL_SELECT

    def add_heart_particles(self, count):
        """添加心形粒子特效"""
        for _ in range(count):
            self.heart_particles.append({
                "x": random.randint(100, SCREEN_WIDTH - 100),
                "y": 400,
                "vy": random.uniform(-3, -1),
                "vx": random.uniform(-1, 1),
                "size": random.randint(10, 20),
                "alpha": 255,
            })

    def update(self):
        """更新游戏状态"""
        # 更新背景动画
        self.background_animation += 1

        # 更新文字动画
        self.text_animation_timer += 1
        if self.text_animation_timer >= 2:
            self.text_animation_timer = 0
            self.text_animation_index += 1

        # 更新心形粒子
        for particle in self.heart_particles[:]:
            particle["y"] += particle["vy"]
            particle["x"] += particle["vx"]
            particle["alpha"] -= 3
            if particle["alpha"] <= 0:
                self.heart_particles.remove(particle)

        # 更新广告冷却
        self.ad_manager.update()

    def draw(self):
        """绘制游戏"""
        # 绘制背景
        self.draw_background()

        # 根据状态绘制
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_GIRL_SELECT:
            self.draw_girl_select()
        elif self.state == STATE_CHATTING:
            self.draw_chat()
        elif self.state == STATE_ENDING:
            self.draw_ending()
        elif self.state == STATE_AD_WATCHING:
            self.draw_ad_screen()

        # 绘制粒子特效
        self.draw_particles()

        pygame.display.flip()

    def draw_background(self):
        """绘制背景"""
        # 渐变背景
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(255 - progress * 30)
            g = int(240 - progress * 20)
            b = int(250 - progress * 10)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # 装饰性元素
        offset = math.sin(self.background_animation * 0.02) * 10
        for i in range(5):
            x = (i * 120 + self.background_animation * 0.5) % (SCREEN_WIDTH + 100) - 50
            y = 100 + i * 30 + offset
            pygame.draw.circle(self.screen, (255, 200, 200, 100), (int(x), int(y)), 5)

    def draw_menu(self):
        """绘制主菜单"""
        # 标题
        title = self.font_large.render("心动物语", True, DEEP_PINK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        subtitle = self.font_medium.render("Love Chat", True, PINK)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # 装饰心形
        self.draw_heart(SCREEN_WIDTH // 2 - 100, 140, 20, DEEP_PINK)
        self.draw_heart(SCREEN_WIDTH // 2 + 80, 140, 20, DEEP_PINK)

        # 按钮
        buttons = [
            ("开始游戏", 400),
            ("继续游戏", 480),
            ("看广告得奖励", 560),
        ]

        for text, y in buttons:
            self.draw_button(text, 140, y, 200, 60)

        # 版本信息
        version = self.font_small.render("免费游戏 - 支持开发者请看广告", True, GRAY)
        version_rect = version.get_rect(center=(SCREEN_WIDTH // 2, 750))
        self.screen.blit(version, version_rect)

    def draw_girl_select(self):
        """绘制角色选择界面"""
        # 标题
        title = self.font_large.render("选择女主角", True, DEEP_PINK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # 返回按钮
        self.draw_button("返回", 20, 20, 80, 40, small=True)

        # 角色卡片
        girl_types = ["cute", "cool", "gentle", "energetic", "mysterious"]
        start_y = 100

        for i, girl_type in enumerate(girl_types):
            row = i // 2
            col = i % 2
            card_x = 30 + col * 220
            card_y = start_y + row * 200

            girl = self.girls[girl_type]
            self.draw_girl_card(girl, card_x, card_y)

    def draw_girl_card(self, girl, x, y):
        """绘制角色卡片"""
        # 卡片背景
        card_color = LIGHT_PINK if girl.unlocked else LIGHT_GRAY
        pygame.draw.rect(self.screen, card_color, (x, y, 200, 180), border_radius=15)
        pygame.draw.rect(self.screen, DEEP_PINK if girl.unlocked else GRAY,
                        (x, y, 200, 180), 3, border_radius=15)

        if girl.unlocked:
            # 绘制小立绘
            girl.draw(self.screen, x + 100, y + 80, scale=0.5)

            # 名字
            name = self.font_medium.render(girl.name, True, BLACK)
            name_rect = name.get_rect(center=(x + 100, y + 140))
            self.screen.blit(name, name_rect)

            # 好感度
            affection_text = f"❤ {girl.affection}"
            affection = self.font_small.render(affection_text, True, RED)
            self.screen.blit(affection, (x + 10, y + 160))

            # 关系
            relation = self.font_small.render(girl.get_affection_title(), True, PURPLE)
            self.screen.blit(relation, (x + 140, y + 160))
        else:
            # 锁定状态
            lock_text = self.font_large.render("🔒", True, GRAY)
            lock_rect = lock_text.get_rect(center=(x + 100, y + 70))
            self.screen.blit(lock_text, lock_rect)

            unlock_text = self.font_small.render("看广告解锁", True, GRAY)
            unlock_rect = unlock_text.get_rect(center=(x + 100, y + 130))
            self.screen.blit(unlock_text, unlock_rect)

    def draw_chat(self):
        """绘制对话界面"""
        # 返回按钮
        self.draw_button("返回", 20, 20, 80, 40, small=True)

        # 好感度显示
        if self.selected_girl:
            heart_text = f"❤ {self.selected_girl.affection} - {self.selected_girl.get_affection_title()}"
            heart = self.font_small.render(heart_text, True, RED)
            self.screen.blit(heart, (SCREEN_WIDTH - 150, 30))

        # 角色立绘
        if self.selected_girl:
            emotion = self.current_dialogue.emotion if self.current_dialogue else "normal"
            if self.showing_response:
                emotion = self.response_emotion
            self.selected_girl.draw(self.screen, SCREEN_WIDTH // 2, 280, scale=1.0, emotion=emotion)

        # 对话框
        self.draw_dialogue_box()

        # 对话内容或选项
        if self.showing_response:
            self.draw_response()
        elif self.current_dialogue:
            self.draw_choices()

    def draw_dialogue_box(self):
        """绘制对话框"""
        # 对话框背景
        box_y = 450
        pygame.draw.rect(self.screen, WHITE, (20, box_y, SCREEN_WIDTH - 40, 330),
                        border_radius=15)
        pygame.draw.rect(self.screen, DEEP_PINK, (20, box_y, SCREEN_WIDTH - 40, 330),
                        3, border_radius=15)

        # 名字标签
        if self.selected_girl:
            name_bg = pygame.Rect(30, box_y - 15, 100, 30)
            pygame.draw.rect(self.screen, DEEP_PINK, name_bg, border_radius=10)
            name = self.font_medium.render(self.selected_girl.name, True, WHITE)
            name_rect = name.get_rect(center=name_bg.center)
            self.screen.blit(name, name_rect)

        # 对话文本
        if self.current_dialogue and not self.showing_response:
            text = self.current_dialogue.girl_text
            animated_text = text[:self.text_animation_index]
            self.draw_wrapped_text(animated_text, 40, box_y + 30, SCREEN_WIDTH - 80,
                                  self.font_medium, BLACK)

    def draw_response(self):
        """绘制女孩回应"""
        # 回应文本
        animated_text = self.response_text[:self.text_animation_index]
        self.draw_wrapped_text(animated_text, 40, 480, SCREEN_WIDTH - 80,
                              self.font_medium, BLACK)

        # 点击继续提示
        if self.text_animation_index >= len(self.response_text):
            hint = self.font_small.render("点击继续...", True, GRAY)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, 750))

            # 闪烁效果
            if (self.background_animation // 30) % 2 == 0:
                self.screen.blit(hint, hint_rect)

    def draw_choices(self):
        """绘制对话选项"""
        if not self.current_dialogue:
            return

        choices = self.current_dialogue.choices
        start_y = 550

        for i, choice in enumerate(choices):
            is_hover = (i == self.choice_hover)
            bg_color = LIGHT_PINK if is_hover else WHITE
            border_color = DEEP_PINK

            choice_rect = pygame.Rect(40, start_y + i * 70, SCREEN_WIDTH - 80, 60)
            pygame.draw.rect(self.screen, bg_color, choice_rect, border_radius=10)
            pygame.draw.rect(self.screen, border_color, choice_rect, 2, border_radius=10)

            # 选项文本
            text = self.font_medium.render(choice.text, True, BLACK)
            text_rect = text.get_rect(center=choice_rect.center)
            self.screen.blit(text, text_rect)

    def draw_ending(self):
        """绘制结局界面"""
        # 背景
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(LIGHT_PINK)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))

        # 结局标题
        affection = self.selected_girl.affection if self.selected_girl else 0

        if affection >= 80:
            title = "完美结局 ❤"
            color = GOLD
            message = "恭喜你，获得了她的芳心！"
        elif affection >= 60:
            title = "好结局"
            color = PINK
            message = "你们成为了恋人~"
        elif affection >= 40:
            title = "普通结局"
            color = BLUE
            message = "也许还有机会..."
        else:
            title = "坏结局"
            color = GRAY
            message = "遗憾地错过了..."

        title_text = self.font_large.render(title, True, color)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)

        # 角色立绘
        if self.selected_girl:
            emotion = "happy" if affection >= 60 else "sad"
            self.selected_girl.draw(self.screen, SCREEN_WIDTH // 2, 400, scale=0.8, emotion=emotion)

        # 结局描述
        msg_text = self.font_medium.render(message, True, BLACK)
        msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(msg_text, msg_rect)

        # 好感度
        affection_text = f"最终好感度: {affection}"
        aff = self.font_medium.render(affection_text, True, RED)
        aff_rect = aff.get_rect(center=(SCREEN_WIDTH // 2, 600))
        self.screen.blit(aff, aff_rect)

        # 返回按钮
        self.draw_button("返回选择", 140, 650, 200, 60)

    def draw_ad_screen(self):
        """绘制广告界面（模拟）"""
        # 背景
        self.screen.fill(WHITE)

        # 模拟广告
        ad_rect = pygame.Rect(40, 100, SCREEN_WIDTH - 80, 400)
        pygame.draw.rect(self.screen, LIGHT_GRAY, ad_rect, border_radius=10)

        ad_text = self.font_large.render("广告位", True, GRAY)
        ad_rect_center = ad_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(ad_text, ad_rect_center)

        # 倒计时或完成按钮
        timer = max(0, int(5 - self.background_animation / 60))
        if timer > 0:
            timer_text = self.font_medium.render(f"请等待 {timer} 秒", True, BLACK)
        else:
            timer_text = self.font_medium.render("点击领取奖励", True, DEEP_PINK)

            # 检测点击领取
            mouse = pygame.mouse.get_pressed()
            if mouse[0]:
                self.ad_manager.show_ad()
                reward = self.ad_manager.get_reward("affection")
                self.background_animation = 0
                self.state = STATE_MENU

        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        self.screen.blit(timer_text, timer_rect)

    def draw_particles(self):
        """绘制粒子特效"""
        for particle in self.heart_particles:
            self.draw_heart(int(particle["x"]), int(particle["y"]),
                          particle["size"], DEEP_PINK, particle["alpha"])

    def draw_heart(self, x, y, size, color, alpha=255):
        """绘制心形"""
        heart_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # 简化心形
        pygame.draw.circle(heart_surface, (*color, alpha), (size // 2, size // 2), size // 2)
        pygame.draw.circle(heart_surface, (*color, alpha), (size + size // 2, size // 2), size // 2)

        points = [
            (0, size // 2),
            (size, size * 2 - 2),
            (size * 2, size // 2),
        ]
        pygame.draw.polygon(heart_surface, (*color, alpha), points)

        self.screen.blit(heart_surface, (x - size, y - size))

    def draw_button(self, text, x, y, width, height, small=False):
        """绘制按钮"""
        mouse_pos = pygame.mouse.get_pos()
        is_hover = x <= mouse_pos[0] <= x + width and y <= mouse_pos[1] <= y + height

        bg_color = LIGHT_PINK if is_hover else WHITE
        border_color = DEEP_PINK

        pygame.draw.rect(self.screen, bg_color, (x, y, width, height), border_radius=10)
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 3, border_radius=10)

        font = self.font_small if small else self.font_medium
        text_surface = font.render(text, True, DEEP_PINK)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)

    def draw_wrapped_text(self, text, x, y, max_width, font, color):
        """绘制自动换行文本"""
        words = list(text)
        lines = []
        current_line = ""

        for char in words:
            test_line = current_line + char
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char

        if current_line:
            lines.append(current_line)

        for i, line in enumerate(lines):
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (x, y + i * 30))

    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
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
