from agents import Agent
from chatkit.agents import AgentContext

title_agent = Agent[AgentContext](
    model="gpt-4.1-nano",
    name="Title generator",
    instructions="""\
Vygeneruj krátký český název konverzace mezi asistentem FAČR a uživatelem.
První zpráva uživatele je uvedena níže.
Neopakuj doslova zprávu uživatele, použij vlastní slova.
MUSÍŠ odpovědět 2–5 slovy bez interpunkce.
""",
)
