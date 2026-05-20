"""
Analytics Bot — Belle Étage
Generates weekly business performance reports and growth recommendations.
"""

import anthropic
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from brand_voice import BRAND_SYSTEM_PROMPT

client = anthropic.Anthropic()

def generate_weekly_report(metrics: dict) -> str:
    """
    Generate a plain-English weekly business report with recommendations.

    metrics dict can include any of:
    - newsletter_subscribers: int
    - new_subscribers_this_week: int
    - open_rate: float (e.g. 0.42 for 42%)
    - click_rate: float
    - affiliate_clicks: dict {product: clicks}
    - affiliate_revenue: float
    - instagram_followers: int
    - instagram_new_followers: int
    - top_performing_post: str
    - pinterest_impressions: int
    - website_visitors: int
    """

    metrics_text = "\n".join([f"- {k}: {v}" for k, v in metrics.items()])

    prompt = f"""You are the business analytics advisor for Belle Étage.

Here are this week's business metrics:
{metrics_text}

Write a weekly performance report for the founder. Include:
1. HEADLINE: One sentence on how the week went overall
2. WHAT'S WORKING: 2-3 specific things performing well and why
3. WHAT TO WATCH: 1-2 things that need attention
4. THIS WEEK'S PRIORITIES: 3 specific, actionable tasks ranked by impact
5. GROWTH TRAJECTORY: Where the business will be in 30 days if current trends continue

Keep it under 300 words. Be honest, specific, and encouraging. Write like a trusted business advisor, not a corporate report."""

    print("\nGenerating weekly analytics report...")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=800,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def generate_growth_strategy(current_state: str, goal: str) -> str:
    """Generate a 30-day growth strategy based on current state and goal."""

    prompt = f"""Create a 30-day growth strategy for Belle Étage.

CURRENT STATE: {current_state}
GOAL: {goal}

Provide:
1. Week 1 focus (foundation/quick wins)
2. Week 2 focus (amplification)
3. Week 3 focus (conversion)
4. Week 4 focus (scale what's working)

For each week: 3 specific daily actions, expected outcome, success metric.

Be specific. No vague advice. Every recommendation should be something she can do in 1-2 hours."""

    print(f"\nGenerating 30-day growth strategy...")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=1200,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def analyze_affiliate_performance(products: list[dict]) -> str:
    """
    Analyze which affiliate products to push harder and which to drop.

    products: list of dicts with keys: name, clicks, conversions, revenue, commission_rate
    """

    products_text = json.dumps(products, indent=2)

    prompt = f"""Analyze this affiliate product performance for Belle Étage and give recommendations.

PRODUCTS DATA:
{products_text}

For each product: rate performance (Strong/Okay/Drop), explain why, suggest how to promote better or whether to cut it.
Then give an overall affiliate strategy recommendation.

Be direct. If something isn't working, say so. Under 250 words."""

    print(f"\nAnalyzing affiliate performance...")
    print("─" * 50)

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-7",
        max_tokens=600,
        thinking={"type": "adaptive"},
        system=BRAND_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print("\n" + "─" * 50)
    return full_response


def save_report(content: str, report_type: str):
    output_dir = os.path.join(os.path.dirname(__file__), "..", "content", "analytics")
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filepath = os.path.join(output_dir, f"{timestamp}_{report_type}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"REPORT: {report_type}\n")
        f.write(f"DATE: {datetime.now().isoformat()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(content)
    print(f"\nSaved to: {filepath}")
    return filepath


if __name__ == "__main__":
    # Demo with sample metrics
    sample_metrics = {
        "newsletter_subscribers": 247,
        "new_subscribers_this_week": 31,
        "open_rate": "44%",
        "click_rate": "8%",
        "affiliate_clicks": {"Thorne Magnesium": 42, "AG1": 28, "Nordic Naturals": 15},
        "affiliate_revenue_this_week": "$67.20",
        "instagram_followers": 892,
        "instagram_new_followers": 54,
        "website_visitors": 412
    }

    report = generate_weekly_report(sample_metrics)
    save_report(report, "weekly_report")
