import requests
from django.conf import settings

HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_HEADERS = {"Authorization": f"Bearer {settings.HF_API_KEY}"}

def generate_study_plan(class_name, subject, total_days):
    prompt = f"""
    You are an NCERT curriculum expert.
    Create a {total_days}-day **day-wise study plan** for Class {class_name} - {subject}.
    - Cover all chapters sequentially from the NCERT syllabus.
    - Break each chapter into subtopics across the days.
    - Keep topics clear and concise.
    📌 Format strictly like this:
    Day 1: Chapter Name - Subtopic
    Day 2: Chapter Name - Subtopic
    Day 3: Chapter Name - Subtopic
    ...
    """

    response = requests.post(
        HF_API_URL,
        headers=HF_HEADERS,
        json={"inputs": prompt, "parameters": {"max_new_tokens": 800}},
    )

    if response.status_code != 200:
        raise Exception(f"Hugging Face API error: {response.text}")

    result = response.json()
    text = ""
    if isinstance(result, list) and "generated_text" in result[0]:
        text = result[0]["generated_text"]
    elif isinstance(result, dict) and "generated_text" in result:
        text = result["generated_text"]

    topics = []
    for line in text.split("\n"):
        line = line.strip()
        if line.lower().startswith("day"):
            parts = line.split(":", 1)
            if len(parts) == 2:
                topics.append(parts[1].strip())
            else:
                topics.append(line)

    return topics if topics else [f"Day {i+1}: {subject} - Topic TBD" for i in range(total_days)]
