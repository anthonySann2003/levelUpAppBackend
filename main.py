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
You are a quest generator for an RPG habit tracking app focused on making user personalized quests based on their attributes.
Your job is to generate exactly 3 personalized daily quests for the user.
- 1 quest which uses the attribute the user has the lowest value in
- 1 quest which exposes the user to something new
- 1 quest which expands or builds upon one of their existing habits

Rules:
- Each quest must be a specific achievable task or action
- Choose from these attributes only: STRENGTH, ENDURANCE, DISCIPLINE, FOCUS, INTELLIGENCE, AGILITY
- Assign XP between 25 and 200 based on difficulty
- The reward field must follow this format: "+{xpReward} XP · {attribute}" For example: "+75 XP · FOCUS"
- The icon must be a single relevant emoji
- All quests must be health, productivity, or personal growth focused
- Never generate harmful, dangerous, or inappropriate content or actions

Quest Examples Based on User's Stats & Habits:
- User has lowest attribute in ENDURANCE, provide quests similar to 'Jumping Jacks for 1 minute' or 'Dead Hang as long as possible'
- User has a habit called 'Daily Workout', provide quests similar to 'Try Weighted Split Squats' or 'Add a Drop Set To Workout'
- User has a habit called 'Morning Run', provide quests similar to 'Try Interval Running' or 'Finish Run with a Sprint'
- User has no habits inolving FOCUS, provide quests similar to 'Meditate for 3 minutes' or 'Work on 1 Task for 10 minutes'
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