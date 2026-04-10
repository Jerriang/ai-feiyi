from app.models import HeritageItem


STYLE_TONE = {
    "历史叙事": "从历史脉络切入，强调时代背景与传承逻辑。",
    "游客陪伴": "像导游一样简洁亲切，突出你此刻该看什么。",
    "儿童科普": "用简单比喻解释工艺，增强趣味与理解。",
    "文艺沉浸": "强调画面感和情绪体验，营造沉浸式氛围。",
}


def generate_story(item: HeritageItem, style: str) -> dict:
    tone = STYLE_TONE.get(style, STYLE_TONE["历史叙事"])
    return {
        "intro": f"欢迎来到{item.name}，我们将用{style}方式开启体验。",
        "body": f"{item.summary} 工艺核心是：{item.process}",
        "qa": "想一想：这项技艺为什么能在当地延续这么久？",
        "extension": f"文化寓意：{item.meaning}",
        "summary": f"本段结束。{tone}",
    }
