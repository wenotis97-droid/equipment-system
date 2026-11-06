# 设备管理系统 + 微信小程序互联

一套面向工程施工企业的设备管理平台，支持**二维码扫码操作**、**后台综合管理**、**微信小程序移动端**三位一体的设备全生命周期管理。

## 核心功能

### 1. 设备档案管理
- 设备基本信息：编号、名称、型号、品牌、类别、出厂编号、发动机号、底盘号等
- 驾驶员/操作手信息：姓名、电话、身份证号
- 保险信息管理
- **自定义扩展字段**：管理员可在后台定义额外字段（如发动机功率、斗容、归属方式等），设备录入时自动渲染
- 维保记录追踪：累计运转台时、上次保养日期/台时
- 设备照片上传

### 2. 维保管理（自动提醒）
- **双重触发提醒机制**：
  - 日历周期：按固定时间间隔（如每季度、每半年）自动提醒
  - 台时周期：按累计运转台时（如每 250 小时）自动提醒
- 维保计划创建与管理
- 维保记录登记（保养类型、内容、费用、下次计划）
- 维保提醒自动生成，后台首页和小程序同步展示

### 3. 加油记录管理
- 每次加油登记：油量、金额、单价、加油站
- **油耗自动计算**：根据运转台时自动计算百公里/百小时油耗
- 加油分析报表

### 4. 设备运转记录
- 每日运转台时登记
- **台时自动累加**：提交运转记录后自动更新设备累计台时
- 交接班记录

### 5. 安全培训记录
- 培训计划管理
- 参训人员记录
- 培训完成状态追踪

### 6. 报修管理
- 小程序扫码一键报修
- 报修工单流转（待处理 → 维修中 → 已完成）
- 维修记录与费用追踪

### 7. 特种设备合规管理
针对**龙门吊、架桥机、履带式起重机**等特种设备，实施严格的合规管理：

| 检查项 | 说明 |
|--------|------|
| 特种设备登记证 | 必须有效 |
| 定期检验报告 | 在有效期内 |
| 操作人员作业证 | 持证上岗 |
| 安装拆卸方案 | 有方案且审批通过 |
| 安装验收记录 | 已验收合格 |

**四级合规状态**：
- ✅ 合规 — 所有检查项均通过
- ⚠️ 即将过期 — 有检查项将在 30 天内过期
- ❌ 已过期 — 有检查项已过期
- 🚫 不合规 — 缺少必要检查项

系统定时扫描特种设备合规状态，自动生成提醒通知。

### 8. 二维码扫码体系
- 每台设备生成**唯一防伪二维码**（UUID4 Token）
- 使用人员微信扫码 → 自动识别设备 → 进入操作菜单
- 支持操作：查看详情、加油登记、运转记录、交接班、报修申请
- 管理人员后台可批量导出/打印二维码

### 9. 通知与提醒
- 维保到期提醒
- 特种设备合规预警
- 报修工单状态变更通知
- 后台顶栏实时展示未读通知

### 10. 仪表盘与统计
- 设备状态分布（使用中/闲置/维修/停用/报废）
- 特种设备合规分布
- 维保提醒统计
- 报修待处理统计
- 月度加油量统计
- ECharts 可视化图表

---

## 技术架构

```
┌───────────────────────────────────────────────────┐
│                   微信小程序（移动端）                │
│          uni-app (Vue3) → 微信小程序 / H5           │
│    扫码入口 │ 设备详情 │ 加油登记 │ 运转记录 │ 报修      │
└────────────────────┬──────────────────────────────┘
                     │ X-Session-Token
┌────────────────────┴──────────────────────────────┐
│              FastAPI 后端（Python）                  │
│   JWT认证 │ 设备CRUD │ 维保提醒 │ 特种设备合规校验      │
│   APScheduler定时任务 │ 二维码生成 │ 统计分析           │
└────────┬───────────────────────────┬───────────────┘
         │                           │
┌────────┴──────────┐    ┌───────────┴──────────────┐
│   SQLite / MySQL   │    │  后台管理前端              │
│  数据持久化          │    │  Vue3 + Element Plus     │
└────────────────────┘    │  设备/维保/加油/运转/报修   │
                          │  培训/统计/系统管理        │
                          └──────────────────────────┘
```

### 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端 | Python FastAPI + SQLAlchemy | 高性能异步框架 |
| 数据库 | SQLite（开发）/ MySQL（生产） | 可平滑切换 |
| 后台前端 | Vue3 + Element Plus + Vite | 组件丰富，开发效率高 |
| 小程序 | uni-app (Vue3 语法) | 一套代码编译微信小程序/H5 |
| 定时任务 | APScheduler | 维保/合规自动检查 |
| 认证 | JWT（双 Token 机制） | 后台 Authorization / 小程序 X-Session-Token |
| 二维码 | Python qrcode + Pillow | 中文字体支持，UUID 防伪 |
| 图表 | ECharts | 仪表盘可视化 |

