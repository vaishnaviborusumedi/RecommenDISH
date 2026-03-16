import os
import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session

from app.db.models import User
from app.features.user_vectors import user_to_vector
from app.utils.logger import logger
from config.settings import settings


def train_kmeans(db: Session) -> KMeans:
    """
    Train K-Means on all users in the database.
    Saves model + scaler to disk.
    """
    users = db.query(User).all()

    if len(users) < settings.n_clusters:
        logger.warning(
            f"Only {len(users)} users — need at least {settings.n_clusters}. "
            f"Using n_clusters=1 for now."
        )
        n_clusters = max(1, len(users))
    else:
        n_clusters = settings.n_clusters

    logger.info(f"Building feature matrix for {len(users)} users...")
    X = np.stack([user_to_vector(u, db) for u in users])

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
        max_iter=300,
    )
    kmeans.fit(X_scaled)

    # Assign cluster IDs back to users
    for user, cluster_id in zip(users, kmeans.labels_):
        user.cluster_id = int(cluster_id)
    db.commit()

    # Save models
    os.makedirs(settings.models_dir, exist_ok=True)
    joblib.dump(kmeans,  settings.kmeans_model_path)
    joblib.dump(scaler,  settings.scaler_path)

    logger.info(f"K-Means trained — {n_clusters} clusters. Models saved.")
    return kmeans


def predict_cluster(user: User, db: Session) -> int:
    """
    Predict which cluster a user belongs to.
    Loads saved model — trains fresh if not found.
    """
    if not os.path.exists(settings.kmeans_model_path):
        logger.warning("No saved K-Means model found — training now...")
        train_kmeans(db)

    kmeans = joblib.load(settings.kmeans_model_path)
    scaler = joblib.load(settings.scaler_path)

    vector = user_to_vector(user, db).reshape(1, -1)
    vector_scaled = scaler.transform(vector)
    cluster_id = int(kmeans.predict(vector_scaled)[0])

    logger.info(f"User {user.id} → cluster {cluster_id}")
    return cluster_id


def get_cluster_peers(user: User, db: Session) -> list:
    """Return all users in the same cluster as this user."""
    cluster_id = user.cluster_id if user.cluster_id is not None \
                 else predict_cluster(user, db)

    peers = (
        db.query(User)
        .filter(User.cluster_id == cluster_id, User.id != user.id)
        .all()
    )
    return peers