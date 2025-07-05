from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, date

engine = create_engine("sqlite:///meals.db")
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    meals = relationship("Meal", back_populates="user")

# Meal table
class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    image_name = Column(String)
    user_query = Column(Text)
    nutrition_report = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="meals")

# Create tables
Base.metadata.create_all(engine)

# Authentication Functions
def register_user(username, password):
    if session.query(User).filter_by(username=username).first():
        return False  # User exists
    user = User(username=username, password=password)
    session.add(user)
    session.commit()
    return True

def login_user(username, password):
    user = session.query(User).filter_by(username=username, password=password).first()
    return user

# Meal Operations
def save_meal(image_name, user_query, report, user_id):
    meal = Meal(image_name=image_name, user_query=user_query, nutrition_report=report, user_id=user_id)
    session.add(meal)
    session.commit()

def get_meals_by_date(selected_date: date, user_id: int):
    start = datetime.combine(selected_date, datetime.min.time())
    end = datetime.combine(selected_date, datetime.max.time())
    return session.query(Meal).filter(Meal.timestamp.between(start, end), Meal.user_id == user_id).order_by(Meal.timestamp.desc()).all()
