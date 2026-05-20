"""
Belle Étage — Automation Dashboard
A simple web interface to control all bots from a browser.
Run: python dashboard.py
Then open: http://localhost:5000
"""

import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, Response
import queue

sys.path.insert(0, os.path.dirname(__file__))

app = Flask(__name__)

# Store active generation output
output_queues = {}

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Belle Étage — Control Center</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --cream: #F5F0E8;
    --green: #2D4A3E;
    --gold: #C9A84C;
    --dark: #1A1A1A;
    --mid: #6B6B6B;
    --light: #E8E2D6;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--cream);
    color: var(--dark);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    min-height: 100vh;
  }
  header {
    background: var(--green);
    color: var(--cream);
    padding: 20px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  header h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px;
    font-weight: 400;
    letter-spacing: 0.02em;
  }
  header .subtitle {
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--gold);
    margin-top: 2px;
  }
  header .status {
    font-size: 12px;
    color: rgba(245,240,232,0.6);
  }
  .container { max-width: 1200px; margin: 0 auto; padding: 40px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; }
  @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
  .card {
    background: white;
    border: 1px solid var(--light);
    border-radius: 4px;
    padding: 28px;
  }
  .card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 500;
    color: var(--green);
    margin-bottom: 6px;
  }
  .card-desc {
    font-size: 12px;
    color: var(--mid);
    margin-bottom: 20px;
    line-height: 1.5;
  }
  label {
    display: block;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--mid);
    margin-bottom: 6px;
    margin-top: 14px;
  }
  label:first-of-type { margin-top: 0; }
  input[type="text"], select, textarea {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--light);
    border-radius: 3px;
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    background: var(--cream);
    color: var(--dark);
    outline: none;
    transition: border-color 0.2s;
  }
  input[type="text"]:focus, select:focus, textarea:focus {
    border-color: var(--green);
  }
  textarea { resize: vertical; min-height: 80px; }
  button {
    margin-top: 16px;
    padding: 12px 24px;
    background: var(--green);
    color: var(--cream);
    border: none;
    border-radius: 3px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.2s;
    width: 100%;
  }
  button:hover { background: #1f3329; }
  button:disabled { background: var(--mid); cursor: not-allowed; }
  .output-section {
    background: white;
    border: 1px solid var(--light);
    border-radius: 4px;
    padding: 28px;
    margin-top: 24px;
  }
  .output-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  .output-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 18px;
    color: var(--green);
  }
  .output-meta {
    font-size: 11px;
    color: var(--mid);
  }
  .output-box {
    background: var(--cream);
    border: 1px solid var(--light);
    border-radius: 3px;
    padding: 20px;
    font-size: 13px;
    line-height: 1.7;
    white-space: pre-wrap;
    max-height: 500px;
    overflow-y: auto;
    font-family: 'Inter', sans-serif;
    min-height: 100px;
    color: var(--dark);
  }
  .output-box.streaming::after {
    content: '▌';
    animation: blink 1s infinite;
    color: var(--gold);
  }
  @keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
  .copy-btn {
    margin-top: 12px;
    background: transparent;
    border: 1px solid var(--green);
    color: var(--green);
    width: auto;
    padding: 8px 16px;
  }
  .copy-btn:hover { background: var(--green); color: var(--cream); }
  .saved-files {
    margin-top: 12px;
    font-size: 11px;
    color: var(--gold);
  }
  .spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid var(--gold);
    border-top-color: transparent;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin-right: 8px;
    vertical-align: middle;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .tabs { display: flex; gap: 0; margin-bottom: 24px; border-bottom: 2px solid var(--light); }
  .tab {
    padding: 12px 20px;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer;
    color: var(--mid);
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    transition: all 0.2s;
    background: none;
    border-top: none;
    border-left: none;
    border-right: none;
    width: auto;
    margin-top: 0;
  }
  .tab.active { color: var(--green); border-bottom-color: var(--green); }
  .tab:hover:not(.active) { color: var(--dark); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
</style>
</head>
<body>
<header>
  <div>
    <h1>Belle Étage</h1>
    <div class="subtitle">Automation Control Center</div>
  </div>
  <div class="status">Powered by Claude AI</div>
</header>

<div class="container">
  <div class="tabs">
    <button class="tab active" onclick="switchTab('newsletter')">Newsletter</button>
    <button class="tab" onclick="switchTab('social')">Social Media</button>
    <button class="tab" onclick="switchTab('email')">Email</button>
    <button class="tab" onclick="switchTab('research')">Research</button>
    <button class="tab" onclick="switchTab('analytics')">Analytics</button>
    <button class="tab" onclick="switchTab('contentbank')">Content Bank</button>
  </div>

  <!-- NEWSLETTER TAB -->
  <div id="tab-newsletter" class="tab-content active">
    <div class="grid">
      <div class="card">
        <div class="card-title">Newsletter Generator</div>
        <div class="card-desc">Generate a complete newsletter issue in the brand voice. Ready to paste into Beehiiv.</div>
        <label>Topic</label>
        <input type="text" id="nl-topic" placeholder="e.g. magnesium and sleep quality" />
        <label>Additional Context (optional)</label>
        <textarea id="nl-context" placeholder="Any specific angle, product to feature, or seasonal note..."></textarea>
        <button onclick="runBot('newsletter')" id="btn-newsletter">Generate Newsletter</button>
      </div>
      <div class="card">
        <div class="card-title">Batch Newsletter Plan</div>
        <div class="card-desc">Generate 4 newsletter topics at once for a full month of content planning.</div>
        <label>Theme or Focus Area</label>
        <input type="text" id="nl-batch-theme" placeholder="e.g. sleep optimization, gut health, stress..." />
        <button onclick="runBot('newsletter_batch')" id="btn-newsletter-batch">Generate 4 Topics</button>
      </div>
    </div>
  </div>

  <!-- SOCIAL TAB -->
  <div id="tab-social" class="tab-content">
    <div class="grid">
      <div class="card">
        <div class="card-title">Instagram Captions</div>
        <div class="card-desc">Generate 5 Instagram captions with hashtags and visual direction.</div>
        <label>Topic</label>
        <input type="text" id="ig-topic" placeholder="e.g. omega-3 and brain health" />
        <button onclick="runBot('instagram')" id="btn-instagram">Generate Captions</button>
      </div>
      <div class="card">
        <div class="card-title">Pinterest Pins</div>
        <div class="card-desc">Generate 5 Pinterest pin titles and descriptions, optimized for search.</div>
        <label>Topic</label>
        <input type="text" id="pin-topic" placeholder="e.g. vitamin D deficiency signs" />
        <button onclick="runBot('pinterest')" id="btn-pinterest">Generate Pins</button>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Weekly Content Plan</div>
      <div class="card-desc">Generate a full 7-day social media schedule around one theme — ready for Buffer or Later.</div>
      <label>Weekly Theme</label>
      <input type="text" id="weekly-theme" placeholder="e.g. women's hormone health" />
      <button onclick="runBot('weekly_plan')" id="btn-weekly-plan">Generate Weekly Plan</button>
    </div>
  </div>

  <!-- EMAIL TAB -->
  <div id="tab-email" class="tab-content">
    <div class="grid">
      <div class="card">
        <div class="card-title">Respond to Subscriber</div>
        <div class="card-desc">Paste a subscriber's email and get a warm, on-brand response drafted instantly.</div>
        <label>Subscriber Name (optional)</label>
        <input type="text" id="sub-name" placeholder="e.g. Sarah" />
        <label>Subscriber's Email</label>
        <textarea id="sub-email" placeholder="Paste the subscriber's email here..."></textarea>
        <button onclick="runBot('email_response')" id="btn-email-response">Draft Response</button>
      </div>
      <div class="card">
        <div class="card-title">Broadcast Email</div>
        <div class="card-desc">Write a short personal broadcast to your whole list — a tip, recommendation, or update.</div>
        <label>What's the email about?</label>
        <input type="text" id="broadcast-topic" placeholder="e.g. my current morning supplement stack" />
        <button onclick="runBot('broadcast')" id="btn-broadcast">Write Broadcast</button>
      </div>
    </div>
  </div>

  <!-- RESEARCH TAB -->
  <div id="tab-research" class="tab-content">
    <div class="grid">
      <div class="card">
        <div class="card-title">Ingredient Deep Dive</div>
        <div class="card-desc">Get a science-backed, brand-voice summary of any supplement ingredient.</div>
        <label>Ingredient</label>
        <input type="text" id="ingredient" placeholder="e.g. ashwagandha, berberine, NMN..." />
        <label>Format</label>
        <select id="research-format">
          <option value="summary">Summary (newsletter-ready, 200-300 words)</option>
          <option value="deep_dive">Deep Dive (full newsletter, 500-700 words)</option>
          <option value="comparison">Forms Comparison</option>
        </select>
        <button onclick="runBot('ingredient')" id="btn-ingredient">Research Ingredient</button>
      </div>
      <div class="card">
        <div class="card-title">Product Evaluation</div>
        <div class="card-desc">Evaluate any supplement product for recommendation or affiliate partnership.</div>
        <label>Product Name</label>
        <input type="text" id="product-name" placeholder="e.g. Thorne Magnesium Bisglycinate" />
        <label>Product Details (optional)</label>
        <textarea id="product-details" placeholder="Ingredients, dose, certifications, etc..."></textarea>
        <button onclick="runBot('product_eval')" id="btn-product-eval">Evaluate Product</button>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Content Calendar Topics</div>
      <div class="card-desc">Generate 12-15 newsletter topic ideas for the next few months.</div>
      <label>Focus Area</label>
      <input type="text" id="calendar-focus" placeholder="e.g. women's health, longevity, sleep..." />
      <button onclick="runBot('calendar')" id="btn-calendar">Generate Topics</button>
    </div>
  </div>

  <!-- ANALYTICS TAB -->
  <div id="tab-analytics" class="tab-content">
    <div class="grid">
      <div class="card">
        <div class="card-title">Weekly Performance Report</div>
        <div class="card-desc">Enter this week's numbers and get a plain-English report with your top 3 priorities.</div>
        <label>Newsletter Subscribers</label>
        <input type="text" id="an-subscribers" placeholder="e.g. 247" />
        <label>New Subscribers This Week</label>
        <input type="text" id="an-new-subs" placeholder="e.g. 31" />
        <label>Email Open Rate</label>
        <input type="text" id="an-open-rate" placeholder="e.g. 44%" />
        <label>Instagram Followers</label>
        <input type="text" id="an-ig-followers" placeholder="e.g. 892" />
        <label>Affiliate Revenue This Week</label>
        <input type="text" id="an-revenue" placeholder="e.g. $67.20" />
        <label>Anything else to note (optional)</label>
        <textarea id="an-notes" placeholder="e.g. posted 3 times this week, launched new product page..."></textarea>
        <button onclick="runBot('analytics_report')" id="btn-analytics-report">Generate Report</button>
      </div>
      <div class="card">
        <div class="card-title">30-Day Growth Strategy</div>
        <div class="card-desc">Describe where you are now and what you want to achieve — get a week-by-week action plan.</div>
        <label>Current State</label>
        <textarea id="an-current" placeholder="e.g. 200 newsletter subscribers, just started Instagram, no affiliate sales yet..."></textarea>
        <label>Your Goal</label>
        <input type="text" id="an-goal" placeholder="e.g. reach 1,000 subscribers and $500/month affiliate income" />
        <button onclick="runBot('growth_strategy')" id="btn-growth-strategy">Generate Strategy</button>
      </div>
    </div>
  </div>

  <!-- CONTENT BANK TAB -->
  <div id="tab-contentbank" class="tab-content">
    <div class="card">
      <div class="card-title">Generate Full Content Bank</div>
      <div class="card-desc">Generate weeks of content at once — 4 newsletters, 20 Instagram captions, 10 Pinterest pins, and 5 email broadcasts all in one go. Takes about 5 minutes.</div>
      <label>Overall Theme or Season</label>
      <input type="text" id="cb-theme" placeholder="e.g. summer wellness, back to school health, sleep month..." />
      <label>Any products to feature?</label>
      <input type="text" id="cb-products" placeholder="e.g. Thorne Magnesium, AG1, Nordic Naturals Omega-3 (optional)" />
      <button onclick="runBot('content_bank')" id="btn-content-bank">Generate Full Content Bank</button>
    </div>
    <div class="card" style="margin-top:24px;">
      <div class="card-title">Quick Batch — Newsletters Only</div>
      <div class="card-desc">Generate 4 newsletter issues on different topics within one theme. Ready to schedule for the month.</div>
      <label>Monthly Theme</label>
      <input type="text" id="cb-nl-theme" placeholder="e.g. gut health, hormonal balance, longevity..." />
      <button onclick="runBot('newsletter_batch')" id="btn-cb-newsletters">Generate 4 Newsletters</button>
    </div>
  </div>

  <!-- OUTPUT SECTION -->
  <div class="output-section" id="output-section" style="display:none;">
    <div class="output-header">
      <div class="output-title" id="output-title">Output</div>
      <div class="output-meta" id="output-meta"></div>
    </div>
    <div class="output-box" id="output-box"></div>
    <div style="display:flex; gap: 12px; align-items:center; flex-wrap:wrap;">
      <button class="copy-btn" onclick="copyOutput()">Copy to Clipboard</button>
      <div class="saved-files" id="saved-notice"></div>
    </div>
  </div>
</div>

<script>
  function switchTab(name) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    event.target.classList.add('active');
  }

  function setLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (loading) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Generating...';
    } else {
      btn.disabled = false;
      btn.innerHTML = btn.getAttribute('data-original') || 'Generate';
    }
  }

  async function runBot(botType) {
    const btnMap = {
      newsletter: 'btn-newsletter',
      newsletter_batch: 'btn-newsletter-batch',
      instagram: 'btn-instagram',
      pinterest: 'btn-pinterest',
      weekly_plan: 'btn-weekly-plan',
      email_response: 'btn-email-response',
      broadcast: 'btn-broadcast',
      ingredient: 'btn-ingredient',
      product_eval: 'btn-product-eval',
      calendar: 'btn-calendar',
      analytics_report: 'btn-analytics-report',
      growth_strategy: 'btn-growth-strategy',
      content_bank: 'btn-content-bank'
    };

    const btnId = btnMap[botType];
    const btn = document.getElementById(btnId);
    if (!btn.getAttribute('data-original')) {
      btn.setAttribute('data-original', btn.textContent);
    }

    const payload = { bot_type: botType };

    // Collect inputs by bot type
    if (botType === 'newsletter') {
      payload.topic = document.getElementById('nl-topic').value || 'wellness optimization';
      payload.context = document.getElementById('nl-context').value;
    } else if (botType === 'newsletter_batch') {
      payload.theme = document.getElementById('nl-batch-theme').value || 'general wellness';
    } else if (botType === 'instagram') {
      payload.topic = document.getElementById('ig-topic').value || 'supplement quality';
    } else if (botType === 'pinterest') {
      payload.topic = document.getElementById('pin-topic').value || 'wellness tips';
    } else if (botType === 'weekly_plan') {
      payload.theme = document.getElementById('weekly-theme').value || 'general wellness';
    } else if (botType === 'email_response') {
      payload.name = document.getElementById('sub-name').value;
      payload.email = document.getElementById('sub-email').value;
    } else if (botType === 'broadcast') {
      payload.topic = document.getElementById('broadcast-topic').value;
    } else if (botType === 'ingredient') {
      payload.ingredient = document.getElementById('ingredient').value || 'magnesium';
      payload.format = document.getElementById('research-format').value;
    } else if (botType === 'product_eval') {
      payload.product = document.getElementById('product-name').value;
      payload.details = document.getElementById('product-details').value;
    } else if (botType === 'calendar') {
      payload.focus = document.getElementById('calendar-focus').value || 'general wellness';
    } else if (botType === 'analytics_report') {
      payload.subscribers = document.getElementById('an-subscribers').value;
      payload.new_subs = document.getElementById('an-new-subs').value;
      payload.open_rate = document.getElementById('an-open-rate').value;
      payload.ig_followers = document.getElementById('an-ig-followers').value;
      payload.revenue = document.getElementById('an-revenue').value;
      payload.notes = document.getElementById('an-notes').value;
    } else if (botType === 'growth_strategy') {
      payload.current = document.getElementById('an-current').value;
      payload.goal = document.getElementById('an-goal').value;
    } else if (botType === 'content_bank') {
      payload.theme = document.getElementById('cb-theme').value || 'general wellness';
      payload.products = document.getElementById('cb-products').value;
    }

    setLoading(btnId, true);

    const outputSection = document.getElementById('output-section');
    const outputBox = document.getElementById('output-box');
    const outputTitle = document.getElementById('output-title');
    const outputMeta = document.getElementById('output-meta');
    const savedNotice = document.getElementById('saved-notice');

    outputSection.style.display = 'block';
    outputBox.textContent = 'Claude is writing... this takes 15-30 seconds.';
    outputBox.classList.add('streaming');
    outputTitle.textContent = 'Generating...';
    outputMeta.textContent = new Date().toLocaleTimeString();
    savedNotice.textContent = '';
    outputSection.scrollIntoView({ behavior: 'smooth' });

    try {
      const response = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      outputBox.classList.remove('streaming');
      if (data.error) {
        outputBox.textContent = 'Error: ' + data.error;
      } else {
        outputBox.textContent = data.text;
        outputTitle.textContent = 'Generated Content';
        if (data.saved_to) {
          savedNotice.textContent = 'Saved: ' + data.saved_to;
        }
      }
    } catch (err) {
      outputBox.classList.remove('streaming');
      outputBox.textContent = 'Error: ' + err.message;
    }

    setLoading(btnId, false);
  }

  function copyOutput() {
    const text = document.getElementById('output-box').textContent;
    navigator.clipboard.writeText(text).then(() => {
      const btn = event.target;
      btn.textContent = 'Copied!';
      setTimeout(() => btn.textContent = 'Copy to Clipboard', 2000);
    });
  }
