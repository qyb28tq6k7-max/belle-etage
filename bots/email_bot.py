"""
Email Response Bot — Belle Étage
Drafts subscriber email responses in the brand voice.
Run: python email_bot.py
"""

import anthropic
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from brand_voice import BRAND_SYSTEM_PROMPT

client = anthropic.Anthropic()

EMAIL_RESPONSE_CONTEXT = """
RESPONDING TO SUBSCRIBER EMAILS
---------------------------------
When responding to subscriber emails:
- Always address them by first name if provided
- Acknowledge their specific question or comment directly in the first sentence
- Keep responses to 100-200 words — warm but concise
- Never diagnose or prescribe. For medical questions, say: "I'd always recommend looping in your doctor or pharmacist for anything specific to your situation — what I can offer is the general science."
- If recommending a product, be transparent about the affiliate relationship
- End with an invitation to reply or a question
- Sign off: "With warmth, [Founder Name]" (use "Belle Étage Team" if no name provided)

RESPONSE TONE GUIDE:
- Product recommendation questions: enthusiastic but measured, explain the why
- Science/ingredient questions: precise but accessible, no jargon without explanation
- Personal wellness questions: empathetic, personal, gentle pivot to general science
- Criticism or concerns: grateful, transparent, never defensive
- Compliments: gracious and genuine, not performative
"""

def draft_email_response(
    subscriber_email: str,
    subscriber_name: str = "",
    topic_or_question: str = "",
    founder_name: str = "Belle Étage Team"
) -> str:
    """
    Draft a response to a subscriber email.

    Args:
        subscriber_email: The email content received from the subscriber
        subscriber_name: Subscriber's first name (optional)
        topic_or_question: Short description of what they're asking about
        founder_name: How to sign the response
    """

    name_context = f"The subscriber's name is {subscriber_name}." if subscriber_name else "No name was provided; use a warm general greeting."

    prompt = f"""Draft a response to this subscriber email for Belle Étage.

{name_context}
Sign off as: {founder_name}

SUBSCRIBER'S EMAIL:
{subscriber_email}

{f"TOPIC/CONTEXT: {topic_or_question}" if topic_or_question else ""}

Write the complete email response, ready to send. Include a subject line if this is a reply that would start a new thread. Keep it 100-200 words, warm, specific, and in brand voice."""

    print(f"\nDrafting response to subscriber email...")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=600,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT + EMAIL_RESPONSE_CONTEXT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def draft_welcome_email(subscriber_name: str = "", lead_magnet_delivered: bool = True) -> str:
    """Generate a personalized welcome email for new subscribers."""

    name_part = f"Their name is {subscriber_name}." if subscriber_name else "No name available."

    prompt = f"""Write a welcome email for a new Belle Étage subscriber.
{name_part}
Lead magnet delivered: {"Yes — they signed up for the free wellness guide" if lead_magnet_delivered else "No — direct subscribe"}

This is the first email they'll receive. Make them feel like they just joined something special and personal — not a mass email list. 150-200 words."""

    print(f"\nDrafting welcome email...")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=500,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT + EMAIL_RESPONSE_CONTEXT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def draft_broadcast_email(subject_focus: str, subscribers_segment: str = "all subscribers") -> str:
    """Draft a broadcast email (not a newsletter — a direct personal note)."""

    prompt = f"""Write a short personal broadcast email from Belle Étage founder.
Focus/reason: {subject_focus}
Audience: {subscribers_segment}

This is NOT a newsletter — it's a personal note, like an email from a friend who happens to run this brand.
80-120 words. Feels like she sat down and wrote it personally. Can be about a recommendation, a personal update, a flash sale, or a quick tip."""

    print(f"\nDrafting broadcast email on: {subject_focus}")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=400,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT + EMAIL_RESPONSE_CONTEXT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def save_email(content: str, email_type: str, context: str = ""):
    """Save draft email to file."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "content", "emails")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{timestamp}_{email_type}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"TYPE: {email_type}\n")
        if context:
            f.write(f"CONTEXT: {context}\n")
        f.write(f"GENERATED: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(content)

    print(f"\nSaved to: {filepath}")
    return filepath


if __name__ == "__main__":
    # Demo: draft a response to a sample subscriber email
    sample_email = """Hi! I've been taking magnesium glycinate for a few months and I noticed your newsletter mentioned it.
I'm curious — how much should I be taking? I currently take 200mg before bed. Is that enough or should I take more?
Thanks so much, Sarah"""

    response = draft_email_response(
        subscriber_email=sample_email,
        subscriber_name="Sarah",
        topic_or_question="magnesium dosing question",
        founder_name="Belle Étage Team"
    )
    save_email(response, "subscriber_response", "magnesium dosing question from Sarah")
