CRISIS_KEYWORDS = [
    "自杀", "轻生", "想死", "不想活", "结束生命", "活不下去", "跳楼", "跳河",
    "上吊", "割腕", "安眠药", "了断", "厌世",
]

CRISIS_HOTLINE_TEXT = (
    "💗 你的感受很重要，请记住你不是一个人。\n"
    "如果你正在经历强烈的痛苦，请立即拨打：\n"
    "• 全国心理援助热线：400-161-9995\n"
    "• 北京心理危机研究与干预中心：010-82951332\n"
    "• 校园心理咨询中心：可在【预约咨询】中预约老师，我们随时陪伴你。"
)


def detect_crisis(text: str) -> bool:
    if not text:
        return False
    return any(kw in text for kw in CRISIS_KEYWORDS)