</script>
</body>
</html>"""


def run_bot(bot_type: str, params: dict):
    """Run a bot and return the full response as a dict."""
    import anthropic as _anthropic
    from brand_voice import BRAND_SYSTEM_PROMPT

    client = _anthropic.Anthropic()

    content_dir = os.path.join(os.path.dirname(__file__), "..", "content")

    def save_to_file(content: str, subfolder: str, label: str) -> str:
        folder = os.path.join(content_dir, subfolder)
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        slug = label.lower().replace(" ", "-")[:25]
        path = os.path.join(folder, f"{timestamp}_{slug}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"GENERATED: {datetime.now().isoformat()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(content)
        return path

    # Build prompt based on bot type
    prompts = {
        "newsletter": f"""Write a complete newsletter issue for Belle Étage.

TOPIC: {params.get('topic', 'wellness optimization')}
{f"ADDITIONAL CONTEXT: {params.get('context')}" if params.get('context') else ""}

Format:
SUBJECT LINE: [max 50 chars]
PREVIEW TEXT: [40-90 chars]
---
[Newsletter body, 400-600 words. Personal opening, 2-3 sections with headers, ritual/question at end.]
Sign off: With warmth, // Belle Étage""",

        "newsletter_batch": f"""Generate 4 distinct newsletter topic ideas for Belle Étage.
Theme: {params.get('theme', 'general wellness')}

For each topic provide:
- Title
- Hook/angle (what makes it timely or interesting)
- Product tie-in (if natural)
- Opening line suggestion

Make them specific, science-forward, and distinct from each other.""",

        "instagram": f"""Generate 5 Instagram captions for Belle Étage on: {params.get('topic', 'supplement quality')}

For each:
CAPTION [n]:
[2-4 sentence caption in brand voice]
HASHTAGS: [5-8 tags]
VISUAL: [ideal image concept]
---""",

        "pinterest": f"""Generate 5 Pinterest pins for Belle Étage on: {params.get('topic', 'wellness')}

For each:
TITLE: [max 100 chars, keyword-rich]
DESCRIPTION: [150-300 chars, helpful]
BOARD: [board name]
---""",

        "weekly_plan": f"""Create a 7-day social media content plan for Belle Étage.
Weekly theme: {params.get('theme', 'general wellness')}

Include: 3 Instagram Feed posts, 2 Instagram Stories concepts, 2 Pinterest pins.
For each: day, platform, content type, full caption, hashtags.""",

        "email_response": f"""Draft a response to this subscriber email for Belle Étage.
{"Subscriber name: " + params.get('name') if params.get('name') else "No name provided."}

SUBSCRIBER'S EMAIL:
{params.get('email', '(No email provided)')}

100-200 words. Warm, specific, honest. Never diagnose. Sign off as: Belle Étage Team""",

        "broadcast": f"""Write a short personal broadcast email from Belle Étage founder.
Topic: {params.get('topic', 'a wellness tip')}

80-120 words. Personal, warm, like a note from a friend who happens to run this brand.""",

        "ingredient": f"""Research and write about: {params.get('ingredient', 'magnesium')}

Format: {'200-300 word newsletter-ready summary' if params.get('format') == 'summary' else '500-700 word deep dive for a full newsletter issue covering mechanism, research, forms, dosing, and buying guidance' if params.get('format') == 'deep_dive' else 'comparison of the main forms with bioavailability and use-case differences'}

Be scientifically accurate, honest about evidence strength. Brand voice: intelligent, warm, accessible.""",

        "product_eval": f"""Evaluate this supplement product for Belle Étage.
PRODUCT: {params.get('product', '(product name)')}
{f"DETAILS: {params.get('details')}" if params.get('details') else ""}

Evaluate: ingredient forms, dosing vs research, certifications, manufacturing transparency, value, who it's for, any concerns. End with clear recommendation. 250-350 words. Be honest.""",

        "calendar": f"""Generate 12-15 newsletter topic ideas for Belle Étage.
Focus area: {params.get('focus', 'general wellness')}

For each: topic title, hook/angle, natural product tie-in, reader interest (High/Medium).
Make them specific, science-forward, and play to nutrition and chemistry credibility.""",

        "analytics_report": f"""You are the business analytics advisor for Belle Étage.

This week's metrics:
- Newsletter subscribers: {params.get('subscribers', 'unknown')}
- New subscribers this week: {params.get('new_subs', 'unknown')}
- Email open rate: {params.get('open_rate', 'unknown')}
- Instagram followers: {params.get('ig_followers', 'unknown')}
- Affiliate revenue this week: {params.get('revenue', 'unknown')}
- Additional notes: {params.get('notes', 'none')}

Write a weekly performance report. Include:
1. HEADLINE: One sentence on how the week went
2. WHAT'S WORKING: 2-3 specific wins and why
3. WHAT TO WATCH: 1-2 things needing attention
4. THIS WEEK'S PRIORITIES: 3 specific actionable tasks ranked by impact
5. 30-DAY OUTLOOK: Where this is heading if trends continue

Under 300 words. Honest, specific, encouraging. Like a trusted advisor.""",

        "growth_strategy": f"""Create a 30-day growth strategy for Belle Étage.

CURRENT STATE: {params.get('current', 'early stage, just launched')}
GOAL: {params.get('goal', 'grow newsletter and generate affiliate income')}

Week 1: Foundation & quick wins
Week 2: Amplification
Week 3: Conversion
Week 4: Scale what's working

For each week: 3 specific daily actions, expected outcome, success metric.
Every recommendation should take 1-2 hours max. Be specific — no vague advice.""",

        "content_bank": f"""Generate a full content bank for Belle Étage around the theme: {params.get('theme', 'general wellness')}.
{f"Products to feature: {params.get('products')}" if params.get('products') else ""}

Generate ALL of the following:

--- 4 NEWSLETTER SUBJECTS ---
Write 4 compelling subject lines with preview text, one per week for the month.

--- 4 NEWSLETTER OPENINGS ---
Write the opening paragraph (3-4 sentences) for each newsletter.

--- 10 INSTAGRAM CAPTIONS ---
5 educational, 3 personal/founder, 2 product spotlights. Each with 6 hashtags.

--- 5 PINTEREST PIN TITLES ---
Keyword-rich, evergreen, highly searchable.

--- 3 EMAIL BROADCASTS ---
Short personal notes (80-100 words each) — one tip, one product rec, one personal story.

Label each section clearly. Make everything ready to copy-paste directly into Beehiiv, Buffer, or Gmail."""
    }

    prompt = prompts.get(bot_type, "Generate helpful wellness content.")

    subfolder_map = {
        "newsletter": "newsletters", "newsletter_batch": "newsletters",
        "instagram": "social", "pinterest": "social", "weekly_plan": "social",
        "email_response": "emails", "broadcast": "emails",
        "ingredient": "research", "product_eval": "research", "calendar": "research",
        "analytics_report": "analytics", "growth_strategy": "analytics",
        "content_bank": "content_bank"
    }

    try:
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            thinking={"type": "adaptive"},
            system=BRAND_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )

        full_text = ""
        for block in message.content:
            if block.type == "text":
                full_text += block.text

        label = params.get('topic') or params.get('theme') or params.get('ingredient') or params.get('product') or bot_type
        saved_path = save_to_file(full_text, subfolder_map.get(bot_type, "misc"), f"{bot_type}_{label}")

        return {"text": full_text, "saved_to": os.path.basename(saved_path)}

    except Exception as e:
        return {"error": str(e)}


@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    bot_type = data.get("bot_type", "newsletter")
    result = run_bot(bot_type, data)
    return jsonify(result)


@app.route("/files")
def list_files():
    """List all generated content files."""
    content_dir = os.path.join(os.path.dirname(__file__), "..", "content")
    files = []
    if os.path.exists(content_dir):
        for root, dirs, filenames in os.walk(content_dir):
            for f in filenames:
                path = os.path.join(root, f)
                files.append({
                    "name": f,
                    "category": os.path.basename(root),
                    "path": path,
                    "created": datetime.fromtimestamp(os.path.getctime(path)).isoformat()
                })
    files.sort(key=lambda x: x["created"], reverse=True)
    return jsonify(files)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "=" * 55)
    print("  Belle Étage — Automation Dashboard")
    print("=" * 55)
    print(f"  Open your browser to: http://localhost:{port}")
    print("  Press Ctrl+C to stop")
    print("=" * 55 + "\n")
    app.run(debug=False, host="0.0.0.0", port=port, threaded=True)
