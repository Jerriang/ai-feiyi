# API 规格（MVP）

> 基础路径：`/api/v1`

## 1. 认证

### 1.1 游客进入
- `POST /auth/guest`
- 返回：`guest_token`

### 1.2 用户登录
- `POST /auth/login`
- 入参：`email/phone + password`
- 返回：`access_token`, `refresh_token`

## 2. 非遗项目

### 2.1 项目列表
- `GET /heritage-items`
- 查询：`keyword`, `tags`, `city`, `page`, `size`

### 2.2 项目详情
- `GET /heritage-items/{id}`
- 返回：基础信息、标签、素材、推荐导览入口

## 3. AI 导览

### 3.1 生成导览段落
- `POST /guide/sessions/{sessionId}/generate`
- 入参：`item_id`, `style`, `current_step`, `context`
- 返回：`sections[]`（intro/body/qa/extension/summary）

### 3.2 导览语音
- `POST /guide/tts`
- 入参：`text`, `voice`
- 返回：`audio_url`

## 4. 路线推荐

### 4.1 生成路线
- `POST /routes/recommend`
- 入参：`duration`, `interests[]`, `travel_type`, `first_time`, `preference`
- 返回：`route`, `nodes[]`, `reasoning`, `total_minutes`

### 4.2 更新路线
- `PATCH /routes/{id}`
- 入参：增删节点、顺序调整

## 5. AIGC 纪念内容

### 5.1 生成海报
- `POST /generated-contents/posters`
- 入参：`route_id`, `template_id`, `photos[]`, `notes`
- 返回：`preview_url`, `download_url`, `share_card`

### 5.2 二次编辑
- `PATCH /generated-contents/{id}`
- 入参：文案、配色、布局参数

## 6. 互动与传播

- `POST /interactions/like`
- `POST /interactions/favorite`
- `POST /interactions/checkin`
- `POST /shares/link`

## 7. 后台（需 admin 权限）

- `GET /admin/dashboard/overview`
- `POST /admin/heritage-items`
- `PATCH /admin/heritage-items/{id}/status`
- `POST /admin/guide-scripts`
- `POST /admin/templates`
- `GET /admin/audit-logs`

## 8. 通用错误码

- `400` 参数错误
- `401` 未认证
- `403` 无权限
- `404` 资源不存在
- `409` 资源冲突
- `422` 业务校验失败
- `429` 请求过频
- `500` 服务内部错误
- `503` 外部 AI 服务不可用（应触发兜底）
