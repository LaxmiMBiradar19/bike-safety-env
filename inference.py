import os
import json
import requests
from openai import OpenAI

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

ENV_URL = "https://laxmimb-bike-safety-env.hf.space"
env_headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

# LLM client pointing to their proxy
llm_client = OpenAI(
    api_key=HF_TOKEN if HF_TOKEN else "dummy-key",
    base_url=API_BASE_URL
)

SYSTEM_PROMPT = """You are an expert email triage agent. Given an email, return ONLY a JSON object with no extra text:
{"category": "...", "priority": "...", "department": "...", "is_spam": true/false}

Rules:
- category: spam, complaint, inquiry, request, or feedback
- priority: urgent (system down, financial issue, time-sensitive), normal, or low
- department: billing (payments/refunds), technical (bugs/access), sales (pricing/plans), general (other)
- is_spam: true for prize scams, phishing, get-rich schemes. false otherwise
Spam always gets priority=low, department=general, is_spam=true"""


def extract_obs(response_json: dict) -> dict:
    """Safely extract observation whether nested or not."""
    if "observation" in response_json:
        return response_json["observation"]
    return response_json


def get_action_llm(obs: dict) -> dict:
    subject = obs.get("subject", "")
    sender = obs.get("sender", "")
    body = obs.get("body", "")
    email_text = f"Subject: {subject}\nFrom: {sender}\n\n{body}"

    response = llm_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text}
        ],
        temperature=0,
        max_tokens=100
    )
    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    return json.loads(text)


def get_action_heuristic(obs: dict) -> dict:
    subject = obs.get("subject", "").lower()
    body = obs.get("body", "").lower()
    sender = obs.get("sender", "").lower()
    text = subject + " " + body + " " + sender

    spam_keywords = ["win", "prize", "free iphone", "claim", "lottery", "make money",
                     "fast cash", "bank details", "selected", "vacation package", "processing fee"]
    spam_domains = [".xyz", ".tk", ".biz", "win-now", "fast-cash", "free-stuff",
                    "free-travel", "random-lottery"]

    is_spam = any(k in text for k in spam_keywords) or any(d in sender for d in spam_domains)
    if is_spam:
        return {"category": "spam", "priority": "low", "department": "general", "is_spam": True}

    urgent_keywords = ["urgent", "down", "crash", "outage", "immediately", "asap",
                       "cannot access", "double charged", "end of day", "end of week",
                       "by friday", "costing"]
    billing_keywords = ["invoice", "billing", "charge", "refund", "payment",
                        "subscription", "cancel", "charged twice"]
    technical_keywords = ["bug", "crash", "error", "not working", "api", "password",
                          "login", "access", "ios", "update", "server"]
    sales_keywords = ["pricing", "enterprise", "quote", "plan", "upgrade", "500 users"]

    priority = "urgent" if any(k in text for k in urgent_keywords) else "normal"

    if any(k in text for k in billing_keywords):
        department = "billing"
        category = "complaint" if any(w in text for w in ["charged", "refund", "wrong", "incorrect"]) else "request"
    elif any(k in text for k in technical_keywords):
        department = "technical"
        category = "complaint" if any(w in text for w in ["cannot", "not working", "crash", "down", "outage"]) else "inquiry"
    elif any(k in text for k in sales_keywords):
        department = "sales"
        category = "inquiry"
    else:
        department = "general"
        category = "feedback" if any(w in text for w in ["love", "great", "outstanding", "impressed", "thank"]) else "request"

    return {"category": category, "priority": priority, "department": department, "is_spam": False}


def get_action(obs: dict) -> dict:
    try:
        return get_action_llm(obs)
    except Exception as e:
        print(f"LLM failed: {e}, using heuristic", flush=True)
        try:
            return get_action_heuristic(obs)
        except Exception as e2:
            print(f"Heuristic failed: {e2}, using default", flush=True)
            return {"category": "inquiry", "priority": "normal", "department": "general", "is_spam": False}


def run_task(task_name: str) -> float:
    print(f"[START] task={task_name}", flush=True)

    try:
        resp = requests.post(f"{ENV_URL}/reset?task={task_name}", headers=env_headers, timeout=30)
        resp.raise_for_status()
        obs = extract_obs(resp.json())
    except Exception as e:
        print(f"Reset failed: {e}", flush=True)
        print(f"[END] task={task_name} score=0.0 steps=0", flush=True)
        return 0.0

    step_num = 0
    total_reward = 0.0

    while True:
        try:
            step_num += 1
            action = get_action(obs)

            resp = requests.post(f"{ENV_URL}/step", json=action, headers=env_headers, timeout=30)
            resp.raise_for_status()
            result = resp.json()

            reward = result.get("reward", 0.0)
            total_reward += reward
            done = result.get("done", False)
            obs = extract_obs(result)

            print(f"[STEP] step={step_num} reward={round(reward, 4)}", flush=True)

            if done:
                break

        except Exception as e:
            print(f"Step {step_num} failed: {e}", flush=True)
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
