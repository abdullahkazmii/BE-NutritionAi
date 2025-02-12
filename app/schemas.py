from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CreateUser(BaseModel):
    name: str
    email: EmailStr
    username: str
    role: str


class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    username: str
    role: str

    class Config:
        orm_mode = True
        from_attributes = True


class UserResponseWithPassword(BaseModel):
    user: UserOut
    password: Optional[str] = None

    class Config:
        orm_mode = True


class PlanRequest(BaseModel):
    gender: str
    ageGroup: str
    currentWeight: float
    weightUnit: str = "kg"
    height: float
    heightUnit: str = "cm"
    targetWeight: float
    targetWeightUnit: str = "kg"
    timeGoal: Optional[str] = None
    planType: str
    activityLevel: Optional[str] = None
    yogaExperience: Optional[str] = None
    experienceDetails: Optional[str] = None
    workoutPreference: Optional[str] = None
    dietType: str
    dietRestrictions: Optional[str] = None
    dietRestrictionsDetails: Optional[str] = None
    mealPreference: str
    dietGoals: Optional[str] = None
    yogaType: Optional[str] = None
    workoutType: Optional[str] = None
    workoutDetails: Optional[str] = None
    workoutDays: Optional[str] = None
    medicalConditions: Optional[str] = None
    medicalDetails: Optional[str] = None


class UserGeneratedPlanResponse(BaseModel):
    id: int
    plan_type: str
    generated_plan: str
    goal_time: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True


class FormRequest(BaseModel):
    gender: str
    ageGroup: str
    currentWeight: float
    weightUnit: str = "kg"
    height: float
    heightUnit: str = "cm"
    targetWeight: float
    targetWeightUnit: str = "kg"
    timeGoal: str
    planType: str
    activityLevel: Optional[str] = None
    yogaExperience: Optional[str] = None
    experienceDetails: Optional[str] = None
    workoutPreference: Optional[str] = None
    dietType: str
    dietRestrictions: Optional[str] = None
    dietRestrictionsDetails: Optional[str] = None
    mealPreference: str
    dietGoals: Optional[str] = None
    yogaType: Optional[str] = None
    workoutType: Optional[str] = None
    workoutDetails: Optional[str] = None
    workoutDays: Optional[str] = None
    medicalConditions: Optional[str] = None
    medicalDetails: Optional[str] = None
