# AI Business Operations Platform
> **Agentic AI-Powered Autonomous Business Operations & Multi-Agent Orchestration Platform**  
> Built with **React 18 + TypeScript + Vite + Tailwind CSS**, orchestrated via **LangGraph & Python FastAPI**, integrated with **Google Gemini LLM**, and persisted with **PostgreSQL / SQLAlchemy**.

---

## 1. Executive Summary & Purpose

The **AI Business Operations Platform** is an enterprise-grade private SaaS platform that automates core business workflows using specialized autonomous AI agents. Unlike standard chatbots or simple CRUD dashboards, this system features a centralized **AI Orchestrator** capable of deconstructing natural-language business directives into multi-agent task graphs, executing approved scoped tools, and enforcing **Human-in-the-Loop (HITL)** manager authorization for sensitive operational decisions.

---

## 2. Multi-Agent Architecture

```
                       ┌────────────────────────────────────────────────────────┐
                       │               React 18 + Vite Frontend                 │
                       │   (Command Center, Live Pipeline Graph, Approvals)     │
                       └──────────────────────────┬─────────────────────────────┘
                                                  │ REST APIs (/api/v1) + JWT
                                                  ▼
                       ┌────────────────────────────────────────────────────────┐
                       │                  FastAPI Backend Server                │
                       │          (Security, RBAC, Routers & Lifespan)          │
                       └──────────────────────────┬─────────────────────────────┘
                                                  │
                                                  ▼
                        ┌──────────────────────────────────────────────────────┐
                        │      LangGraph Multi-Agent Orchestration Engine      │
                        │    (Planner ➔ Finance ➔ Support ➔ RAG ➔ Report)      │
                        └──────────┬───────────────────────────────┬───────────┘
                                   │                               │
                                   ▼                               ▼
       ┌──────────────────────────────────────────────┐  ┌───────────────────────────────────┐
       │         Specialized Agent Workers            │  │  Human-in-the-Loop (HITL) Policy  │
       ├──────────────────────────────────────────────┤  ├───────────────────────────────────┤
       │ - Task Planning Agent (Task Graphs)          │  │ Pauses state execution when       │
       │ - Finance Agent (Sales & Anomaly Detection)  │  │ high-risk actions are triggered.  │
       │ - Customer Support Agent (SLA & Sentiment)   │  │ Requires manager sign-off before  │
       │ - Document RAG Agent (Vector Retrieval)      │  │ funds disbursement or emails.     │
       │ - Executive Reporting Agent (Markdown/HTML)  │  └───────────────────────────────────┘
       └───────────────────────┬──────────────────────┘
                               │
                               ▼
       ┌───────────────────────────────────────────────────────────────────────┐
       │                      Relational Database Layer                        │
       │     PostgreSQL / SQLite ORM (Workflows, Approvals, Chunks, Audit)     │
       └───────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Layer | Technologies | Role / Responsibility |
| :--- | :--- | :--- |
| **Frontend** | **React 18, TypeScript, Vite** | Fast, responsive Single Page Application (SPA). |
| **Styling & UI** | **Tailwind CSS, Lucide Icons, Recharts** | Modern dark-themed dashboard, pipeline visualization & analytics. |
| **Backend API** | **Python 3.10+, FastAPI, Uvicorn** | High-performance asynchronous REST API. |
| **Orchestration**| **LangGraph / Python StateGraph** | State persistence, conditional branching & multi-agent routing. |
| **LLM Engine** | **Google Gemini API** (`gemini-2.5-flash`) | Natural language understanding & structured JSON schemas. |
| **Database ORM** | **SQLAlchemy 2.0 & Alembic** | Schema relationships, transactions & migrations. |
| **Database** | **PostgreSQL (pgvector)** / SQLite | Persistent transactional data, vector chunks, and audit logs. |
| **Security** | **JWT (HS256) & Passlib (Bcrypt)** | Strict Role-Based Access Control (`Admin`, `Manager`, `Employee`). |

---

## 4. Live demo (LinkedIn / recruiters)

Host the whole app as **one public URL** (React UI + API together) on [Render](https://render.com):

1. Push this repo to GitHub (already at `geesaraserasinghe09/AI-business-operations-platform`).
2. Open [Render New Blueprint](https://dashboard.render.com/select-repo?type=blueprint), sign in with GitHub, and select this repository.
3. Apply the `render.yaml` blueprint (free web service). After the first build, Render prints a URL like `https://ai-business-operations-platform.onrender.com`.
4. Share that URL. On the login screen, use **Instant Demo Account Sign-In** (Admin / Manager / Employee).

