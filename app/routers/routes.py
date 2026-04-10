from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import HeritageItem, RouteNode, RoutePlan
from app.schemas import RouteRecommendRequest
from app.services.recommendation import recommend_nodes

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/recommend")
def recommend(payload: RouteRecommendRequest, db: Session = Depends(get_db)):
    item = db.query(HeritageItem).filter(HeritageItem.id == payload.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="项目不存在")

    nodes = recommend_nodes(payload.duration, payload.preference)
    route = RoutePlan(
        item_id=item.id,
        duration_minutes=payload.duration,
        travel_type=payload.travel_type,
        preference=payload.preference,
        reasoning="依据停留时长与偏好自动生成，可手动调整。",
    )
    db.add(route)
    db.flush()

    for n in nodes:
        db.add(
            RouteNode(
                route_id=route.id,
                node_order=n["node_order"],
                node_title=n["node_title"],
                stay_minutes=n["stay_minutes"],
                highlight=n["highlight"],
                skippable=n["skippable"],
            )
        )

    db.commit()
    db.refresh(route)
    saved_nodes = db.query(RouteNode).filter(RouteNode.route_id == route.id).order_by(RouteNode.node_order).all()
    response_nodes = []
    for i, node in enumerate(saved_nodes):
        reason = nodes[i].get("reason", "该站点与偏好匹配，建议优先体验。")
        response_nodes.append(
            {
                "node_order": node.node_order,
                "node_title": node.node_title,
                "stay_minutes": node.stay_minutes,
                "highlight": node.highlight,
                "reason": reason,
                "skippable": node.skippable,
            }
        )

    return {
        "route_id": route.id,
        "item_id": route.item_id,
        "total_minutes": route.duration_minutes,
        "reasoning": route.reasoning,
        "nodes": response_nodes,
    }
