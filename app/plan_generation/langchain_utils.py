import os
from app import schemas
from app.auth import oauth
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import ValidationError
from fastapi import status, HTTPException, APIRouter, Depends
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from app.database import get_db
from app.models import UserGeneratedPlan
from typing import List
from rich import traceback

traceback.install()

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, openai_api_key=OPENAI_API_KEY)
router = APIRouter(tags=["Diet Plan"])

diet_plan_template = ChatPromptTemplate.from_template(
    "Create a personalized diet plan for a {gender} person whose ageGroup is {ageGroup} and who is {height} {heightUnit} tall and weighs {currentWeight} {weightUnit} and their target goal weight is {targetWeight} {targetWeightUnit}. "
    "They have the following dietary preferences: Diet Type is {dietType}, with the following {dietRestrictions} dietary restrictions. "
    "They prefer {mealPreference} meals per day. create meal day by day. (e.g if the user ask 1 month meal preference, create the plan for 30 days, if the user ask 2 months meal preference, create the plan for 60 days and if the user ask 3 months meal preference, create the plan for 90 days plan). Meals name has to be Breakfast, Lunch and Dinner. and if they ask more than 3 meals a day then the rest meals will be named as Snacks."
    "Their time goal is to achieve the target weight is {timeGoal} and key goals for the diet plan is {dietGoals} . "
    "Generate meal plans for each day separately over the specified time period of {timeGoal} (e.g., 1 month = 30 days, 2 months = 60 days and so on)."
    "they may or may not have additional information regarding their {medicalConditions} which should be consider while creating the plan."
    "Ensure the diet plan complements their fitness level, target weight, and keyGoals."
    "The response should be in Structured JSON Format only and not in markdown or any other format. It should be in simple JSON Format and please do not give any other information."
    "The JSON structure should strictly follow this format:"
    "the keys JSON structure have will be only: 1. planType: 2. duration: 3. meals_per_day: 4. diet_type: 5. target_weight: 6. diet_goal: 7. meal_plan:  "
)


diet_yoga_plan_template = ChatPromptTemplate.from_template(
    "Create a personalized diet with yoga plan for a {gender} person whose ageGroup is {ageGroup} and who is {height} {heightUnit} tall and weighs {currentWeight} {weightUnit} and their target goal weight is {targetWeight} {targetWeightUnit}. "
    "they may or may not have previous yoga experience: {yogaExperience} experience. "
    "For yoga, focus on {yogaType}, which aligns with their their current activity level: {activityLevel} and also yoga weekly schedule must align with the timeGoal {timeGoal} of the plan (e.g., 1 month timeGoal = 4 weeks) and each week will consist of yoga plan"
    "They have the following dietary preferences: Diet Type is {dietType}, with the following {dietRestrictions} dietary restrictions. "
    "They prefer {mealPreference} meals per day. create meal day by day. (e.g if the user ask 1 month meal preference, create the plan for 30 days, if the user ask 2 months meal preference, create the plan for 60 days and if the user ask 3 months meal preference, create the plan for 90 days plan). Meals name has to be Breakfast, Lunch and Dinner. and if they ask more than 3 meals a day then the rest meals will be named as Snacks."
    "Their time goal is to achieve the target weight is {timeGoal} and key goals for the diet plan is {dietGoals} . "
    "Generate meal plans for each day separately over the specified time period of {timeGoal} (e.g., 1 month = 30 days, 2 months = 60 days and so on)."
    "they may or may not have additional information regarding their {medicalConditions} which should be consider while creating the plan"
    "Ensure the diet with yoga plan complements their fitness level, target weight and keyGoals."
    "The response should be in Structured JSON Format only and not in markdown or any other format. It should be in simple JSON Format and please do not give any other information."
    "The JSON structure should strictly follow this format:"
    "the keys JSON structure have will be only: 1. planType: 2. duration: 3. meals_per_day: 4. diet_type: 5. target_weight: 6. diet_goal: 7. meal_plan: 8. yoga_plan: "
)