The first request after idle time can take ~30–60 seconds (free tier sleep). Demo data is seeded automatically. Optional: set `GEMINI_API_KEY` and `LLM_PROVIDER=gemini` in Render for live LLM calls; otherwise the built-in mock agents still run a full workflow demo.

---

## 5. Quick Start Commands (Frontend & Backend)

Use the table below to start both servers locally:

| Component | Directory | Activation & Run Commands | Default URL |
| :--- | :--- | :--- | :--- |
| **Backend** | `backend/` | `.\venv\Scripts\Activate.ps1`<br>`uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` | `http://localhost:8000/docs` |
| **Frontend** | `frontend/` | `npm run dev` | `http://localhost:5173` |

### Step-by-Step Local Setup

#### Terminal 1 — Start Backend:
```powershell
cd "backend"
.\venv\Scripts\Activate.ps1
# (First time only) Initialize & seed demo data:
python -m app.db.init_db
python -m app.db.seed_data
# Run server:
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 — Start Frontend:
```powershell
cd "frontend"
npm install
npm run dev
```

---

## 6. Pre-Configured Demo Accounts

| Role | Email | Password | Permissions & Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@operations.ai` | `admin123` | Full system control, user management, agent toggle, audit trails. |
| **Manager** | `manager@operations.ai` | `manager123` | Workflow supervision, **Human-in-the-Loop approvals**, executive reports. |
| **Employee**| `employee@operations.ai` | `employee123` | Submit business directives, inspect personal tasks, upload documents. |

---

## 7. How the System Works & Connects

### End-to-End Execution Flow
1. **User Interaction (Frontend):** An employee or manager submits a directive (e.g., *"Analyze sales data, audit open customer tickets, and prepare an executive report"*) via the **AI Command Center**.
2. **API Communication:** The frontend sends an authenticated HTTP `POST` request with a **JWT Bearer Token** via Axios to `/api/v1/workflows`.
3. **AI Task Decomposition:** The central **Task Planner Agent** analyzes the request and dynamically constructs a task dependency graph containing Finance, Support, and Reporting steps.
4. **Autonomous Agent Execution:**
   - **Finance Agent:** Executes read-only queries against `sales_records` to calculate revenue and isolate anomalies.
   - **Customer Support Agent:** Analyzes `support_tickets` for sentiment and identifies critical SLA breach risks.
5. **Human-in-the-Loop (HITL) Checkpoint:** If an agent flags a high-risk action (such as an automated customer email or financial refund), the orchestrator **halts workflow execution** and enters the `waiting_for_human` state.
6. **Manager Authorization:** The manager inspects the AI rationale and payload on the **Approvals** page and authorizes the action.
7. **Synthesis & Reporting:** The workflow resumes, triggers the **Reporting Agent**, and synthesizes an executive Markdown/HTML briefing report available for immediate inspection and download.
8. **Audit Trail:** Every action, decision note, and state transition is permanently recorded in the `activity_logs` table for enterprise compliance.

---

## 8. License
Licensed under the [MIT License](LICENSE).



2️⃣ LinkedIn Post එක සඳහා 


🚀 Excited to showcase my latest project: AI Business Operations Platform — an Enterprise-Grade Multi-Agent AI System! 🤖🏢

Unlike standard conversational chatbots or simple CRUD dashboards, this platform is an Autonomous Agentic AI Operations System designed to orchestrate and execute real-world enterprise workflows with built-in safety guardrails.

✨ Key Architectural Highlights:
🔹 Multi-Agent Orchestration (LangGraph): Autonomous coordination between specialized agents (Task Planner, Finance Analytics, Customer Support & SLA Monitoring, Document RAG, and Executive Reporting).
🔹 Human-in-the-Loop (HITL) Checkpoints: Strict safety policies ensuring high-risk actions (financial adjustments, official client emails) pause execution and require authenticated manager authorization before proceeding.
🔹 Hybrid Document RAG: Semantic vector search + lexical retrieval allowing employees to query internal business policies and contracts directly.
🔹 Enterprise Security & RBAC: Role-Based Access Control (Admin, Manager, Employee) enforced via JWT bearer authentication and immutable audit logging.

🛠️ Tech Stack:
• Frontend: React 18, TypeScript, Vite, Tailwind CSS, Recharts
• Backend: Python, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic
• AI / LLM: LangGraph, Google Gemini API (with deterministic offline fallback)
• Database: PostgreSQL (with pgvector support) / SQLite

Always excited about building scalable, secure, and production-ready AI agent systems! Let me know your thoughts in the comments. 👇

#ArtificialIntelligence #AI #GenerativeAI #LangGraph #FastAPI #ReactJS #FullStackDevelopment #MachineLearning #EnterpriseAI #Python #SoftwareEngineering