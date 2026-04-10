def node_reason(node_title: str, preference: str) -> str:
    if preference == "history":
        return f"从{node_title}切入，能快速建立这项非遗的历史认知。"
    if preference == "interactive":
        return f"{node_title}互动性更强，适合边玩边学，体验感更高。"
    return f"{node_title}内容均衡，兼顾理解、体验与打卡价值。"


def recommend_nodes(duration: int, preference: str) -> list[dict]:
    base = [
        {"title": "起源故事区", "highlight": "了解非遗起源与代表人物"},
        {"title": "工艺流程区", "highlight": "观看关键工艺步骤与材料"},
        {"title": "互动体验区", "highlight": "完成一次简化版工艺互动"},
        {"title": "成果展示区", "highlight": "查看代表作品并打卡"},
    ]

    if preference == "history":
        weights = [0.35, 0.3, 0.15, 0.2]
    elif preference == "interactive":
        weights = [0.2, 0.25, 0.4, 0.15]
    else:
        weights = [0.25, 0.3, 0.25, 0.2]

    result = []
    for idx, (node, w) in enumerate(zip(base, weights), start=1):
        stay = max(5, round(duration * w))
        result.append(
            {
                "node_order": idx,
                "node_title": node["title"],
                "stay_minutes": stay,
                "highlight": node["highlight"],
                "reason": node_reason(node["title"], preference),
                "skippable": idx == 4,
            }
        )
    return result
