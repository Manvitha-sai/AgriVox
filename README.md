# 🌿 AgriVox: Next-Generation Crop Intelligence

AgriVox is an advanced, multimodal AI diagnostic tool designed to help farmers identify crop diseases with expert-level accuracy. By leveraging state-of-the-art vision models, it provides real-time pathology analysis and generates actionable, multilingual treatment plans.

## ✨ Core Features
* **🎯 Precision Diagnostics:** Users can isolate specific leaf symptoms using an interactive cropping tool before running the analysis.
* **🧠 Multimodal AI Engine:** Powered by Google's Gemini 2.5 Flash, the app analyzes visual pathology alongside user-provided crop context for highly accurate results.
* **🌍 Multilingual Audio Briefings:** Automatically synthesizes treatment plans and outputs spoken audio in 11 different local languages (Hindi, Telugu, Tamil, etc.) for field accessibility.
* **📊 Local Database Logging:** Automatically logs all scan histories, diagnoses, and confidence metrics into a dynamic, exportable CSV database.

## 🛠️ Technology Stack
* **Frontend & Framework:** [Streamlit](https://streamlit.io/) (Python)
* **AI Vision Model:** Google [Gemini 2.5 Flash](https://aistudio.google.com/) via `google-generativeai`
* **Audio Synthesis:** Google Text-to-Speech (`gTTS`)
* **Data Handling:** Pandas
* **UI/UX:** Custom CSS & Lottie Animations