---

## 项目结构

```
equipment-system/
├── backend/                    # 后端 API 服务
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── dependencies.py    # 依赖注入（认证等）
│   │   ├── models/            # 数据模型
│   │   │   ├── base.py        # 模型基类
│   │   │   ├── sys_user.py    # 用户/角色/部门
│   │   │   ├── equipment.py   # 设备/类别/字段定义/保险
│   │   │   ├── special_equipment.py  # 特种设备扩展
│   │   │   ├── maintenance.py # 维保计划/记录/提醒
│   │   │   ├── fuel.py        # 加油记录
│   │   │   ├── operation.py   # 运转记录
│   │   │   ├── repair.py      # 报修
│   │   │   ├── training.py    # 培训
│   │   │   └── misc.py        # 项目/通知/二维码日志
│   │   ├── schemas/           # Pydantic 数据模型
│   │   ├── services/          # 业务逻辑层
│   │   ├── routers/           # API 路由
│   │   │   ├── admin/         # 后台管理 API
│   │   │   └── miniapp/       # 小程序 API
│   │   ├── scheduler/         # 定时任务
│   │   ├── utils/             # 工具类（JWT/二维码/文件上传/微信API）
│   │   └── init_data.py       # 初始化示例数据
│   ├── uploads/               # 上传文件（二维码、设备照片）
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # 后台管理前端
│   ├── src/
│   │   ├── views/             # 页面
│   │   │   ├── login/         # 登录
│   │   │   ├── dashboard/     # 仪表盘
│   │   │   ├── equipment/     # 设备管理
│   │   │   ├── special-equipment/  # 特种设备
│   │   │   ├── maintenance/   # 维保管理
│   │   │   ├── fuel/          # 加油记录
│   │   │   ├── operation/     # 运转记录
│   │   │   ├── repair/        # 报修管理
│   │   │   ├── training/      # 培训管理
│   │   │   ├── statistics/    # 统计分析
│   │   │   └── system/        # 系统管理（用户/字段定义）
│   │   ├── api/               # API 封装
│   │   ├── stores/            # Pinia 状态管理
│   │   └── router/            # 路由
│   ├── vite.config.js
│   └── Dockerfile
├── miniapp/                    # 微信小程序（uni-app）
│   ├── src/
│   │   ├── pages/             # 页面
│   │   │   ├── index/         # 首页（扫码入口）
│   │   │   ├── login/         # 微信登录
│   │   │   ├── equipment/     # 设备详情
│   │   │   ├── fuel/          # 加油登记
│   │   │   ├── operation/     # 运转记录/交接班
│   │   │   ├── repair/        # 报修申请
│   │   │   ├── training/      # 培训
│   │   │   └── history/       # 我的记录
│   │   ├── api/               # API 封装
│   │   └── store/             # Vuex 状态管理
│   ├── vite.config.js
│   └── package.json
└── docker-compose.yml         # 一键部署
```

---

## 快速开始

### 方式一：本地开发运行

#### 1. 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务（自动建表 + 初始化示例数据 + 启动定时任务）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- API 文档：http://localhost:8000/docs
- 默认管理员账号：`admin` / `admin123`

#### 2. 启动后台管理前端

```bash
cd frontend

npm install        # 或 pnpm install
npm run dev        # 或 pnpm dev
```

访问 http://localhost:5173 ，使用 `admin` / `admin123` 登录。

#### 3. 构建微信小程序

```bash
cd miniapp

pnpm install

# 构建 H5 版本（浏览器可直接访问）
pnpm run build:h5

# 构建微信小程序版本
pnpm run build:mp-weixin
```

构建微信小程序后，用**微信开发者工具**导入 `miniapp/dist/build/mp-weixin` 目录即可预览。

> **注意**：微信登录功能需在 `miniapp/src/pages/login/index.vue` 中配置真实的微信 AppID，并在 `backend/app/config.py` 中设置 `WX_APPID` 和 `WX_SECRET`。

---

### 方式二：Docker 一键部署

```bash
# 在项目根目录
docker-compose up -d
```

服务启动后：
- 后端 API：http://localhost:8000
- 后台管理：http://localhost:5173

---

### 生产部署（云服务器）

#### 1. 环境准备

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 安装 docker-compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### 2. 配置

编辑 `docker-compose.yml`，修改以下环境变量：

```yaml
environment:
  - DATABASE_URL=mysql+pymysql://user:password@mysql-host:3306/equipment
  - JWT_SECRET_KEY=your-production-secret-key
  - QR_BASE_URL=http://your-domain.com
  - WX_APPID=your-wechat-appid
  - WX_SECRET=your-wechat-secret
  - CORS_ORIGINS=http://your-domain.com
```

