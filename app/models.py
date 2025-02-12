from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from .database import Base
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    weight = Column(Float, nullable=True)
    target_weight = Column(Float, nullable=True)
    weight_unit = Column(String, nullable=True)
    target_weight_unit = Column(String, nullable=True)
    height = Column(Float, nullable=True)
    target_height_unit = Column(String, nullable=True)
    age_group = Column(String, nullable=True)
    role = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    plan = relationship("UserPlan", back_populates="user")
    activity = relationship("UserActivity", back_populates="user")
    meal = relationship("Meal", back_populates="user")
    generated_plans = relationship("UserGeneratedPlan", back_populates="user")


class PlanType(Base):
    __tablename__ = "plan_type"

    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user_plan = relationship("UserPlan", back_populates="plan_type")
    activity = relationship("Activity", back_populates="plan_type")
    meal = relationship("Meal", back_populates="plan_type")


class UserPlan(Base):
    __tablename__ = "user_plan"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    plan_type_id = Column(
        Integer,
        ForeignKey("plan_type.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_time = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user = relationship("User", back_populates="plan")
    plan_type = relationship("PlanType", back_populates="user_plan")


class Activity(Base):
    __tablename__ = "activity"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(
        Integer, ForeignKey("plan_type.id", ondelete="CASCADE"), nullable=False
    )
    yoga_experience = Column(String, nullable=True)
    yoga_type = Column(String, nullable=True)
    workout_preference = Column(String, nullable=True)
    workout_days = Column(String, nullable=True)
    workout_days = Column(String, nullable=True)
    activity_level = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    plan_type = relationship("PlanType", back_populates="activity")
    user_activity = relationship("UserActivity", back_populates="activity")


class UserActivity(Base):
    __tablename__ = "user_activity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    activity_id = Column(
        Integer, ForeignKey("activity.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user = relationship("User", back_populates="activity")
    activity = relationship("Activity", back_populates="user_activity")


class Meal(Base):
    __tablename__ = "meal"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_id = Column(
        Integer, ForeignKey("plan_type.id", ondelete="CASCADE"), nullable=False
    )
    diet_type = Column(String, nullable=False)
    meal_preference = Column(String, nullable=False)
    diet_restrictions = Column(String, nullable=False)
    key_goals = Column(String, nullable=False)
    medical_restrictions = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user = relationship("User", back_populates="meal")
    plan_type = relationship("PlanType", back_populates="meal")


class UserGeneratedPlan(Base):
    __tablename__ = "user_generated_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    plan_type = Column(String, nullable=False)
    generated_plan = Column(Text, nullable=False)
    goal_time = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    user = relationship("User", back_populates="generated_plans")
