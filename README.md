# 📧 Nexus: Prompt-Driven Email Productivity Agent

**Nexus** is an intelligent, AI-powered email assistant designed to solve inbox overload. Unlike traditional email filters that use rigid rules (e.g., "if subject contains 'sale'"), Nexus uses a **Prompt-Driven Architecture** powered by Google Gemini 1.5.

This allows users to define logic in plain English (e.g., "Flag emails about Project Titan as Urgent"), making the agent highly adaptable without changing a single line of code.

---

## 🚀 Features

### 1. 🧠 Prompt-Driven "Brain"
* **Customizable Logic:** Users can edit the "Categorization," "Action Extraction," and "Drafting" prompts in real-time.
* **Persistent State:** Prompts are saved in a local SQLite database, so the agent "remembers" your preferences.

### 2. ⚡ High-Performance Ingestion
* **Bulk Processing:** Utilizes `asyncio` to batch-process emails in a single API call, bypassing rate limits and reducing latency by 90%.
* **Robust Parsing:** Includes self-healing JSON parsers to handle LLM outputs gracefully.

### 3. 🤖 Context-Aware Copilot (RAG-Lite)
* **Thread Awareness:** The chat agent reads the entire email thread, not just the current message, providing accurate context (e.g., "What was the budget mentioned in the previous email?").
* **Safe Drafting:** Generates professional email replies based on user instructions but **never** sends them automatically. Drafts are saved to a local database for review.

### 4. 📊 Analytics Dashboard
* Visualizes inbox health, priority distribution, and category breakdowns using interactive Plotly charts.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit (Python)
* **AI Model:** Google Gemini 1.5 Flash (via `google-generativeai`)
* **Database:** SQLite (Embedded, no setup required)
* **Visualization:** Plotly
* **Async Processing:** Python `asyncio`

---

## ⚙️ Setup Instructions

### Prerequisites
* Python 3.9 or higher
* A Google Gemini API Key (Get one [here](https://aistudio.google.com/app/apikey))

### 1. Installation
Clone the repository and install the dependencies:

```bash
pip install -r requirements.txt
