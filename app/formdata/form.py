from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserPlan, PlanType, Activity, Meal, UserActivity
from app.schemas import FormRequest
from app.auth.oauth import get_current_user

router = APIRouter(tags=["Onboarding"])


@router.post("/onboarding", status_code=status.HTTP_201_CREATED)
def onboarding(
    form_data: FormRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Fetch the current user
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.gender = form_data.gender
        user.age_group = form_data.ageGroup
        user.weight = form_data.currentWeight
        user.weight_unit = form_data.weightUnit
        user.target_weight = form_data.targetWeight
        user.target_weight_unit = form_data.targetWeightUnit
        user.height = form_data.height
        user.target_height_unit = form_data.heightUnit
        db.add(user)

        plan_type = (
            db.query(PlanType).filter(PlanType.plan_name == form_data.planType).first()
        )
        if not plan_type:
            plan_type = PlanType(plan_name=form_data.planType)
            db.add(plan_type)
            db.commit()
            db.refresh(plan_type)

        user_plan = UserPlan(
            user_id=current_user.id,
            plan_type_id=plan_type.id,
            goal_time=form_data.timeGoal,
        )
        db.add(user_plan)
        db.commit()

        activity = Activity(
            plan_id=plan_type.id,
            yoga_experience=form_data.yogaExperience,
            yoga_type=form_data.yogaType,
            workout_preference=form_data.workoutPreference,
            workout_days=form_data.workoutDays,
            activity_level=form_data.activityLevel,
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)

        user_activity = UserActivity(user_id=current_user.id, activity_id=activity.id)
        db.add(user_activity)

        meal = db.query(Meal).filter(Meal.user_id == current_user.id).first()
        if not meal:
            meal = Meal(user_id=current_user.id, plan_id=user_plan.plan_type_id)

        meal.diet_type = form_data.dietType
        meal.diet_restrictions = form_data.dietRestrictions
        meal.meal_preference = form_data.mealPreference
        meal.key_goals = form_data.dietGoals
        meal.medical_restrictions = form_data.medicalConditions
        db.add(meal)

        db.commit()

        return JSONResponse(
            content={
                "message": "Onboarding data submitted successfully",
                "submitted_data": form_data.model_dump(),
            },
            status_code=status.HTTP_201_CREATED,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"An error occurred: {str(e)}",
        )
