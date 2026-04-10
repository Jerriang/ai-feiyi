# 遗境焕活（Heritage Revive）

面向地方非遗场景的 **AI 故事化导览与传播转化平台**，当前仓库已提供“可运行的 MVP 应用骨架（前台 + API + 数据模型）”。

## 已实现能力（当前版本）

- **用户入口页（/）**：产品价值主视觉 + 核心 CTA
- **主题页（/themes）**：非遗项目卡片浏览
- **API（/api/v1）**：游客/注册登录、项目列表/详情、AI 导览（SSE 流式）、路线推荐、PNG 纪念海报生成、后台概览
- **数据库模型（SQLite）**：用户、项目、内容、路线、节点、生成内容等核心实体
- **内置种子数据**：南京云锦、苏州缂丝
- **基础测试**：路线推荐、海报预览生成单测

## 技术栈

- FastAPI + SQLAlchemy + Jinja2
- TailwindCSS（CDN）+ Swiper.js + GSAP + Howler.js + Lottie（沉浸式动效/音效）
- SQLite（可平滑替换 PostgreSQL）
- JWT 鉴权（游客与用户 token）

## 快速启动

```bash
# 安装依赖
pip install -e .

# 运行服务
./scripts/run.sh
```

启动后可访问：

- 前台首页：`http://localhost:8000/`
- AI 导览页：`http://localhost:8000/guide`
- 路线推荐页：`http://localhost:8000/route`
- 后台管理页：`http://localhost:8000/admin`
- 主题页：`http://localhost:8000/themes`
- API 文档：`http://localhost:8000/docs`

## 项目结构

```text
app/
  core/            # 配置与安全
  db/              # 数据库连接
  routers/         # API 路由
  services/        # 业务服务（导览/推荐/生成）
  templates/       # 前端页面模板
  static/css/      # 样式
  main.py          # 应用入口
tests/             # 基础测试
docs/              # 产品与架构文档
db/schema.sql      # PostgreSQL 目标模型（设计版）
```

## 研发建议下一步

1. 对接真实 LLM/TTS/图片生成服务（替换当前规则引擎）。
2. 引入 RBAC 中间件与后台细粒度权限控制。
3. 增加可观测能力（trace-id、错误告警、性能指标）。
4. 将 SQLite 迁移到 PostgreSQL，并接入 Alembic 迁移。


## 视觉规范

- 设计 Token 文档：`design-tokens.md`（主色、底色、字体、间距、圆角、阴影）
- 首页采用移动端优先布局，固定底部导航，禁止横向滚动。


## 后台演示账号

- 邮箱：`admin@heritage.local`
- 密码：`admin123`
- 可在后台卡片点击后，通过 Quill 编辑器修改“南京云锦”等项目的 description 与 image_url。


## PNG 海报生成接口

- `POST /api/v1/generate/poster-image`
- 参数：`user_id`, `heritage_id`, `template_style`（国风/文艺/社媒）
- 返回：`image_url`（PNG 可下载地址）


## 行为埋点接口

- `POST /api/v1/analytics/track`：上报 page_view / guide_start / guide_complete / poster_generate / poster_share
- `GET /api/v1/analytics/overview`：后台看板读取今日核心指标（需管理员 token）


## 对话记忆能力

- 导览 SSE 接口支持 `session_id`、`user_input`、`concise` 参数，自动带入最近 5 轮上下文摘要。
- 新增 `conversation_history` 持久化历史（含摘要与向量占位），支持追问“再说一遍/那个工艺是什么”。


## 沉浸式感官体验层

- 首页入场：GSAP 云纹扩散 + 标题逐字浮现。
- 页面切换：卡片点击后共享过渡到详情页（图片飞入）。
- 音效系统：Howler.js 管理点击/切换/成功/水滴音，并提供全局静音开关。
- 加载艺术：Lottie "非遗纹样编织中" + 窗格纹样骨架背景。


## 守护人成长体系

- 经验规则：完成导览 +50、生成海报 +20、分享海报 +30。
- 等级称号：见习 → 传承 → 大师。
- 支持组队码同步导览，完成后可获得“知音”勋章。
- 完成 3 个非遗项目后解锁“非遗大师的私藏故事”。
