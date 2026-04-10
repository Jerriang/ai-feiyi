from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import HeritageItem, User
from app.routers import admin, analytics, auth, generate, generate_image, guide, heritage, routes, team

app = FastAPI(title=settings.app_name, version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

def ensure_dev_migrations():
    db: Session = SessionLocal()
    try:
        cols = {row[1] for row in db.execute(text("PRAGMA table_info(heritage_items)")).fetchall()}
        if "description" not in cols:
            db.execute(text("ALTER TABLE heritage_items ADD COLUMN description TEXT DEFAULT ''"))
        if "image_url" not in cols:
            db.execute(text("ALTER TABLE heritage_items ADD COLUMN image_url VARCHAR(500) DEFAULT ''"))
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_dev_migrations()
    seed_data()


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(heritage.router, prefix=settings.api_prefix)
app.include_router(guide.router, prefix=settings.api_prefix)
app.include_router(routes.router, prefix=settings.api_prefix)
app.include_router(generate.router, prefix=settings.api_prefix)
app.include_router(generate_image.router, prefix=settings.api_prefix)
app.include_router(team.router, prefix=settings.api_prefix)
app.include_router(admin.router, prefix=settings.api_prefix)


def seed_data():
    db: Session = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@heritage.local").first()
        if not admin:
            db.add(User(email="admin@heritage.local", hashed_password=hash_password("admin123"), role="admin", nickname="管理员"))
            db.commit()

        if db.query(HeritageItem).count() > 0:
            return
        db.add_all(
            [
                HeritageItem(
                    name="南京云锦",
                    category="传统织造",
                    city="南京",
                    summary="南京云锦以华丽纹样和复杂织造技法著称，是中国传统丝织工艺代表。",
                    description="南京云锦是中国传统丝织工艺瑰宝，兼具宫廷礼制与审美价值。",
                    image_url="https://images.unsplash.com/photo-1473447198193-c7c3b070f0b0?auto=format&fit=crop&w=1200&q=80",
                    process="挑花结本、通经断纬、多色纬线叠加",
                    meaning="体现礼制文化与东方审美，承载历史记忆与工艺智慧。",
                ),
                HeritageItem(
                    name="苏州缂丝",
                    category="传统美术",
                    city="苏州",
                    summary="缂丝以通经断纬逐色缂织，细节精密，被誉为“织中圣品”。",
                    description="苏州缂丝以刀刻般清晰的织造边界著称，体现文人雅趣与匠心。",
                    image_url="https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=1200&q=80",
                    process="画稿分色、起稿上机、分区缂织、整饰装裱",
                    meaning="兼具艺术价值与文人审美，体现精工细作精神。",
                ),
                HeritageItem(
                    name="宜兴紫砂",
                    category="传统技艺",
                    city="无锡",
                    summary="紫砂壶以泥料与烧制闻名，讲究器形与实用并重。",
                    description="紫砂工艺强调泥、形、工、火的平衡，是生活美学与手工智慧结合。",
                    image_url="https://images.unsplash.com/photo-1517649763962-0c623066013b?auto=format&fit=crop&w=1200&q=80",
                    process="选泥炼泥、成型修坯、铭刻装饰、入窑烧制",
                    meaning="承载茶文化与匠人精神，体现东方器物哲学。",
                ),
            ]
        )
        db.commit()
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    db: Session = SessionLocal()
    try:
        items = db.query(HeritageItem).order_by(HeritageItem.id.asc()).limit(3).all()
    finally:
        db.close()
    return templates.TemplateResponse("index.html", {"request": request, "title": settings.app_name, "items": items})


@app.get("/themes", response_class=HTMLResponse)
def themes(request: Request):
    db: Session = SessionLocal()
    try:
        items = db.query(HeritageItem).all()
    finally:
        db.close()
    return templates.TemplateResponse("themes.html", {"request": request, "items": items})


@app.get("/guide", response_class=HTMLResponse)
def guide_page(request: Request):
    db: Session = SessionLocal()
    try:
        items = db.query(HeritageItem).order_by(HeritageItem.id.asc()).all()
    finally:
        db.close()
    return templates.TemplateResponse("guide.html", {"request": request, "items": items})


@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/route", response_class=HTMLResponse)
def route_page(request: Request):
    db: Session = SessionLocal()
    try:
        items = db.query(HeritageItem).order_by(HeritageItem.id.asc()).all()
    finally:
        db.close()
    return templates.TemplateResponse("route.html", {"request": request, "items": items})


@app.get("/heritage/{item_id}", response_class=HTMLResponse)
def heritage_detail(request: Request, item_id: int):
    db: Session = SessionLocal()
    try:
        item = db.query(HeritageItem).filter(HeritageItem.id == item_id).first()
    finally:
        db.close()
    if not item:
        return templates.TemplateResponse("themes.html", {"request": request, "items": []})
    return templates.TemplateResponse("detail.html", {"request": request, "item": item})
