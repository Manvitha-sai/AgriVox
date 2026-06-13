import streamlit as st
from PIL import Image
import os
import google.generativeai as genai
from gtts import gTTS
import tempfile
import requests
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu 
from streamlit_cropper import st_cropper 
import time
import json 
import pandas as pd 
from datetime import datetime 
import base64
from io import BytesIO

# ==========================================
# 1. PAGE SETUP & EXTERNAL CSS
# ==========================================
st.set_page_config(page_title="AgriVox | Smart Farming", page_icon="🌿", layout="wide")

# Function to load external CSS
def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Styling file '{file_name}' not found. Please create it for the premium UI.")

# Load the CSS file (Ensure style.css is in the same folder!)
local_css("style.css")

@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

lottie_scanning = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_njghytle.json")

# ==========================================
# 2. SECRETS & HELPERS
# ==========================================
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except (KeyError, FileNotFoundError):
    GEMINI_API_KEY = None
    st.error("❌ API Key not found! Please make sure you have a .streamlit/secrets.toml file with GEMINI_API_KEY='your_key_here'")

LANGUAGES = ["English", "Hindi", "Telugu", "Tamil", "Kannada", "Malayalam", "Marathi", "Bengali", "Gujarati", "Punjabi", "Odia"]
LANG_MAP = {"English": "en", "Hindi": "hi", "Telugu": "te", "Tamil": "ta", "Kannada": "kn", "Malayalam": "ml", "Marathi": "mr", "Bengali": "bn", "Gujarati": "gu", "Punjabi": "pa", "Odia": "or"}
HISTORY_FILE = "scan_history.csv" 

if 'latest_disease' not in st.session_state:
    st.session_state['latest_disease'] = None


# 🚨 NEW: Helper function to convert image to text for the CSV
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# 🚨 UPDATED: Now accepts the 'image' variable
def save_to_history(plant, disease, confidence, is_healthy, image):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    status = "Healthy" if is_healthy else "Disease Detected"
    
    # Convert the cropped image to a base64 string
    img_base64 = image_to_base64(image)
    
    new_data = pd.DataFrame([{
        "Preview": img_base64,  # <-- Adds the image column first!
        "Date & Time": timestamp, 
        "Plant": plant, 
        "Diagnosis": disease, 
        "Confidence": f"{confidence:.1f}%", 
        "Status": status
    }])
    
    if os.path.exists(HISTORY_FILE):
        new_data.to_csv(HISTORY_FILE, mode='a', header=False, index=False)
    else:
        new_data.to_csv(HISTORY_FILE, index=False)


# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.markdown("<br><h2 style='text-align: center; color: #0F4C3A; font-weight: 800;'>🌿 AgriVox</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5C7765; margin-top: -15px;'>Smart Diagnostics</p>", unsafe_allow_html=True)
    st.write("---")
    
    selected = option_menu(
        menu_title=None, 
        options=["Home", "Dashboard", "Treatment & Audio", "History Log", "AI Chatbot"], 
        icons=["house", "camera", "volume-up", "clock-history", "robot"], 
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#1A5D1A", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"5px 0px", "border-radius":"10px", "color":"#4A5568"},
            "nav-link-selected": {"background": "linear-gradient(135deg, #1A5D1A 0%, #2D8A4E 100%)", "color": "white", "icon-color": "white", "box-shadow": "0 4px 10px rgba(26,93,26,0.2)"},
        }
    )

# ==========================================
# 4. APP ROUTING
# ==========================================

