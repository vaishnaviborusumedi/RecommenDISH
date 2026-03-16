from sqlalchemy.orm import Session
from app.ml.clustering import train_kmeans
from app.ml.association_rules import train_association_rules
from app.utils.logger import logger


def train_all(db: Session):
    """Train K-Means + association rules in one call."""
    logger.info("=== Starting full model training ===")

    logger.info("Training K-Means clustering...")
    train_kmeans(db)

    logger.info("Mining association rules...")
    train_association_rules(db)

    logger.info("=== Training complete ===")