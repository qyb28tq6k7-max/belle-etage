"""
Newsletter Bot — Belle Étage
Generates complete newsletter issues in the brand voice.
Run: python newsletter_bot.py
"""

import anthropic
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from brand_voice import BRAND_SYSTEM_PROMPT

client = anthropic.Anthropic()

def generate_newsletter(topic: str, issue_number: int = None, additional_context: str = "") -> dict:
    """
    Generate a complete newsletter issue on the given topic.
    Returns a dict with subject, preview_text, and body.
    """

    issue_str = f"Issue #{issue_number}" if issue_number else f"Issue dated {datetime.now().strftime('%B %d, %Y')}"

    user_prompt = f"""Write a complete newsletter issue for Belle Étage.

ISSUE: {issue_str}
TOPIC: {topic}
{f"ADDITIONAL CONTEXT: {additional_context}" if additional_context else ""}

Deliver the newsletter in this exact format:

SUBJECT LINE: [max 50 characters, elegant and curiosity-driven]

PREVIEW TEXT: [40-90 characters, complements the subject line]

---

[Newsletter body — 400-600 words total]

Start with a warm personal opening from the founder (2-3 sentences). Then cover 2-3 focused sections with small title-case headers. End with a ritual suggestion or a question for the reader.

Sign off: With warmth, // Belle Étage

Make it feel like it came from a real, brilliant, warm human — not a marketing department."""

    print(f"\nGenerating newsletter on: {topic}")
    print("─" * 50)

    full_response = ""

    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=1500,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)

    # Parse the response into parts
    lines = full_response.strip().split("\n")
    subject = ""
    preview = ""
    body_lines = []
    in_body = False

    for line in lines:
        if line.startswith("SUBJECT LINE:"):
            subject = line.replace("SUBJECT LINE:", "").strip()
        elif line.startswith("PREVIEW TEXT:"):
            preview = line.replace("PREVIEW TEXT:", "").strip()
        elif line.strip() == "---":
            in_body = True
        elif in_body:
            body_lines.append(line)

    return {
        "subject": subject,
        "preview_text": preview,
        "body": "\n".join(body_lines).strip(),
        "full_text": full_response,
        "topic": topic,
        "generated_at": datetime.now().isoformat()
    }


def save_newsletter(newsletter: dict, output_dir: str = None):
    """Save the generated newsletter to a text file."""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "content", "newsletters")

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    topic_slug = newsletter["topic"].lower().replace(" ", "-")[:30]
    filename = f"{timestamp}_{topic_slug}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"SUBJECT: {newsletter['subject']}\n")
        f.write(f"PREVIEW: {newsletter['preview_text']}\n")
        f.write(f"GENERATED: {newsletter['generated_at']}\n")
        f.write("=" * 60 + "\n\n")
        f.write(newsletter["body"])

    print(f"\nSaved to: {filepath}")
    return filepath


def batch_generate(topics: list[str]) -> list[dict]:
    """Generate newsletters for a list of topics."""
    results = []
    for i, topic in enumerate(topics, 1):
        print(f"\n[{i}/{len(topics)}] Generating newsletter...")
        newsletter = generate_newsletter(topic, issue_number=i)
        filepath = save_newsletter(newsletter)
        results.append({**newsletter, "saved_to": filepath})
    return results


if __name__ == "__main__":
    # Example: run from command line with a topic
    # python newsletter_bot.py "magnesium and sleep quality"

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        # Default demonstration
        topic = "magnesium and sleep quality"

    newsletter = generate_newsletter(topic)
    save_newsletter(newsletter)

    print("\nDone! Newsletter ready to copy into Beehiiv.")
