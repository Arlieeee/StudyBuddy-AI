# StudyBuddy AI 智能学习伴侣 🎓

StudyBuddy AI 是一个集成了 **RAG (检索增强生成)**、**多模态生成 (Gemini 3.0)** 和 **智能推荐系统** 的全栈 AI 学习助手。它旨在帮助用户更高效地理解复杂的学习资料，通过对话问答和知识可视化图解（思维导图、流程图）来辅助学习。

![Gemini 3](https://img.shields.io/badge/Gemini-3%20Flash-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)
![React](https://img.shields.io/badge/React-18-61dafb)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

![StudyBuddy Preview](/img/preview.png)

## 🚀 核心功能

### 1. 📚 智能文档问答 (Chat Mode)
- **文档上传与解析**：支持 PDF、PPTX、DOCX、TXT 等多种格式文档上传。
- **RAG 检索增强**：基于 ChromaDB 向量数据库，精准检索文档片段，回答从摘要到细节的各类问题。
- **上下文感知**：支持多轮对话，能够根据上下文进行深入探讨。
- **公式支持**：完美支持 LaTeX 数学公式渲染。

### 2. 🎨 知识可视化图解 (Visualization Mode)
- **多风格图解生成**：
    - **🗺️ 思维导图**：梳理知识结构和层级。
    - **📊 流程图**：解析算法步骤或时间线。
    - **📖 知识图谱**：展示概念间的关联。
- **RAG 驱动生成**：结合文档内容和用户指令，由 Gemini 3.0 先“思考”规划内容，再生成高质量图解。
- **高清预览与下载**：支持全屏预览和高清图片下载。

### 3. 💡 智能推荐系统 (Smart Recommendations)
- **双模式推荐**：
    - **图解模式**：自动分析文档核心概念，推荐适合可视化的主题（如"第三章核心概念对比"）。
    - **对话模式**：根据文档内容生成"复习提问"、"关键概念解释"等引导性问题。
- **即时响应**：点击推荐气泡即可自动填充并发送指令。
- **智能截断**：前端优化长文本处理，确保生成指令精准且节省 Token。

### 4. 🛠️ 现代化交互体验
- **极简 UI 设计**：清爽的亮色主题，类似现代 chat 界面。
- **流式响应**：实时显示 AI 思考过程和生成进度。
- **Markdown 支持**：丰富的文本格式渲染。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- uv (Python 包管理器)
- Google Gemini API Key

### 1. 克隆项目
```bash
git clone https://github.com/Arlieeee/StudyBuddy-AI.git
cd StudyBuddy-AI
```

### 2. 后端启动
```bash
cd backend
# 1. 创建并激活虚拟环境 (推荐使用 uv)
uv venv .venv
.venv\Scripts\activate

# 2. 安装依赖
uv pip install -r requirements.txt

# 3. 配置环境变量
# 复制 .env.example 为 .env
cp .env.example .env

# ⚠️ 重要: 请务必在 .env 文件中填入您自己的 Google Gemini API Key
# 获取地址: https://aistudio.google.com/app/apikey
# GOOGLE_API_KEY=your_api_key_here

# 4. 启动服务 (默认端口 8001)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### 3. 前端启动
```bash
cd frontend
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```


### 访问应用
- 前端界面：http://localhost:5173
- API 文档：http://localhost:8001/docs

## 🧩 项目结构
```
StudyBuddy-AI/
├── backend/
│   ├── app/
│   │   ├── models/       # Pydantic 数据模型
│   │   ├── routers/      # API 路由定义 (generate, qa, recommendations)
│   │   ├── services/     # 核心业务逻辑 (rag, image, gemini, recommendation)
│   │   └── main.py       # 程序入口
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── assets/       # 静态资源
│   │   ├── App.jsx       # 主应用组件
│   │   ├── App.css       # 全局样式
│   │   ├── ImagePreviewModal.jsx # 图片预览组件
│   │   └── main.jsx
│   └── package.json
└── README.md
```

## 🏗️ 技术架构

### 后端 (Backend)
- **框架**: FastAPI (Python)
- **LLM 模型**: Google Gemini 2.0 Flash (文本/推理) / Gemini 3.0 Pro (图像生成)
- **向量数据库**: ChromaDB (本地持久化存储)
- **文档处理**: PyMuPDF, python-docx, python-pptx
- **依赖管理**: uv (高性能 Python 包管理器)

### 前端 (Frontend)
- **框架**: React + Vite
- **语言**: JavaScript (ES6+)
- **样式**: CSS3 (Variables, Flexbox/Grid)
- **组件库**: 轻量级组件 (无需重型 UI 库)
- **Markdown**: react-markdown, remark-gfm, rehype-katex

## ⚠️ 注意事项
- **API 配额**：项目使用 Google Gemini API，请确保账号有足够配额。
- **端口配置**：后端默认运行在 8001 端口，如需更改请同步修改前端 `App.jsx` 中的 `API_BASE`。
- **文件存储**：后端默认将上传的文件存储在 `backend/data/uploads` 目录下，如需更改请同步修改前端 `App.jsx` 中的 `API_BASE`。
- **示例文件**：目前文件目录下保存着“计算机系统结构”课程的部分Slides，可供用户直接测试体验

## 🔮 未来计划
- [ ] 用户会话模式，保留历史记录，将RAG独立与当前会话绑定
- [ ] 支持更多文档格式 (Excel, Markdown)
- [ ] 增加用户账户系统与云端同步
- [ ] 引入更多可视化风格 (如手绘风)
- [ ] 多语言支持
- [ ] 引入本地上传的视频、录音、笔记照片多模态解析
- [ ] 接入Bilibili等视频平台API解析复习视频
- [ ] 移动端适配优化

## 📜 License

MIT License
