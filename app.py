from flask import Flask, render_template, send_file, request, redirect, url_for
import os, json, tempfile, re
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
from collections import Counter
from werkzeug.utils import secure_filename
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Define folders for storing data and uploaded files
DATA_FOLDER = "data"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"mp3", "mp4"}  # Supported audio/video formats

# Store last 5 search queries
recent_searches = []

# Create folders if not exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to check if uploaded file type is allowed
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Load all meeting JSON files from data folder
def load_meetings():
    files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".json")]
    meetings = []
    for f in files:
        with open(os.path.join(DATA_FOLDER, f), "r") as file:
            data = json.load(file)
            data["file_name"] = f
            meetings.append(data)
    return meetings

# Homepage route: display meetings, search bar, recent searches
@app.route("/", methods=["GET"])
def index():
    meetings = load_meetings()
    keyword = request.args.get("q", "").strip().lower()

    # Handle search logic
    if keyword:
        recent_searches.insert(0, keyword)
        if len(recent_searches) > 5:
            recent_searches.pop()
        meetings = [
            m for m in meetings
            if keyword in m.get("summary", "").lower()
            or any(keyword in p.lower() for p in m.get("participants", []))
            or keyword in m.get("meeting_id", "").lower()
            or keyword in m.get("date", "").lower()
        ]

    return render_template("index.html", meetings=meetings, recent_searches=recent_searches)

# Meeting detail view: speaker stats, keyword analytics
@app.route("/meeting/<filename>")
def meeting_detail(filename):
    file_path = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(file_path):
        return "Meeting not found", 404

    with open(file_path, "r") as file:
        meeting = json.load(file)

    meeting["file_name"] = filename
    chart_html = ""
    keyword_html = ""

    # ✅ Calculate speaker talk time if missing
    if "speaker_stats" not in meeting and "segments" in meeting:
        speaker_stats = {}
        for seg in meeting["segments"]:
            speaker = seg.get("speaker", "Unknown")
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            duration = max(0, end - start)
            speaker_stats[speaker] = speaker_stats.get(speaker, 0) + round(duration / 60, 2)
        meeting["speaker_stats"] = speaker_stats

    # ✅ Create speaker bar chart using Plotly
    if "speaker_stats" in meeting and meeting["speaker_stats"]:
        df = pd.DataFrame(list(meeting["speaker_stats"].items()), columns=["Speaker", "Talk Time (mins)"])
        fig = px.bar(
            df, x="Speaker", y="Talk Time (mins)",
            title="Speaker Talk Time (Bar Chart)", color="Speaker",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(template="plotly_white", title_font=dict(size=20))
        chart_html = fig.to_html(full_html=False)

    # ✅ Extract top keywords if not already done
    if "keywords" not in meeting:
        summary_text = meeting.get("summary", "").lower()
        words = re.findall(r'\b\w+\b', summary_text)
        stopwords = set([
            'the', 'is', 'in', 'it', 'and', 'of', 'to', 'a', 'that', 'this', 'we',
            'on', 'for', 'with', 'as', 'at', 'be', 'an', 'are', 'by', 'will', 'or',
            'can', 'not', 'should', 'you', 'our', 'they', 'about'
        ])
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        freq = Counter(filtered_words)
        meeting["keywords"] = dict(freq.most_common(5))

    # ✅ Display keywords on HTML
    if meeting.get("keywords"):
        keyword_html = "<h5 class='mt-3 text-success'>Keyword Analytics</h5><ul>"
        for kw, freq in meeting["keywords"].items():
            keyword_html += f"<li><strong>{kw}</strong>: {freq} mentions</li>"
        keyword_html += "</ul>"

    return render_template("meeting.html", meeting=meeting, chart_html=chart_html, keyword_html=keyword_html)

# Delete selected meeting JSON file
@app.route("/delete/<filename>")
def delete_meeting(filename):
    file_path = os.path.join(DATA_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for("index"))

# Clear recent search keywords
@app.route("/clear_searches")
def clear_searches():
    recent_searches.clear()
    return redirect(url_for("index"))

# Download meeting summary as TXT or PDF
@app.route("/download/<filename>/<fmt>")
def download_file(filename, fmt):
    file_path = os.path.join(DATA_FOLDER, filename)
    if not os.path.exists(file_path):
        return "File not found", 404

    with open(file_path, "r") as file:
        meeting = json.load(file)

    # Plain text download
    if fmt == "txt":
        lines = [
            f"Meeting ID: {meeting.get('meeting_id')}",
            f"Date: {meeting.get('date', 'N/A')}",
            f"Duration: {meeting.get('duration_minutes')} minutes",
            f"Participants: {', '.join(meeting.get('participants', []))}",
            f"Summary: {meeting.get('summary')}",
            f"Action Items: {', '.join(meeting.get('action_items', []))}",
            f"Decisions: {', '.join(meeting.get('decisions', []))}"
        ]
        buffer = BytesIO("\n\n".join(lines).encode("utf-8"))
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="meeting_summary.txt", mimetype="text/plain")

    # PDF download using FPDF
    elif fmt == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Voice to Text Generator", ln=True, align="C")
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)

        def add_section(title, content):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 10, f"{title}:", ln=True)
            pdf.set_font("Arial", "", 12)
            if isinstance(content, list):
                for item in content:
                    pdf.multi_cell(0, 10, f"- {item}")
            else:
                pdf.multi_cell(0, 10, content)
            pdf.ln(4)

        add_section("Meeting ID", meeting.get("meeting_id"))
        add_section("Date", meeting.get("date", "N/A"))
        add_section("Duration", f"{meeting.get('duration_minutes')} minutes")
        add_section("Participants", meeting.get("participants", []))
        add_section("Summary", meeting.get("summary"))
        add_section("Action Items", meeting.get("action_items", []))
        add_section("Decisions", meeting.get("decisions", []))

        if "keywords" in meeting:
            add_section("Keyword Analytics", [f"{k}: {v} mentions" for k, v in meeting["keywords"].items()])

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(tmp.name)
        return send_file(tmp.name, as_attachment=True, download_name="meeting_summary.pdf", mimetype="application/pdf")

    return "Invalid format", 400

