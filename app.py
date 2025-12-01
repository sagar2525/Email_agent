import streamlit as st
import pandas as pd
import asyncio
import plotly.express as px
import os
from dotenv import load_dotenv
from email_service import EmailService
from llm_brain import LLMBrain

load_dotenv()

st.set_page_config(page_title="Nexus Email Agent", layout="wide", page_icon="⚡")

# Custom CSS for "Pro" look
st.markdown("""
<style>
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 5px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Services Init
if 'db' not in st.session_state:
    st.session_state.db = EmailService()

# Sidebar
with st.sidebar:
    st.title("⚡ Nexus Agent")
    api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GOOGLE_API_KEY", ""))
    if not api_key:
        st.warning("API Key required")
        st.stop()
        
    st.divider()
    st.markdown("### System Status")
    emails = st.session_state.db.get_all_emails()
    processed_count = len(emails[emails['category'] != 'Unprocessed']) if not emails.empty else 0
    st.metric("Emails Ingested", len(emails))
    st.metric("AI Processed", processed_count)

llm = LLMBrain(api_key)

# Main Navigation
tab_dash, tab_inbox, tab_brain, tab_agent = st.tabs(["📊 Analytics Dashboard", "📥 Smart Inbox", "🧠 Agent Brain", "🤖 Copilot"])

# --- TAB 1: DASHBOARD (The "Unique" Factor) ---
with tab_dash:
    st.header("Inbox Analytics")
    if emails.empty:
        st.info("Load data in the Inbox tab to see analytics.")
    else:
        col1, col2 = st.columns(2)
        stats = st.session_state.db.get_stats()
        
        with col1:
            st.subheader("Category Distribution")
            if not stats.empty:
                fig = px.pie(stats, values='count', names='category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Priority Heatmap")
            if not stats.empty and 'priority' in stats.columns:
                fig2 = px.bar(stats, x='category', y='count', color='priority', barmode='group')
                st.plotly_chart(fig2, use_container_width=True)

# --- TAB 2: SMART INBOX (The "Efficient" Factor) ---
with tab_inbox:
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🔄 Reset / Load Inbox"):
            st.session_state.db.load_mock_data("mock_inbox.json")
            st.rerun()
            
    with col2:
        if st.button("⚡ Batch Process (Async)"):
            unprocessed = emails[emails['category'] == 'Unprocessed']
            if unprocessed.empty:
                st.success("All emails processed!")
            else:
                with st.spinner(f"Parallel processing {len(unprocessed)} emails..."):
                    # Convert DF to list of dicts
                    batch_data = unprocessed.to_dict('records')
                    
                    # Fetch Prompts
                    cat_p = st.session_state.db.get_prompt("categorization", "Categorize: Work, Spam, Personal.")
                    act_p = st.session_state.db.get_prompt("action_extraction", "Extract tasks.")
                    
                    # ASYNC RUN
                    results = asyncio.run(llm.process_inbox_parallel(batch_data, cat_p, act_p))
                    
                    # Bulk Save
                    st.session_state.db.bulk_update_emails(results)
                    st.success("Processing Complete!")
                    st.rerun()

    # Modern Grid Display
    if not emails.empty:
        # Style the dataframe (Highlight High priority)
        def highlight_priority(val):
            color = '#ffcccb' if val == 'High' else ''
            return f'background-color: {color}'

        display_df = emails[['id', 'subject', 'category', 'priority', 'sender']].copy()
        st.dataframe(display_df.style.applymap(highlight_priority, subset=['priority']), use_container_width=True)

# --- TAB 3: AGENT BRAIN ---
with tab_brain:
    st.header("Configure Agent Logic")
    col1, col2 = st.columns(2)
    with col1:
        cat_val = st.text_area("Categorization Logic", value=st.session_state.db.get_prompt("categorization", "Categorize emails into: Work, Spam, Urgent."))
    with col2:
        act_val = st.text_area("Action Extraction Logic", value=st.session_state.db.get_prompt("action_extraction", "Extract tasks with deadlines."))
    
    reply_val = st.text_area("Drafting Persona", value=st.session_state.db.get_prompt("auto_reply", "You are a professional executive assistant. Be concise."))
    
    if st.button("Save Brain Configuration"):
        st.session_state.db.save_prompt("categorization", cat_val)
        st.session_state.db.save_prompt("action_extraction", act_val)
        st.session_state.db.save_prompt("auto_reply", reply_val)
        st.toast("Configuration Saved", icon="✅")

# --- TAB 4: COPILOT (The "Robust" Factor) ---
with tab_agent:
    st.header("Context-Aware Email Assistant")
    
    if emails.empty:
        st.warning("Inbox empty.")
    else:
        # Selection
        selected_id = st.selectbox("Select Email:", emails['id'].tolist(), format_func=lambda x: f"ID {x} - {emails[emails['id']==x]['subject'].values[0]}")
        
        email_row = emails[emails['id'] == selected_id].iloc[0]
        
        # Thread Awareness
        thread_emails = st.session_state.db.get_thread(email_row['thread_id']).to_dict('records')
        
        col_left, col_right = st.columns([1, 1])
        
        with col_left:
            st.markdown("### 📧 Current Email")
            st.info(f"**From:** {email_row['sender']}\n\n{email_row['body']}")
            
            if len(thread_emails) > 1:
                with st.expander(f"View Thread ({len(thread_emails)} msgs)"):
                    for msg in thread_emails:
                        st.caption(f"{msg['timestamp']} - {msg['sender']}")
                        st.text(msg['body'][:50] + "...")
                        st.divider()

        with col_right:
            st.markdown("### 🤖 Actions")
            action_mode = st.radio("Mode:", ["Chat with Thread", "Draft Reply"], horizontal=True)
            
            if action_mode == "Chat with Thread":
                user_q = st.text_input("Ask about this thread:")
                if st.button("Ask Agent"):
                    resp = llm.chat_with_context(email_row['body'], thread_emails, user_q)
                    st.markdown(resp)
            
            elif action_mode == "Draft Reply":
                instr = st.text_input("Instructions (e.g. 'Decline politely'):")
                if st.button("Generate Draft"):
                    persona = st.session_state.db.get_prompt("auto_reply")
                    draft = llm.generate_draft(email_row['body'], persona, instr)
                    st.text_area("Draft Result:", value=draft, height=200)
                    st.button("Save to Drafts Folder")