# --- HOME ---
if selected == "Home":
    st.markdown("<br><h1 style='text-align: center; font-size: 4rem; margin-bottom: 0;'>🌾 AgriVox</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.5rem; color: #5C7765;'>Next-Generation Crop Intelligence</p>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🌟 Why Choose AgriVox?")
        st.markdown("""
        <div style="font-size: 1.1rem; line-height: 1.8; color: #4A5568;">
        <b>✨ Advanced Multimodal AI:</b> Powered by Gemini 2.5 Flash.<br>
        <b>🎯 Precision Cropping:</b> Isolate diseases for maximum accuracy.<br>
        <b>🌍 Multilingual Audio:</b> Treatment plans in 11 local languages.<br>
        <b>📊 Data Analytics:</b> Cloud-ready scan history and logging.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        lottie_plant = load_lottieurl("https://lottie.host/801a24d5-8ef6-4d0d-bda8-566b6e4e5b31/f0zGf3sWMy.json")
        if lottie_plant: st_lottie(lottie_plant, height=350, key="plant")

# --- DASHBOARD ---
elif selected == "Dashboard":
    st.title("Scanner Dashboard")
    st.markdown("##### 📸 Upload or snap a photo of a leaf to begin.")
    st.write("---")

    crop_choice = st.selectbox("Select Crop Type Context:", [
        "Tomato 🍅", "Pepper / Chili 🌶️", "Potato 🥔", "Cotton 🌿",
        "Corn / Maize 🌽", "Wheat 🌾", "Rice 🍚", "Apple 🍎",
        "Grape 🍇", "Citrus (Lemon/Orange) 🍋", "Other / Unknown 🪴"
    ])

    st.write("") 

    tab1, tab2 = st.tabs(["📁 Upload Image", "📸 Camera"])
    with tab1: uploaded_file = st.file_uploader("Drag and drop your specimen here...", type=["jpg", "jpeg", "png", "bmp"])
    with tab2: camera_photo = st.camera_input("Snap a picture")

    source_image = camera_photo if camera_photo is not None else uploaded_file

    if source_image is not None:
        st.write("---")
        st.markdown("#### ✂️ Isolate the Symptom")
        raw_image = Image.open(source_image).convert('RGB')
        
        # Interactive Cropper
        cropped_image = st_cropper(raw_image, realtime_update=True, box_color='#1A5D1A', aspect_ratio=None)
        st.write("---")
        
        col_img, col_res = st.columns([1, 1.2])
        with col_img:
            st.image(cropped_image, caption='Final Analysis Sample', use_container_width=True, clamp=True)
            analyze_btn = st.button('🔍 Run AI Diagnostics', use_container_width=True)
            
        with col_res:
            if analyze_btn:
                if not GEMINI_API_KEY:
                    st.error("Missing Gemini API Key!")
                else:
                    with st.spinner(""):
                        lottie_placeholder = st.empty()
                        with lottie_placeholder.container():
                            if lottie_scanning is not None: st_lottie(lottie_scanning, height=150)
                            st.markdown("<p style='text-align: center; color: #1A5D1A; font-weight: bold;'>AgriVox Vision Engine Active...</p>", unsafe_allow_html=True)
                        
                        try:
                            vision_model = genai.GenerativeModel('gemini-2.5-flash')
                            
                            # 🚨 NEW: Dynamic Context Logic
                            if "Unknown" in crop_choice:
                                context_instruction = "The farmer does not know what type of plant this is. Please attempt to identify the plant family/species, and then diagnose the specific disease based solely on visual symptoms."
                            else:
                                context_instruction = f"The farmer has indicated this crop is likely: {crop_choice}. Use this context to confidently guide your specific diagnosis."

                            # The main prompt using our dynamic instruction
                            prompt = f"""
                            You are an expert agronomist. Analyze this image.
                            {context_instruction}

                            CRITICAL RULE 1: If it is NOT a plant, leaf, or crop, set "is_plant" to false.
                            CRITICAL RULE 2: Do NOT use generic terms. Identify the highly specific disease type.

                            Return ONLY valid JSON with exactly these 6 keys (do not wrap in markdown):
                            "is_plant": (boolean), "plant_name": (string), "diagnosis": (string), "confidence": (number), "is_healthy": (boolean), "reasoning": (string).
                            """
                            
                            try:
                                response = vision_model.generate_content([cropped_image, prompt], generation_config={"temperature": 0.1, "response_mime_type": "application/json"})
                            except Exception as e:
                                if "429" in str(e) or "Quota" in str(e):
                                    st.warning("⏳ Google limits reached. Retrying in 60s...")
                                    time.sleep(60) 
                                    response = vision_model.generate_content([cropped_image, prompt], generation_config={"temperature": 0.1, "response_mime_type": "application/json"}) 
                                else: raise e
                                    
                            ai_data = json.loads(response.text.strip())
                            lottie_placeholder.empty()

                            if not ai_data.get("is_plant", True):
                                st.error("🚫 **Invalid Image:** Please provide a clear picture of a leaf or crop.")
                            else:
                                plant_name = ai_data.get("plant_name", "Unknown Plant")
                                if "pepper" in plant_name.lower(): plant_name = "Chili"
                                result = ai_data.get("diagnosis", "Unknown Condition")

                                confidence = float(ai_data.get("confidence", 0.0))

                                # 🚨 Auto-correct decimals! If the AI returns 0.8, multiply by 100 to make it 80%
                                if 0.0 < confidence <= 1.0:
                                    confidence = confidence * 100
                                    
                                is_healthy = ai_data.get("is_healthy", False)
                                reasoning = ai_data.get("reasoning", "No symptoms described.")
                                
                                full_disease_name = f"{plant_name}: {result}"
                                st.session_state['latest_disease'] = full_disease_name

                                save_to_history(plant_name, result, confidence, is_healthy, cropped_image)
                                
                                card_class = "healthy" if is_healthy else "disease"
                                icon = "✅" if is_healthy else "🦠"
                                st.markdown(f"""
                                    <div class="diagnosis-card {card_class}">
                                        <h4 style="margin-top:0; color: #0F4C3A;">{icon} Analysis Complete</h4>
                                        <p style="margin-bottom:0px; font-size: 1.1rem;"><b>Subject:</b> {plant_name}</p>
                                        <p style="margin-bottom:0px; font-size: 1.1rem;"><b>Condition:</b> {result}</p>
                                        <p style="margin-bottom:0px; font-size: 1.1rem; color: #5C7765;"><b>Confidence:</b> {confidence:.1f}%</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                st.info(f"**🔍 AI Reasoning:** {reasoning}")
                                if not is_healthy: st.success("👉 View **Treatment & Audio** tab for action plan.")
                            
                        except Exception as e:
                            lottie_placeholder.empty()
                            st.error(f"Error parsing AI response: {e}")

# --- TREATMENT & AUDIO ---
elif selected == "Treatment & Audio":
    st.title("🔊 Action Plan")
    st.write("---")
    if not st.session_state.get('latest_disease'): 
        st.warning("⚠️ Awaiting data. Please scan a plant in the Dashboard.")
    elif "healthy" in st.session_state['latest_disease'].lower(): 
        st.success(f"✅ Plant is **Healthy**! No action required.")
    else:
        disease_display = st.session_state['latest_disease']
        st.markdown(f"### Target Pathology: <span style='color:#FF6B6B;'>{disease_display}</span>", unsafe_allow_html=True)
        col_lang, col_btn_audio = st.columns([1, 1])
        with col_lang: selected_lang = st.selectbox("Output Language:", LANGUAGES)
        with col_btn_audio:
            st.write("") 
            st.write("")
            generate_audio_btn = st.button(f"🔊 Generate Briefing in {selected_lang}", use_container_width=True)

        if generate_audio_btn:
            if not GEMINI_API_KEY:
                st.error("Missing Gemini API Key!")
            else:
                memory_key = f"saved_{disease_display}_{selected_lang}"
                if memory_key in st.session_state:
                    st.success("⚡ Accessed from Cache.")
                    st.markdown(f"<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>{st.session_state[memory_key]['text']}</div>", unsafe_allow_html=True)
                    st.audio(st.session_state[memory_key]['audio'], format="audio/mp3")
                else:
                    with st.spinner(f"Synthesizing instructions in {selected_lang}..."):
                        try:
                            llm = genai.GenerativeModel('gemini-2.5-flash')
                            prompt = f"Diagnosed with '{disease_display}'. Provide 3-4 short, actionable bullet points for treatment. First line MUST be diagnosis. Language: {selected_lang}. Max 85 words. No chatty text."
                            translated_text = llm.generate_content(prompt).text
                            clean_audio_text = translated_text.replace("*", "").replace("#", "").replace("_", "")
                            
                            st.success("Synthesis Complete.")
                            st.markdown(f"<div style='background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05);'>{translated_text}</div>", unsafe_allow_html=True)
                            
                            tts = gTTS(text=clean_audio_text, lang=LANG_MAP.get(selected_lang, "en"))
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                                tts.save(fp.name)
                                st.audio(fp.name, format="audio/mp3")
                            st.session_state[memory_key] = {'text': translated_text, 'audio': fp.name}
                        except Exception as e:
                            st.error(f"Error generating translation/audio: {e}")

# --- HISTORY LOG ---
elif selected == "History Log":
    st.title("📂 Database")
    st.markdown("##### Historical scan records and analytics.")
    st.write("---")
    
    if os.path.exists(HISTORY_FILE):
        df = pd.read_csv(HISTORY_FILE)
        col1, col2 = st.columns(2)
        col1.metric("Total Scans Logged", len(df))
        col2.metric("Pathogens Detected", len(df[df['Status'] == 'Disease Detected']))
        st.write("---")
        
        # 🚨 NEW: Tells Streamlit to render the 'Preview' column as an image
        st.dataframe(
            df, 
            column_config={
                "Preview": st.column_config.ImageColumn("Leaf Preview", help="Cropped specimen")
            },
            use_container_width=True, 
            hide_index=True
        )
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Export Database (CSV)", data=csv, file_name='agrivox_data.csv', mime='text/csv')
    else:
        st.info("Database is empty. Scans will populate here automatically.")

# --- CHATBOT ---
elif selected == "AI Chatbot":
    st.title("💬 Agronomy Assistant")
    st.write("---")
    if not GEMINI_API_KEY: st.warning("⚠️ API Link Offline. Please add API key.")
    else:
        ai_model = genai.GenerativeModel('gemini-2.5-flash')
        if "messages" not in st.session_state: st.session_state.messages = []
        chat_container = st.container(height=500)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if user_question := st.chat_input("Ask a question (e.g., 'Best NPK ratio for early tomatoes?'):"):
            with chat_container:
                with st.chat_message("user"): st.markdown(user_question)
                st.session_state.messages.append({"role": "user", "content": user_question})
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        try:
                            response = ai_model.generate_content(f"Give a short, practical answer to this farmer: {user_question}")
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Error connecting to AI: {e}")