# Upload audio file (mp3/mp4), simulate summary JSON
@app.route("/upload", methods=["POST"])
def upload():
    if "audio_file" not in request.files:
        return "No file part", 400

    file = request.files["audio_file"]
    if file.filename == "":
        return "No selected file", 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # --- Simulated summary generation (dummy data) ---
        now = datetime.now()
        meeting_data = {
            "meeting_id": f"M{now.strftime('%Y%m%d-%H%M')}",
            "date": now.strftime("%Y-%m-%d"),
            "duration_minutes": 5,
            "participants": ["spk_0", "spk_1"],
            "summary": "This is a mock summary generated after uploading the file.",
            "action_items": ["Finalize report", "Send follow-up email"],
            "decisions": ["Move to next sprint"],
            "segments": [
                {"speaker": "spk_0", "start": 0, "end": 60},
                {"speaker": "spk_1", "start": 60, "end": 180}
            ]
        }

        # Compute speaker stats from segments
        speaker_stats = {}
        for seg in meeting_data["segments"]:
            spk = seg["speaker"]
            duration = seg["end"] - seg["start"]
            speaker_stats[spk] = speaker_stats.get(spk, 0) + round(duration / 60, 2)
        meeting_data["speaker_stats"] = speaker_stats

        # Extract top 5 keywords from mock summary
        summary_text = meeting_data["summary"].lower()
        words = re.findall(r'\b\w+\b', summary_text)
        stopwords = set([
            'the', 'is', 'in', 'it', 'and', 'of', 'to', 'a', 'that', 'this', 'we',
            'on', 'for', 'with', 'as', 'at', 'be', 'an', 'are', 'by', 'will', 'or',
            'can', 'not', 'should', 'you', 'our', 'they', 'about'
        ])
        filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
        freq = Counter(filtered_words)
        meeting_data["keywords"] = dict(freq.most_common(5))

        # Save to data folder
        output_filename = f"{meeting_data['meeting_id']}.json"
        with open(os.path.join(DATA_FOLDER, output_filename), "w") as f:
            json.dump(meeting_data, f, indent=2)

        return redirect(url_for("index"))

    return "Invalid file type", 400

# Run the app on local server (debug mode)
if __name__ == "__main__":
    app.run(debug=True)
