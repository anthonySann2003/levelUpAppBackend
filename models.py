from pydantic import BaseModel

#What the app sends to the server
#Information about the user's habits
class Habit(BaseModel):
    name: str
    attribute: str

#Information about the user's attributes and level
class UserContext(BaseModel):
    habits: list[Habit]
    attributes: dict[str, int]
    level: int

#What the server sends back
#Information about the quest to be created
class Quest(BaseModel):
    icon: str
    title: str
    reward: str
    xpReward: int
    attribute: str

#List of quests to be created
class QuestList(BaseModel):
    quests: list[Quest]
