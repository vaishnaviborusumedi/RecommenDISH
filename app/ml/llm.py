import anthropic
from app.utils.logger import logger
from config.settings import settings


client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def build_prompt(context: dict) -> str:
    user  = context["user"]
    gaps  = context["gaps"]
    recs  = context["recommendations"]
    recent = context["recent_foods"]

    rec_lines = "\n".join([
        f"  {i+1}. {r['food_name']} — {r['calories']} kcal, "
        f"{r['protein_g']}g protein, {r['fiber_g']}g fiber"
        for i, r in enumerate(recs)
    ])

    prompt = f"""You are RecommenDISH, a friendly and knowledgeable nutrition assistant.

USER PROFILE:
- Name: {user['name']}
- Goal: {user['goal'].replace('_', ' ')}
- Activity level: {user['activity_level']} out of 5

TODAY'S NUTRIENT GAPS (what they still need):
- Calories remaining: {gaps['calories_gap']} kcal
- Protein needed: {gaps['protein_gap']}g
- Carbs needed: {gaps['carbs_gap']}g
- Fat needed: {gaps['fat_gap']}g
- Fiber needed: {gaps['fiber_gap']}g

RECENTLY EATEN: {', '.join(recent) if recent else 'Nothing logged yet'}

TOP RECOMMENDED FOODS (ranked by our engine):
{rec_lines}

YOUR TASK:
Write a short, friendly, personalized meal recommendation for {user['name']}.
- Suggest how to combine 2-3 of the recommended foods into a meal
- Explain briefly WHY these foods suit their goal
- Keep it conversational, warm, and motivating
- Max 4 sentences
- Do NOT use bullet points, just natural flowing text
"""
    return prompt


def get_llm_recommendation(context: dict) -> str:
    """
    Send recommendation context to Claude and get
    a natural language meal suggestion back.
    """
    prompt = build_prompt(context)

    logger.info(f"Sending prompt to {settings.llm_model}...")

    try:
        message = client.messages.create(
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        response = message.content[0].text
        logger.info("LLM response received")
        return response

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return _fallback_recommendation(context)


def _fallback_recommendation(context: dict) -> str:
    """Simple fallback if LLM call fails."""
    user = context["user"]
    recs = context["recommendations"]
    top  = recs[0]["food_name"] if recs else "a balanced meal"

    return (
        f"Hi {user['name']}! Based on your {user['goal'].replace('_',' ')} goal, "
        f"we recommend starting with {top} for your next meal. "
        f"It aligns well with your nutritional needs today."
    )