"""
Social Media Bot — Belle Étage
Generates Instagram captions and Pinterest pin descriptions in the brand voice.
Run: python social_bot.py
"""

import anthropic
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from brand_voice import BRAND_SYSTEM_PROMPT

client = anthropic.Anthropic()


def generate_instagram_captions(topic: str, count: int = 5) -> list[dict]:
    """Generate Instagram captions for a topic."""

    prompt = f"""Generate {count} Instagram captions for Belle Étage on this topic: {topic}

For each caption, provide:
1. The caption text (2-4 sentences, brand voice, no excessive hashtags, ends with a subtle call to action or question)
2. 5-8 relevant hashtags (mix of niche and broad)
3. A suggested visual direction (1 sentence describing the ideal image/reel concept)

Format each as:
---
CAPTION {'{n}'}:
[caption text]

HASHTAGS: #hashtag1 #hashtag2 ...

VISUAL: [image concept]
---

Make each caption feel distinct — vary the angle, format, and opening. Some can be educational, some personal, some product-forward."""

    print(f"\nGenerating {count} Instagram captions on: {topic}")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=2000,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)

    # Parse into structured list
    captions = []
    blocks = full_response.split("---")
    for block in blocks:
        block = block.strip()
        if not block or "CAPTION" not in block:
            continue

        caption_data = {"raw": block}

        lines = block.split("\n")
        caption_text = []
        hashtags = ""
        visual = ""
        mode = None

        for line in lines:
            line = line.strip()
            if line.startswith("CAPTION"):
                mode = "caption"
            elif line.startswith("HASHTAGS:"):
                hashtags = line.replace("HASHTAGS:", "").strip()
                mode = "hashtags"
            elif line.startswith("VISUAL:"):
                visual = line.replace("VISUAL:", "").strip()
                mode = "visual"
            elif mode == "caption" and line and not line.startswith("CAPTION"):
                caption_text.append(line)

        caption_data["text"] = "\n".join(caption_text).strip()
        caption_data["hashtags"] = hashtags
        caption_data["visual"] = visual

        if caption_data["text"]:
            captions.append(caption_data)

    return captions


def generate_pinterest_pins(topic: str, count: int = 5) -> list[dict]:
    """Generate Pinterest pin titles and descriptions."""

    prompt = f"""Generate {count} Pinterest pin descriptions for Belle Étage on this topic: {topic}

Pinterest content should be highly searchable, helpful, and evergreen.

For each pin:
1. Pin Title (max 100 characters, keyword-rich but natural)
2. Pin Description (150-300 characters, educational, includes a soft call to action)
3. Board suggestion (which board this belongs on)

Format:
---
PIN {'{n}'}:
TITLE: [title]
DESCRIPTION: [description]
BOARD: [board name]
---"""

    print(f"\nGenerating {count} Pinterest pins on: {topic}")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=1500,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)

    # Parse into structured list
    pins = []
    blocks = full_response.split("---")
    for block in blocks:
        block = block.strip()
        if not block or "PIN" not in block:
            continue

        pin_data = {"raw": block}
        for line in block.split("\n"):
            line = line.strip()
            if line.startswith("TITLE:"):
                pin_data["title"] = line.replace("TITLE:", "").strip()
            elif line.startswith("DESCRIPTION:"):
                pin_data["description"] = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("BOARD:"):
                pin_data["board"] = line.replace("BOARD:", "").strip()

        if pin_data.get("title"):
            pins.append(pin_data)

    return pins


def generate_weekly_content_plan(theme: str) -> str:
    """Generate a full week of social content around a theme."""

    prompt = f"""Create a 7-day social media content plan for Belle Étage around the theme: {theme}

For each day, provide:
- Day + Platform (e.g., Monday - Instagram Feed)
- Content type (educational post, personal story, product spotlight, recipe, quote, reel idea)
- Caption (2-4 sentences)
- Hashtags (5-6)

Cover a mix of: Instagram Feed posts (3), Instagram Stories ideas (2), Pinterest pins (2).

Format cleanly so it can be copy-pasted into a scheduling tool like Buffer."""

    print(f"\nGenerating weekly content plan for theme: {theme}")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=2500,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def save_social_content(content: str | list, content_type: str, topic: str):
    """Save generated social content to file."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "content", "social")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    topic_slug = topic.lower().replace(" ", "-")[:30]
    filename = f"{timestamp}_{content_type}_{topic_slug}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"TYPE: {content_type}\n")
        f.write(f"TOPIC: {topic}\n")
        f.write(f"GENERATED: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")

        if isinstance(content, list):
            for i, item in enumerate(content, 1):
                f.write(f"\n--- Item {i} ---\n")
                f.write(item.get("raw", str(item)))
                f.write("\n")
        else:
            f.write(content)

    print(f"\nSaved to: {filepath}")
    return filepath


if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "instagram"
    topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "omega-3 fatty acids and brain health"

    if mode == "instagram":
        captions = generate_instagram_captions(topic, count=5)
        save_social_content(captions, "instagram", topic)
    elif mode == "pinterest":
        pins = generate_pinterest_pins(topic, count=5)
        save_social_content(pins, "pinterest", topic)
    elif mode == "weekly":
        plan = generate_weekly_content_plan(topic)
        save_social_content(plan, "weekly_plan", topic)
    else:
        print("Usage: python social_bot.py [instagram|pinterest|weekly] [topic]")
