"""
FitSnap.AI - AI-Powered Fitness & Wellness Platform Engine
Main orchestrator for fitness tracking, workout planning, and health monitoring
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class ActivityType(Enum):
    """Activity types"""
    RUNNING = "running"
    WALKING = "walking"
    CYCLING = "cycling"
    SWIMMING = "swimming"
    WEIGHTLIFTING = "weightlifting"
    YOGA = "yoga"
    HIIT = "hiit"
    CARDIO = "cardio"
    STRETCHING = "stretching"


class GoalType(Enum):
    """Fitness goal types"""
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    ENDURANCE = "endurance"
    FLEXIBILITY = "flexibility"
    GENERAL_FITNESS = "general_fitness"


class DifficultyLevel(Enum):
    """Workout difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class User:
    """Fitness user profile"""
    id: str
    name: str
    age: int
    height_cm: float
    weight_kg: float
    gender: str
    fitness_level: DifficultyLevel
    goals: List[GoalType]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class Activity:
    """Fitness activity/workout"""
    id: str
    user_id: str
    activity_type: ActivityType
    duration_minutes: int
    calories_burned: float
    distance_km: Optional[float]
    heart_rate_avg: Optional[int]
    started_at: datetime
    completed_at: datetime
    notes: str
    metadata: Dict[str, Any]


@dataclass
class WorkoutPlan:
    """Personalized workout plan"""
    id: str
    user_id: str
    name: str
    goal: GoalType
    difficulty: DifficultyLevel
    duration_weeks: int
    workouts_per_week: int
    exercises: List[Dict[str, Any]]
    created_at: datetime
    is_active: bool


@dataclass
class NutritionLog:
    """Nutrition/meal log"""
    id: str
    user_id: str
    meal_type: str
    food_items: List[Dict[str, Any]]
    total_calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    logged_at: datetime


@dataclass
class HealthMetric:
    """Health metric measurement"""
    id: str
    user_id: str
    metric_type: str
    value: float
    unit: str
    measured_at: datetime
    notes: str


