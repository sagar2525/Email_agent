📧 Nexus: Prompt-Driven Email Productivity Agent

Nexus is an intelligent, AI-powered email assistant designed to solve inbox overload using a Prompt-Driven Architecture. Unlike traditional filters, Nexus uses Google's Gemini 2.5 Flash model to adaptively categorize emails, extract actionable tasks, and draft replies based on user-defined logic.

🚀 Features

Prompt-Driven Brain: Users can define logic in plain English (e.g., "Mark invoices over $1,000 as High Priority") to control the agent's behavior.

Bulk Async Processing: Utilizes asyncio to batch-process the inbox in a single API call, optimizing for speed and token efficiency.

Context-Aware Copilot (RAG-Lite): The chat interface understands email threads and context, allowing users to query specific details (e.g., "What is the meeting time?").

Safety-First Drafting: The agent generates professional drafts but never sends emails automatically. Drafts are saved to a local SQLite database for review.

Analytics Dashboard: Visualizes inbox health and priority distribution.

📂 Project Structure

email_agent/
├── app.py                # Frontend: Main Streamlit UI application
├── email_service.py      # Backend: Database (SQLite) & Analytics logic
├── llm_brain.py          # Backend: Gemini API integration & Bulk Processing
├── mock_inbox.json       # Asset: High-fidelity mock email dataset
├── requirements.txt      # Dependencies
└── README.md             # Documentation


⚙️ Setup Instructions

1. Prerequisites

Python 3.9 or higher installed.

A Google Gemini API Key (Get one here: Google AI Studio).

2. Installation

Open your terminal in the project folder and install the required dependencies:

pip install -r requirements.txt


(Note: Dependencies include streamlit, pandas, google-generativeai, python-dotenv, and plotly)

3. API Key Configuration

You have two options to configure your API key:

UI Method (Recommended): Enter the key directly in the sidebar when the app launches.

Environment Variable: Create a .env file in the root directory and add:

GOOGLE_API_KEY=your_actual_key_here


🖥️ How to Run

The application uses Streamlit, which runs the UI and backend services simultaneously.

Navigate to the project directory in your terminal.

Run the application:

streamlit run app.py


The application will open automatically in your browser at http://localhost:8501.

📖 Usage Guide

1. How to Load the Mock Inbox

Navigate to the "Smart Inbox" tab.

Click the "Reset / Load Inbox" button.
This will load 20 high-fidelity mock emails (including invoices, security alerts, and threads) into the SQLite database.

2. How to Configure Prompts

The agent's behavior is controlled by the "Agent Brain".

Navigate to the "Agent Brain" tab.

Enter your custom logic into the text areas.

Recommended Configuration for Demo:

Categorization Logic:

Categorize emails into: Work, Personal, Spam, Urgent.
CRITICAL RULES:
1. Mark any email mentioning a dollar amount over $1,000 as "High Priority".
2. Mark any Security Alerts or Fraud warnings as "Critical".
3. Mark emails from "boss@company.com" as "Urgent".


Action Extraction Logic:

Extract specific tasks, deadlines, and financial details.
1. If it is a meeting, extract the date and time.
2. If it is an invoice, extract the exact amount.
3. If it is a security alert, extract the location and card number.


Drafting Persona:

You are a professional Executive Assistant. Be concise, formal, and helpful. Use the email context to fill in facts.


Click "Save Brain Configuration" to apply these rules.

3. How to Process Emails

Return to the "Smart Inbox" tab.

Click "Batch Process (Async)".
The system will pack the emails into a single payload and send them to Gemini.
Once complete (approx. 5-10 seconds), the table will update with Categories, Priorities, and AI Reasoning.

4. Using the Email Agent (Copilot)

Navigate to the "Copilot" tab.

Select an email from the dropdown (e.g., ID 6 - URGENT: Suspicious Activity).

Chat: Type "What is the amount and location?" and click Ask Agent.

Draft:

Switch the mode to "Draft Reply".

Enter instructions: "Draft a professional reply confirming it was me."

Click "Generate Draft".

Review the output and click "Save to Drafts Folder".

🛡️ Safety & Robustness

Rate Limiting: The application uses bulk processing to respect API rate limits.

Error Handling: If the LLM returns invalid JSON, the system defaults to a safe "Error" state rather than crashing.

No Auto-Send: The system is architected to only store drafts. No SMTP integration exists, ensuring safety.
