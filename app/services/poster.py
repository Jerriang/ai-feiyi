import uuid


def generate_poster_preview(template_id: str, notes: str) -> tuple[str, str]:
    slug = uuid.uuid4().hex[:10]
    preview = (
        f"【{template_id}】\n"
        "遗境焕活 · 非遗体验纪念\n"
        f"你的体验感受：{notes or '我完成了一次沉浸式非遗导览。'}\n"
        "#非遗 #文化传承 #遗境焕活"
    )
    return preview, slug
