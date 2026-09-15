# Agent 工程实践 · 12 周学习路线

中文自学课程网站，包含准备课、12 周课程、73 个知识点、22 张概念图、22 个 Python 示例、按日任务、验收与官方参考资料。

## 文件

- `dist/index.html`、`style.css`、`app.js`：响应式阅读界面与按周导航。
- `content/course.py`：课程内容与示例的单一数据源。
- `dist/course.js`：生成的课程数据。
- `content/diagrams.py`：概念图的 SVG 生成与知识点挂接。
- `dist/diagrams/`：22 张流程、结构、时序和边界图，附读图说明。
- `dist/examples/`：逐周源代码、运行说明、依赖和 ZIP。
- `dist/examples.zip`：完整代码包。

修改课程后运行 `python content/course.py`，生成网页数据与下载包。网站为静态资源，无需 Node 依赖与后端密钥。

## 验证范围

在 Python 3.12 中运行标准库与 Pydantic 示例、FastMCP 客户端、LangGraph 状态与审批、Chroma 显式向量示例、SQLite 记忆与幂等、离线 RAG/角色协作、评估及交付测试。FastAPI 使用 ASGI 客户端验证鉴权、输入校验、SSE 事件与槽位释放。

Langfuse 与 Ragas 检查了导入与接口构造。Ragas 0.4.3 需要本课程锁定的 langchain-community 0.3.31 兼容组合。真实 API、外部平台写入、embedding 权重下载及 Docker 运行未在本次验证中执行。

网页进行了 JavaScript 语法、所有周内容渲染、下载链接、源代码一致性及 ZIP 完整性检查；未进行浏览器视觉测试。

依赖范围与实际运行限制在各周 README 中说明。所有 fixture 输出仅用于机制验证，不代表真实模型效果。

## 本地预览

```bash
git clone https://github.com/a-persimmons/agent-engineering-12-week.git
cd agent-engineering-12-week
python content/course.py
python scripts/check_site.py
python -m http.server 8000 --directory dist
```

打开 http://localhost:8000。构建只需要 Python 3.12 的标准库，无需安装课程示例依赖。运行各周 Python 示例时，再按该周 README 安装依赖。

## GitHub Pages 自动部署

工作流：`.github/workflows/pages.yml`。每次推送到 `main` 自动生成课程数据、22 张 SVG 配图和全部 Python 下载包，校验后发布 `dist`；也可在 Actions 中手动执行 **Deploy GitHub Pages → Run workflow**。

新仓库需一次性打开 **Settings → Pages → Build and deployment → Source → GitHub Actions**。如果首次工作流在 Set up Pages 处提示找不到 Pages，请先完成此设置，再在 Actions 中重跑失败的工作流。

部署成功后的地址：https://a-persimmons.github.io/agent-engineering-12-week/

生成的课程数据、SVG 与 ZIP 不重复提交，由 `content/course.py` 和 `content/diagrams.py` 统一生成。页面使用相对资源路径，支持 GitHub Pages 的仓库子路径。

修改课程请编辑 `content/course.py`，修改配图请编辑 `content/diagrams.py`；修改界面请编辑 `dist/index.html`、`dist/style.css`、`dist/app.js`。提交这些源文件即可更新网站。
