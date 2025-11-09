import json
import os
from datetime import datetime
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
import re
from collections import Counter

# Ensure 'data' folder exists
os.makedirs("data", exist_ok=True)

# 1. Load cleaned transcript
with open("clean_transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

# 2. Generate summary using TextRank
parser = PlaintextParser.from_string(transcript, Tokenizer("english"))
summarizer = TextRankSummarizer()
summary_sentences = summarizer(parser.document, 5)
summary = "\n".join(str(sentence) for sentence in summary_sentences)

# 3. Extract Action Items and Decisions 
actions = []
decisions = []

for line in transcript.splitlines():
    line = line.strip()
    lower = line.lower()

    # Heuristics for action items
    if any(kw in lower for kw in ["we need to", "let's", "make sure to", "remember to", "assign", "follow up", "should", "todo", "schedule"]):
        actions.append(line)

    # Heuristics for decisions
    if any(kw in lower for kw in ["we decided", "it was agreed", "the decision is", "we will", "we chose", "we agreed", "it was concluded", "final decision"]):
        decisions.append(line)

# If none found, use fallback labels
if not actions:
    actions.append("No clear action items found in transcript.")
if not decisions:
    decisions.append("No clear decisions found in transcript.")

# 4. Metadata
now = datetime.now()
metadata = {
    "meeting_id": f"M{now.strftime('%Y%m%d-%H%M')}",
    "date": now.strftime("%Y-%m-%d"),
    "duration_minutes": 25,
    "participants": ["spk_0", "spk_1", "spk_2"]
}

# 5. Simulated speaker segments
segments = [
    {"speaker": "spk_0", "start": 0, "end": 300},
    {"speaker": "spk_1", "start": 300, "end": 700},
    {"speaker": "spk_2", "start": 700, "end": 1000}
]

# 6. Speaker stats
speaker_stats = {}
for seg in segments:
    spk = seg["speaker"]
    duration = seg["end"] - seg["start"]
    speaker_stats[spk] = speaker_stats.get(spk, 0) + round(duration / 60, 2)

# 7. Keyword extraction
words = re.findall(r'\b\w+\b', summary.lower())
stopwords = set([
    'the', 'is', 'in', 'it', 'and', 'of', 'to', 'a', 'that', 'this', 'we',
    'on', 'for', 'with', 'as', 'at', 'be', 'an', 'are', 'by', 'will', 'or',
    'can', 'not', 'should', 'you', 'our', 'they', 'about'
])
filtered_words = [word for word in words if word not in stopwords and len(word) > 2]
keywords = dict(Counter(filtered_words).most_common(5))

# 8. Combine all
meeting_data = {
    **metadata,
    "summary": summary,
    "action_items": actions,
    "decisions": decisions,
    "segments": segments,
    "speaker_stats": speaker_stats,
    "keywords": keywords
}

# 9. Save to JSON
output_path = os.path.join("data", f"{metadata['meeting_id']}.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(meeting_data, f, indent=2)

# 10. Optional: Save plain text for download
with open("module4-final summary/summary_out1.txt", "w", encoding="utf-8") as f:
    f.write(f"Summary:\n{summary}\n\n")
    f.write(f"Action Items:\n" + "\n".join(actions) + "\n\n")
    f.write(f"Decisions:\n" + "\n".join(decisions))

# 11. Optional: Save as separate JSON too
with open("module4_summary_generation/summary_out1.json", "w", encoding="utf-8") as f:
    json.dump(meeting_data, f, indent=2)

print(f"✅ Summary JSON saved to {output_path}")
