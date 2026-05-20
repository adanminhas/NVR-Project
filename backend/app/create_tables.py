from app.database import Base, engine
from app.models.camera_model import Camera  # noqa: F401 — register table with Base


def init_db():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully")


if __name__ == "__main__":
    init_db()
