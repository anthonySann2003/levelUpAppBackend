from fastapi import FastAPI
from dotenv import load_dotenv
from openai import OpenAI
import os
from models import UserContext, QuestList
from langsmith import traceable

load_dotenv()

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#Notes on system prompt: Not making personalized quests, not focusing on weak attributes, make it generate more specialized quests EX: User has a habit to spend time with friends, generate a quest to buy a gift for them
SYSTEM_PROMPT = """
You are a quest generator for an RPG habit tracking app called Bounties.
Your job is to generate exactly 3 personalized daily bounties for the user based on their habits and attributes.

Rules:
- Each bounty must be a short task between 1 and 15 minutes
- Choose from these attributes only: STRENGTH, ENDURANCE, DISCIPLINE, FOCUS, INTELLIGENCE, AGILITY
- Assign XP between 25 and 150 based on difficulty
- The reward field must follow this format: "+{xpReward} XP · {attribute}" For example: "+75 XP · FOCUS"
- The icon must be a single relevant emoji
- Generate a mix of quests similar to the user's existing habits and quests that expose them to something new
- Base attribute and XP choices on the user's current attribute levels — favor quests that help weaker attributes grow
- All quests must be health, productivity, or personal growth focused
- Never generate harmful, dangerous, or inappropriate content or actions
"""

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/generate-bounties")
@traceable
def generate_bounties(user: UserContext):
    try:
        #sanitize habit names to 50 characters
        sanitized_habits = [
            {"name": h.name[:50], "attribute": h.attribute}
            for h in user.habits
        ]

        user_message = f"""
        User level: {user.level}
        Current attributes: {user.attributes}
        Current habits: {sanitized_habits}
        
        Generate 3 personalized bounties for this user.
        """

        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            response_format=QuestList
        )

        result = response.choices[0].message.parsed
        return result

    except Exception as e:
        print(f"Error generating bounties: {e}")
        return QuestList(quests=[])