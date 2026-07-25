from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Float,
    String,
    DateTime
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)

from datetime import datetime

from config import DATABASE_PATH


DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


engine = create_engine(

    DATABASE_URL,

    connect_args={
        "check_same_thread": False
    }

)


SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine

)


Base = declarative_base()



class MarketHistory(Base):

    __tablename__ = "market_history"


    id = Column(

        Integer,

        primary_key=True,

        index=True

    )


    gold = Column(Float)

    usd = Column(Float)

    ounce = Column(Float)

    coin = Column(Float)


    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )



class AnalysisHistory(Base):

    __tablename__ = "analysis_history"


    id = Column(

        Integer,

        primary_key=True,

        index=True

    )


    score = Column(Float)

    decision = Column(String)

    confidence = Column(Float)

    reason = Column(String)

    created_at = Column(

        DateTime,

        default=datetime.utcnow

    )



def create_database():

    Base.metadata.create_all(

        bind=engine

    )



def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()