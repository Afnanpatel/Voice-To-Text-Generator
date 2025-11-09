import json
import re
from datetime import datetime, timedelta
import boto3
from collections import Counter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

class MeetingSummaryGenerator:
    def __init__(self):
        # Get English stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Keywords for detecting action items and decisions
        self.action_keywords = [
            "will", "should", "must", "need to", "have to", "going to",
            "action", "task", "assign", "responsible", "deadline", "due",
            "complete", "finish", "deliver", "submit"
        ]
        
        self.decision_keywords = [
            "decided", "agreed", "approved", "confirmed", "finalized",
            "concluded", "resolved", "determined", "chosen", "selected"
        ]
        
    def load_transcript(self, filename="clean_transcript.json"):
        """Load the clean transcript from JSON file"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def calculate_duration(self, transcript):
        """Calculate meeting duration from transcript timestamps"""
        if not transcript:
            return 0
            
        # Parse the last timestamp to get total duration
        last_entry = transcript[-1]
        time_str = last_entry['start_time']
        
        # Parse time format "H:MM:SS.microseconds"
        time_parts = time_str.split(':')
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        seconds = float(time_parts[2])
        
        total_minutes = hours * 60 + minutes + seconds / 60
        return round(total_minutes)
    
    def extract_speakers(self, transcript):
        """Extract unique speakers from transcript"""
        speakers = set()
        for entry in transcript:
            speakers.add(entry['speaker'])
        return list(speakers)
    
    def generate_extractive_summary(self, transcript, num_sentences=3):
        """Generate summary using extractive summarization with NLTK"""
        # Combine all text
        full_text = " ".join([entry['text'] for entry in transcript])
        
        # Tokenize into sentences
        sentences = sent_tokenize(full_text)
        
        if len(sentences) <= num_sentences:
            return full_text
        
        # Calculate word frequencies
        words = word_tokenize(full_text.lower())
        # Filter out stopwords and non-alphabetic tokens
        words = [word for word in words if word.isalpha() and word not in self.stop_words]
        word_freq = Counter(words)
        
        # Score sentences based on word frequency
        sentence_scores = {}
        for sent in sentences:
            sent_words = word_tokenize(sent.lower())
            sent_words = [word for word in sent_words if word.isalpha() and word not in self.stop_words]
            
            if len(sent_words) > 0:
                score = sum([word_freq[word] for word in sent_words if word in word_freq])
                # Normalize by sentence length
                sentence_scores[sent] = score / len(sent_words)
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), 
                             key=lambda x: x[1], reverse=True)[:num_sentences]
        
        # Sort by original order
        summary_sentences = []
        for sent in sentences:
            for top_sent, _ in top_sentences:
                if sent == top_sent:
                    summary_sentences.append(sent)
                    break
        
        summary = " ".join(summary_sentences)
        return summary
    
    def extract_action_items(self, transcript):
        """Extract potential action items from transcript"""
        action_items = []
        
        for entry in transcript:
            text = entry['text'].lower()
            
            # Check for action keywords
            for keyword in self.action_keywords:
                if keyword in text:
                    # Extract the sentence containing the keyword
                    sentences = sent_tokenize(entry['text'])
                    for sent in sentences:
                        if keyword in sent.lower():
                            action_items.append({
                                'text': sent.strip(),
                                'speaker': entry['speaker'],
                                'timestamp': entry['start_time']
                            })
                            break
        
        # Remove duplicates
        unique_items = []
        seen = set()
        for item in action_items:
            if item['text'] not in seen:
                unique_items.append(item)
                seen.add(item['text'])
        
        return unique_items[:5]  # Limit to top 5 action items
    
    def extract_decisions(self, transcript):
        """Extract decisions made during the meeting"""
        decisions = []
        
        for entry in transcript:
            text = entry['text'].lower()
            
            # Check for decision keywords
            for keyword in self.decision_keywords:
                if keyword in text:
                    sentences = sent_tokenize(entry['text'])
                    for sent in sentences:
                        if keyword in sent.lower():
                            decisions.append({
                                'text': sent.strip(),
                                'speaker': entry['speaker'],
                                'timestamp': entry['start_time']
                            })
                            break
        
        # Remove duplicates
        unique_decisions = []
        seen = set()
        for decision in decisions:
            if decision['text'] not in seen:
                unique_decisions.append(decision)
                seen.add(decision['text'])
        
        return unique_decisions[:3]  # Limit to top 3 decisions
    
    def generate_meeting_summary(self, transcript_file="clean_transcript.json"):
        """Generate complete meeting summary"""
        # Load transcript
        transcript = self.load_transcript(transcript_file)
        
        # Extract metadata
        duration = self.calculate_duration(transcript)
        speakers = self.extract_speakers(transcript)
        
        # Generate summary components
        summary_text = self.generate_extractive_summary(transcript)
        action_items = self.extract_action_items(transcript)
        decisions = self.extract_decisions(transcript)
        
        # Create meeting summary object
        meeting_summary = {
            "meeting_id": f"M{datetime.now().strftime('%Y%m%d-%H%M')}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "duration_minutes": duration,
            "participants": speakers,
            "summary": summary_text,
            "action_items": [item['text'] for item in action_items],
            "decisions": [decision['text'] for decision in decisions],
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "transcript_file": transcript_file,
                "total_segments": len(transcript)
            }
        }
        
        return meeting_summary
    
    def save_summary_to_json(self, summary, filename="meeting_summary.json"):
        """Save summary to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to {filename}")
    
    def save_summary_to_txt(self, summary, filename="meeting_summary.txt"):
        """Save summary to text file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("MEETING SUMMARY\n")
            f.write("="*50 + "\n\n")
            f.write(f"Meeting ID: {summary['meeting_id']}\n")
            f.write(f"Date: {summary['date']}\n")
            f.write(f"Duration: {summary['duration_minutes']} minutes\n")
            f.write(f"Participants: {', '.join(summary['participants'])}\n\n")
            
            f.write("SUMMARY:\n")
            f.write(summary['summary'] + "\n\n")
            
            if summary['action_items']:
                f.write("ACTION ITEMS:\n")
                for i, item in enumerate(summary['action_items'], 1):
                    f.write(f"{i}. {item}\n")
                f.write("\n")
            
            if summary['decisions']:
                f.write("KEY DECISIONS:\n")
                for i, decision in enumerate(summary['decisions'], 1):
                    f.write(f"{i}. {decision}\n")
        
        print(f"Text summary saved to {filename}")
    
    def save_summary_to_pdf(self, summary, filename="meeting_summary.pdf"):
        """Save summary to PDF file"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='darkblue',
            spaceAfter=30
        )
        story.append(Paragraph("Meeting Summary", title_style))
        
        # Meeting metadata
        story.append(Paragraph(f"<b>Meeting ID:</b> {summary['meeting_id']}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {summary['date']}", styles['Normal']))
        story.append(Paragraph(f"<b>Duration:</b> {summary['duration_minutes']} minutes", styles['Normal']))
        story.append(Paragraph(f"<b>Participants:</b> {', '.join(summary['participants'])}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary
        story.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
        story.append(Paragraph(summary['summary'], styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Action Items
        if summary['action_items']:
            story.append(Paragraph("<b>Action Items:</b>", styles['Heading2']))
            for item in summary['action_items']:
                story.append(Paragraph(f"• {item}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Decisions
        if summary['decisions']:
            story.append(Paragraph("<b>Key Decisions:</b>", styles['Heading2']))
            for decision in summary['decisions']:
                story.append(Paragraph(f"• {decision}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"PDF summary saved to {filename}")
    
    def upload_to_s3(self, filename, bucket_name, s3_key=None):
        """Upload file to S3 bucket"""
        if s3_key is None:
            s3_key = f"summaries/{os.path.basename(filename)}"
        
        try:
            s3_client = boto3.client('s3')
            s3_client.upload_file(filename, bucket_name, s3_key)
            print(f"File uploaded to s3://{bucket_name}/{s3_key}")
            return True
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False

# Main execution
if __name__ == "__main__":
    # Initialize the generator
    generator = MeetingSummaryGenerator()
    
    # Generate meeting summary from existing clean_transcript.json
    print("Generating meeting summary...")
    summary = generator.generate_meeting_summary("clean_transcript.json")
    
    # Save to JSON
    generator.save_summary_to_json(summary)
    
    # Save to TXT
    generator.save_summary_to_txt(summary)
    
    # Save to PDF
    generator.save_summary_to_pdf(summary)
    
    # Print summary to console
    print("\n" + "="*50)
    print("MEETING SUMMARY")
    print("="*50)
    print(json.dumps(summary, indent=2))

     # Upload to S3 (configure bucket name first)
    bucket_name = "your-meeting-summaries-bucket"
    generator.upload_to_s3("meeting_summary.json", bucket_name)
    generator.upload_to_s3("meeting_summary.txt", bucket_name)
    generator.upload_to_s3("meeting_summary.pdf", bucket_name)
