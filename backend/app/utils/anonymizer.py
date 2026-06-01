import hashlib
import random

ANIMAL_LIST = [
    "小熊", "小猫", "小狗", "小鹿", "小狐", "小兔", "小象", "小鸟",
    "树懒", "海豚", "考拉", "刺猬", "松鼠", "水獭", "羊驼", "企鹅",
    "狮子", "老虎", "熊猫", "麋鹿", "鲸鱼", "海獭", "锦鲤", "蝴蝶",
]

ADJ_LIST = [
    "温柔的", "快乐的", "勇敢的", "安静的", "明亮的", "柔软的", "甜蜜的", "梦想的",
    "微笑的", "晴朗的", "温暖的", "慵懒的", "迷糊的", "认真的", "可爱的", "暖色的",
    "夜空的", "晨曦的", "月光的", "星星的", "云朵的", "微风的", "露水的", "向阳的",
]


def gen_anonymous_nickname(seed_str: str) -> str:
    """根据种子（user_id+post_id）确定性生成匿名昵称。"""
    h = hashlib.md5(seed_str.encode()).hexdigest()
    n1 = int(h[:8], 16) % len(ADJ_LIST)
    n2 = int(h[8:16], 16) % len(ANIMAL_LIST)
    suffix = int(h[16:20], 16) % 10000
    return f"{ADJ_LIST[n1]}{ANIMAL_LIST[n2]}#{suffix:04d}"


def gen_random_nickname() -> str:
    return f"{random.choice(ADJ_LIST)}{random.choice(ANIMAL_LIST)}#{random.randint(0, 9999):04d}"
