"""
NurseEdu Chat
Created by: Sachindra
Year: 2025

A modern, interactive chatbot for nursing education using Google's Gemini Pro AI.
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import os
import logging
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)

# Configure PaLM API
genai.configure(api_key=os.getenv('PALM_API_KEY', ''))

SYSTEM_PROMPT = """You are NurseEdu, an engaging and friendly nursing education assistant. Your responses should be:

1. VISUAL AND STRUCTURED:
   - Use emojis appropriately (1-2 per section)
   - Break information into clear sections
   - Use bullet points and numbered lists
   - Include relevant headings

2. INTERACTIVE:
   - Add quick knowledge check questions at the end
   - Include "Did you know?" fun facts
   - Suggest related topics to explore

3. STUDENT-FRIENDLY:
   - Use simple, clear language
   - Provide memorable examples
   - Include mnemonics where helpful
   - Break down complex concepts

4. CLINICAL RELEVANCE:
   - Include real-world applications
   - Share practical tips
   - Reference common clinical scenarios

Format your response with clear sections, using markdown-style formatting:

# Main Topic 🎯
[Brief introduction]

## Key Points 📝
• Point 1
• Point 2
• Point 3

## Clinical Application 👩‍⚕️
[Practical examples]

## Quick Tips 💡
[Easy-to-remember tips]

## Did You Know? 🤔
[Interesting fact]

## Knowledge Check ✅
[1-2 quick questions]

## Want to Learn More? 📚
[Related topics]

Remember to maintain professional accuracy while being engaging and educational."""

def format_response(text):
    # Add emoji to main headings if not present
    text = re.sub(r'^# ([^🎯\n]+)$', r'# \1 🎯', text, flags=re.MULTILINE)
    text = re.sub(r'^## Key Points([^\n]+)$', r'## Key Points 📝', text, flags=re.MULTILINE)
    text = re.sub(r'^## Clinical Application([^\n]+)$', r'## Clinical Application 👩‍⚕️', text, flags=re.MULTILINE)
    text = re.sub(r'^## Quick Tips([^\n]+)$', r'## Quick Tips 💡', text, flags=re.MULTILINE)
    text = re.sub(r'^## Did You Know\?([^\n]+)$', r'## Did You Know? 🤔', text, flags=re.MULTILINE)
    text = re.sub(r'^## Knowledge Check([^\n]+)$', r'## Knowledge Check ✅', text, flags=re.MULTILINE)
    text = re.sub(r'^## Want to Learn More\?([^\n]+)$', r'## Want to Learn More? 📚', text, flags=re.MULTILINE)
    
    # Convert bullet points to HTML
    text = text.replace('•', '●')
    
    return text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']
        logger.debug(f"Received message: {user_message}")
        
        # Check API key
        if not os.getenv('PALM_API_KEY'):
            raise ValueError("Google PaLM API key is not set")
        
        # Get model
        model = genai.GenerativeModel('gemini-pro')
        
        # Combine system prompt with user message
        full_prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nAssistant: Let me help you understand this in an engaging way:\n\n"
        
        logger.debug("Making API request to PaLM...")
        response = model.generate_content(full_prompt)
        logger.debug("Received response from PaLM")
        
        if response.text:
            formatted_response = format_response(response.text)
            return jsonify({
                "response": formatted_response,
                "success": True
            })
        else:
            raise ValueError("No response generated")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in chat endpoint: {error_msg}", exc_info=True)
        return jsonify({
            "error": error_msg,
            "success": False
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5005)