#### 3. Nginx 反向代理（推荐）

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 后台前端
    location / {
        proxy_pass http://127.0.0.1:5173;
    }

    # API 接口
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # 二维码/上传文件
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
    }

    # 扫码重定向
    location /scan/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

#### 4. 切换 MySQL（可选）

修改 `backend/app/config.py` 中的 `DATABASE_URL`：

```python
DATABASE_URL: str = "mysql+pymysql://user:password@localhost:3306/equipment_db"
```

安装 MySQL 驱动：

```bash
pip install pymysql
```

---

## 默认账号

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 系统管理员 | admin | admin123 | 全部权限 |
| 设备管理员 | manager | manager123 | 设备管理 |
| 操作员 | operator1 | operator123 | 小程序操作 |

---

## 示例数据

系统首次启动会自动初始化以下示例数据：

**6 台设备**（含 3 台特种设备）：

| 编号 | 设备名称 | 类别 | 是否特种设备 |
|------|---------|------|-------------|
| EXC-001 | 小松PC200挖掘机 | 挖掘机 | 否 |
| LOD-001 | 柳工855N装载机 | 装载机 | 否 |
| ROL-001 | 三一STR130压路机 | 压路机 | 否 |
| GANTRY-001 | 20t龙门吊 | 龙门吊 | ✅ 是 |
| BRG-001 | 160t架桥机 | 架桥机 | ✅ 是 |
| CRC-001 | 150t履带式起重机 | 履带式起重机 | ✅ 是 |

每台设备自动生成防伪二维码，存放于 `backend/uploads/qrcodes/` 目录。

---

## 二维码使用流程

```
管理员后台生成二维码 → 打印贴在设备上
                                ↓
              使用人员微信扫码 → /scan?token=EQ_xxxx
                                ↓
              自动跳转小程序设备详情页
                                ↓
         ┌──────────┬──────────┬──────────┐
         ↓          ↓          ↓          ↓
      加油登记   运转记录   交接班     报修申请
```

---

## 维保自动提醒机制

系统内置 APScheduler 定时任务，每天自动执行：

1. **日历维保检查**：扫描所有维保计划，如果距离上次保养超过计划周期，生成提醒
2. **台时维保检查**：扫描所有维保计划，如果累计运转台时超过保养台时阈值，生成提醒
3. **特种设备合规检查**：扫描所有特种设备，检查五项合规检查项的有效期，生成预警

提醒通过 Notification 表存储，后台顶栏实时展示。

---

## API 接口概览

### 后台管理 API（`/api/admin/`）

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/auth/login` | 管理员登录 |
| 用户 | `/users` | 用户 CRUD |
| 设备 | `/equipment` | 设备 CRUD |
| 特种设备 | `/special-equipment` | 合规管理 |
| 维保 | `/maintenance/plan` `/maintenance/record` `/maintenance/reminder` | 维保全流程 |
| 加油 | `/business/fuel` | 加油记录 |
| 运转 | `/business/operation` | 运转记录 |
| 报修 | `/business/repair` | 报修工单 |
| 培训 | `/business/training` | 培训管理 |
| 统计 | `/statistics/dashboard` | 仪表盘数据 |
| 字段定义 | `/equipment/field-defs` | 自定义扩展字段 |

### 小程序 API（`/api/miniapp/`）

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/auth/login` | 微信 code 登录 |
| 设备 | `/equipment/{qr_token}` | 扫码获取设备详情 |
| 加油 | `/fuel` | 提交加油记录 |
| 运转 | `/operation` | 提交运转记录 |
| 报修 | `/repair` | 提交报修申请 |
| 培训 | `/training` | 培训列表/详情 |
| 历史 | `/history` | 我的操作记录 |
| 文件 | `/upload` | 图片上传 |

完整 API 文档：启动后端后访问 http://localhost:8000/docs

---

## 微信小程序配置说明

### 1. 微信公众平台配置

1. 登录 [微信公众平台](https://mp.weixin.qq.com)，注册小程序
2. 获取 AppID 和 AppSecret
3. 在「开发管理 → 开发设置」中配置服务器域名：
   - request 合法域名：`https://your-domain.com`

### 2. 项目配置

- `miniapp/src/manifest.json` 中填入微信 AppID
- `backend/app/config.py` 中设置 `WX_APPID` 和 `WX_SECRET`

### 3. 网络适配

小程序已内置以下网络适配机制：
- 请求自动重试（默认 3 次）
- 离线缓存待提交（网络恢复后自动重试）
- X-Session-Token 认证

---

## 许可证

本项目为私有项目，版权归建设方所有。
