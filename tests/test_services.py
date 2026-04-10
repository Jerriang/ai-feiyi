from app.services.poster import generate_poster_preview
from app.services.recommendation import recommend_nodes


def test_recommend_nodes_total_positive():
    nodes = recommend_nodes(120, "balanced")
    assert len(nodes) == 4
    assert sum(n["stay_minutes"] for n in nodes) > 0


def test_generate_poster_preview_has_hash_tag():
    preview, slug = generate_poster_preview("guofeng_v1", "今天体验很棒")
    assert "#非遗" in preview
    assert len(slug) == 10
