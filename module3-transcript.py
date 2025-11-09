import json
import re
from datetime import timedelta

# Load transcript JSON file
with open("new audio file.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract necessary fields
segments = data['results']['speaker_labels']['segments']
items = data['results']['items']

# Create word-level map with speaker labels and timestamps
word_map = []
for item in items:
    if item['type'] == 'pronunciation':
        word_map.append({
            'word': item['alternatives'][0]['content'],
            'start_time': float(item['start_time']),
            'end_time': float(item['end_time']),
            'speaker_label': item.get('speaker_label', '')
        })
    elif item['type'] == 'punctuation':
        if word_map:
            word_map[-1]['word'] += item['alternatives'][0]['content']

# Define common filler words to remove
filler_words = {"um", "uh", "erm", "ah", "hmm", "like", "you know", "mm", "eh"}

# Exclude specific speaker labels
excluded_speakers = {"spk_2"}

# Group words into speaker-based paragraphs
clean_transcript = []
current_speaker = ""
current_sentence = ""
start_time = None

for word_info in word_map:
    word = word_info['word']
    speaker = word_info['speaker_label']

    # Skip excluded speakers
    if speaker in excluded_speakers:
        continue

    if speaker != current_speaker:
        if current_sentence:
            clean_transcript.append({
                "speaker": current_speaker,
                "start_time": str(timedelta(seconds=start_time)),
                "text": current_sentence.strip()
            })
        current_speaker = speaker
        current_sentence = ""
        start_time = word_info['start_time']

    if word.lower() not in filler_words:
        current_sentence += word + " "

# Append the last sentence
if current_sentence and current_speaker not in excluded_speakers:
    clean_transcript.append({
        "speaker": current_speaker,
        "start_time": str(timedelta(seconds=start_time)),
        "text": current_sentence.strip()
    })

# Optional: Fix lowercase "i"
for entry in clean_transcript:
    entry['text'] = re.sub(r"\bi\b", "I", entry['text'])

# Save to JSON
with open("clean_transcript.json", "w", encoding="utf-8") as f:
    json.dump(clean_transcript, f, indent=2)

# Save to TXT
with open("clean_transcript.txt", "w", encoding="utf-8") as f:
    for entry in clean_transcript:
        f.write(f"[{entry['start_time']}] {entry['speaker']}: {entry['text']}\n\n")
