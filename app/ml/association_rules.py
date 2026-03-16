import os
import joblib
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from sqlalchemy.orm import Session

from app.db.models import MealLog, Food
from app.utils.logger import logger
from config.settings import settings


def build_transactions(db: Session) -> list[list[str]]:
    """
    Build transaction list from meal logs.
    Each transaction = all foods a user ate in one day.
    """
    logs = (
        db.query(MealLog, Food)
        .join(Food, MealLog.food_id == Food.id)
        .order_by(MealLog.user_id, MealLog.logged_at)
        .all()
    )

    # Group by user_id + date
    buckets: dict = {}
    for log, food in logs:
        date_key = f"{log.user_id}_{log.logged_at.date()}"
        buckets.setdefault(date_key, []).append(food.name)

    transactions = [foods for foods in buckets.values() if len(foods) > 1]
    logger.info(f"Built {len(transactions)} transactions from meal logs")
    return transactions


def train_association_rules(db: Session) -> pd.DataFrame:
    """
    Run Apriori and generate association rules.
    Saves rules to disk.
    """
    transactions = build_transactions(db)

    if len(transactions) < 5:
        logger.warning("Not enough transactions to mine rules — need 5+")
        return pd.DataFrame()

    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    df = pd.DataFrame(te_array, columns=te.columns_)

    frequent_items = apriori(
        df,
        min_support=settings.min_support,
        use_colnames=True,
    )

    if frequent_items.empty:
        logger.warning("No frequent itemsets found — try lowering min_support")
        return pd.DataFrame()

    rules = association_rules(
        frequent_items,
        metric="confidence",
        min_threshold=settings.min_confidence,
    )

    rules = rules.sort_values("lift", ascending=False).reset_index(drop=True)

    os.makedirs(settings.models_dir, exist_ok=True)
    joblib.dump(rules, settings.rules_path)

    logger.info(f"Mined {len(rules)} association rules. Saved.")
    return rules


def get_rules_for_food(food_name: str) -> pd.DataFrame:
    """
    Given a food name, return all rules where it appears
    as an antecedent (i.e. what to recommend alongside it).
    """
    if not os.path.exists(settings.rules_path):
        logger.warning("No saved rules found")
        return pd.DataFrame()

    rules = joblib.load(settings.rules_path)

    if rules.empty:
        return pd.DataFrame()

    matched = rules[
        rules["antecedents"].apply(lambda x: food_name in x)
    ]
    return matched.head(5)


def get_top_consequents(food_names: list[str]) -> list[str]:
    """
    Given a list of recently eaten foods, return top
    recommended foods from association rules.
    """
    if not os.path.exists(settings.rules_path):
        return []

    rules = joblib.load(settings.rules_path)
    if rules.empty:
        return []

    candidates: dict = {}

    for food in food_names:
        matched = rules[
            rules["antecedents"].apply(lambda x: food in x)
        ]
        for _, row in matched.iterrows():
            for consequent in row["consequents"]:
                if consequent not in food_names:
                    candidates[consequent] = candidates.get(
                        consequent, 0
                    ) + row["lift"]

    # Sort by cumulative lift score
    ranked = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    return [food for food, _ in ranked[:settings.n_recommendations]]