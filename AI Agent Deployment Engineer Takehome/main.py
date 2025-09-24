import os
import json
import logging
import argparse
from typing import List, Dict, Any, Optional
from openai import OpenAI

"""""
If I had two more hours, I would extend the architecture by introducing a more structured multi-agent workflow. 
The system would use a lightweight classifier model to quickly categorize the user’s request, then a dedicated “Storyteller” model 
fine-tuned or few-shot primed for children’s storytelling. The draft would always be passed through a “Judge” model using a JSON-schema 
rubric to enforce safety, clarity, and age-appropriateness. If revisions were required, a “Reviser” agent would apply targeted changes before returning the story.

To optimize results further, I would:

- Add few-shot exemplars per story category (bedtime-calming, adventure, animals) to improve consistency.
- Implement schema validation (e.g., Pydantic) so Judge outputs are always machine-readable.
- Add a fast, deterministic model (low-temperature) for classification/judging and reserve the higher-creativity storyteller pass for generation.
- Optionally expose a user feedback loop with guardrails (max two revisions), so the final story balances both internal QC and user preference.

This architecture ensures stories are imaginative yet always safe, age-appropriate, and polished, while keeping runtime efficient.
"""""

# Config
DEFAULT_MODEL = "gpt-3.5-turbo"
MAX_INTERNAL_REVISIONS = 1   # Judge/Reviser loop before user sees story
MAX_USER_REVISIONS = 2       # Prevent endless user feedback loop
TIMEOUT_SECS = 60

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
)
logger = logging.getLogger("story_system")

# OpenAI Call Helper

def ensure_api_key():
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY not set.")



client = OpenAI()

def chat_once(messages, temperature=0.5, max_tokens=1000) -> str:
    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp.choices[0].message.content

# Agents
def classify_request(user_request: str) -> str:
    """Categorize the request for tailored generation."""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a story category classifier for bedtime stories (ages 5–10).\n"
                "Read the request and assign ONE of these categories:\n"
                "['animals', 'adventure', 'friendship', 'bedtime-calming', 'fantasy', 'other'].\n"
                "Return ONLY the category name."
            ),
        },
        {"role": "user", "content": user_request},
    ]
    return chat_once(messages, temperature=0.0, max_tokens=10).strip().lower()

def storyteller_messages(user_request: str, category: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                f'You are "The Careful Storyteller," writing for ages 5–10. '
                f"Category: {category}. "
                "Always:\n"
                "- Use a classic story arc (setup → challenge → resolution).\n"
                "- Keep language simple, vivid, and warm.\n"
                "- Avoid violence, horror, or adult topics.\n"
                "Output as Markdown with:\n# Title\n## Story\n## Moral"
            ),
        },
        {"role": "user", "content": user_request},
    ]

def judge_messages(user_request: str, story_md: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                'You are "The Gentle Judge," reviewing a story for ages 5–10.\n'
                "Return ONLY JSON with keys:\n"
                "{age_appropriateness, clarity_simple_language, coherence_story_arc,\n"
                "warmth_and_kindness, engagement_imagination, safety_flags,\n"
                "required_changes, recommendations, require_revision, summary}"
            ),
        },
        {
            "role": "user",
            "content": f"USER REQUEST:\n{user_request}\n\nSTORY:\n{story_md}",
        },
    ]

def reviser_messages(user_request: str, story_md: str, feedback: str) -> List[Dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You are 'The Skilled Reviser.' Improve the story while keeping it safe and age-appropriate. "
                "Respect the Markdown structure (# Title, ## Story, ## Moral)."
            ),
        },
        {
            "role": "user",
            "content": (
                f"ORIGINAL REQUEST:\n{user_request}\n\n"
                f"CURRENT STORY:\n{story_md}\n\n"
                f"FEEDBACK:\n{feedback}"
            ),
        },
    ]


# Helpers
def parse_judge(text: str) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        return {"require_revision": True, "required_changes": ["Fix JSON parsing"], "safety_flags": []}

# Pipeline
def generate_polished_story(user_request: str) -> str:
    """Classifier → Storyteller → Judge/Reviser loop (internal quality check)."""
    category = classify_request(user_request)
    story = chat_once(storyteller_messages(user_request, category), temperature=0.7)

    for _ in range(MAX_INTERNAL_REVISIONS + 1):
        judge_out = chat_once(judge_messages(user_request, story), temperature=0.0, max_tokens=500)
        judge = parse_judge(judge_out)
        if not judge.get("require_revision", False):
            return story  # Accepted by judge
        story = chat_once(reviser_messages(user_request, story, "Apply judge feedback"), temperature=0.5)
    return story

def user_feedback_loop(user_request: str, story: str) -> str:
    """Interactive loop: show story, ask user, allow up to MAX_USER_REVISIONS."""
    for i in range(MAX_USER_REVISIONS + 1):
        print("\n=== STORY DRAFT ===\n")
        print(story)
        feedback = input("\nHow does that sound? Enter feedback (or press Enter to accept): ").strip()
        if not feedback:
            print("\n Final story accepted.")
            return story
        story = chat_once(reviser_messages(user_request, story, feedback), temperature=0.6)
    print("\n Reached max user revisions. Returning last version.")
    return story

# CLI
def main():
    parser = argparse.ArgumentParser(description="Bedtime Story Generator (ages 5–10)")
    parser.add_argument("-p", "--prompt", type=str, help="Story request", required=False)
    args = parser.parse_args()

    ensure_api_key()
    user_request = args.prompt or input("What kind of story do you want? ")

    polished = generate_polished_story(user_request)
    final_story = user_feedback_loop(user_request, polished)
    print("\n=== FINAL STORY ===\n")
    print(final_story)

if __name__ == "__main__":
    main()
