import os
import json
import requests
from openai import OpenAI

# Their proxy injects these - API_BASE_URL is the LLM proxy, NOT the env URL
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# The environment always lives here
ENV_URL = "https://laxmimb-bike-safety-env.hf.space"
env_headers = {}

# LLM client uses API_BASE_URL as their proxy
llm_client = OpenAI(
    api_key=HF_TOKEN if HF_TOKEN else "dummy-key",
    base_url=API_BASE_URL,
)

SYSTEM_PROMPT = """You are an expert email triage agent. Given an email, return ONLY a valid JSON object with no extra text, no markdown, no explanation:
{"category": "...", "priority": "...", "department": "...", "is_spam": true/false}

Rules:
- category must be one of: spam, complaint, inquiry, request, feedback
- priority must be one of: urgent, normal, low
  * urgent = system down, financial issue, time-sensitive, ASAP
  * low = spam, feature requests, general feedback
  * normal = everything else
- department must be one of: billing, technical, general, sales
  * billing = payments, invoices, refunds, subscriptions
  * technical = bugs, errors, access issues, API
  * sales = pricing, plans, enterprise, upgrades
  * general = everything else
- is_spam = true ONLY for prize scams, phishing, get-rich schemes, lottery

Spam emails always get: category=spam, priority=low, department=general, is_spam=true"""


def call_llm(subject: str, sender: str, body: str) -> dict:
    """Call the LLM proxy to classify an email."""
    email_text = f"Subject: {subject}\nFrom: {sender}\n\nBody:\n{body}"
    response = llm_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text}
        ],
        temperature=0,
        max_tokens=150
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def heuristic_classify(subject: str, sender: str, body: str) -> dict:
    """Fallback rule-based classifier."""
    text = (subject + " " + body + " " + sender).lower()

    spam_words = ["win", "prize", "free iphone", "claim", "lottery", "make money",
                  "fast cash", "bank details", "selected", "vacation package",
                  "processing fee", "congratulations", "million", "transfer"]
    spam_domains = [".xyz", ".tk", ".biz", "win-now", "fast-cash", "free-stuff",
                    "free-travel", "random-lottery", "win-prizes"]

    if any(k in text for k in spam_words) or any(d in sender.lower() for d in spam_domains):
        return {"category": "spam", "priority": "low", "department": "general", "is_spam": True}

    urgent = ["urgent", "down", "crash", "outage", "immediately", "asap",
              "cannot access", "double charged", "end of day", "end of week",
              "by friday", "costing", "critical", "all users affected"]
    billing = ["invoice", "billing", "charge", "refund", "payment", "subscription",
               "cancel", "charged twice", "wrong tax", "incorrect"]
    technical = ["bug", "crash", "error", "not working", "api", "password",
                 "login", "access", "ios", "update", "server", "production"]
    sales = ["pricing", "enterprise", "quote", "plan", "upgrade", "500 users", "procurement"]

    priority = "urgent" if any(k in text for k in urgent) else "normal"

    if any(k in text for k in billing):
        dept = "billing"
        cat = "complaint" if any(w in text for w in ["charged", "refund", "wrong", "incorrect", "twice"]) else "request"
    elif any(k in text for k in technical):
        dept = "technical"
        cat = "complaint" if any(w in text for w in ["cannot", "not working", "crash", "down", "outage"]) else "inquiry"
    elif any(k in text for k in sales):
        dept = "sales"
        cat = "inquiry"
    else:
        dept = "general"
        cat = "feedback" if any(w in text for w in ["love", "great", "outstanding", "impressed", "thank"]) else "request"

    return {"category": cat, "priority": priority, "department": dept, "is_spam": False}


def get_action(obs: dict) -> dict:
    subject = obs.get("subject", "")
    sender = obs.get("sender", "")
    body = obs.get("body", "")

    try:
        result = call_llm(subject, sender, body)
        assert result.get("category") in ["spam", "complaint", "inquiry", "request", "feedback"]
        assert result.get("priority") in ["urgent", "normal", "low"]
        assert result.get("department") in ["billing", "technical", "general", "sales"]
        assert isinstance(result.get("is_spam"), bool)
        return result
    except Exception as e:
        print(f"LLM call failed: {e}, falling back to heuristic", flush=True)
        return heuristic_classify(subject, sender, body)


def safe_get_obs(data: dict) -> dict:
    if "observation" in data:
        return data["observation"]
    return data


def run_task(task_name: str) -> float:
    print(f"[START] task={task_name}", flush=True)

    try:
        r = requests.post(f"{ENV_URL}/reset?task={task_name}", headers=env_headers, timeout=30)
        r.raise_for_status()
        obs = safe_get_obs(r.json())
    except Exception as e:
        print(f"Reset failed for {task_name}: {e}", flush=True)
        print(f"[END] task={task_name} score=0.0 steps=0", flush=True)
        return 0.0

    step_num = 0
    total_reward = 0.0

    while True:
        try:
            step_num += 1
            action = get_action(obs)

            r = requests.post(f"{ENV_URL}/step", json=action, headers=env_headers, timeout=30)
            r.raise_for_status()
            result = r.json()

            reward = float(result.get("reward", 0.0))
            total_reward += reward
            done = result.get("done", False)
            obs = safe_get_obs(result)

            print(f"[STEP] step={step_num} reward={round(reward, 4)}", flush=True)

            if done:
                break

            if step_num >= 20:
                break

        except Exception as e:
            print(f"Step {step_num} error: {e}", flush=True)
            print(f"[STEP] step={step_num} reward=0.0", flush=True)
            break

    score = round(total_reward / step_num, 4) if step_num > 0 else 0.0
    print(f"[END] task={task_name} score={score} steps={step_num}", flush=True)
    return score


TASKS = ["spam_detection", "priority_routing", "full_triage"]

if __name__ == "__main__":
    for task in TASKS:
        try:
            run_task(task)
        except Exception as e:
            print(f"Task {task} crashed: {e}", flush=True)
            print(f"[END] task={task} score=0.0 steps=0", flush=True)
