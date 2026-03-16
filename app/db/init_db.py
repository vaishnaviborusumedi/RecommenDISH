from app.db.database import engine, SessionLocal
from app.db import models
from app.utils.logger import logger


def create_tables():
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def seed_foods():
    db = SessionLocal()

    if db.query(models.Food).count() > 0:
        logger.info("Foods already seeded, skipping")
        db.close()
        return

    sample_foods = [
        models.Food(name="Chicken Breast", category="protein",
                    calories=165, protein_g=31, carbs_g=0, fat_g=3.6,
                    fiber_g=0, sugar_g=0, sodium_mg=74,
                    is_vegetarian=False, is_vegan=False, is_gluten_free=True),

        models.Food(name="Brown Rice", category="grain",
                    calories=216, protein_g=5, carbs_g=45, fat_g=1.8,
                    fiber_g=3.5, sugar_g=0, sodium_mg=10,
                    is_vegetarian=True, is_vegan=True, is_gluten_free=True),

        models.Food(name="Broccoli", category="vegetable",
                    calories=55, protein_g=3.7, carbs_g=11, fat_g=0.6,
                    fiber_g=5.1, sugar_g=2.6, sodium_mg=33,
                    vitamin_c_mg=89, is_vegetarian=True, is_vegan=True,
                    is_gluten_free=True),

        models.Food(name="Eggs", category="protein",
                    calories=155, protein_g=13, carbs_g=1.1, fat_g=11,
                    fiber_g=0, sugar_g=1.1, sodium_mg=124,
                    is_vegetarian=True, is_vegan=False, is_gluten_free=True),

        models.Food(name="Oats", category="grain",
                    calories=389, protein_g=17, carbs_g=66, fat_g=7,
                    fiber_g=10.6, sugar_g=0, sodium_mg=2,
                    glycemic_index=55, is_vegetarian=True,
                    is_vegan=True, is_gluten_free=False),

        models.Food(name="Salmon", category="protein",
                    calories=208, protein_g=20, carbs_g=0, fat_g=13,
                    fiber_g=0, sugar_g=0, sodium_mg=59,
                    is_vegetarian=False, is_vegan=False, is_gluten_free=True),

        models.Food(name="Sweet Potato", category="vegetable",
                    calories=86, protein_g=1.6, carbs_g=20, fat_g=0.1,
                    fiber_g=3, sugar_g=4.2, sodium_mg=55,
                    glycemic_index=63, is_vegetarian=True,
                    is_vegan=True, is_gluten_free=True),

        models.Food(name="Greek Yogurt", category="dairy",
                    calories=100, protein_g=17, carbs_g=6, fat_g=0.7,
                    fiber_g=0, sugar_g=6, sodium_mg=36,
                    calcium_mg=200, is_vegetarian=True,
                    is_vegan=False, is_gluten_free=True),

        models.Food(name="Banana", category="fruit",
                    calories=89, protein_g=1.1, carbs_g=23, fat_g=0.3,
                    fiber_g=2.6, sugar_g=12, sodium_mg=1,
                    glycemic_index=51, is_vegetarian=True,
                    is_vegan=True, is_gluten_free=True),

        models.Food(name="Lentils", category="protein",
                    calories=230, protein_g=18, carbs_g=40, fat_g=0.8,
                    fiber_g=15.6, sugar_g=3.6, sodium_mg=4,
                    is_vegetarian=True, is_vegan=True, is_gluten_free=True),

        models.Food(name="Almonds", category="fat",
                    calories=579, protein_g=21, carbs_g=22, fat_g=50,
                    fiber_g=12.5, sugar_g=4.4, sodium_mg=1,
                    is_vegetarian=True, is_vegan=True, is_gluten_free=True),

        models.Food(name="Spinach", category="vegetable",
                    calories=23, protein_g=2.9, carbs_g=3.6, fat_g=0.4,
                    fiber_g=2.2, sugar_g=0.4, sodium_mg=79,
                    iron_mg=2.7, vitamin_c_mg=28,
                    is_vegetarian=True, is_vegan=True, is_gluten_free=True),
    ]

    db.add_all(sample_foods)
    db.commit()
    logger.info(f"Seeded {len(sample_foods)} foods into database")
    db.close()


def init_db():
    create_tables()
    seed_foods()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")