from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import streamlit as st
import os
import google.generativeai as genai
import time
import requests
st.markdown("""
    <style>
    .stApp {
        background: black;
    }
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .assistant-message {
        background: #36454F;
        border-left: 4px solid #2196f3;
    }
    .user-message {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
    .st-emotion-cache-1qg05tj {
        padding: 1rem 1.5rem;
    }
    .stSidebar {
        background: black;
        border-right: 1px solid #e0e0e0;
    }
    .title-text {
        color: #16d0f5;
        font-size: 2.5rem !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    .caption-text {
        color: #636e72 !important;
        font-size: 1.1rem !important;
        text-align: center;
        margin-bottom: 2rem !important;
    }
    .sidebar-header {
        color: #2d3436 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        background: linear-gradient(90deg, #2196f3, #4caf50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stSpinner > div {
        border-color: #2196f3 transparent transparent transparent !important;
    }
    </style>
""", unsafe_allow_html=True)
def generate_plantuml_image(plantuml_code):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get("https://www.plantuml.com/")
        textarea = driver.find_element(By.ID, "inflated")
        textarea.clear()
        textarea.send_keys(plantuml_code)
        time.sleep(3)

        png_url_element = driver.find_element(By.ID, "url")
        png_url = png_url_element.get_attribute("value") 

        if png_url.startswith("//"):
            png_url = "https:" + png_url

        return png_url
    
    finally:
        driver.quit()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("API key is missing. Set the GOOGLE_API_KEY environment variable.")
else:
    genai.configure(api_key=API_KEY)

icons = {"assistant": "robot.png", "user": "user.png"}

model = genai.GenerativeModel('gemini-1.5-flash-latest')

prompt = """You are SkilFlo AI, a programming teaching assistant created by Akshat, an AI enthusiast.  
Your role is to generate a concise **PlantUML code for a roadmap (under 100 words)** for any programming-related topic provided by the user.  

### Guidelines:  
1. **Respond ONLY with valid PlantUML code** that visualizes a structured learning roadmap.  
2. The roadmap must be **brief (less than 100 words)** while maintaining clarity.  
3. If the user's input is **not** related to programming or coding or technical topics, respond with:  
   _"Please enter a technical topic name to generate a roadmap."_  
4. You may answer **basic greetings** like 'Who are you?' or 'Who created you?'.  

### Context:  
**Previous Chat History:**  
{chat_history}  

### User Input:  
**Human:** {human_input}  
**Chatbot:**"""

def get_response(query):
    previous_response = ""
    
    for chat in st.session_state.get('history', []):
        previous_response += f"Human: {chat[0]}\nChatbot: {chat[1]}\n"

    response = model.generate_content(prompt.format(human_input=query, chat_history=previous_response))
    response_text = response.text if hasattr(response, "text") else "Error: No response received."
    
    st.session_state['history'].append((query, response_text))
    return response_text

def response_streaming(text):
    for char in text:
        yield char
        time.sleep(0.001)

st.markdown('<p class="title-text">🌊 SkilFlo AI</p>', unsafe_allow_html=True)
st.markdown('<p class="caption-text">Your Visual Roadmap Generator for Tech Mastery 🚀</p>', unsafe_allow_html=True)

st.sidebar.markdown('<p class="sidebar-header">ABOUT</p>', unsafe_allow_html=True)
with st.sidebar.expander("📌 What can SkilFlo AI do?", expanded=True):
    st.markdown("""
    - 🗺️ Generate visual learning roadmaps
    - 🎯 Create structured skill development paths
    - 📈 Suggest optimal learning sequences
    - 💡 Recommend essential resources
    """)

st.sidebar.markdown('<p class="sidebar-header">CREATOR</p>', unsafe_allow_html=True)
st.sidebar.success("""
**Built with ❤️ by [Akshat😎](https://github.com/akshat-shah-2003)**  
🔗 [Contact Me](mailto:akshats1607@gmail.com)  
🐙 [Contribute on GitHub](https://github.com/)
""")

if 'messages' not in st.session_state:
    st.session_state.messages = [{'role': 'assistant', 'content': "I'm here to guide you master a technical skill! 😉"}]
if 'history' not in st.session_state:
    st.session_state.history = []

for message in st.session_state.messages:
    custom_class = "assistant-message" if message['role'] == 'assistant' else "user-message"
    with st.chat_message(message['role'], avatar=icons.get(message['role'])):
        st.markdown(f'<div class="{custom_class}">{message["content"]}</div>', unsafe_allow_html=True)

user_input = st.chat_input("Enter your topic 👉..")
if user_input:
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    with st.chat_message("user", avatar=icons["user"]):
        st.write(user_input)

    with st.spinner("Generating Roadmap..."):
        image_url = generate_plantuml_image(get_response(user_input).replace("```", "").replace("plantuml", ""))
    
    if image_url:
        image_data = requests.get(image_url).content
        with st.chat_message("assistant", avatar=icons["assistant"]):
            st.image(image_data, caption="Generated Roadmap", use_container_width=True)
    else:
        st.session_state.messages.append({"role": "assistant", "content": "Error: No image found."})
        with st.chat_message("assistant", avatar=icons["assistant"]):
            st.write("Error: Unable to generate image.")
