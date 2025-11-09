# 🎙️ Voice Minutes — AI-Powered Meeting Minutes Generator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![AWS](https://img.shields.io/badge/AWS-Transcribe%20%7C%20Lambda%20%7C%20S3-orange?logo=amazonaws)
![NLP](https://img.shields.io/badge/NLP-spaCy%20%7C%20TextRank%20%7C%20GPT-blueviolet)
![Framework](https://img.shields.io/badge/Framework-Flask%20%7C%20Streamlit-red)
![License](https://img.shields.io/badge/License-Apache%202.0-green)
![Status](https://img.shields.io/badge/Status-Active-success)


> **“Turning conversations into concise, actionable summaries.”**  
An intelligent system that automatically generates **meeting transcripts** and **summaries** from uploaded audio files using **AWS Transcribe**, **Lambda**, and **Natural Language Processing (NLP)**.

---

## 🚀 Overview

Manually documenting meeting minutes is slow and error-prone.  
**Voice Minutes** automates this process by:
- Transcribing uploaded audio recordings from **AWS S3** using **AWS Transcribe**.
- Cleaning and structuring the text with **Python scripts**.
- Summarizing the transcript with **NLP algorithms** (TextRank, spaCy, or GPT models).
- Displaying everything neatly on a **dashboard** with options to download reports (PDF/TXT).

📄 **Result:** A fully automated meeting assistant that saves hours of manual note-taking.

---

## 🧩 System Architecture
🎤 Audio Upload → ☁️ AWS S3 → 🧠 AWS Transcribe → ⚙️ Lambda Processing
→ 🧹 Text Cleaning & Summarization → 📊 Dashboard & Downloadable Report


---

## 💡 Core Features

| Feature | Description |
|----------|--------------|
| 🎧 **Audio Upload & S3 Integration** | Upload .mp3/.mp4 files and store securely in S3. |
| 🧠 **Speech-to-Text** | Uses AWS Transcribe to convert speech into text. |
| 🧹 **Post-Processing** | Cleans filler words, formats text, extracts speaker info. |
| 🪶 **NLP Summarization** | Generates key highlights, action points, and concise summaries. |
| 📊 **Dashboard & Reports** | View, search, and download meeting transcripts as PDF/TXT. |
| 🔒 **Secure Access (Optional)** | User login and access control for private meetings. |

---

## 🛠️ Tech Stack

| Category | Tools & Technologies |
|-----------|----------------------|
| 💻 **Programming** | Python |
| ☁️ **Cloud Services** | AWS S3, AWS Lambda, AWS Transcribe |
| 🧮 **NLP Libraries** | spaCy, NLTK, TextRank |
| 🧰 **Web Framework** | Flask / Streamlit |
| 🗂️ **File Formats** | JSON, TXT, PDF |
| ⚙️ **Other Tools** | Boto3 SDK, FPDF, Pandas |
| 🔄 **Methodology** | Agile (Scrum/Kanban) |

---

## 🧱 Project Modules

1️⃣ **Audio Upload & S3 Integration**  
   → Handles file uploads and stores them in AWS S3.

2️⃣ **AWS Transcribe Setup**  
   → Automatically triggers Transcribe jobs when new files are uploaded.

3️⃣ **Transcript Post-Processing**  
   → Removes noise, cleans formatting, and adds timestamps.

4️⃣ **Meeting Summary Generation (NLP)**  
   → Extracts main discussion points and action items.

5️⃣ **Dashboard & Downloadable Reports**  
   → User-friendly interface for viewing and downloading meeting notes.

---

## 🧩 Folder Structure
VoiceMinutes/
│
├── src/
│ ├── upload_audio.py
│ ├── transcribe_handler.py
│ ├── postprocess_transcript.py
│ ├── summarize_meeting.py
│ └── dashboard_app.py
│
├── Voice Minutes Case.pdf
├── requirements.txt
├── .gitignore
└── README.md

## ⚙️ How to Run Locally
Setup_Instructions:
  - step: "Set up Virtual Environment"
    commands:
      - "python -m venv venv"
      - "venv\\Scripts\\activate  # (Windows)"
      - "source venv/bin/activate  # (Mac/Linux)"

  - step: "Install Dependencies"
    commands:
      - "pip install -r requirements.txt"

  - step: "Run the Dashboard"
    commands:
      - "streamlit run src/dashboard_app.py"
 ## 🧪 Sample Output
 {
  "meeting_id": "M2025-001",
  "summary": "Discussed Q2 project deadlines, assigned tasks to team leads, and finalized budget approvals.",
  "action_items": [
    "Submit design documents by June 25",
    "Start development by July 1"
  ],
  "duration_minutes": 45,
  "participants": ["Alice", "Bob", "Priya"]
}





