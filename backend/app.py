# Import the tools we need
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
from pymongo import MongoClient
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["agenthub"]
# Load the .env file (this reads your OPENAI_API_KEY)
load_dotenv('../.env')

# Create the Flask app
app = Flask(__name__)
CORS(app)  # This allows your HTML to talk to this server

# Connect to GROQ
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── AGENT PERSONALITIES ─────────────────────────────────────────
# Each agent gets a unique system prompt that defines its behavior
AGENT_PROMPTS = {
    'Personal AI Assistant': """You are a Personal AI Assistant specialized in
    productivity. Help users with task management, scheduling, reminders,
    and personal organization. Be concise, friendly, and practical.""",

    'Business Workflow': """You are a Business Workflow Automation expert.
    Help businesses automate their processes, improve CRM workflows, generate
    reports, and optimize operations. Be professional and data-driven.""",

    'Content Creator': """You are a Creative Content Generation AI.
    Help users write blogs, social media posts, scripts, ad copy, and creative
    content. Be creative, engaging, and adapt to different tones.""",

    'Data Insights': """You are a Data Analysis and Business Intelligence AI.
    Help users understand their data, identify trends, suggest visualizations,
    and provide analytical insights. Be precise and data-focused.""",

    'Code Assistant': """You are an expert Software Development AI Assistant.
    Help with coding in any language, debugging, code reviews, architecture
    decisions, and documentation. Be technical, clear, and thorough.""",

    'Tutor AI': """You are a Personal AI Tutor. Help students learn any subject,
    explain concepts in simple terms, create quizzes, and guide study plans.
    Be patient, encouraging, and use clear examples.""",

    'Marketing AI': """You are a Marketing and E-commerce AI Agent.
    Help with SEO strategies, ad campaigns, email marketing, content calendars,
    and customer segmentation. Be strategic and results-focused.""",

    'Finance AI': """You are a Financial Advisor AI. Help users with budget
    planning, investment analysis, expense tracking, and financial decisions.
    Provide clear advice with appropriate disclaimers.""",
}

# Default prompt if agent name not in our list
DEFAULT_PROMPT = "You are a helpful AI agent on AgentHub marketplace. Be concise and helpful."


# ── CHAT ROUTE ──────────────────────────────────────────────────
# This is the endpoint your JavaScript calls
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get the data sent from JavaScript
        data = request.get_json()
        agent_name = data.get('agent', 'Assistant')
        user_message = data.get('message', '')
        history = data.get('history', [])

        # Get the right personality for this agent
        system_prompt = AGENT_PROMPTS.get(agent_name, DEFAULT_PROMPT)

        # Build the full message list for OpenAI
        messages = [{ "role": "system", "content": system_prompt }]

        # Add previous messages (so AI remembers conversation)
        # Only keep last 10 messages to save money
        for msg in history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Call OpenAI's GPT-4o-mini (cheap & fast, perfect for hackathon)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=500,         # Limit response length
            temperature=0.7          # 0=boring, 1=creative, 0.7=balanced
        )

        # Extract the AI's reply text
        reply = response.choices[0].message.content

        # Send it back to the browser
        return jsonify({ 'reply': reply })

    except Exception as e:
        # If anything goes wrong, send an error
        return jsonify({ 'reply': f'Error: {str(e)}' }), 500


# ── HEALTH CHECK ─────────────────────────────────────────────
# Visit http://localhost:5000/health to confirm server is running
@app.route('/health', methods=['GET'])
def health():
    return jsonify({ 'status': 'AgentHub backend is running!' })


# ── START THE SERVER ─────────────────────────────────────────
if __name__ == '__main__':
    print("🚀 AgentHub backend starting on http://localhost:5000")
    app.run(debug=True, port=5000)