from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6)


class HeritageItemOut(BaseModel):
    id: int
    name: str
    category: str
    city: str
    summary: str


class GuideGenerateRequest(BaseModel):
    item_id: int
    style: str = "历史叙事"
    current_step: str = "intro"


class RouteRecommendRequest(BaseModel):
    item_id: int
    duration: int = Field(ge=20, le=300)
    travel_type: str = "solo"
    preference: str = "balanced"


class PosterGenerateRequest(BaseModel):
    route_id: int | None = None
    template_id: str = "guofeng_v1"
    notes: str = ""