diet_workout_plan_template = ChatPromptTemplate.from_template(
    "Create a personalized diet with workout plan for a {gender} person whose ageGroup is {ageGroup} and who is {height} {heightUnit} tall and weighs {currentWeight} {weightUnit} and their target goal weight is {targetWeight} {targetWeightUnit}. "
    "For workout, focus on {workoutPreference}, and they are willing to do workout for {workoutDays} a week. their current activity level is {activityLevel} and also workout weekly schedule must align with the timeGoal {timeGoal} of the plan (e.g., 1 month timeGoal = 4 weeks) and each week will consist of daily workout exercises"
    "They have the following dietary preferences: Diet Type is {dietType}, with the following {dietRestrictions} dietary restrictions. "
    "They prefer {mealPreference} meals per day. create meal day by day. (e.g if the user ask 1 month meal preference, create the plan for 30 days, if the user ask 2 months meal preference, create the plan for 60 days and if the user ask 3 months meal preference, create the plan for 90 days plan). Meals name has to be Breakfast, Lunch and Dinner. and if they ask more than 3 meals a day then the rest meals will be named as Snacks."
    "Their time goal is to achieve the target weight is {timeGoal} and key goals for the diet plan is {dietGoals} . "
    "Generate meal plans for each day separately over the specified time period of {timeGoal} (e.g., 1 month = 30 days, 2 months = 60 days and so on)."
    "they may or may not have additional information regarding their {medicalConditions} which should be consider while creating the plan"
    "Ensure the diet with workout plan complements their fitness level, target weight and keyGoals."
    "The response should be in Structured JSON Format only and not in markdown or any other format. It should be in simple JSON Format and please do not give any other information."
    "The JSON structure should strictly follow this format:"
    "the keys JSON structure have will be only: 1. planType: 2. duration: 3. meals_per_day: 4. diet_type: 5. target_weight: 6. diet_goal: 7. meal_plan: 8. workout_plan: "
)


diet_yoga_workout_plan_template = ChatPromptTemplate.from_template(
    "Create a personalized diet with both yoga and workout plan for a {gender} person whose ageGroup is {ageGroup} and who is {height} {heightUnit} tall and weighs {currentWeight} {weightUnit} and their target goal weight is {targetWeight} {targetWeightUnit}. "
    "they may or may not have previous yoga experience: {yogaExperience} experience. "
    "For yoga, focus on {yogaType}, which aligns with their their current activity level: {activityLevel} and also yoga weekly schedule must align with the timeGoal {timeGoal} of the plan (e.g., 1 month timeGoal = 4 weeks) and each week will consist of yoga plan"
    "For workout, focus on {workoutPreference}, and they are willing to do workout for {workoutDays} a week. their current activity level is {activityLevel} and also workout weekly schedule must align with the timeGoal {timeGoal} of the plan (e.g., 1 month timeGoal = 4 weeks) and each week will consist of daily workout exercises"
    "They have the following dietary preferences: Diet Type is {dietType}, with the following {dietRestrictions} dietary restrictions. "
    "They prefer {mealPreference} meals per day. create meal day by day. (e.g if the user ask 1 month meal preference, create the plan for 30 days, if the user ask 2 months meal preference, create the plan for 60 days and if the user ask 3 months meal preference, create the plan for 90 days plan). Meals name has to be Breakfast, Lunch and Dinner. and if they ask more than 3 meals a day then the rest meals will be named as Snacks."
    "Their time goal is to achieve the target weight is {timeGoal} and key goals for the diet plan is {dietGoals} . "
    "Generate meal plans for each day separately over the specified time period of {timeGoal} (e.g., 1 month = 30 days, 2 months = 60 days and so on)."
    "they may or may not have additional information regarding their {medicalConditions} which should be consider while creating the plan"
    "Ensure the diet with both yoga and workout plan complements their fitness level, target weight and keyGoals."
    "The response should be in Structured JSON Format only and not in markdown or any other format. It should be in simple JSON Format and please do not give any other information."
    "The JSON structure should strictly follow this format:"
    "the keys JSON structure have will be only: 1. planType: 2. duration: 3. meals_per_day: 4. diet_type: 5. target_weight: 6. diet_goal: 7. meal_plan: 8. workout_plan: 9. Yoga_Plan "
)


@router.post("/generate-plan/", status_code=status.HTTP_201_CREATED)
def generate_plan(
    request: schemas.PlanRequest,
    db: Session = Depends(get_db),
    get_current_users: int = Depends(oauth.get_current_user),
):
    try:
        templates = {
            "diet": diet_plan_template,
            "dietYoga": diet_yoga_plan_template,
            "dietWorkout": diet_workout_plan_template,
            "dietYogaWorkout": diet_yoga_workout_plan_template,
        }
        selected_template = templates[request.planType]
        plan_output = selected_template.format(**request.model_dump())
        result = chat.invoke(plan_output)

        generated_plan = UserGeneratedPlan(
            user_id=get_current_users.id,
            plan_type=request.planType,
            generated_plan=result.content,
            goal_time=request.timeGoal,
        )
        db.add(generated_plan)
        db.commit()
        return JSONResponse(
            content=result.content,
            status_code=status.HTTP_200_OK,
        )

    except ValidationError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"An error occurred: {str(e)}",
        )


@router.get(
    "/user-generated-plans/", response_model=List[schemas.UserGeneratedPlanResponse]
)
def get_user_generated_plans(
    db: Session = Depends(get_db),
    get_current_users: int = Depends(oauth.get_current_user),
):
    try:
        plans = (
            db.query(UserGeneratedPlan)
            .filter(UserGeneratedPlan.user_id == get_current_users.id)
            .all()
        )

        if not plans:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No plans found for this user",
            )

        return plans

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"An error occurred: {str(e)}",
        )
