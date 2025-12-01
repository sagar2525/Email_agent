import google.generativeai as genai
import json
import asyncio

class LLMBrain:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    def _clean_json_response(self, text):
        """Helper to extract JSON from markdown."""
        cleaned = text.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0]
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0]
        return cleaned.strip()

    # ==========================================
    # 1. BULK PROCESSING (For "Smart Inbox" Tab)
    # ==========================================
    async def process_inbox_parallel(self, emails_list, cat_prompt, act_prompt):
        """
        BULK MODE: Sends ALL emails in a SINGLE API request.
        Solves '429 Rate Limit' and is much faster.
        """
        if not emails_list:
            return []

        # Prepare the Bulk Payload
        bulk_text = "INBOX DATA:\n"
        for email in emails_list:
            bulk_text += f"""
            --- EMAIL ID: {email['id']} ---
            From: {email['sender']}
            Subject: {email['subject']}
            Body: {email['body']}
            -------------------------------
            """

        system_instruction = f"""
        You are an elite email productivity agent.
        
        Your Goal: Process the {len(emails_list)} emails provided above.
        
        INSTRUCTIONS:
        1. Categorize using this logic: "{cat_prompt}"
        2. Extract tasks using this logic: "{act_prompt}"
        
        OUTPUT FORMAT:
        Return a SINGLE JSON LIST containing an object for every email.
        Strictly follow this structure:
        [
            {{
                "id": <MATCHING_EMAIL_ID>,
                "reasoning": "Brief explanation",
                "category": "Work/Personal/Spam",
                "priority": "High/Medium/Low",
                "action_items": [ {{ "task": "...", "deadline": "..." }} ]
            }},
            ...
        ]
        """

        try:
            print("Sending bulk request to Gemini...")
            model = genai.GenerativeModel(self.model_name)
            
            # Single API Call
            response = await model.generate_content_async(
                f"{system_instruction}\n\n{bulk_text}"
            )
            
            cleaned_json = self._clean_json_response(response.text)
            parsed_results = json.loads(cleaned_json)
            
            if isinstance(parsed_results, list):
                return parsed_results
            else:
                return []

        except Exception as e:
            print(f"Bulk Processing Failed: {e}")
            return []

    # ==========================================
    # 2. CHAT FUNCTIONS (For "Copilot" Tab)
    # ==========================================
    def chat_with_context(self, current_email_body, thread_emails, user_query):
        """
        Restored Method: Allows RAG-like chat with the email thread.
        """
        model = genai.GenerativeModel(self.model_name)
        
        # Build context from thread history
        context_str = "PREVIOUS EMAILS IN THREAD:\n"
        if isinstance(thread_emails, list):
            for e in thread_emails:
                sender = e.get('sender', 'Unknown')
                body = e.get('body', '')
                context_str += f"- From {sender}: {body[:200]}...\n"
        
        prompt = f"""
        CONTEXT:
        {context_str}
        
        CURRENT EMAIL BODY:
        {current_email_body}
        
        USER QUESTION: {user_query}
        
        Please answer the user's question based strictly on the email context provided.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating chat response: {str(e)}"

    def generate_draft(self, email_body, reply_prompt, user_instructions):
        """
        Restored Method: Generates email drafts.
        """
        model = genai.GenerativeModel(self.model_name)
        
        full_prompt = f"""
        You are a professional email assistant.
        
        YOUR PERSONA/STRATEGY:
        {reply_prompt}
        
        USER INSTRUCTIONS:
        {user_instructions}
        
        INCOMING EMAIL:
        {email_body}
        
        Draft a clear, professional reply based on the persona and instructions.
        """
        
        try:
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            return f"Error generating draft: {str(e)}"