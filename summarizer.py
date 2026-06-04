import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODELS = [
    "llama-3.1-8b-instant",
    "llama3-8b-8192",
    "llama-3.3-70b-versatile",
]

def call_groq(prompt, max_tokens=600):
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if "rate_limit" in str(e) or "429" in str(e) or "decommissioned" in str(e):
                print(f"{model} not available, trying next model...")
                time.sleep(2)
                continue
            else:
                raise e
    return "Could not generate notes — all models at limit. Try again in a few minutes."

def chunk_text(segments, max_words=1500):
    chunks = []
    current_chunk = []
    current_words = 0
    for seg in segments:
        words = len(seg["text"].split())
        if current_words + words > max_words and current_chunk:
            chunks.append(current_chunk)
            current_chunk = [seg]
            current_words = words
        else:
            current_chunk.append(seg)
            current_words += words
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def summarize_transcript(segments):
    print("Generating notes...")
    chunks = chunk_text(segments, max_words=1500)
    print(f"Split into {len(chunks)} chunks")

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        text = ""
        for seg in chunk:
            minutes = int(seg["start"] // 60)
            seconds = int(seg["start"] % 60)
            text += f"[{minutes:02d}:{seconds:02d}] {seg['text']}\n"

        summary = call_groq(f"""You are a professional note-taker for students.
From this video transcript extract:
- Every important concept with full explanation
- Code examples if any are mentioned
- Key definitions with meaning
- Important points a student must remember
- Any tips or warnings mentioned

Be detailed and thorough. Write like a textbook. Do NOT skip anything important.

Transcript:
{text}""", max_tokens=800)

        chunk_summaries.append(summary)
        time.sleep(3)

    combined = "\n\n".join(chunk_summaries)

    final_prompt = f"""You are an expert study notes writer. Using the content below, write PROPER DETAILED STUDY NOTES that a student can study from without watching the video at all.

Use this exact format:

## [Main Topic Name]

### [Sub Topic]
- Detailed explanation of the concept
- Example if mentioned
- Why it is important

### [Another Sub Topic]
- Explanation
- Code example if any

## Key Timestamps
- [00:00] What is covered at this time

## Action Items
- Specific things the student should do or practice

Rules:
- Be DETAILED — write full explanations not one word bullets
- Include EVERYTHING important from the video
- A student must be able to study ONLY from these notes
- Use proper headings and sub-headings
- Include examples wherever mentioned

Content to convert into notes:
{combined[:5000]}"""

    result = call_groq(final_prompt, max_tokens=2000)
    print("Notes generated!")
    return result

if __name__ == "__main__":
    with open("transcript.json", "r") as f:
        segments = json.load(f)
    notes = summarize_transcript(segments)
    print(notes)
    with open("notes.txt", "w") as f:
        f.write(notes)
    print("Saved to notes.txt")