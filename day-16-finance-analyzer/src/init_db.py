from .database import engine
from .db_models import metadata

def init_db():
    metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