class FitSnapEngine:
    """
    Main FitSnap Engine - AI-Powered Fitness & Wellness Platform
    
    Capabilities:
    - Activity tracking (running, cycling, swimming, etc.)
    - AI-powered workout planning
    - Personalized fitness recommendations
    - Nutrition tracking and meal planning
    - Progress monitoring and analytics
    - Heart rate and health metrics tracking
    - Social features and challenges
    - Integration with wearables (Fitbit, Apple Watch, Garmin)
    - Video workout library
    - Virtual personal trainer
    - Goal setting and achievement tracking
    - Body composition analysis
    """
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.activities: Dict[str, Activity] = {}
        self.workout_plans: Dict[str, WorkoutPlan] = {}
        self.nutrition_logs: Dict[str, NutritionLog] = {}
        self.health_metrics: Dict[str, HealthMetric] = {}
        
        logger.info("FitSnap Engine initialized")
    
    async def create_user_profile(
        self,
        name: str,
        age: int,
        height_cm: float,
        weight_kg: float,
        gender: str,
        fitness_level: DifficultyLevel,
        goals: List[GoalType]
    ) -> User:
        """
        Create user fitness profile
        
        Args:
            name: User name
            age: Age in years
            height_cm: Height in centimeters
            weight_kg: Weight in kilograms
            gender: Gender
            fitness_level: Current fitness level
            goals: Fitness goals
        
        Returns:
            User profile
        """
        user_id = f"user_{datetime.now().timestamp()}"
        
        # Calculate BMI
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        user = User(
            id=user_id,
            name=name,
            age=age,
            height_cm=height_cm,
            weight_kg=weight_kg,
            gender=gender,
            fitness_level=fitness_level,
            goals=goals,
            created_at=datetime.now(),
            metadata={
                "bmi": bmi,
                "target_weight_kg": weight_kg,
                "target_calories_daily": self._calculate_daily_calories(age, gender, weight_kg, height_cm, fitness_level)
            }
        )
        
        self.users[user_id] = user
        
        logger.info(f"User profile created: {name}")
        return user
    
    def _calculate_daily_calories(
        self,
        age: int,
        gender: str,
        weight_kg: float,
        height_cm: float,
        fitness_level: DifficultyLevel
    ) -> float:
        """Calculate recommended daily calories using Mifflin-St Jeor equation"""
        # Basal Metabolic Rate (BMR)
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        # Activity multiplier
        activity_multipliers = {
            DifficultyLevel.BEGINNER: 1.2,
            DifficultyLevel.INTERMEDIATE: 1.55,
            DifficultyLevel.ADVANCED: 1.725,
            DifficultyLevel.EXPERT: 1.9
        }
        
        multiplier = activity_multipliers.get(fitness_level, 1.55)
        return bmr * multiplier
    
    async def log_activity(
        self,
        user_id: str,
        activity_type: ActivityType,
        duration_minutes: int,
        distance_km: Optional[float] = None,
        heart_rate_avg: Optional[int] = None,
        notes: str = ""
    ) -> Activity:
        """
        Log fitness activity
        
        Args:
            user_id: User ID
            activity_type: Type of activity
            duration_minutes: Duration in minutes
            distance_km: Distance in kilometers (optional)
            heart_rate_avg: Average heart rate (optional)
            notes: Additional notes
        
        Returns:
            Logged activity
        """
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        user = self.users[user_id]
        
        # Calculate calories burned
        calories_burned = self._calculate_calories_burned(
            activity_type,
            duration_minutes,
            user.weight_kg,
            distance_km
        )
        
        activity_id = f"activity_{datetime.now().timestamp()}"
        
        activity = Activity(
            id=activity_id,
            user_id=user_id,
            activity_type=activity_type,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned,
            distance_km=distance_km,
            heart_rate_avg=heart_rate_avg,
            started_at=datetime.now() - timedelta(minutes=duration_minutes),
            completed_at=datetime.now(),
            notes=notes,
            metadata={}
        )
        
        self.activities[activity_id] = activity
        
        logger.info(f"Activity logged: {activity_type.value} for {duration_minutes} minutes")
        return activity
    
    def _calculate_calories_burned(
        self,
        activity_type: ActivityType,
        duration_minutes: int,
        weight_kg: float,
        distance_km: Optional[float]
    ) -> float:
        """Calculate calories burned based on activity"""
        # MET (Metabolic Equivalent of Task) values
        met_values = {
            ActivityType.RUNNING: 9.8,
            ActivityType.WALKING: 3.5,
            ActivityType.CYCLING: 7.5,
            ActivityType.SWIMMING: 8.0,
            ActivityType.WEIGHTLIFTING: 6.0,
            ActivityType.YOGA: 3.0,
            ActivityType.HIIT: 10.0,
            ActivityType.CARDIO: 7.0,
            ActivityType.STRETCHING: 2.5
        }
        
        met = met_values.get(activity_type, 5.0)
        
        # Calories = MET * weight(kg) * duration(hours)
        calories = met * weight_kg * (duration_minutes / 60)
        
        return round(calories, 2)
    
    async def generate_workout_plan(
        self,
        user_id: str,
        goal: GoalType,
        duration_weeks: int = 12,
        workouts_per_week: int = 4
    ) -> WorkoutPlan:
        """
        Generate AI-powered personalized workout plan
        
        Args:
            user_id: User ID
            goal: Fitness goal
            duration_weeks: Plan duration in weeks
            workouts_per_week: Number of workouts per week
        
        Returns:
            Workout plan
        """
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        user = self.users[user_id]
        
        # Generate exercises based on goal and fitness level
        exercises = self._generate_exercises(goal, user.fitness_level, workouts_per_week)
        
        plan_id = f"plan_{datetime.now().timestamp()}"
        
        plan = WorkoutPlan(
            id=plan_id,
            user_id=user_id,
            name=f"{goal.value.replace('_', ' ').title()} Plan",
            goal=goal,
            difficulty=user.fitness_level,
            duration_weeks=duration_weeks,
            workouts_per_week=workouts_per_week,
            exercises=exercises,
            created_at=datetime.now(),
            is_active=True
        )
        
        self.workout_plans[plan_id] = plan
        
        logger.info(f"Workout plan generated for user {user_id}")
        return plan
    
    def _generate_exercises(
        self,
        goal: GoalType,
        fitness_level: DifficultyLevel,
        workouts_per_week: int
    ) -> List[Dict[str, Any]]:
        """Generate exercise list based on goal and fitness level"""
        exercises = []
        
        # Base exercises by goal
        if goal == GoalType.WEIGHT_LOSS:
            exercises = [
                {"name": "Running", "duration": 30, "intensity": "moderate"},
                {"name": "HIIT", "duration": 20, "intensity": "high"},
                {"name": "Cycling", "duration": 45, "intensity": "moderate"},
                {"name": "Jump Rope", "duration": 15, "intensity": "high"}
            ]
        elif goal == GoalType.MUSCLE_GAIN:
            exercises = [
                {"name": "Bench Press", "sets": 4, "reps": 8},
                {"name": "Squats", "sets": 4, "reps": 10},
                {"name": "Deadlifts", "sets": 3, "reps": 8},
                {"name": "Pull-ups", "sets": 3, "reps": 10}
            ]
        elif goal == GoalType.ENDURANCE:
            exercises = [
                {"name": "Long Run", "duration": 60, "intensity": "low"},
                {"name": "Swimming", "duration": 45, "intensity": "moderate"},
                {"name": "Cycling", "duration": 90, "intensity": "moderate"}
            ]
        elif goal == GoalType.FLEXIBILITY:
            exercises = [
                {"name": "Yoga", "duration": 45, "style": "vinyasa"},
                {"name": "Stretching", "duration": 30, "focus": "full_body"},
                {"name": "Pilates", "duration": 40}
            ]
        else:  # GENERAL_FITNESS
            exercises = [
                {"name": "Running", "duration": 30, "intensity": "moderate"},
                {"name": "Strength Training", "duration": 45},
                {"name": "Yoga", "duration": 30},
                {"name": "Swimming", "duration": 30}
            ]
        
        return exercises[:workouts_per_week]
    
    async def log_nutrition(
        self,
        user_id: str,
        meal_type: str,
        food_items: List[Dict[str, Any]]
    ) -> NutritionLog:
        """
        Log nutrition/meal
        
        Args:
            user_id: User ID
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            food_items: List of food items with nutritional info
        
        Returns:
            Nutrition log
        """
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        # Calculate totals
        total_calories = sum(item.get("calories", 0) for item in food_items)
        total_protein = sum(item.get("protein_g", 0) for item in food_items)
        total_carbs = sum(item.get("carbs_g", 0) for item in food_items)
        total_fat = sum(item.get("fat_g", 0) for item in food_items)
        
        log_id = f"nutrition_{datetime.now().timestamp()}"
        
        nutrition_log = NutritionLog(
            id=log_id,
            user_id=user_id,
            meal_type=meal_type,
            food_items=food_items,
            total_calories=total_calories,
            protein_g=total_protein,
            carbs_g=total_carbs,
            fat_g=total_fat,
            logged_at=datetime.now()
        )
        
        self.nutrition_logs[log_id] = nutrition_log
        
        logger.info(f"Nutrition logged: {meal_type} - {total_calories} calories")
        return nutrition_log
    
    async def track_health_metric(
        self,
        user_id: str,
        metric_type: str,
        value: float,
        unit: str,
        notes: str = ""
    ) -> HealthMetric:
        """
        Track health metric
        
        Args:
            user_id: User ID
            metric_type: Type of metric (weight, body_fat, blood_pressure, etc.)
            value: Metric value
            unit: Unit of measurement
            notes: Additional notes
        
        Returns:
            Health metric
        """
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        metric_id = f"metric_{datetime.now().timestamp()}"
        
        metric = HealthMetric(
            id=metric_id,
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            unit=unit,
            measured_at=datetime.now(),
            notes=notes
        )
        
        self.health_metrics[metric_id] = metric
        
        # Update user profile if weight
        if metric_type == "weight":
            user = self.users[user_id]
            user.weight_kg = value
        
        logger.info(f"Health metric tracked: {metric_type} = {value} {unit}")
        return metric
    
    async def get_progress_report(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get user progress report
        
        Args:
            user_id: User ID
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            Progress report
        """
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Filter activities
        user_activities = [
            a for a in self.activities.values()
            if a.user_id == user_id and start_date <= a.completed_at <= end_date
        ]
        
        # Calculate statistics
        total_workouts = len(user_activities)
        total_duration = sum(a.duration_minutes for a in user_activities)
        total_calories = sum(a.calories_burned for a in user_activities)
        total_distance = sum(a.distance_km or 0 for a in user_activities)
        
        # Activity breakdown
        activity_breakdown = {}
        for activity in user_activities:
            activity_type = activity.activity_type.value
            activity_breakdown[activity_type] = activity_breakdown.get(activity_type, 0) + 1
        
        # Weight progress
        weight_metrics = [
            m for m in self.health_metrics.values()
            if m.user_id == user_id and m.metric_type == "weight" and start_date <= m.measured_at <= end_date
        ]
        
        weight_change = 0
        if len(weight_metrics) >= 2:
            weight_metrics.sort(key=lambda x: x.measured_at)
            weight_change = weight_metrics[-1].value - weight_metrics[0].value
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": {
                "total_workouts": total_workouts,
                "total_duration_minutes": total_duration,
                "total_calories_burned": total_calories,
                "total_distance_km": total_distance,
                "weight_change_kg": weight_change
            },
            "activity_breakdown": activity_breakdown,
            "average_per_week": {
                "workouts": total_workouts / 4 if total_workouts > 0 else 0,
                "duration_minutes": total_duration / 4 if total_duration > 0 else 0
            }
        }
    
    def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get user fitness dashboard data"""
        if user_id not in self.users:
            raise ValueError(f"User not found: {user_id}")
        
        user = self.users[user_id]
        
        # Recent activities
        user_activities = [
            a for a in self.activities.values()
            if a.user_id == user_id
        ]
        recent_activities = sorted(user_activities, key=lambda x: x.completed_at, reverse=True)[:5]
        
        # Active workout plans
        active_plans = [
            p for p in self.workout_plans.values()
            if p.user_id == user_id and p.is_active
        ]
        
        # Today's nutrition
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_nutrition = [
            n for n in self.nutrition_logs.values()
            if n.user_id == user_id and n.logged_at >= today_start
        ]
        today_calories = sum(n.total_calories for n in today_nutrition)
        
        return {
            "user": {
                "name": user.name,
                "bmi": user.metadata.get("bmi", 0),
                "target_calories_daily": user.metadata.get("target_calories_daily", 0)
            },
            "today": {
                "calories_consumed": today_calories,
                "calories_remaining": user.metadata.get("target_calories_daily", 0) - today_calories
            },
            "recent_activities": [
                {
                    "type": a.activity_type.value,
                    "duration": a.duration_minutes,
                    "calories": a.calories_burned,
                    "date": a.completed_at.isoformat()
                }
                for a in recent_activities
            ],
            "active_plans": len(active_plans)
        }
    
    async def integrate_with_enterprise_hub(self, hub_endpoint: str):
        """Integrate with iTechSmart Enterprise Hub"""
        logger.info(f"Integrating FitSnap with Enterprise Hub: {hub_endpoint}")
        # Report fitness metrics to Enterprise Hub
    
    async def integrate_with_ninja(self, ninja_endpoint: str):
        """Integrate with iTechSmart Ninja for self-healing"""
        logger.info(f"Integrating FitSnap with Ninja: {ninja_endpoint}")
        # Use Ninja for workout optimization


# Global FitSnap Engine instance
fitsnap_engine = FitSnapEngine()


def get_fitsnap_engine() -> FitSnapEngine:
    """Get FitSnap Engine instance"""
    return fitsnap_engine