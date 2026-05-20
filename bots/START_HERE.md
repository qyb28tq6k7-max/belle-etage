# Belle Étage — Automation Bots

## Setup (one time only)

Open Terminal / PowerShell and run:

```
pip install anthropic flask
```

Then set your Anthropic API key (get it at https://console.anthropic.com):

**Windows:**
```
$env:ANTHROPIC_API_KEY = "sk-ant-..."
```

---

## The Dashboard (easiest — recommended)

Start the visual control panel and run all bots from your browser:

```
cd refined-remedy\bots
python dashboard.py
```

Then open **http://localhost:5000** in your browser.

The dashboard lets you:
- Generate newsletters (paste into Beehiiv)
- Generate Instagram captions and Pinterest pins
- Draft responses to subscriber emails
- Research any supplement ingredient
- Evaluate products for your affiliate list
- Plan a week of content at once

Everything is automatically saved to `refined-remedy/content/`.

---

## Individual Bots (command line)

### Newsletter Bot
```
python newsletter_bot.py "magnesium and sleep quality"
python newsletter_bot.py "omega-3 and brain health"
python newsletter_bot.py "the truth about collagen supplements"
```

### Social Media Bot
```
python social_bot.py instagram "vitamin D deficiency"
python social_bot.py pinterest "gut health tips"
python social_bot.py weekly "sleep optimization"
```

### Email Bot
```
python email_bot.py
```
(Edit the sample email at the bottom of email_bot.py)

### Research Bot
```
python research_bot.py ingredient "berberine"
python research_bot.py product "Thorne Magnesium Bisglycinate"
python research_bot.py calendar "women's hormonal health"
```

---

## Where Files Are Saved

All generated content is saved automatically:

```
refined-remedy/
  content/
    newsletters/   ← newsletter issues
    social/        ← Instagram and Pinterest content
    emails/        ← subscriber responses and broadcasts
    research/      ← ingredient deep-dives and product evals
```

---

## Tips

- The dashboard streams output in real time — you see it generate word by word
- Copy the output directly into Beehiiv, Buffer, or Gmail
- The bots use Claude Opus 4.7 — the most capable model available
- Every generation costs roughly $0.01–$0.05 depending on length
