from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Import models to register with SQLAlchemy
from .asset import Asset  # noqa: F401,E402
from .maintenance_record import MaintenanceRecord  # noqa: F401,E402
from .document import Document  # noqa: F401,E402
