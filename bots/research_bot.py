"""
Research Bot — Belle Étage
Researches supplement ingredients and products, generates science summaries.
Run: python research_bot.py
"""

import anthropic
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from brand_voice import BRAND_SYSTEM_PROMPT

client = anthropic.Anthropic()

RESEARCH_CONTEXT = """
RESEARCH GUIDELINES
-------------------
When researching ingredients or products:
- Lead with the mechanism of action (how it works in the body)
- Reference specific study types when relevant (RCT, meta-analysis, observational)
- Note the dose used in research vs. typical supplement doses
- Flag any important drug interactions or contraindications
- Note quality markers to look for when buying (forms, certifications, bioavailability)
- Distinguish between animal studies and human studies
- Be honest about the strength of evidence (strong vs. emerging vs. weak)
- Never overstate the evidence

OUTPUT FORMATS:
- "summary": 200-300 word plain-English overview for newsletter use
- "deep_dive": 500-700 word detailed breakdown for a full newsletter issue
- "product_eval": Evaluation of a specific supplement product
- "comparison": Side-by-side comparison of multiple products or forms
"""


def research_ingredient(ingredient: str, output_format: str = "summary") -> str:
    """
    Research a supplement ingredient and generate a science summary.

    Args:
        ingredient: The ingredient to research (e.g., "magnesium glycinate")
        output_format: "summary", "deep_dive", "product_eval", or "comparison"
    """

    format_instructions = {
        "summary": "Write a 200-300 word plain-English summary suitable for a newsletter section. Include: what it is, main evidence-backed benefits, optimal forms and doses, who benefits most.",
        "deep_dive": """Write a 500-700 word deep dive for a full newsletter issue. Structure:
1. What it is and where it comes from
2. Mechanism of action (how it works in the body)
3. What the research actually shows (be specific about study quality)
4. Best forms and why they matter
5. Dosing ranges used in research
6. Who should consider it and who should be cautious
7. What to look for when buying""",
        "product_eval": "Evaluate this as a supplement product: quality markers, form, dose, certifications, value. Write 200-300 words as a product recommendation with full transparency.",
        "comparison": "Compare the main forms/variations of this ingredient. What are the differences in bioavailability, effects, and ideal use cases? 300-400 words."
    }

    prompt = f"""Research and write about: {ingredient}

Format: {format_instructions.get(output_format, format_instructions["summary"])}

Apply the research guidelines. Be scientifically accurate and honest about the strength of evidence. Write in Belle Étage brand voice — intelligent, warm, accessible."""

    print(f"\nResearching: {ingredient} ({output_format})")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=1500,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT + RESEARCH_CONTEXT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def evaluate_affiliate_product(product_name: str, product_details: str = "") -> str:
    """
    Evaluate a specific product for potential affiliate partnership or recommendation.
    """

    prompt = f"""Evaluate this supplement product for Belle Étage's affiliate program and reader recommendations.

PRODUCT: {product_name}
{f"DETAILS: {product_details}" if product_details else ""}

Evaluate:
1. Ingredient quality and forms used
2. Dosing (does it match research doses?)
3. Third-party certifications (NSF, USP, Informed Sport, etc.)
4. Manufacturing transparency
5. Value relative to category
6. Who it's best for
7. Any concerns or limitations
8. Recommendation: Strongly recommend / Recommend with caveats / Do not recommend

Write as a genuine product evaluation, 250-350 words. Be honest — our readers trust us."""

    print(f"\nEvaluating product: {product_name}")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=800,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT + RESEARCH_CONTEXT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def generate_content_calendar_topics(focus_area: str = "general wellness", months_ahead: int = 3) -> str:
    """
    Generate newsletter topic ideas for future planning.
    """

    prompt = f"""Generate newsletter topic ideas for Belle Étage.

Focus area: {focus_area}
Planning horizon: {months_ahead} months

Generate 12-15 topic ideas that:
- Are scientifically grounded and newsworthy
- Haven't been overdone in wellness media
- Play to the founder's nutrition and chemistry background
- Can naturally include affiliate product recommendations
- Cover a mix of: ingredient deep-dives, lifestyle topics, recipe angles, founder-perspective pieces

For each topic, include:
- Topic title
- Angle/hook (what makes this interesting right now)
- Natural product tie-in (if any)
- Estimated reader interest level (High/Medium)

Format as a clean list ready to drop into a content calendar."""

    print(f"\nGenerating content calendar topics for: {focus_area}")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=1500,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT + RESEARCH_CONTEXT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def save_research(content: str, research_type: str, subject: str):
    """Save research output to file."""
    output_dir = os.path.join(os.path.dirname(__file__), "..", "content", "research")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    subject_slug = subject.lower().replace(" ", "-")[:30]
    filename = f"{timestamp}_{research_type}_{subject_slug}.txt"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"RESEARCH TYPE: {research_type}\n")
        f.write(f"SUBJECT: {subject}\n")
        f.write(f"GENERATED: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(content)

    print(f"\nSaved to: {filepath}")
    return filepath


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "ingredient"
    subject = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "ashwagandha"

    if mode == "ingredient":
        result = research_ingredient(subject, output_format="deep_dive")
        save_research(result, "ingredient_deep_dive", subject)
    elif mode == "product":
        result = evaluate_affiliate_product(subject)
        save_research(result, "product_evaluation", subject)
    elif mode == "calendar":
        result = generate_content_calendar_topics(subject)
        save_research(result, "content_calendar", subject)
    else:
        print("Usage: python research_bot.py [ingredient|product|calendar] [subject]")
