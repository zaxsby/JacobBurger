import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import json
import calendar
import random
from functools import lru_cache
from typing import Dict, List, Any, Optional, Tuple, Union, Set
import sys

# Check for required dependencies
def check_dependencies():
    missing_packages = []
    
    # Try to import each required package
    try:
        import ttkthemes
    except ImportError:
        missing_packages.append("ttkthemes")
    
    try:
        from ttkbootstrap import Style
    except ImportError:
        missing_packages.append("ttkbootstrap")
    
    try:
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    except ImportError:
        missing_packages.append("matplotlib")
    
    try:
        import customtkinter as ctk
    except ImportError:
        missing_packages.append("customtkinter")
    
    # If any packages are missing, show an error message
    if missing_packages:
        error_message = "The following required packages are missing:\n"
        for package in missing_packages:
            error_message += f"- {package}\n"
        error_message += "\nPlease install them using pip:\n"
        error_message += f"pip install {' '.join(missing_packages)}"
        
        # Try to show a messagebox if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Missing Dependencies", error_message)
            root.destroy()
        except:
            print(error_message)
        
        return False
    
    return True

# Check dependencies before importing
if not check_dependencies():
    sys.exit(1)

# UI Libraries - now we can safely import these
import ttkthemes
from ttkbootstrap import Style
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

# Type aliases for better code readability
FoodEntry = Dict[str, Any]
ExerciseEntry = Dict[str, Any]
DayData = Dict[str, Any]
History = Dict[str, DayData]
Achievement = Dict[str, Any]
Challenge = Dict[str, Any]


class GamificationManager:
    """Class to handle gamification features including achievements, challenges, and rewards."""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.gamification_file = "burger_tracker_gamification.json"
        
        # Initialize gamification data
        self.data = self.load_gamification_data()
        
        # Initialize achievements
        self.achievements = self._initialize_achievements()
        
        # Initialize challenges
        self.daily_challenges = self._initialize_daily_challenges()
        self.weekly_challenges = self._initialize_weekly_challenges()
        
        # Generate today's challenges if needed
        self._ensure_daily_challenges()
    
    def load_gamification_data(self) -> Dict[str, Any]:
        """Load gamification data from file."""
        if os.path.exists(self.gamification_file):
            try:
                with open(self.gamification_file, "r") as f:
                    data = json.load(f)
                return data
            except Exception as e:
                print(f"Failed to load gamification data: {e}")
                return self._initialize_gamification_data()
        return self._initialize_gamification_data()
    
    def _initialize_gamification_data(self) -> Dict[str, Any]:
        """Initialize default gamification data structure."""
        return {
            "points": 0,
            "level": 1,
            "unlocked_achievements": [],
            "daily_challenges": {},
            "weekly_challenges": {},
            "streaks": {
                "food_logging": 0,
                "exercise_logging": 0,
                "weight_logging": 0
            },
            "last_login_date": datetime.datetime.now().strftime("%Y-%m-%d")
        }
    
    def save_gamification_data(self) -> bool:
        """Save gamification data to file."""
        try:
            with open(self.gamification_file, "w") as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save gamification data: {e}")
            return False
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize the achievement system."""
        return {
            "first_burger": {
                "id": "first_burger",
                "name": "Burger Novice",
                "description": "Log your first burger",
                "icon": "🍔",
                "points": 10,
                "condition": lambda: self._has_food_category("Burgers")
            },
            "burger_enthusiast": {
                "id": "burger_enthusiast",
                "name": "Burger Enthusiast",
                "description": "Log 10 different types of burgers",
                "icon": "🍔🍔",
                "points": 50,
                "condition": lambda: self._count_unique_foods_in_category("Burgers") >= 10
            },
            "burger_master": {
                "id": "burger_master",
                "name": "Burger Master",
                "description": "Log 20 different types of burgers",
                "icon": "🍔👑",
                "points": 100,
                "condition": lambda: self._count_unique_foods_in_category("Burgers") >= 20
            },
            "exercise_beginner": {
                "id": "exercise_beginner",
                "name": "Exercise Beginner",
                "description": "Log your first exercise",
                "icon": "🏃",
                "points": 10,
                "condition": lambda: self._has_any_exercise()
            },
            "exercise_enthusiast": {
                "id": "exercise_enthusiast",
                "name": "Exercise Enthusiast",
                "description": "Burn 1000 calories through exercise",
                "icon": "🏃‍♂️🔥",
                "points": 50,
                "condition": lambda: self._total_calories_burnt() >= 1000
            },
            "weight_tracker": {
                "id": "weight_tracker",
                "name": "Weight Tracker",
                "description": "Log your weight for the first time",
                "icon": "⚖️",
                "points": 10,
                "condition": lambda: self._has_any_weight_entry()
            },
            "consistent_logger": {
                "id": "consistent_logger",
                "name": "Consistent Logger",
                "description": "Log food for 7 consecutive days",
                "icon": "📝✅",
                "points": 70,
                "condition": lambda: self.data["streaks"]["food_logging"] >= 7
            },
            "calorie_conscious": {
                "id": "calorie_conscious",
                "name": "Calorie Conscious",
                "description": "Stay under your calorie goal for 5 consecutive days",
                "icon": "🥗👍",
                "points": 50,
                "condition": lambda: self._days_under_calorie_goal(5)
            },
            "custom_creator": {
                "id": "custom_creator",
                "name": "Custom Creator",
                "description": "Create your first custom food",
                "icon": "🍳",
                "points": 20,
                "condition": lambda: self._has_custom_foods()
            },
            "exercise_variety": {
                "id": "exercise_variety",
                "name": "Exercise Variety",
                "description": "Try 5 different types of exercises",
                "icon": "🏊‍♂️🚴‍♂️🏃‍♂️",
                "points": 30,
                "condition": lambda: self._count_unique_exercises() >= 5
            }
        }
    
    def _initialize_daily_challenges(self) -> List[Challenge]:
        """Initialize the daily challenge templates."""
        return [
            {
                "id": "log_burger",
                "name": "Burger Day",
                "description": "Log a burger today",
                "icon": "🍔",
                "points": 15,
                "condition": lambda: self._logged_food_category_today("Burgers")
            },
            {
                "id": "log_exercise",
                "name": "Active Day",
                "description": "Log at least 30 minutes of exercise today",
                "icon": "🏃‍♂️",
                "points": 20,
                "condition": lambda: self._exercise_minutes_today() >= 30
            },
            {
                "id": "log_weight",
                "name": "Weigh In",
                "description": "Log your weight today",
                "icon": "⚖️",
                "points": 10,
                "condition": lambda: self._logged_weight_today()
            },
            {
                "id": "stay_under_goal",
                "name": "Goal Keeper",
                "description": "Stay under your calorie goal today",
                "icon": "🎯",
                "points": 25,
                "condition": lambda: self._under_calorie_goal_today()
            },
            {
                "id": "balanced_diet",
                "name": "Balanced Diet",
                "description": "Log foods from at least 3 different categories today",
                "icon": "🥗",
                "points": 20,
                "condition": lambda: self._food_category_variety_today() >= 3
            },
            {
                "id": "burn_calories",
                "name": "Calorie Burner",
                "description": "Burn at least 200 calories through exercise today",
                "icon": "🔥",
                "points": 20,
                "condition": lambda: self._calories_burnt_today() >= 200
            }
        ]
    
    def _initialize_weekly_challenges(self) -> List[Challenge]:
        """Initialize the weekly challenge templates."""
        return [
            {
                "id": "week_consistency",
                "name": "Weekly Consistency",
                "description": "Log food every day this week",
                "icon": "📊",
                "points": 50,
                "condition": lambda: self._logged_food_days_this_week() >= 7
            },
            {
                "id": "exercise_week",
                "name": "Active Week",
                "description": "Exercise at least 3 days this week",
                "icon": "🏋️‍♂️",
                "points": 40,
                "condition": lambda: self._exercise_days_this_week() >= 3
            },
            {
                "id": "calorie_week",
                "name": "Calorie Master",
                "description": "Stay under your calorie goal for 5 days this week",
                "icon": "🏆",
                "points": 60,
                "condition": lambda: self._days_under_calorie_goal_this_week() >= 5
            },
            {
                "id": "variety_week",
                "name": "Variety Seeker",
                "description": "Try 5 different foods this week",
                "icon": "🍽️",
                "points": 30,
                "condition": lambda: self._unique_foods_this_week() >= 5
            }
        ]
    
    def _ensure_daily_challenges(self) -> None:
        """Ensure daily challenges are generated for today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Check if we need to update the last login streak
        if "last_login_date" in self.data:
            last_date = datetime.datetime.strptime(self.data["last_login_date"], "%Y-%m-%d")
            today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
            
            # If last login was yesterday, increment streaks
            if (today_date - last_date).days == 1:
                if self._logged_food_yesterday():
                    self.data["streaks"]["food_logging"] += 1
                else:
                    self.data["streaks"]["food_logging"] = 0
                
                if self._logged_exercise_yesterday():
                    self.data["streaks"]["exercise_logging"] += 1
                else:
                    self.data["streaks"]["exercise_logging"] = 0
                
                if self._logged_weight_yesterday():
                    self.data["streaks"]["weight_logging"] += 1
                else:
                    self.data["streaks"]["weight_logging"] = 0
            # If more than a day has passed, reset streaks
            elif (today_date - last_date).days > 1:
                self.data["streaks"]["food_logging"] = 0
                self.data["streaks"]["exercise_logging"] = 0
                self.data["streaks"]["weight_logging"] = 0
        
        # Update last login date
        self.data["last_login_date"] = today
        
        # Generate daily challenges if not already generated for today
        if today not in self.data["daily_challenges"]:
            # Select 3 random challenges for today
            selected_challenges = random.sample(self.daily_challenges, min(3, len(self.daily_challenges)))
            
            self.data["daily_challenges"][today] = {
                "challenges": [challenge["id"] for challenge in selected_challenges],
                "completed": []
            }
        
        # Check if we need to generate weekly challenges
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        week_start = (today_date - datetime.timedelta(days=today_date.weekday())).strftime("%Y-%m-%d")
        
        if week_start not in self.data["weekly_challenges"]:
            # Select 2 random weekly challenges
            selected_challenges = random.sample(self.weekly_challenges, min(2, len(self.weekly_challenges)))
            
            self.data["weekly_challenges"][week_start] = {
                "challenges": [challenge["id"] for challenge in selected_challenges],
                "completed": []
            }
    
    def check_achievements(self) -> List[Achievement]:
        """Check for newly unlocked achievements."""
        newly_unlocked = []
        
        for achievement_id, achievement in self.achievements.items():
            if (achievement_id not in self.data["unlocked_achievements"] and 
                achievement["condition"]()):
                # Unlock the achievement
                self.data["unlocked_achievements"].append(achievement_id)
                # Award points
                self.data["points"] += achievement["points"]
                # Add to newly unlocked list
                newly_unlocked.append(achievement)
                # Check if level up is needed
                self._check_level_up()
        
        # Save if any achievements were unlocked
        if newly_unlocked:
            self.save_gamification_data()
            
        return newly_unlocked
    
    def check_challenges(self) -> Tuple[List[Challenge], List[Challenge]]:
        """Check for completed challenges."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        week_start = (today_date - datetime.timedelta(days=today_date.weekday())).strftime("%Y-%m-%d")
        
        newly_completed_daily = []
        newly_completed_weekly = []
        
        # Check daily challenges
        if today in self.data["daily_challenges"]:
            daily_data = self.data["daily_challenges"][today]
            
            for challenge_id in daily_data["challenges"]:
                if challenge_id not in daily_data["completed"]:
                    # Find the challenge definition
                    challenge = next((c for c in self.daily_challenges if c["id"] == challenge_id), None)
                    
                    if challenge and challenge["condition"]():
                        # Complete the challenge
                        daily_data["completed"].append(challenge_id)
                        # Award points
                        self.data["points"] += challenge["points"]
                        # Add to newly completed list
                        newly_completed_daily.append(challenge)
                        # Check if level up is needed
                        self._check_level_up()
        
        # Check weekly challenges
        if week_start in self.data["weekly_challenges"]:
            weekly_data = self.data["weekly_challenges"][week_start]
            
            for challenge_id in weekly_data["challenges"]:
                if challenge_id not in weekly_data["completed"]:
                    # Find the challenge definition
                    challenge = next((c for c in self.weekly_challenges if c["id"] == challenge_id), None)
                    
                    if challenge and challenge["condition"]():
                        # Complete the challenge
                        weekly_data["completed"].append(challenge_id)
                        # Award points
                        self.data["points"] += challenge["points"]
                        # Add to newly completed list
                        newly_completed_weekly.append(challenge)
                        # Check if level up is needed
                        self._check_level_up()
        
        # Save if any challenges were completed
        if newly_completed_daily or newly_completed_weekly:
            self.save_gamification_data()
            
        return newly_completed_daily, newly_completed_weekly
    
    def get_active_daily_challenges(self) -> List[Challenge]:
        """Get the active daily challenges."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        if today not in self.data["daily_challenges"]:
            self._ensure_daily_challenges()
            
        daily_data = self.data["daily_challenges"].get(today, {"challenges": [], "completed": []})
        
        active_challenges = []
        for challenge_id in daily_data["challenges"]:
            challenge = next((c for c in self.daily_challenges if c["id"] == challenge_id), None)
            if challenge:
                # Add completion status
                challenge = challenge.copy()
                challenge["completed"] = challenge_id in daily_data["completed"]
                active_challenges.append(challenge)
                
        return active_challenges
    
    def get_active_weekly_challenges(self) -> List[Challenge]:
        """Get the active weekly challenges."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        week_start = (today_date - datetime.timedelta(days=today_date.weekday())).strftime("%Y-%m-%d")
        
        if week_start not in self.data["weekly_challenges"]:
            self._ensure_daily_challenges()  # This also ensures weekly challenges
            
        weekly_data = self.data["weekly_challenges"].get(week_start, {"challenges": [], "completed": []})
        
        active_challenges = []
        for challenge_id in weekly_data["challenges"]:
            challenge = next((c for c in self.weekly_challenges if c["id"] == challenge_id), None)
            if challenge:
                # Add completion status
                challenge = challenge.copy()
                challenge["completed"] = challenge_id in weekly_data["completed"]
                active_challenges.append(challenge)
                
        return active_challenges
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        unlocked = []
        for achievement_id in self.data["unlocked_achievements"]:
            if achievement_id in self.achievements:
                unlocked.append(self.achievements[achievement_id])
        return unlocked
    
    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements."""
        locked = []
        for achievement_id, achievement in self.achievements.items():
            if achievement_id not in self.data["unlocked_achievements"]:
                locked.append(achievement)
        return locked
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements with unlock status."""
        all_achievements = []
        for achievement_id, achievement in self.achievements.items():
            achievement_copy = achievement.copy()
            achievement_copy["unlocked"] = achievement_id in self.data["unlocked_achievements"]
            all_achievements.append(achievement_copy)
        return all_achievements
    
    def get_level_progress(self) -> Tuple[int, int, int]:
        """Get current level, points, and points needed for next level."""
        current_level = self.data["level"]
        current_points = self.data["points"]
        points_for_next_level = self._points_for_level(current_level + 1)
        points_for_current_level = self._points_for_level(current_level)
        
        return current_level, current_points - points_for_current_level, points_for_next_level - points_for_current_level
    
    def _check_level_up(self) -> bool:
        """Check if user should level up based on points."""
        current_level = self.data["level"]
        next_level = current_level + 1
        points_needed = self._points_for_level(next_level)
        
        if self.data["points"] >= points_needed:
            self.data["level"] = next_level
            return True
        
        return False
    
    def _points_for_level(self, level: int) -> int:
        """Calculate points needed for a given level."""
        # Simple formula: 100 * level^1.5
        return int(100 * (level ** 1.5))
    
    # Helper methods for achievement and challenge conditions
    
    def _has_food_category(self, category: str) -> bool:
        """Check if user has logged any food in the specified category."""
        for date, day_data in self.data_manager.history.items():
            for food in day_data.get("food", []):
                if food.get("category") == category:
                    return True
        return False
    
    def _count_unique_foods_in_category(self, category: str) -> int:
        """Count unique foods logged in a specific category."""
        unique_foods = set()
        for date, day_data in self.data_manager.history.items():
            for food in day_data.get("food", []):
                if food.get("category") == category:
                    unique_foods.add(food["food"])
        return len(unique_foods)
    
    def _has_any_exercise(self) -> bool:
        """Check if user has logged any exercise."""
        for date, day_data in self.data_manager.history.items():
            if day_data.get("exercise", []):
                return True
        return False
    
    def _total_calories_burnt(self) -> int:
        """Calculate total calories burnt through exercise."""
        total = 0
        for date, day_data in self.data_manager.history.items():
            for exercise in day_data.get("exercise", []):
                total += exercise.get("calories_burnt", 0)
        return total
    
    def _has_any_weight_entry(self) -> bool:
        """Check if user has logged any weight entries."""
        for date, day_data in self.data_manager.history.items():
            if day_data.get("weight") is not None:
                return True
        return False
    
    def _days_under_calorie_goal(self, days: int) -> bool:
        """Check if user stayed under calorie goal for specified consecutive days."""
        # This is a simplified version - would need to track goal history for accuracy
        consecutive_days = 0
        dates = sorted(self.data_manager.history.keys())
        
        for i in range(len(dates) - 1, -1, -1):
            date = dates[i]
            day_data = self.data_manager.history[date]
            
            # Calculate net calories
            total_in = sum(food.get("calories", 0) for food in day_data.get("food", []))
            total_out = sum(ex.get("calories_burnt", 0) for ex in day_data.get("exercise", []))
            net_calories = total_in - total_out
            
            # Assume goal is 2000 calories (simplified)
            if net_calories <= 2000:
                consecutive_days += 1
                if consecutive_days >= days:
                    return True
            else:
                consecutive_days = 0
                
        return False
    
    def _has_custom_foods(self) -> bool:
        """Check if user has created any custom foods."""
        return os.path.exists(self.data_manager.custom_food_file) and os.path.getsize(self.data_manager.custom_food_file) > 2
    
    def _count_unique_exercises(self) -> int:
        """Count unique exercises logged."""
        unique_exercises = set()
        for date, day_data in self.data_manager.history.items():
            for exercise in day_data.get("exercise", []):
                unique_exercises.add(exercise["exercise"])
        return len(unique_exercises)
    
    def _logged_food_category_today(self, category: str) -> bool:
        """Check if user logged food in specified category today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(today)
        
        for food in day_data.get("food", []):
            if food.get("category") == category:
                return True
        return False
    
    def _exercise_minutes_today(self) -> float:
        """Calculate total exercise minutes logged today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(today)
        
        return sum(ex.get("duration", 0) for ex in day_data.get("exercise", []))
    
    def _logged_weight_today(self) -> bool:
        """Check if user logged weight today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(today)
        
        return day_data.get("weight") is not None
    
    def _under_calorie_goal_today(self) -> bool:
        """Check if user is under calorie goal today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(today)
        
        # Calculate net calories
        total_in = sum(food.get("calories", 0) for food in day_data.get("food", []))
        total_out = sum(ex.get("calories_burnt", 0) for ex in day_data.get("exercise", []))
        net_calories = total_in - total_out
        
        # Assume goal is 2000 calories (simplified)
        return net_calories <= 2000
    
    def _food_category_variety_today(self) -> int:
        """Count unique food categories logged today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(today)
        
        categories = set()
        for food in day_data.get("food", []):
            if "category" in food:
                categories.add(food["category"])
        
        return len(categories)
    
    def _calories_burnt_today(self) -> int:
        """Calculate calories burnt through exercise today."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(today)
        
        return sum(ex.get("calories_burnt", 0) for ex in day_data.get("exercise", []))
    
    def _logged_food_days_this_week(self) -> int:
        """Count days with food logs this week."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        
        # Get start of week (Monday)
        week_start = today_date - datetime.timedelta(days=today_date.weekday())
        
        days_with_food = 0
        for i in range(7):
            date = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = self.data_manager.get_day_data(date)
            
            if day_data.get("food", []):
                days_with_food += 1
                
        return days_with_food
    
    def _exercise_days_this_week(self) -> int:
        """Count days with exercise logs this week."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        
        # Get start of week (Monday)
        week_start = today_date - datetime.timedelta(days=today_date.weekday())
        
        days_with_exercise = 0
        for i in range(7):
            date = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = self.data_manager.get_day_data(date)
            
            if day_data.get("exercise", []):
                days_with_exercise += 1
                
        return days_with_exercise
    
    def _days_under_calorie_goal_this_week(self) -> int:
        """Count days under calorie goal this week."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        
        # Get start of week (Monday)
        week_start = today_date - datetime.timedelta(days=today_date.weekday())
        
        days_under_goal = 0
        for i in range(7):
            date = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = self.data_manager.get_day_data(date)
            
            # Calculate net calories
            total_in = sum(food.get("calories", 0) for food in day_data.get("food", []))
            total_out = sum(ex.get("calories_burnt", 0) for ex in day_data.get("exercise", []))
            net_calories = total_in - total_out
            
            # Assume goal is 2000 calories (simplified)
            if net_calories <= 2000:
                days_under_goal += 1
                
        return days_under_goal
    
    def _unique_foods_this_week(self) -> int:
        """Count unique foods logged this week."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.datetime.strptime(today, "%Y-%m-%d")
        
        # Get start of week (Monday)
        week_start = today_date - datetime.timedelta(days=today_date.weekday())
        
        unique_foods = set()
        for i in range(7):
            date = (week_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = self.data_manager.get_day_data(date)
            
            for food in day_data.get("food", []):
                unique_foods.add(food["food"])
                
        return len(unique_foods)
    
    def _logged_food_yesterday(self) -> bool:
        """Check if user logged food yesterday."""
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(yesterday)
        
        return len(day_data.get("food", [])) > 0
    
    def _logged_exercise_yesterday(self) -> bool:
        """Check if user logged exercise yesterday."""
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(yesterday)
        
        return len(day_data.get("exercise", [])) > 0
    
    def _logged_weight_yesterday(self) -> bool:
        """Check if user logged weight yesterday."""
        today = datetime.datetime.now()
        yesterday = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        day_data = self.data_manager.get_day_data(yesterday)
        
        return day_data.get("weight") is not None


class DataManager:
    """Class to handle all data operations including loading, saving, and manipulating data."""
    
    def __init__(self):
        self.data_file = "burger_tracker_data.json"
        self.custom_food_file = "custom_foods.json"
        self.custom_exercise_file = "custom_exercises.json"
        
        # Initialize databases
        self.food_database = self._initialize_food_database()
        self.exercise_database = self._initialize_exercise_database()
        
        # Load custom databases
        self.load_custom_databases()
        
        # Load history
        self.history = self.load_history()
        
        # Today's date string
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Today's entries
        self.today_entries = self.get_day_data(self.current_date)
    
    def _initialize_food_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the default food database."""
        return {
            # Burgers
            "Single Patty Burger": {"calories": 500, "category": "Burgers"},
            "Double Patty Burger": {"calories": 700, "category": "Burgers"},
            "Single Patty Cheeseburger": {"calories": 775, "category": "Burgers"},
            "Double Patty Cheeseburger": {"calories": 850, "category": "Burgers"},
            "Big Smasher Burger": {"calories": 1500, "category": "Burgers"},
            "Floyd Burger": {"calories": 1000, "category": "Burgers"},
            "The Biggest Burger": {"calories": 10000, "category": "Burgers"},
            "Iftar Burger": {"calories": 3000, "category": "Burgers"},
            "White Castle Box": {"calories": 1400, "category": "Burgers"},
            
            # Sides
            "Beef Tallow Fries": {"calories": 800, "category": "Sides"},
            "Southwestern Eggrolls": {"calories": 1200, "category": "Sides"},
            "Onion Rings": {"calories": 600, "category": "Sides"},
            "Curly Fries": {"calories": 550, "category": "Sides"},
            "Mozzarella Sticks": {"calories": 650, "category": "Sides"},
            "Potato Wedges": {"calories": 520, "category": "Sides"},
            "Coleslaw": {"calories": 320, "category": "Sides"},
            "Mac and Cheese": {"calories": 480, "category": "Sides"},
            
            # Drinks
            "Soda (Large)": {"calories": 300, "category": "Drinks"},
            "Milkshake": {"calories": 750, "category": "Drinks"},
            "Iced Tea": {"calories": 120, "category": "Drinks"},
            "Lemonade": {"calories": 220, "category": "Drinks"}
        }
    
    def _initialize_exercise_database(self) -> Dict[str, float]:
        """Initialize the default exercise database."""
        return {
            "Walking": 5,              # calories per minute
            "Jogging": 10,
            "Running": 14,
            "Swimming": 11,
            "Cycling": 10,
            "Weight Training": 8,
            "Basketball": 10,
            "Soccer": 10,
            "Tennis": 9,
            "Yoga": 5,
            "Dancing": 8,
            "HIIT": 15,
            "Elliptical": 9,
            "Jumping Rope": 13,
            "Boxing": 12,
            "Hiking": 7,
            "StairMaster": 9,
            "Rowing": 11,
            "Pilates": 5
        }
    
    def load_custom_databases(self) -> None:
        """Load custom foods and exercises from files."""
        # Load custom foods
        try:
            if os.path.exists(self.custom_food_file):
                with open(self.custom_food_file, "r") as f:
                    custom_foods = json.load(f)
                    # Add custom foods to the main database
                    self.food_database.update(custom_foods)
        except Exception as e:
            print(f"Error loading custom foods: {e}")
        
        # Load custom exercises
        try:
            if os.path.exists(self.custom_exercise_file):
                with open(self.custom_exercise_file, "r") as f:
                    custom_exercises = json.load(f)
                    # Add custom exercises to the main database
                    self.exercise_database.update(custom_exercises)
        except Exception as e:
            print(f"Error loading custom exercises: {e}")
    
    def load_history(self) -> History:
        """Load history from file with error handling and format conversion."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    history = json.load(f)
                    
                    # Convert old format to new format if needed
                    for date, entries in history.items():
                        if isinstance(entries, list):  # Old format
                            history[date] = {"food": entries, "exercise": [], "weight": None}
                        elif "weight" not in entries:  # Add weight field if missing
                            history[date]["weight"] = None
                    
                    return history
            except Exception as e:
                print(f"Failed to load history: {e}")
                return {}
        return {}
    
    def save_history(self) -> bool:
        """Save history to file with error handling."""
        # Save current entries to today's date
        self.history[self.current_date] = self.today_entries
        
        # Save history to file
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.history, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save history: {e}")
            return False
    
    def get_day_data(self, date_str: str) -> DayData:
        """Get food and exercise data for a specific day."""
        # If it's today and not in history, use today's entries if they exist
        if date_str == self.current_date and date_str not in self.history:
            # Check if today_entries exists to avoid circular reference during initialization
            if hasattr(self, 'today_entries'):
                return self.today_entries
            # During initialization, return default empty structure
            return {"food": [], "exercise": [], "weight": None}
        # Otherwise get from history
        return self.history.get(date_str, {"food": [], "exercise": [], "weight": None})
    
    def save_custom_food(self, name: str, calories: int, category: str) -> bool:
        """Save a custom food to the database."""
        # Add to the main database
        self.food_database[name] = {"calories": calories, "category": category}
        
        # Load existing custom foods or create empty dict
        custom_foods = {}
        if os.path.exists(self.custom_food_file):
            try:
                with open(self.custom_food_file, "r") as f:
                    custom_foods = json.load(f)
            except:
                pass
        
        # Add the new food
        custom_foods[name] = {"calories": calories, "category": category}
        
        # Save back to file
        try:
            with open(self.custom_food_file, "w") as f:
                json.dump(custom_foods, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving custom food: {e}")
            return False
    
    def save_custom_exercise(self, name: str, calories_per_min: float) -> bool:
        """Save a custom exercise to the database."""
        # Add to the main database
        self.exercise_database[name] = calories_per_min
        
        # Load existing custom exercises or create empty dict
        custom_exercises = {}
        if os.path.exists(self.custom_exercise_file):
            try:
                with open(self.custom_exercise_file, "r") as f:
                    custom_exercises = json.load(f)
            except:
                pass
        
        # Add the new exercise
        custom_exercises[name] = calories_per_min
        
        # Save back to file
        try:
            with open(self.custom_exercise_file, "w") as f:
                json.dump(custom_exercises, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving custom exercise: {e}")
            return False
    
    def add_food_entry(self, date: str, food: str, amount: float, calories: int, 
                      category: str, kyle_tax: bool) -> None:
        """Add a food entry to the specified date."""
        entry = {
            "food": food,
            "amount": amount,
            "calories": calories,
            "category": category,
            "kyle_tax": kyle_tax
        }
        
        if date == self.current_date:
            if "food" not in self.today_entries:
                self.today_entries["food"] = []
            self.today_entries["food"].append(entry)
        else:
            if date not in self.history:
                self.history[date] = {"food": [], "exercise": [], "weight": None}
            
            if "food" not in self.history[date]:
                self.history[date]["food"] = []
                
            self.history[date]["food"].append(entry)
    
    def add_exercise_entry(self, date: str, exercise: str, duration: float, 
                          calories_burnt: int) -> None:
        """Add an exercise entry to the specified date."""
        entry = {
            "exercise": exercise,
            "duration": duration,
            "calories_burnt": calories_burnt
        }
        
        if date == self.current_date:
            if "exercise" not in self.today_entries:
                self.today_entries["exercise"] = []
                
            self.today_entries["exercise"].append(entry)
        else:
            if date not in self.history:
                self.history[date] = {"food": [], "exercise": [], "weight": None}
            
            if "exercise" not in self.history[date]:
                self.history[date]["exercise"] = []
                
            self.history[date]["exercise"].append(entry)
    
    def update_weight(self, date: str, weight: Optional[float]) -> None:
        """Update weight for a specific date."""
        day_data = self.get_day_data(date)
        day_data["weight"] = weight
        
        # If it's today, update today_entries
        if date == self.current_date:
            self.today_entries["weight"] = weight
        
        # Update history
        self.history[date] = day_data
    
    def delete_food_entries(self, date: str, indices: List[int]) -> None:
        """Delete food entries at specified indices for a date."""
        day_data = self.get_day_data(date)
        food_entries = day_data.get("food", [])
        
        # Build new list without deleted items
        new_entries = [entry for i, entry in enumerate(food_entries) if i not in indices]
        
        # Update entries
        if date == self.current_date and date not in self.history:
            self.today_entries["food"] = new_entries
        else:
            if date not in self.history:
                self.history[date] = {"food": [], "exercise": [], "weight": None}
            self.history[date]["food"] = new_entries
    
    def delete_exercise_entries(self, date: str, indices: List[int]) -> None:
        """Delete exercise entries at specified indices for a date."""
        day_data = self.get_day_data(date)
        exercise_entries = day_data.get("exercise", [])
        
        # Build new list without deleted items
        new_entries = [entry for i, entry in enumerate(exercise_entries) if i not in indices]
        
        # Update entries
        if date == self.current_date and date not in self.history:
            self.today_entries["exercise"] = new_entries
        else:
            if date not in self.history:
                self.history[date] = {"food": [], "exercise": [], "weight": None}
            self.history[date]["exercise"] = new_entries
    
    def clear_food_entries(self, date: str) -> None:
        """Clear all food entries for a specific date."""
        if date == self.current_date and date not in self.history:
            self.today_entries["food"] = []
        else:
            if date in self.history:
                self.history[date]["food"] = []
    
    def clear_exercise_entries(self, date: str) -> None:
        """Clear all exercise entries for a specific date."""
        if date == self.current_date and date not in self.history:
            self.today_entries["exercise"] = []
        else:
            if date in self.history:
                self.history[date]["exercise"] = []
    
    def clear_today(self) -> None:
        """Clear all entries for today."""
        self.today_entries = {"food": [], "exercise": [], "weight": None}
    
    def delete_all_history(self) -> None:
        """Delete all history data."""
        self.history = {}
        self.today_entries = {"food": [], "exercise": [], "weight": None}
    
    def get_weight_history(self) -> List[Tuple[str, float]]:
        """Get all weight entries sorted by date."""
        weights = []
        for date, data in self.history.items():
            weight = data.get("weight")
            if weight is not None:
                weights.append((date, weight))
        
        # Sort by date (newest first)
        weights.sort(reverse=True)
        return weights
    
    def get_weekly_data(self, end_date_str: str) -> Tuple[List[str], List[int], List[int]]:
        """Get data for the last 7 days ending on the specified date."""
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        start_date = end_date - datetime.timedelta(days=6)
        
        dates = []
        calories_in = []
        calories_out = []
        
        # Collect data for each day
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            dates.append(current.strftime("%a"))  # Abbreviated day name
            
            # Get data for the day
            day_data = self.get_day_data(date_str)
            food_entries = day_data.get("food", [])
            exercise_entries = day_data.get("exercise", [])
            
            # Calculate total calories in
            total_in = 0
            for entry in food_entries:
                cal = entry["calories"]
                if entry.get("kyle_tax", False):
                    cal = int(cal * 0.85)
                total_in += cal
            
            # Calculate total calories out
            total_out = sum(ex.get("calories_burnt", 0) for ex in exercise_entries)
            
            calories_in.append(total_in)
            calories_out.append(total_out)
            
            current += datetime.timedelta(days=1)
        
        return dates, calories_in, calories_out
    
    def get_food_categories_data(self) -> Dict[str, int]:
        """Get total calories by food category across all dates."""
        food_categories = {}
        
        for date, day_data in self.history.items():
            food_entries = day_data.get("food", [])
            for entry in food_entries:
                category = entry.get("category", "Uncategorized")
                if category not in food_categories:
                    food_categories[category] = 0
                
                food_categories[category] += entry["calories"]
        
        # Also add today's entries if not in history
        if self.current_date not in self.history:
            for entry in self.today_entries.get("food", []):
                category = entry.get("category", "Uncategorized")
                if category not in food_categories:
                    food_categories[category] = 0
                
                food_categories[category] += entry["calories"]
        
        return food_categories
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all data."""
        total_days = len(self.history)
        total_foods = sum(len(day_data.get("food", [])) for day_data in self.history.values())
        total_exercises = sum(len(day_data.get("exercise", [])) for day_data in self.history.values())
        
        # Calculate total calories consumed and burned
        total_calories = 0
        total_burned = 0
        for day_data in self.history.values():
            # Calculate consumed calories with Kyle Tax
            for entry in day_data.get("food", []):
                calories = entry["calories"]
                if entry.get("kyle_tax", False):
                    calories = int(calories * 0.85)
                total_calories += calories
            
            # Calculate burned calories
            for exercise in day_data.get("exercise", []):
                total_burned += exercise.get("calories_burnt", 0)
        
        # Get weight data
        weights = []
        for day_data in self.history.values():
            weight = day_data.get("weight")
            if weight is not None:
                weights.append(weight)
        
        stats = {
            "total_days": total_days,
            "total_foods": total_foods,
            "total_exercises": total_exercises,
            "total_calories": total_calories,
            "total_burned": total_burned,
            "net_calories": total_calories - total_burned,
            "weights": weights
        }
        
        return stats


class ChartManager:
    """Class to handle chart creation and visualization."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Create a figure and axis with the appropriate styling."""
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#2b3e50')  # Match background
        ax.set_facecolor('#2b3e50')
        ax.tick_params(colors='white')  # White ticks
        
        # Set title text color to white
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        
        return fig, ax
    
    def create_weekly_chart(self, ax: plt.Axes, date_str: str, goal: int) -> None:
        """Create a weekly net calories chart."""
        dates, calories_in, calories_out = self.data_manager.get_weekly_data(date_str)
        
        # Create the stacked bar chart for net calories
        net_calories = [in_cal - out_cal for in_cal, out_cal in zip(calories_in, calories_out)]
        
        # Plot bars
        bars = ax.bar(dates, net_calories, color='#5cb85c')
        
        # Color bars based on positive/negative values
        for i, bar in enumerate(bars):
            if net_calories[i] < 0:
                bar.set_color('#d9534f')  # Red for negative net calories
        
        ax.set_title('Net Calories - Last 7 Days')
        ax.set_xlabel('Day')
        ax.set_ylabel('Net Calories (In - Out)')
        
        # Add goal line if set
        if goal > 0:
            ax.axhline(y=goal, color='r', linestyle='--', label=f'Goal ({goal} cal)')
            ax.legend()
    
    def create_distribution_chart(self, ax: plt.Axes, date_str: str) -> None:
        """Create a pie chart showing calorie distribution for a specific date."""
        day_data = self.data_manager.get_day_data(date_str)
        food_entries = day_data.get("food", [])
        
        if not food_entries:
            ax.text(0.5, 0.5, "No food data for selected date", 
                   horizontalalignment='center', verticalalignment='center')
            return
        
        # Extract food names and calorie values
        foods = []
        calories = []
        
        for entry in food_entries:
            foods.append(entry["food"])
            cal = entry["calories"]
            if entry.get("kyle_tax", False):
                cal = int(cal * 0.85)
            calories.append(cal)
        
        # Create pie chart
        ax.pie(calories, labels=foods, autopct='%1.1f%%', startangle=90)
        ax.set_title(f'Calorie Distribution - {date_str}')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    def create_food_types_chart(self, ax: plt.Axes) -> None:
        """Create a pie chart showing calories by food category."""
        food_categories = self.data_manager.get_food_categories_data()
        
        if not food_categories:
            ax.text(0.5, 0.5, "No data available", 
                   horizontalalignment='center', verticalalignment='center')
            return
        
        # Create the pie chart
        labels = list(food_categories.keys())
        sizes = list(food_categories.values())
        
        # Custom colors for categories
        colors = {
            "Burgers": "#FF9E00",  # Orange
            "Sides": "#4CAF50",    # Green
            "Drinks": "#2196F3",   # Blue
            "Uncategorized": "#9E9E9E"  # Gray
        }
        
        # Get colors for each category
        chart_colors = [colors.get(category, "#9E9E9E") for category in labels]
        
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=chart_colors)
        ax.set_title('Calories by Food Category')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    def create_calories_in_out_chart(self, ax: plt.Axes, date_str: str) -> None:
        """Create a bar chart comparing calories in vs calories out."""
        dates, calories_in, calories_out = self.data_manager.get_weekly_data(date_str)
        
        # Create the comparison bar chart
        x = range(len(dates))
        width = 0.35
        
        # Plot bars
        ax.bar([i - width/2 for i in x], calories_in, width, label='Calories In', color='#d9534f')
        ax.bar([i + width/2 for i in x], calories_out, width, label='Calories Out', color='#5cb85c')
        
        ax.set_title('Calories In vs. Calories Out - Last 7 Days')
        ax.set_xlabel('Day')
        ax.set_ylabel('Calories')
        ax.set_xticks(x)
        ax.set_xticklabels(dates)
        ax.legend()
    
    def create_weight_tracking_chart(self, ax: plt.Axes) -> None:
        """Create a line chart showing weight over time."""
        # Get weight entries from history
        weight_history = self.data_manager.get_weight_history()
        
        # Sort by date (oldest first for the chart)
        weight_history.sort(key=lambda x: x[0])
        
        if not weight_history:
            ax.text(0.5, 0.5, "No weight data available", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   color='white',
                   fontsize=14)
            return
        
        dates, weights = zip(*weight_history)
        
        # Format dates for display
        formatted_dates = [datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%b %d") for date in dates]
        
        # Create the weight tracking line chart
        ax.plot(formatted_dates, weights, marker='o', linestyle='-', linewidth=2, markersize=8, color='#5cb85c')
        
        # Calculate 7-day moving average if enough data points
        if len(weights) >= 7:
            moving_avg = []
            for i in range(len(weights)):
                if i < 6:  # Not enough data for 7-day average at the beginning
                    moving_avg.append(None)
                else:
                    avg = sum(weights[i-6:i+1]) / 7
                    moving_avg.append(avg)
            
            # Plot the moving average
            ax.plot(formatted_dates, moving_avg, marker='', linestyle='--', linewidth=1.5, color='#f0ad4e', 
                    label='7-day Moving Average')
            ax.legend(loc='best')
        
        # Set chart title and labels
        ax.set_title("Weight Tracking Over Time", fontsize=16, color='white')
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Weight (lb)", fontsize=12)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Set grid
        ax.grid(True, linestyle='--', alpha=0.7, color='gray')
        
        # Tight layout
        plt.tight_layout()


class CalendarDialog:
    """Class to handle the calendar dialog for date selection."""
    
    def __init__(self, parent, current_date_var, history, on_date_selected):
        self.parent = parent
        self.current_date_var = current_date_var
        self.history = history
        self.on_date_selected = on_date_selected
        
        # Parse current date
        try:
            current_date = datetime.datetime.strptime(self.current_date_var.get(), "%Y-%m-%d")
        except ValueError:
            current_date = datetime.datetime.now()
        
        # Create variables to store selected date
        self.cal_year = tk.IntVar(value=current_date.year)
        self.cal_month = tk.IntVar(value=current_date.month)
        self.cal_day = tk.IntVar(value=current_date.day)
        
        # Create the dialog
        self.create_dialog()
    
    def create_dialog(self):
        # Create a toplevel window for the calendar
        self.cal_window = tk.Toplevel(self.parent)
        self.cal_window.title("Select Date")
        self.cal_window.geometry("300x320")
        self.cal_window.resizable(False, False)
        self.cal_window.transient(self.parent)  # Make it transient to the main window
        self.cal_window.grab_set()  # Modal dialog
        
        # Center window
        self.cal_window.update_idletasks()
        width = self.cal_window.winfo_width()
        height = self.cal_window.winfo_height()
        x = (self.cal_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.cal_window.winfo_screenheight() // 2) - (height // 2)
        self.cal_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Month and year selection
        nav_frame = ttk.Frame(self.cal_window)
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        # Previous month button
        prev_btn = ttk.Button(
            nav_frame, 
            text="◀", 
            width=2,
            command=lambda: self.change_month(-1)
        )
        prev_btn.pack(side="left", padx=5)
        
        # Month combo
        months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        month_combo = ttk.Combobox(
            nav_frame, 
            values=months, 
            width=10, 
            state="readonly",
            textvariable=tk.StringVar(value=months[self.cal_month.get()-1])
        )
        month_combo.pack(side="left", padx=5)
        month_combo.bind("<<ComboboxSelected>>", 
                         lambda e: [self.cal_month.set(month_combo.current()+1), 
                                    self.update_days()])
        
        # Year spinbox
        year_spin = ttk.Spinbox(
            nav_frame, 
            from_=1900, 
            to=2100, 
            width=6,
            textvariable=self.cal_year
        )
        year_spin.pack(side="left", padx=5)
        year_spin.bind("<Return>", lambda e: self.update_days())
        
        # Next month button
        next_btn = ttk.Button(
            nav_frame, 
            text="▶", 
            width=2,
            command=lambda: self.change_month(1)
        )
        next_btn.pack(side="left", padx=5)
        
        # Days of the week
        days_frame = ttk.Frame(self.cal_window)
        days_frame.pack(fill="x", padx=10, pady=2)
        
        for i, day in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            label = ttk.Label(days_frame, text=day, width=3, anchor="center")
            label.grid(row=0, column=i, padx=1, pady=1)
        
        # Days frame where we'll add the day buttons
        self.days_frame = ttk.Frame(self.cal_window)
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Update the calendar
        self.update_days()
        
        # Button frame
        button_frame = ttk.Frame(self.cal_window)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Today button
        ttk.Button(
            button_frame, 
            text="Today", 
            style="Info.TButton",
            command=lambda: [
                self.cal_year.set(datetime.datetime.now().year),
                self.cal_month.set(datetime.datetime.now().month),
                self.cal_day.set(datetime.datetime.now().day),
                self.update_days()
            ]
        ).pack(side="left", padx=10)
        
        # Select button
        ttk.Button(
            button_frame, 
            text="Select", 
            style="Success.TButton",
            command=self.select_date
        ).pack(side="right", padx=10)
        
        # Cancel button
        ttk.Button(
            button_frame, 
            text="Cancel", 
            style="Secondary.TButton",
            command=self.cal_window.destroy
        ).pack(side="right", padx=10)
    
    def update_days(self):
        # Clear existing day buttons
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        # Get the number of days in the selected month
        year = self.cal_year.get()
        month = self.cal_month.get()
        
        # Get the first day of the month (0 = Monday, 6 = Sunday in the calendar module)
        first_day, num_days = calendar.monthrange(year, month)
        
        # Adjust for Sunday as first day of week (calendar.monthrange returns 0 for Monday)
        first_day = (first_day + 1) % 7
        
        # Create day buttons
        btn_style = ttk.Style()
        btn_style.configure("Cal.TButton", font=("Roboto", 9))
        
        day = 1
        for row in range(6):  # 6 weeks max
            if day > num_days:
                break
                
            for col in range(7):  # 7 days per week
                if row == 0 and col < first_day:
                    # Empty cell before first day
                    label = ttk.Label(self.days_frame, text="", width=3)
                    label.grid(row=row, column=col, padx=1, pady=1)
                elif day <= num_days:
                    # Create the day button
                    btn = ttk.Button(
                        self.days_frame, 
                        text=str(day), 
                        width=3,
                        style="Cal.TButton",
                        command=lambda d=day: [self.cal_day.set(d), self.select_date()]
                    )
                    
                    # Highlight today
                    today = datetime.datetime.now()
                    if day == today.day and month == today.month and year == today.year:
                        btn.configure(style="Accent.TButton")
                    
                    # Highlight selected day
                    if day == self.cal_day.get() and month == self.cal_month.get() and year == self.cal_year.get():
                        btn.configure(style="Accent.TButton")
                    
                    # Check if there's data for this date
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    if date_str in self.history:
                        has_data = False
                        has_weight = False
                        day_data = self.history[date_str]
                        
                        if day_data.get("food") or day_data.get("exercise"):
                            has_data = True
                            
                        if day_data.get("weight") is not None:
                            has_weight = True
                        
                        if has_data and has_weight:
                            btn.configure(style="Success.TButton", text=f"{day}*")
                        elif has_data:
                            btn.configure(style="Info.TButton", text=f"{day}*")
                        elif has_weight:
                            btn.configure(style="Success.TButton")
                    
                    btn.grid(row=row, column=col, padx=1, pady=1)
                    day += 1
    
    def change_month(self, delta):
        # Update the month and year when navigating
        month = self.cal_month.get() + delta
        year = self.cal_year.get()
        
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        
        self.cal_month.set(month)
        self.cal_year.set(year)
        self.update_days()
    
    def select_date(self):
        # Get the selected date
        year = self.cal_year.get()
        month = self.cal_month.get()
        day = self.cal_day.get()
        
        # Format the date as YYYY-MM-DD
        formatted_date = f"{year}-{month:02d}-{day:02d}"
        
        # Set the date variable
        self.current_date_var.set(formatted_date)
        
        # Close the calendar window
        self.cal_window.destroy()
        
        # Call the callback function
        if self.on_date_selected:
            self.on_date_selected(formatted_date)


class BurgerTracker:
    """Main application class for the Jacob Burger Tracker."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Jacob Burger Tracker")
        
        # Set initial geometry
        self.root.geometry("900x700")
        
        # Make window resizable
        self.root.resizable(True, True)
        
        # Configure responsive behavior
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Add window resize event handler
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Register custom themes
        self.register_custom_themes()
        
        # Apply modern theme
        self.style = Style(theme="superhero")
    
    def register_custom_themes(self):
        """Register custom themes for the application."""
        try:
            # Try to import register_theme, but handle if it's not available
            try:
                from ttkbootstrap.themes import register_theme
                
                # Flashy Themes
                
                # Neon Theme - Bright neon colors with dark background
                neon_colors = {
                    "primary": "#FF00FF",  # Bright pink
                    "secondary": "#00FFFF", # Cyan
                    "success": "#00FF00",   # Neon green
                    "info": "#00BFFF",      # Deep sky blue
                    "warning": "#FFFF00",   # Bright yellow
                    "danger": "#FF0000",    # Bright red
                    "bg": "#121212",        # Very dark gray
                    "fg": "#FFFFFF",        # White
                    "selectbg": "#FF00FF",  # Bright pink
                    "selectfg": "#FFFFFF",  # White
                    "border": "#333333",    # Dark gray
                    "inputfg": "#FFFFFF",   # White
                    "inputbg": "#333333",   # Dark gray
                }
                register_theme("neon", neon_colors)
                
                # Retro Theme - 80s/90s inspired colors
                retro_colors = {
                    "primary": "#FF6B6B",   # Coral red
                    "secondary": "#4ECDC4", # Turquoise
                    "success": "#FFE66D",   # Pale yellow
                    "info": "#1A535C",      # Dark teal
                    "warning": "#FF9F1C",   # Orange
                    "danger": "#F71735",    # Bright red
                    "bg": "#292F36",        # Dark blue-gray
                    "fg": "#FFFFFF",        # White
                    "selectbg": "#FF6B6B",  # Coral red
                    "selectfg": "#FFFFFF",  # White
                    "border": "#4ECDC4",    # Turquoise
                    "inputfg": "#FFFFFF",   # White
                    "inputbg": "#1A535C",   # Dark teal
                }
                register_theme("retro", retro_colors)
                
                # Party Theme - Colorful and playful
                party_colors = {
                    "primary": "#FF1493",   # Deep pink
                    "secondary": "#00BFFF", # Deep sky blue
                    "success": "#32CD32",   # Lime green
                    "info": "#9370DB",      # Medium purple
                    "warning": "#FFD700",   # Gold
                    "danger": "#FF4500",    # Orange red
                    "bg": "#FFFFFF",        # White
                    "fg": "#333333",        # Dark gray
                    "selectbg": "#FF1493",  # Deep pink
                    "selectfg": "#FFFFFF",  # White
                    "border": "#00BFFF",    # Deep sky blue
                    "inputfg": "#333333",   # Dark gray
                    "inputbg": "#F0F0F0",   # Light gray
                }
                register_theme("party", party_colors)
                
                # Minimal Themes
                
                # Monochrome Theme - Black and white with minimal accent
                monochrome_colors = {
                    "primary": "#333333",   # Dark gray
                    "secondary": "#666666", # Medium gray
                    "success": "#999999",   # Light gray
                    "info": "#CCCCCC",      # Very light gray
                    "warning": "#666666",   # Medium gray
                    "danger": "#000000",    # Black
                    "bg": "#FFFFFF",        # White
                    "fg": "#000000",        # Black
                    "selectbg": "#333333",  # Dark gray
                    "selectfg": "#FFFFFF",  # White
                    "border": "#CCCCCC",    # Very light gray
                    "inputfg": "#000000",   # Black
                    "inputbg": "#F5F5F5",   # Off-white
                }
                register_theme("monochrome", monochrome_colors)
                
                # Pastel Theme - Soft pastel colors
                pastel_colors = {
                    "primary": "#A0D2EB",   # Pastel blue
                    "secondary": "#D0BDF4", # Pastel purple
                    "success": "#8EECF5",   # Pastel cyan
                    "info": "#E2F0CB",      # Pastel green
                    "warning": "#FFCAD4",   # Pastel pink
                    "danger": "#F3B0C3",    # Pastel red
                    "bg": "#FFFFFF",        # White
                    "fg": "#6D6875",        # Muted gray
                    "selectbg": "#A0D2EB",  # Pastel blue
                    "selectfg": "#FFFFFF",  # White
                    "border": "#E2F0CB",    # Pastel green
                    "inputfg": "#6D6875",   # Muted gray
                    "inputbg": "#F8F9FA",   # Off-white
                }
                register_theme("pastel", pastel_colors)
                
                # Zen Theme - Calm, neutral colors
                zen_colors = {
                    "primary": "#5D5C61",   # Slate gray
                    "secondary": "#938E94", # Taupe
                    "success": "#7395AE",   # Dusty blue
                    "info": "#557A95",      # Steel blue
                    "warning": "#B1A296",   # Taupe
                    "danger": "#8D8741",    # Olive
                    "bg": "#F5F5F5",        # Off-white
                    "fg": "#333333",        # Dark gray
                    "selectbg": "#7395AE",  # Dusty blue
                    "selectfg": "#FFFFFF",  # White
                    "border": "#B1A296",    # Taupe
                    "inputfg": "#333333",   # Dark gray
                    "inputbg": "#FFFFFF",   # White
                }
                register_theme("zen", zen_colors)
                
                # Configure global styling
                self.style.configure("TButton", font=("Roboto", 10))
                self.style.configure("TLabel", font=("Roboto", 10))
                self.style.configure("TFrame", background="#2b3e50")
                
                print("Custom themes registered successfully")
            except ImportError as e:
                print(f"register_theme not available in this version of ttkbootstrap: {e}")
                # Skip custom theme registration but continue with default theme
                pass
                
        except Exception as e:
            print(f"Error registering custom themes: {e}")
            
        # Fall back to default theme if custom themes fail
        try:
            self.style = Style(theme="superhero")  # Use a default theme that comes with ttkbootstrap
        except:
            print("Could not apply any theme, using system default")
        
        
        # App version
        self.app_version = "1.8"  # Updated version number for gamification update
        
        # ASCII art for the app
        self.ascii_art = """
              _                          _                 
             | |   __ _    ___    ___   | |__              
          _  | |  / _` |  / __|  / _ \  | '_ \             
         | |_| | | (_| | | (__  | (_) | | |_) |            
          \___/   \__,_|  \___|  \___/  |_.__/             
         | __ )   _   _   _ __    __ _    ___   _ __       
         |  _ \  | | | | | '__|  / _` |  / _ \ | '__|      
         | |_) | | |_| | | |    | (_| | |  __/ | |         
         |____/   \__,_| |_|     \__, | _\___| |_|         
         |_   _|  _ __    __ _   |___/ | | __   ___   _ __ 
           | |   | '__|  / _` |  / __| | |/ /  / _ \ | '__|
           | |   | |    | (_| | | (__  |   <  |  __/ | |   
           |_|   |_|     \__,_|  \___| |_|\_\  \___| |_|                       
"""
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Initialize gamification manager
        self.gamification_manager = GamificationManager(self.data_manager)
        
        # Initialize chart manager
        self.chart_manager = ChartManager(self.data_manager)
        
        # Kyle Tax enabled flag
        self.kyle_tax_enabled = tk.BooleanVar(value=False)
        
        # Create menu
        self.create_menu()
        
        # Create the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure main frame for responsive scaling
        for i in range(5):  # Generous number of columns
            self.main_frame.columnconfigure(i, weight=1)
        for i in range(5):  # Generous number of rows
            self.main_frame.rowconfigure(i, weight=1)
        
        # Create a header with logo and title
        self.create_header()
        
        # Create tabs for different views
        self.create_notebook()
        
        # Setup tracking tab
        self.setup_tracking_tab()

        # Setup exercise tab
        self.setup_exercise_tab()
        
        # Setup weight tracking tab
        self.setup_weight_tab()
        
        # Setup stats tab
        self.setup_stats_tab()
        
        # Setup achievements tab
        self.setup_achievements_tab()
        
        # Load today's entries
        self.load_entries()
        self.load_exercises()  # Load exercises
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create the application header with logo and title."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=10)
        
        # App logo (using emoji as placeholder)
        logo_label = ttk.Label(header_frame, text="🍔", font=("Arial", 24))
        logo_label.pack(side=tk.LEFT, padx=10)
        
        # App title
        title_label = ttk.Label(
            header_frame, 
            text="Jacob Burger Tracker", 
            font=("Roboto", 20, "bold"),
            foreground="#5cb85c"
        )
        title_label.pack(side=tk.LEFT, padx=10)
    
    def create_notebook(self):
        """Create the notebook with tabs for different views."""
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure notebook for responsive behavior
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create tab for daily tracking
        self.tracking_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.exercise_tab = ttk.Frame(self.notebook)  # New tab for exercise tracking
        self.weight_tab = ttk.Frame(self.notebook)  # New tab for weight tracking
        self.achievements_tab = ttk.Frame(self.notebook)  # New tab for achievements
        
        # Configure tab frames for responsive behavior
        for tab in [self.tracking_tab, self.stats_tab, self.exercise_tab, self.weight_tab, self.achievements_tab]:
            for i in range(5):  # Generous number of columns
                tab.columnconfigure(i, weight=1)
            for i in range(5):  # Generous number of rows
                tab.rowconfigure(i, weight=1)
        
        self.notebook.add(self.tracking_tab, text="Daily Tracking")
        self.notebook.add(self.exercise_tab, text="Exercise Log")  # New exercise tab
        self.notebook.add(self.weight_tab, text="Weight Tracker")  # New weight tracking tab
        self.notebook.add(self.stats_tab, text="Statistics")
        self.notebook.add(self.achievements_tab, text="Achievements")  # New achievements tab
    
    def create_status_bar(self):
        """Create the status bar at the bottom of the application."""
        status_bar = ttk.Frame(self.main_frame)
        status_bar.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_bar, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Version info
        version_label = ttk.Label(status_bar, text=f"v{self.app_version}", anchor=tk.E)
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_tracking_tab(self):
        """Setup the daily tracking tab."""
        # Upper section with date and goal controls
        control_frame = ttk.Frame(self.tracking_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left side - Date selection
        date_frame = ttk.LabelFrame(control_frame, text="Date Selection")
        date_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        date_controls = ttk.Frame(date_frame)
        date_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(date_controls, text="Date:").pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar(value=self.data_manager.current_date)
        date_entry = ttk.Entry(date_controls, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        # Bind double-click and Enter key to show calendar
        date_entry.bind("<Double-1>", lambda e: self.show_calendar())
        date_entry.bind("<Return>", lambda e: self.load_entries())
        
        # Calendar button with icon
        cal_button = ttk.Button(
            date_controls,
            text="📅",  # Calendar emoji
            width=2,
            command=self.show_calendar
        )
        cal_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            date_controls, 
            text="←", 
            width=2,
            style="Accent.TButton",
            command=lambda: self.change_date(-1)
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_controls, 
            text="Today", 
            style="Accent.TButton",
            command=self.go_to_today
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            date_controls, 
            text="→", 
            width=2,
            style="Accent.TButton",
            command=lambda: self.change_date(1)
        ).pack(side=tk.LEFT)
        
        # Right side - Calorie goal
        goal_frame = ttk.LabelFrame(control_frame, text="Daily Calorie Goal")
        goal_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.X, expand=True)
        
        goal_controls = ttk.Frame(goal_frame)
        goal_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(goal_controls, text="Goal:").pack(side=tk.LEFT, padx=5)
        
        self.goal_var = tk.StringVar(value="2000")
        goal_entry = ttk.Entry(goal_controls, textvariable=self.goal_var, width=8)
        goal_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            goal_controls, 
            text="Set Goal", 
            style="Accent.TButton",
            command=self.set_goal
        ).pack(side=tk.LEFT, padx=5)
        
        # Kyle Tax switch
        kyle_frame = ttk.LabelFrame(control_frame, text="Special Options")
        kyle_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.X, expand=True)
        
        kyle_controls = ttk.Frame(kyle_frame)
        kyle_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Checkbutton(
            kyle_controls,
            text="Enable Kyle Tax (-15% calories)",
            variable=self.kyle_tax_enabled,
            command=self.apply_kyle_tax
        ).pack(side=tk.LEFT, padx=5)
        
        # Create the food log frame
        log_frame = ttk.LabelFrame(self.tracking_tab, text="Food Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for food entries
        columns = ("Food", "Quantity", "Category", "Calories", "Kyle Tax")
        self.tree = ttk.Treeview(log_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Food", width=150)
        self.tree.column("Quantity", width=60)
        self.tree.column("Category", width=80)
        self.tree.column("Calories", width=80)
        self.tree.column("Kyle Tax", width=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create button frame
        button_frame = ttk.Frame(self.tracking_tab)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Add buttons with improved styling
        ttk.Button(
            button_frame, 
            text="Add Food Item", 
            style="Success.TButton",
            command=self.add_food
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Delete Selected", 
            style="Danger.TButton",
            command=self.delete_food
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Clear All", 
            style="Warning.TButton",
            command=self.clear_all
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Save Data", 
            style="Info.TButton",
            command=self.save_history
        ).pack(side="right", padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(self.tracking_tab)
        progress_frame.pack(fill="x", padx=10, pady=10)
        
        # Calorie progress bar
        self.progress_var = tk.DoubleVar(value=0)
        ttk.Label(progress_frame, text="Daily Progress:").pack(side=tk.LEFT, padx=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate",
            variable=self.progress_var
        )
        self.progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Total calories display and remaining
        stats_frame = ttk.Frame(self.tracking_tab)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_var = tk.StringVar(value="Total Calories: 0")
        self.burnt_var = tk.StringVar(value="Calories Burnt: 0")
        self.net_var = tk.StringVar(value="Net Calories: 0")
        self.remaining_var = tk.StringVar(value="Remaining: 2000")
        
        # Create a grid layout for the calorie information
        calorie_grid = ttk.Frame(stats_frame)
        calorie_grid.pack(fill="x", expand=True)
        
        ttk.Label(
            calorie_grid, 
            textvariable=self.total_var,
            font=("Roboto", 12, "bold")
        ).grid(row=0, column=0, padx=10, sticky="w")
        
        ttk.Label(
            calorie_grid, 
            textvariable=self.burnt_var,
            font=("Roboto", 12, "bold"),
            foreground="#5cb85c"  # Green for calories burnt
        ).grid(row=0, column=1, padx=10)
        
        ttk.Label(
            calorie_grid, 
            textvariable=self.net_var,
            font=("Roboto", 12, "bold")
        ).grid(row=1, column=0, padx=10, sticky="w", pady=5)
        
        ttk.Label(
            calorie_grid, 
            textvariable=self.remaining_var,
            font=("Roboto", 12, "bold")
        ).grid(row=1, column=1, padx=10, pady=5)
    
    def setup_exercise_tab(self):
        """Setup the exercise tracking tab."""
        # Exercise tab main container
        exercise_frame = ttk.Frame(self.exercise_tab)
        exercise_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Upper controls - same date selector as in tracking tab
        control_frame = ttk.Frame(exercise_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        date_frame = ttk.LabelFrame(control_frame, text="Date Selection")
        date_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        date_controls = ttk.Frame(date_frame)
        date_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(date_controls, text="Date:").pack(side=tk.LEFT, padx=5)
        
        # Use the same date variable as the main tab
        date_entry = ttk.Entry(date_controls, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        # Bind double-click and Enter key to show calendar
        date_entry.bind("<Double-1>", lambda e: self.show_calendar())
        date_entry.bind("<Return>", lambda e: self.load_exercises())
        
        # Calendar button with icon
        cal_button = ttk.Button(
            date_controls,
            text="📅",  # Calendar emoji
            width=2,
            command=self.show_calendar
        )
        cal_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            date_controls, 
            text="←", 
            width=2,
            style="Accent.TButton",
            command=lambda: self.change_date(-1)
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_controls, 
            text="Today", 
            style="Accent.TButton",
            command=self.go_to_today
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            date_controls, 
            text="→", 
            width=2,
            style="Accent.TButton",
            command=lambda: self.change_date(1)
        ).pack(side=tk.LEFT)
        
        # Exercise log
        log_frame = ttk.LabelFrame(exercise_frame, text="Exercise Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create treeview for exercise entries
        columns = ("Exercise", "Duration (min)", "Calories Burnt")
        self.exercise_tree = ttk.Treeview(log_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings
        for col in columns:
            self.exercise_tree.heading(col, text=col)
        
        self.exercise_tree.column("Exercise", width=150)
        self.exercise_tree.column("Duration (min)", width=120)
        self.exercise_tree.column("Calories Burnt", width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.exercise_tree.yview)
        self.exercise_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.exercise_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons
        button_frame = ttk.Frame(exercise_frame)
        button_frame.pack(fill="x", padx=5, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Add Exercise", 
            style="Success.TButton",
            command=self.add_exercise
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Delete Selected", 
            style="Danger.TButton",
            command=self.delete_exercise
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Clear All", 
            style="Warning.TButton",
            command=self.clear_all_exercises
        ).pack(side="left", padx=5)
        
        # Summary frame
        summary_frame = ttk.Frame(exercise_frame)
        summary_frame.pack(fill="x", padx=5, pady=10)
        
        self.total_exercise_var = tk.StringVar(value="Total Exercise Time: 0 minutes")
        self.total_burnt_var = tk.StringVar(value="Total Calories Burnt: 0")
        
        ttk.Label(
            summary_frame, 
            textvariable=self.total_exercise_var,
            font=("Roboto", 12)
        ).pack(side="left", padx=20)
        
        ttk.Label(
            summary_frame, 
            textvariable=self.total_burnt_var,
            font=("Roboto", 12, "bold"),
            foreground="#5cb85c"  # Green color for burnt calories
        ).pack(side="right", padx=20)
    
    def setup_weight_tab(self):
        """Setup the weight tracking tab."""
        # Weight tracking tab main container
        weight_frame = ttk.Frame(self.weight_tab)
        weight_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Upper controls - same date selector as in tracking tab
        control_frame = ttk.Frame(weight_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        date_frame = ttk.LabelFrame(control_frame, text="Date Selection")
        date_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        date_controls = ttk.Frame(date_frame)
        date_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(date_controls, text="Date:").pack(side=tk.LEFT, padx=5)
        
        # Use the same date variable as the main tab
        date_entry = ttk.Entry(date_controls, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        # Bind double-click and Enter key to show calendar
        date_entry.bind("<Double-1>", lambda e: self.show_calendar())
        date_entry.bind("<Return>", lambda e: self.load_weight_history())
        
        # Calendar button with icon
        cal_button = ttk.Button(
            date_controls,
            text="📅",  # Calendar emoji
            width=2,
            command=self.show_calendar
        )
        cal_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            date_controls, 
            text="←", 
            width=2,
            style="Accent.TButton",
            command=lambda: self.change_date(-1)
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_controls, 
            text="Today", 
            style="Accent.TButton",
            command=self.go_to_today
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            date_controls, 
            text="→", 
            width=2,
            style="Accent.TButton",
            command=lambda: self.change_date(1)
        ).pack(side=tk.LEFT)
        
        # Current weight entry section
        current_weight_frame = ttk.LabelFrame(weight_frame, text="Enter Today's Weight")
        current_weight_frame.pack(fill=tk.X, padx=5, pady=10)
        
        weight_entry_frame = ttk.Frame(current_weight_frame)
        weight_entry_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(weight_entry_frame, text="Weight (lb):").pack(side=tk.LEFT, padx=5)
        
        self.weight_var = tk.StringVar()
        weight_entry = ttk.Entry(weight_entry_frame, textvariable=self.weight_var, width=10)
        weight_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            weight_entry_frame,
            text="Save Weight",
            style="Success.TButton",
            command=self.save_weight
        ).pack(side=tk.LEFT, padx=5)
        
        # History section
        history_frame = ttk.LabelFrame(weight_frame, text="Weight History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create treeview for weight entries
        columns = ("Date", "Weight (lb)")
        self.weight_tree = ttk.Treeview(history_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings
        for col in columns:
            self.weight_tree.heading(col, text=col)
        
        self.weight_tree.column("Date", width=150)
        self.weight_tree.column("Weight (lb)", width=120)
        
        # Add scrollbar
        weight_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.weight_tree.yview)
        self.weight_tree.configure(yscrollcommand=weight_scrollbar.set)
        
        self.weight_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        weight_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        weight_button_frame = ttk.Frame(weight_frame)
        weight_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            weight_button_frame,
            text="Delete Selected",
            style="Danger.TButton",
            command=self.delete_weight
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            weight_button_frame,
            text="Edit Selected",
            style="Info.TButton",
            command=self.edit_weight
        ).pack(side=tk.LEFT, padx=5)
        
        # Load initial weight history
        self.load_weight_history()
    
    def setup_stats_tab(self):
        """Setup the statistics tab."""
        # Create frames for stats display
        chart_frame = ttk.Frame(self.stats_tab)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(chart_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Select Chart:").pack(side=tk.LEFT, padx=5)
        
        chart_options = ["Weekly Calories", "Daily Distribution", "Food Types", "Calories In vs Out", "Weight Tracking"]
        self.chart_var = tk.StringVar(value=chart_options[0])
        
        chart_combo = ttk.Combobox(
            control_frame, 
            textvariable=self.chart_var, 
            values=chart_options, 
            state="readonly",
            width=20
        )
        chart_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            control_frame,
            text="Generate Chart",
            style="Info.TButton",
            command=self.generate_chart
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame for the chart
        self.figure_frame = ttk.Frame(chart_frame)
        self.figure_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Summary stats
        summary_frame = ttk.LabelFrame(self.stats_tab, text="Summary Statistics")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.stats_text = tk.Text(summary_frame, height=6, width=40, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_text.config(state=tk.DISABLED)
    
    def setup_achievements_tab(self):
        """Setup the achievements tab."""
        # Main container
        achievements_frame = ttk.Frame(self.achievements_tab)
        achievements_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Level progress section
        level_frame = ttk.LabelFrame(achievements_frame, text="Level Progress")
        level_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Level display
        level_info_frame = ttk.Frame(level_frame)
        level_info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.level_var = tk.StringVar(value="Level 1")
        level_label = ttk.Label(
            level_info_frame, 
            textvariable=self.level_var,
            font=("Roboto", 16, "bold")
        )
        level_label.pack(side=tk.LEFT, padx=20)
        
        self.points_var = tk.StringVar(value="0 points")
        points_label = ttk.Label(
            level_info_frame, 
            textvariable=self.points_var,
            font=("Roboto", 14)
        )
        points_label.pack(side=tk.RIGHT, padx=20)
        
        # Progress bar
        progress_frame = ttk.Frame(level_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.level_progress_var = tk.DoubleVar(value=0)
        self.level_progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=300,
            mode="determinate",
            variable=self.level_progress_var
        )
        self.level_progress_bar.pack(fill=tk.X, padx=10, pady=5)
        
        self.next_level_var = tk.StringVar(value="0/100 to next level")
        next_level_label = ttk.Label(
            progress_frame, 
            textvariable=self.next_level_var,
            font=("Roboto", 10)
        )
        next_level_label.pack(pady=5)
        
        # Notebook for achievements and challenges
        achievements_notebook = ttk.Notebook(achievements_frame)
        achievements_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Achievements tab
        achievements_list_frame = ttk.Frame(achievements_notebook)
        challenges_frame = ttk.Frame(achievements_notebook)
        
        achievements_notebook.add(achievements_list_frame, text="Achievements")
        achievements_notebook.add(challenges_frame, text="Challenges")
        
        # Achievements list
        achievements_scroll = ttk.Scrollbar(achievements_list_frame)
        achievements_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.achievements_canvas = tk.Canvas(
            achievements_list_frame,
            yscrollcommand=achievements_scroll.set,
            highlightthickness=0
        )
        self.achievements_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        achievements_scroll.config(command=self.achievements_canvas.yview)
        
        self.achievements_inner_frame = ttk.Frame(self.achievements_canvas)
        self.achievements_canvas.create_window((0, 0), window=self.achievements_inner_frame, anchor="nw")
        
        self.achievements_inner_frame.bind("<Configure>", lambda e: self.achievements_canvas.configure(
            scrollregion=self.achievements_canvas.bbox("all")
        ))
        
        # Challenges frame with tabs for daily and weekly
        challenges_notebook = ttk.Notebook(challenges_frame)
        challenges_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        daily_challenges_frame = ttk.Frame(challenges_notebook)
        weekly_challenges_frame = ttk.Frame(challenges_notebook)
        
        challenges_notebook.add(daily_challenges_frame, text="Daily Challenges")
        challenges_notebook.add(weekly_challenges_frame, text="Weekly Challenges")
        
        # Daily challenges list
        self.daily_challenges_frame = ttk.Frame(daily_challenges_frame)
        self.daily_challenges_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Weekly challenges list
        self.weekly_challenges_frame = ttk.Frame(weekly_challenges_frame)
        self.weekly_challenges_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        refresh_button = ttk.Button(
            achievements_frame,
            text="Refresh Achievements",
            style="Info.TButton",
            command=self.refresh_achievements
        )
        refresh_button.pack(pady=10)
    
    def refresh_achievements(self):
        """Refresh the achievements display."""
        # Check for new achievements and challenges
        new_achievements = self.gamification_manager.check_achievements()
        new_daily, new_weekly = self.gamification_manager.check_challenges()
        
        # Show notifications for new unlocks
        for achievement in new_achievements:
            self.show_achievement_notification(achievement)
            
        for challenge in new_daily + new_weekly:
            self.show_challenge_notification(challenge)
        
        # Update level progress
        level, points, points_needed = self.gamification_manager.get_level_progress()
        self.level_var.set(f"Level {level}")
        self.points_var.set(f"{self.gamification_manager.data['points']} points")
        self.next_level_var.set(f"{points}/{points_needed} to next level")
        
        # Update progress bar
        progress_pct = (points / points_needed) * 100 if points_needed > 0 else 0
        self.level_progress_var.set(progress_pct)
        
        # Clear existing achievements
        for widget in self.achievements_inner_frame.winfo_children():
            widget.destroy()
            
        # Add all achievements
        all_achievements = self.gamification_manager.get_all_achievements()
        
        # Sort achievements: unlocked first, then by ID
        all_achievements.sort(key=lambda a: (not a["unlocked"], a["id"]))
        
        for i, achievement in enumerate(all_achievements):
            self.create_achievement_widget(achievement, i)
            
        # Clear existing challenges
        for widget in self.daily_challenges_frame.winfo_children():
            widget.destroy()
            
        for widget in self.weekly_challenges_frame.winfo_children():
            widget.destroy()
            
        # Add daily challenges
        daily_challenges = self.gamification_manager.get_active_daily_challenges()
        for i, challenge in enumerate(daily_challenges):
            self.create_challenge_widget(challenge, i, self.daily_challenges_frame)
            
        # Add weekly challenges
        weekly_challenges = self.gamification_manager.get_active_weekly_challenges()
        for i, challenge in enumerate(weekly_challenges):
            self.create_challenge_widget(challenge, i, self.weekly_challenges_frame)
            
        # Update status
        self.status_var.set("Achievements and challenges refreshed")
    
    def create_achievement_widget(self, achievement, index):
        """Create a widget for displaying an achievement."""
        frame = ttk.Frame(self.achievements_inner_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Achievement icon
        icon_label = ttk.Label(frame, text=achievement["icon"], font=("Segoe UI Emoji", 24))
        icon_label.pack(side=tk.LEFT, padx=10)
        
        # Achievement details
        details_frame = ttk.Frame(frame)
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Title with unlock status
        title_text = achievement["name"]
        if achievement["unlocked"]:
            title_text += " ✓"
            title_color = "#5cb85c"  # Green for unlocked
        else:
            title_color = "#999999"  # Gray for locked
            
        title_label = ttk.Label(
            details_frame, 
            text=title_text, 
            font=("Roboto", 12, "bold"),
            foreground=title_color
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ttk.Label(details_frame, text=achievement["description"], wraplength=400)
        desc_label.pack(anchor="w")
        
        # Points
        points_label = ttk.Label(
            frame, 
            text=f"+{achievement['points']} pts", 
            font=("Roboto", 10, "bold"),
            foreground="#f0ad4e"  # Orange for points
        )
        points_label.pack(side=tk.RIGHT, padx=10)
        
        # Add separator except for last item
        if index < len(self.gamification_manager.achievements) - 1:
            ttk.Separator(self.achievements_inner_frame, orient="horizontal").pack(fill=tk.X, padx=20, pady=5)
    
    def create_challenge_widget(self, challenge, index, parent_frame):
        """Create a widget for displaying a challenge."""
        frame = ttk.Frame(parent_frame)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Challenge icon
        icon_label = ttk.Label(frame, text=challenge["icon"], font=("Segoe UI Emoji", 20))
        icon_label.pack(side=tk.LEFT, padx=10)
        
        # Challenge details
        details_frame = ttk.Frame(frame)
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Title with completion status
        title_text = challenge["name"]
        if challenge.get("completed", False):
            title_text += " ✓"
            title_color = "#5cb85c"  # Green for completed
        else:
            title_color = "#f0ad4e"  # Orange for active
            
        title_label = ttk.Label(
            details_frame, 
            text=title_text, 
            font=("Roboto", 12, "bold"),
            foreground=title_color
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ttk.Label(details_frame, text=challenge["description"], wraplength=400)
        desc_label.pack(anchor="w")
        
        # Points
        points_label = ttk.Label(
            frame, 
            text=f"+{challenge['points']} pts", 
            font=("Roboto", 10, "bold"),
            foreground="#f0ad4e"  # Orange for points
        )
        points_label.pack(side=tk.RIGHT, padx=10)
    
    def show_achievement_notification(self, achievement):
        """Show a notification for a newly unlocked achievement."""
        notification = tk.Toplevel(self.root)
        notification.title("Achievement Unlocked!")
        notification.geometry("400x200")
        notification.attributes("-topmost", True)
        
        # Set a custom icon if available
        try:
            notification.iconbitmap("trophy.ico")
        except:
            pass
        
        # Main frame
        frame = ttk.Frame(notification, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            frame, 
            text="🏆 Achievement Unlocked! 🏆", 
            font=("Roboto", 14, "bold"),
            foreground="#f0ad4e"
        )
        header_label.pack(pady=10)
        
        # Achievement details
        name_label = ttk.Label(
            frame, 
            text=achievement["name"], 
            font=("Roboto", 12, "bold")
        )
        name_label.pack()
        
        desc_label = ttk.Label(
            frame, 
            text=achievement["description"], 
            wraplength=350
        )
        desc_label.pack(pady=5)
        
        points_label = ttk.Label(
            frame, 
            text=f"+{achievement['points']} points", 
            font=("Roboto", 12),
            foreground="#5cb85c"
        )
        points_label.pack(pady=5)
        
        # Close button
        ttk.Button(
            frame, 
            text="Awesome!", 
            style="Success.TButton",
            command=notification.destroy
        ).pack(pady=10)
        
        # Auto-close after 10 seconds
        notification.after(10000, notification.destroy)
    
    def show_challenge_notification(self, challenge):
        """Show a notification for a completed challenge."""
        notification = tk.Toplevel(self.root)
        notification.title("Challenge Completed!")
        notification.geometry("400x200")
        notification.attributes("-topmost", True)
        
        # Main frame
        frame = ttk.Frame(notification, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_label = ttk.Label(
            frame, 
            text="🎯 Challenge Completed! 🎯", 
            font=("Roboto", 14, "bold"),
            foreground="#5cb85c"
        )
        header_label.pack(pady=10)
        
        # Challenge details
        name_label = ttk.Label(
            frame, 
            text=challenge["name"], 
            font=("Roboto", 12, "bold")
        )
        name_label.pack()
        
        desc_label = ttk.Label(
            frame, 
            text=challenge["description"], 
            wraplength=350
        )
        desc_label.pack(pady=5)
        
        points_label = ttk.Label(
            frame, 
            text=f"+{challenge['points']} points", 
            font=("Roboto", 12),
            foreground="#5cb85c"
        )
        points_label.pack(pady=5)
        
        # Close button
        ttk.Button(
            frame, 
            text="Great!", 
            style="Success.TButton",
            command=notification.destroy
        ).pack(pady=10)
        
        # Auto-close after 8 seconds
        notification.after(8000, notification.destroy)
    
    def show_achievements(self):
        """Show the achievements tab."""
        self.notebook.select(self.achievements_tab)
        self.refresh_achievements()
    
    def show_challenges(self):
        """Show the challenges tab within the achievements tab."""
        self.notebook.select(self.achievements_tab)
        # Select the challenges tab in the inner notebook
        for child in self.achievements_tab.winfo_children():
            if isinstance(child, ttk.Notebook):
                for i, tab in enumerate(child.tabs()):
                    if "challenges" in str(tab).lower():
                        child.select(i)
                        break
        self.refresh_achievements()
    
    def show_level_progress(self):
        """Show a detailed view of level progress."""
        level_window = tk.Toplevel(self.root)
        level_window.title("Level Progress")
        level_window.geometry("500x400")
        level_window.transient(self.root)
        
        # Main frame
        frame = ttk.Frame(level_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Current level and points
        level, points, points_needed = self.gamification_manager.get_level_progress()
        total_points = self.gamification_manager.data["points"]
        
        level_label = ttk.Label(
            frame, 
            text=f"Level {level}", 
            font=("Roboto", 24, "bold"),
            foreground="#5cb85c"
        )
        level_label.pack(pady=10)
        
        points_label = ttk.Label(
            frame, 
            text=f"Total Points: {total_points}", 
            font=("Roboto", 16)
        )
        points_label.pack(pady=5)
        
        # Progress to next level
        progress_frame = ttk.LabelFrame(frame, text="Progress to Next Level")
        progress_frame.pack(fill=tk.X, pady=15, padx=10)
        
        progress_var = tk.DoubleVar(value=(points / points_needed) * 100 if points_needed > 0 else 0)
        progress_bar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            variable=progress_var
        )
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        progress_label = ttk.Label(
            progress_frame, 
            text=f"{points}/{points_needed} points needed for Level {level+1}",
            font=("Roboto", 12)
        )
        progress_label.pack(pady=5)
        
        # Level benefits
        benefits_frame = ttk.LabelFrame(frame, text="Level Benefits")
        benefits_frame.pack(fill=tk.BOTH, expand=True, pady=15, padx=10)
        
        benefits_text = tk.Text(benefits_frame, height=8, width=40, wrap=tk.WORD)
        benefits_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add some fictional benefits based on level
        benefits = [
            "• Access to basic tracking features",
            "• Unlock custom food entries",
            "• Unlock custom exercise entries",
            "• Unlock advanced statistics",
            "• Unlock custom themes",
            "• Unlock meal planning features",
            "• Unlock social sharing features",
            "• Unlock AI recommendations",
            "• Unlock premium badges",
            "• Unlock ultimate burger master status"
        ]
        
        for i, benefit in enumerate(benefits[:min(level + 2, len(benefits))]):
            if i < level:
                benefits_text.insert(tk.END, f"{benefit} ✓\n", "unlocked")
            else:
                benefits_text.insert(tk.END, f"{benefit} (Next level)\n", "locked")
        
        benefits_text.tag_configure("unlocked", foreground="#5cb85c")
        benefits_text.tag_configure("locked", foreground="#999999")
        benefits_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            frame, 
            text="Close", 
            style="Info.TButton",
            command=level_window.destroy
        ).pack(pady=15)
    
    def create_menu(self):
        """Create the application menu."""
        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Create File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Data", command=self.save_history)
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Create Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Today's Log", command=self.clear_today)
        tools_menu.add_command(label="Delete All History", command=self.delete_history)
        tools_menu.add_separator()
        tools_menu.add_command(label="Food Statistics", command=self.show_stats)
        tools_menu.add_command(label="Weight Tracker", command=self.show_weight_tracker)
        tools_menu.add_command(label="Refresh Charts", command=self.generate_chart)
        tools_menu.add_separator()
        tools_menu.add_command(label="Manage Custom Database", command=self.manage_custom_database)
        
        # Create View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        
        # Default themes
        default_theme_menu = tk.Menu(theme_menu, tearoff=0)
        theme_menu.add_cascade(label="Default", menu=default_theme_menu)
        
        default_themes = ["Draco", "Justin", "Mason", "William", "Chaka"]
        for theme in default_themes:
            default_theme_menu.add_command(
                label=theme.capitalize(),
                command=lambda theme=theme: self.change_theme(theme)
            )
        
        # Flashy themes
        flashy_theme_menu = tk.Menu(theme_menu, tearoff=0)
        theme_menu.add_cascade(label="Flashy", menu=flashy_theme_menu)
        
        flashy_themes = ["Neon", "Retro", "Party"]
        for theme in flashy_themes:
            flashy_theme_menu.add_command(
                label=theme,
                command=lambda theme=theme: self.change_theme(theme)
            )
        
        # Minimal themes
        minimal_theme_menu = tk.Menu(theme_menu, tearoff=0)
        theme_menu.add_cascade(label="Minimal", menu=minimal_theme_menu)
        
        minimal_themes = ["Monochrome", "Pastel", "Zen"]
        for theme in minimal_themes:
            minimal_theme_menu.add_command(
                label=theme,
                command=lambda theme=theme: self.change_theme(theme)
            )
        
        # Create Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_guide)
        
        # Create Achievements menu
        achievements_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Achievements", menu=achievements_menu)
        achievements_menu.add_command(label="View Achievements", command=self.show_achievements)
        achievements_menu.add_command(label="View Challenges", command=self.show_challenges)
        achievements_menu.add_command(label="View Level Progress", command=self.show_level_progress)
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        # Recreate the style with the new theme
        self.style = Style(theme=theme_name.lower())
        
        # Configure styles for the new theme
        self.style.configure("TButton", font=("Roboto", 10))
        self.style.configure("TLabel", font=("Roboto", 10))
        self.style.configure("TFrame", background=self.style.colors.bg)
        
        # Update the status bar
        self.status_var.set(f"Theme changed to {theme_name.capitalize()}")
        
        # Force theme update by recreating the notebook
        current_tab = self.notebook.index('current')
        self.notebook.destroy()
        self.create_notebook()
        self.setup_tracking_tab()
        self.setup_exercise_tab()
        self.setup_weight_tab()
        self.setup_stats_tab()
        self.setup_achievements_tab()
        self.notebook.select(current_tab)
        
        # Reload data for the current tab
        self.on_tab_changed(None)
    
    def export_report(self):
        """Export a report of the current day's data."""
        filename = f"burger_report_{self.date_var.get()}.txt"
        try:
            with open(filename, "w") as f:
                f.write(f"JACOB BURGER TRACKER REPORT\n")
                f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write(f"Date: {self.date_var.get()}\n")
                f.write(f"Daily Goal: {self.goal_var.get()} calories\n")
                f.write(f"Kyle Tax Enabled: {'Yes' if self.kyle_tax_enabled.get() else 'No'}\n\n")
                
                f.write("ITEMS CONSUMED:\n")
                f.write("--------------\n")
                
                # Get entries for the selected date
                selected_date = self.date_var.get()
                day_data = self.data_manager.get_day_data(selected_date)
                food_entries = day_data.get("food", [])
                exercise_entries = day_data.get("exercise", [])
                
                total_calories = 0
                for entry in food_entries:
                    calories = entry["calories"]
                    if entry.get("kyle_tax", False):
                        calories = int(calories * 0.85)
                    
                    f.write(f"{entry['food']} ({entry.get('category', 'Food')}) x {entry['amount']}: {calories} calories\n")
                    total_calories += calories
                
                f.write("\nEXERCISE ACTIVITY:\n")
                f.write("------------------\n")
                
                total_burnt = 0
                for exercise in exercise_entries:
                    burnt = exercise["calories_burnt"]
                    f.write(f"{exercise['exercise']} for {exercise['duration']} minutes: {burnt} calories burnt\n")
                    total_burnt += burnt
                
                f.write("\nSUMMARY:\n")
                f.write("--------\n")
                f.write(f"Total Calories Consumed: {total_calories}\n")
                f.write(f"Total Calories Burnt: {total_burnt}\n")
                
                net_calories = total_calories - total_burnt
                f.write(f"Net Calories: {net_calories}\n")
                
                goal = int(self.goal_var.get())
                remaining = max(0, goal - net_calories)
                f.write(f"Remaining Calories: {remaining}\n")
                
                if net_calories > goal:
                    f.write(f"Exceeded Goal by: {net_calories - goal}\n")
            
            messagebox.showinfo("Export Successful", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export report: {e}")
    
    def show_guide(self):
        """Show the user guide dialog."""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        guide_window.transient(self.root)
        guide_window.grab_set()
        
        # Create a scrollable text widget
        guide_text = tk.Text(guide_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(guide_window, command=guide_text.yview)
        guide_text.configure(yscrollcommand=scrollbar.set)
        
        guide_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add guide content
        guide_content = """
# Jacob Burger Tracker User Guide

1. Get hella burgers

2. Get hella burgers for iftar

3. Get sword from draco that was forged in China

4. Crash into trashcan

5. Track your sides along with your burgers

6. Log your exercise to offset your calorie intake

7. Add custom foods:
   - Click "Add Food Item"
   - Select "Enter custom food"
   - Fill in the name, calories, and category
   - Check "Save to food database" to use it again later

8. Add custom exercises:
   - Click "Add Exercise"
   - Select "Enter custom exercise"
   - Fill in the name and calories per minute
   - Check "Save to exercise database" to use it again later

9. Manage custom items:
   - Click "Tools" → "Manage Custom Database"
   - View, edit, or delete your custom foods and exercises

10. Earn achievements and complete challenges:
   - Track your food and exercise regularly
   - Try different types of burgers and exercises
   - Meet your calorie goals
   - Check the Achievements tab to see your progress
   - Level up to unlock new features
"""
        guide_text.insert(tk.END, guide_content)
        guide_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(
            guide_window, 
            text="Close", 
            command=guide_window.destroy
        ).pack(pady=10)
    
    def generate_chart(self):
        """Generate and display the selected chart."""
        # Clear the current chart
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        
        # Create figure and axis
        fig, ax = self.chart_manager.create_figure()
        
        # Create the selected chart
        selected_chart = self.chart_var.get()
        
        try:
            goal = int(self.goal_var.get())
        except ValueError:
            goal = 2000
        
        if selected_chart == "Weekly Calories":
            self.chart_manager.create_weekly_chart(ax, self.date_var.get(), goal)
        elif selected_chart == "Daily Distribution":
            self.chart_manager.create_distribution_chart(ax, self.date_var.get())
        elif selected_chart == "Food Types":
            self.chart_manager.create_food_types_chart(ax)
        elif selected_chart == "Calories In vs Out":
            self.chart_manager.create_calories_in_out_chart(ax, self.date_var.get())
        elif selected_chart == "Weight Tracking":
            self.chart_manager.create_weight_tracking_chart(ax)
        
        # Create canvas for chart
        self.canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Update stats text
        self.update_stats_text()
    
    def update_stats_text(self):
        """Update the statistics text display."""
        stats = self.data_manager.get_stats_summary()
        
        # Generate stats text
        stats_text = f"Total days tracked: {stats['total_days']}\n"
        stats_text += f"Total food entries: {stats['total_foods']}\n"
        stats_text += f"Total exercise entries: {stats['total_exercises']}\n"
        stats_text += f"Total calories consumed: {stats['total_calories']}\n"
        stats_text += f"Total calories burned: {stats['total_burned']}\n"
        stats_text += f"Net calories: {stats['net_calories']}\n"
        
        # Add weight stats if available
        weights = stats['weights']
        if weights:
            current_weight = weights[-1]
            start_weight = weights[0]
            weight_change = current_weight - start_weight
            
            stats_text += f"\nWeight Statistics:\n"
            stats_text += f"Starting weight: {start_weight} lb\n"
            stats_text += f"Current weight: {current_weight} lb\n"
            stats_text += f"Weight change: {weight_change:+.1f} lb\n"
            
            if len(weights) >= 2:
                avg_weight = sum(weights) / len(weights)
                min_weight = min(weights)
                max_weight = max(weights)
                
                stats_text += f"Average weight: {avg_weight:.1f} lb\n"
                stats_text += f"Minimum weight: {min_weight} lb\n"
                stats_text += f"Maximum weight: {max_weight} lb\n"
        
        # Update the text widget
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state=tk.DISABLED)
    
    def load_weight_history(self):
        """Load and display weight history."""
        # Clear the weight treeview
        for item in self.weight_tree.get_children():
            self.weight_tree.delete(item)
        
        # Get weight history
        weights = self.data_manager.get_weight_history()
        
        # Add to treeview
        for date, weight in weights:
            self.weight_tree.insert("", "end", values=(date, weight))
        
        # Load current date's weight if it exists
        selected_date = self.date_var.get()
        day_data = self.data_manager.get_day_data(selected_date)
        current_weight = day_data.get("weight")
        
        if current_weight is not None:
            self.weight_var.set(str(current_weight))
        else:
            self.weight_var.set("")
    
    def save_weight(self):
        """Save weight for the current date."""
        # Get the weight value
        try:
            weight = float(self.weight_var.get())
            if weight <= 0:
                messagebox.showerror("Error", "Weight must be a positive number")
                return
                
            # Get the selected date
            selected_date = self.date_var.get()
            
            # Update the weight for this date
            self.data_manager.update_weight(selected_date, weight)
            
            # Save to file
            self.data_manager.save_history()
            
            # Refresh the weight history display
            self.load_weight_history()
            
            # Check for achievements and challenges
            new_achievements = self.gamification_manager.check_achievements()
            new_daily, new_weekly = self.gamification_manager.check_challenges()
            
            # Show notifications for new unlocks
            for achievement in new_achievements:
                self.show_achievement_notification(achievement)
                
            for challenge in new_daily + new_weekly:
                self.show_challenge_notification(challenge)
            
            # Show confirmation
            self.status_var.set(f"Weight for {selected_date} saved: {weight} lb")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight value")
    
    def delete_weight(self):
        """Delete the selected weight entry."""
        # Get selected item
        selected = self.weight_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a weight entry to delete")
            return
        
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Delete selected weight entry?"):
            return
        
        # Get date of selected item
        item_date = self.weight_tree.item(selected[0], "values")[0]
        
        # Remove weight from history for this date
        self.data_manager.update_weight(item_date, None)
        
        # Save to file
        self.data_manager.save_history()
        
        # Refresh the weight history display
        self.load_weight_history()
        
        # Show confirmation
        self.status_var.set(f"Weight for {item_date} deleted")
    
    def edit_weight(self):
        """Edit the selected weight entry."""
        # Get selected item
        selected = self.weight_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a weight entry to edit")
            return
        
        # Get date and weight of selected item
        item_values = self.weight_tree.item(selected[0], "values")
        item_date = item_values[0]
        item_weight = item_values[1]
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Weight")
        dialog.geometry("300x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Dialog content
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Date: {item_date}").grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        ttk.Label(frame, text="Weight (lb):").grid(row=1, column=0, pady=10, sticky="w")
        weight_var = tk.StringVar(value=item_weight)
        ttk.Entry(frame, textvariable=weight_var, width=10).grid(row=1, column=1, pady=10, sticky="w")
        
        # Save function
        def save_edit():
            try:
                new_weight = float(weight_var.get())
                if new_weight <= 0:
                    messagebox.showerror("Error", "Weight must be a positive number")
                    return
                
                # Update weight for this date
                self.data_manager.update_weight(item_date, new_weight)
                
                # Save to file
                self.data_manager.save_history()
                
                # Refresh the weight history display
                self.load_weight_history()
                
                # Show confirmation
                self.status_var.set(f"Weight for {item_date} updated: {new_weight} lb")
                
                # Close dialog
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid weight value")
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", style="Success.TButton", command=save_edit).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def change_date(self, days):
        """Change the selected date by the specified number of days."""
        # Change the selected date
        try:
            date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
            new_date = date + datetime.timedelta(days=days)
            self.date_var.set(new_date.strftime("%Y-%m-%d"))
            self.load_entries()
            self.load_exercises()
            
            # Also update weight data for the selected date
            if hasattr(self, 'weight_var'):
                selected_date = self.date_var.get()
                day_data = self.data_manager.get_day_data(selected_date)
                current_weight = day_data.get("weight")
                
                if current_weight is not None:
                    self.weight_var.set(str(current_weight))
                else:
                    self.weight_var.set("")
                    
        except ValueError:
            self.go_to_today()
    
    def go_to_today(self):
        """Set the date to today and load data."""
        # Set date to today
        self.date_var.set(self.data_manager.current_date)
        
        # Load entries and exercises
        self.load_entries()
        self.load_exercises()
        
        # Also update weight data for today
        if hasattr(self, 'weight_var'):
            day_data = self.data_manager.get_day_data(self.data_manager.current_date)
            current_weight = day_data.get("weight")
            
            if current_weight is not None:
                self.weight_var.set(str(current_weight))
            else:
                self.weight_var.set("")
    
    def load_entries(self):
        """Load and display food entries for the selected date."""
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get selected date
        selected_date = self.date_var.get()
        
        # Get data for the selected date
        day_data = self.data_manager.get_day_data(selected_date)
        food_entries = day_data.get("food", [])
        
        # Add entries to treeview
        for entry in food_entries:
            calories = entry["calories"]
            kyle_tax_applied = entry.get("kyle_tax", False)
            
            if kyle_tax_applied or self.kyle_tax_enabled.get():
                adjusted_calories = int(calories * 0.85)
                kyle_status = "Applied"
            else:
                adjusted_calories = calories
                kyle_status = "No"
                
            self.tree.insert("", "end", values=(
                entry["food"],
                entry["amount"],
                entry.get("category", "Food"),
                adjusted_calories,
                kyle_status
            ))
        
        # Update totals
        self.update_totals()
    
    def load_exercises(self):
        """Load and display exercise entries for the selected date."""
        # Clear the exercise treeview
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
        
        # Get selected date
        selected_date = self.date_var.get()
        
        # Get data for the selected date
        day_data = self.data_manager.get_day_data(selected_date)
        exercise_entries = day_data.get("exercise", [])
        
        # Add entries to treeview
        for entry in exercise_entries:
            self.exercise_tree.insert("", "end", values=(
                entry["exercise"],
                entry["duration"],
                entry["calories_burnt"]
            ))
        
        # Update exercise summary
        self.update_exercise_summary(exercise_entries)
        
        # Update the main tab totals as well (to reflect burnt calories)
        self.update_totals()
    
    def update_exercise_summary(self, exercises=None):
        """Update the exercise summary display."""
        # Calculate exercise statistics
        if exercises is None:
            day_data = self.data_manager.get_day_data(self.date_var.get())
            exercises = day_data.get("exercise", [])
        
        total_time = sum(ex["duration"] for ex in exercises)
        total_burnt = sum(ex["calories_burnt"] for ex in exercises)
        
        # Update display
        self.total_exercise_var.set(f"Total Exercise Time: {total_time} minutes")
        self.total_burnt_var.set(f"Total Calories Burnt: {total_burnt}")
    
    def update_totals(self):
        """Update the calorie totals display."""
        # Get food entries
        day_data = self.data_manager.get_day_data(self.date_var.get())
        food_entries = day_data.get("food", [])
        exercise_entries = day_data.get("exercise", [])
        
        # Calculate total calories with Kyle Tax if enabled
        total_in = 0
        for entry in food_entries:
            calories = entry["calories"]
            if entry.get("kyle_tax", False) or self.kyle_tax_enabled.get():
                calories = int(calories * 0.85)
            total_in += calories
        
        # Calculate total calories burnt
        total_burnt = sum(ex.get("calories_burnt", 0) for ex in exercise_entries)
        
        # Calculate net calories
        net_calories = total_in - total_burnt
        
        # Update display
        self.total_var.set(f"Total Calories: {total_in}")
        self.burnt_var.set(f"Calories Burnt: {total_burnt}")
        self.net_var.set(f"Net Calories: {net_calories}")
        
        # Get goal
        try:
            goal = int(self.goal_var.get())
        except ValueError:
            goal = 2000
        
        # Update remaining (based on net calories)
        remaining = max(0, goal - net_calories)
        self.remaining_var.set(f"Remaining: {remaining}")
        
        # Update progress bar (based on net calories)
        progress_pct = min(100, (net_calories / goal) * 100)
        self.progress_var.set(progress_pct)
        
        # Update progress bar color
        if progress_pct < 75:
            self.progress_bar.configure(style="success.Horizontal.TProgressbar")
        elif progress_pct < 100:
            self.progress_bar.configure(style="warning.Horizontal.TProgressbar")
        else:
            self.progress_bar.configure(style="danger.Horizontal.TProgressbar")
    
    def apply_kyle_tax(self):
        """Apply or remove Kyle Tax and update display."""
        # Re-load entries to apply or remove Kyle Tax
        self.load_entries()
        
        if self.kyle_tax_enabled.get():
            self.status_var.set("Kyle Tax applied: 15% calorie reduction")
        else:
            self.status_var.set("Kyle Tax removed")
    
    def set_goal(self):
        """Set the daily calorie goal."""
        try:
            goal = int(self.goal_var.get())
            if goal <= 0:
                messagebox.showerror("Error", "Goal must be positive")
                return
            
            # Update display
            self.update_totals()
            self.status_var.set(f"Calorie goal set to {goal}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_food(self):
        """Show dialog to add a food item."""
        # Create a modern dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Food Item")
        dialog.geometry("500x450")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Style the dialog to match the main app
        dialog_frame = ttk.Frame(dialog, padding=20)
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add option to choose between preset and custom food
        entry_mode_var = tk.StringVar(value="preset")
        
        preset_radio = ttk.Radiobutton(dialog_frame, text="Select from presets", variable=entry_mode_var, value="preset")
        preset_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        custom_radio = ttk.Radiobutton(dialog_frame, text="Enter custom food", variable=entry_mode_var, value="custom")
        custom_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Create frames for preset and custom entry
        preset_frame = ttk.Frame(dialog_frame)
        preset_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        custom_frame = ttk.Frame(dialog_frame)
        custom_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # === PRESET FOOD SECTION ===
        
        # Category selection
        ttk.Label(preset_frame, text="Category:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        categories = ["Burgers", "Sides", "Drinks"]
        category_var = tk.StringVar(value=categories[0])
        category_combo = ttk.Combobox(
            preset_frame, 
            textvariable=category_var, 
            values=categories, 
            width=15,
            state="readonly"
        )
        category_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Form fields with better layout
        ttk.Label(preset_frame, text="Select Food:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        # Combobox with food options
        food_var = tk.StringVar()
        self.food_combo = ttk.Combobox(preset_frame, textvariable=food_var, width=25, style="TCombobox")
        self.food_combo.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Update food list based on category
        def update_food_list(*args):
            selected_category = category_var.get()
            food_options = [food for food, data in self.data_manager.food_database.items() 
                           if data["category"] == selected_category]
            
            self.food_combo['values'] = food_options
            if food_options:
                food_var.set(food_options[0])
            else:
                food_var.set("")
        
        # Bind category change to update food list
        category_var.trace_add("write", update_food_list)
        update_food_list()  # Initial update
        
        # === CUSTOM FOOD SECTION ===
        
        # Custom food entry
        ttk.Label(custom_frame, text="Food Name:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        custom_food_var = tk.StringVar()
        custom_food_entry = ttk.Entry(custom_frame, textvariable=custom_food_var, width=25)
        custom_food_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Custom calories entry
        ttk.Label(custom_frame, text="Calories:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        custom_calories_var = tk.StringVar()
        custom_calories_entry = ttk.Entry(custom_frame, textvariable=custom_calories_var, width=10)
        custom_calories_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Custom food category
        ttk.Label(custom_frame, text="Category:", font=("Roboto", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        custom_category_var = tk.StringVar(value=categories[0])
        custom_category_combo = ttk.Combobox(
            custom_frame, 
            textvariable=custom_category_var, 
            values=categories + ["Other"],  # Add "Other" category for custom items
            width=15,
            state="readonly"
        )
        custom_category_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Option to save custom food to database
        save_custom_var = tk.BooleanVar(value=False)
        save_custom_check = ttk.Checkbutton(
            custom_frame,
            text="Save to food database for future use",
            variable=save_custom_var
        )
        save_custom_check.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # === COMMON FIELDS ===
        
        # Quantity field (shared)
        quantity_frame = ttk.Frame(dialog_frame)
        quantity_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ttk.Label(quantity_frame, text="Quantity:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        amount_var = tk.StringVar(value="1")
        ttk.Entry(quantity_frame, textvariable=amount_var, width=10).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Kyle Tax checkbox
        kyle_tax_var = tk.BooleanVar(value=self.kyle_tax_enabled.get())
        kyle_check = ttk.Checkbutton(
            quantity_frame, 
            text="Apply Kyle Tax (-15%)", 
            variable=kyle_tax_var
        )
        kyle_check.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Calorie display frame
        calorie_frame = ttk.LabelFrame(dialog_frame, text="Calorie Impact")
        calorie_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Original calories display
        original_cal_var = tk.StringVar(value="Original: 0 cal")
        ttk.Label(calorie_frame, textvariable=original_cal_var).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Adjusted calories display if Kyle Tax applied
        adjusted_cal_var = tk.StringVar(value="With Kyle Tax: 0 cal")
        ttk.Label(calorie_frame, textvariable=adjusted_cal_var).pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Toggle between preset and custom frames based on selection
        def toggle_entry_mode(*args):
            if entry_mode_var.get() == "preset":
                preset_frame.grid()
                custom_frame.grid_remove()
                update_calories()  # Update calories based on preset selection
            else:
                preset_frame.grid_remove()
                custom_frame.grid()
                update_custom_calories()  # Update calories based on custom entry
        
        entry_mode_var.trace_add("write", toggle_entry_mode)
        
        # Update calories when food or amount changes for preset
        def update_calories(*args):
            if entry_mode_var.get() != "preset":
                return
                
            food = food_var.get()
            try:
                amount = float(amount_var.get())
                if food in self.data_manager.food_database:
                    original_cal = self.data_manager.food_database[food]["calories"] * amount
                    original_cal_var.set(f"Original: {int(original_cal)} cal")
                    
                    # Calculate with Kyle Tax
                    adjusted_cal = int(original_cal * 0.85)
                    adjusted_cal_var.set(f"With Kyle Tax: {adjusted_cal} cal")
                else:
                    original_cal_var.set("Original: 0 cal")
                    adjusted_cal_var.set("With Kyle Tax: 0 cal")
            except ValueError:
                original_cal_var.set("Original: 0 cal")
                adjusted_cal_var.set("With Kyle Tax: 0 cal")
        
        # Update calories for custom entry
        def update_custom_calories(*args):
            if entry_mode_var.get() != "custom":
                return
                
            try:
                calories = float(custom_calories_var.get() or "0")
                amount = float(amount_var.get())
                total_cal = calories * amount
                
                original_cal_var.set(f"Original: {int(total_cal)} cal")
                
                # Calculate with Kyle Tax
                adjusted_cal = int(total_cal * 0.85)
                adjusted_cal_var.set(f"With Kyle Tax: {adjusted_cal} cal")
            except ValueError:
                original_cal_var.set("Original: 0 cal")
                adjusted_cal_var.set("With Kyle Tax: 0 cal")
        
        # Connect update functions to variables
        food_var.trace_add("write", update_calories)
        amount_var.trace_add("write", lambda *args: update_calories() if entry_mode_var.get() == "preset" else update_custom_calories())
        kyle_tax_var.trace_add("write", lambda *args: update_calories() if entry_mode_var.get() == "preset" else update_custom_calories())
        
        # Connect custom entry variables
        custom_food_var.trace_add("write", update_custom_calories)
        custom_calories_var.trace_add("write", update_custom_calories)
        
        # Initial setup
        toggle_entry_mode()
        
        # Buttons
        def save_entry():
            try:
                amount = float(amount_var.get())
                apply_kyle = kyle_tax_var.get()
                
                if entry_mode_var.get() == "preset":
                    # Get values from preset selection
                    food = food_var.get()
                    if not (food and food in self.data_manager.food_database and amount > 0):
                        messagebox.showerror("Error", "Please select a valid food and amount")
                        return
                        
                    calories = self.data_manager.food_database[food]["calories"] * amount
                    category = self.data_manager.food_database[food]["category"]
                else:
                    # Get values from custom entry
                    food = custom_food_var.get().strip()
                    if not food:
                        messagebox.showerror("Error", "Please enter a food name")
                        return
                        
                    try:
                        cal_per_unit = float(custom_calories_var.get())
                        if cal_per_unit <= 0:
                            messagebox.showerror("Error", "Calories must be greater than 0")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Please enter valid calories")
                        return
                        
                    calories = cal_per_unit * amount
                    category = custom_category_var.get()
                    
                    # Save custom food to database if option is selected
                    if save_custom_var.get():
                        if self.data_manager.save_custom_food(food, int(cal_per_unit), category):
                            self.status_var.set(f"Added and saved {food} to database")
                        else:
                            messagebox.showwarning("Warning", "Could not save food to database, but it will be added to today's log")
                
                # Add to data manager
                self.data_manager.add_food_entry(
                    self.date_var.get(),
                    food,
                    amount,
                    int(calories),
                    category,
                    apply_kyle
                )
                
                # Add to tree
                display_calories = int(calories * 0.85) if apply_kyle else int(calories)
                self.tree.insert("", "end", values=(
                    food,
                    f"{amount:.1f}",
                    category,
                    display_calories,
                    "Applied" if apply_kyle else "No"
                ))
                
                # Update total
                self.update_totals()
                self.status_var.set(f"Added {amount} {food}")
                
                # Check for achievements and challenges
                new_achievements = self.gamification_manager.check_achievements()
                new_daily, new_weekly = self.gamification_manager.check_challenges()
                
                # Show notifications for new unlocks
                for achievement in new_achievements:
                    self.show_achievement_notification(achievement)
                    
                for challenge in new_daily + new_weekly:
                    self.show_challenge_notification(challenge)
                
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
        
        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", style="Success.TButton", command=save_entry).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
    
    def add_exercise(self):
        """Show dialog to add an exercise."""
        # Create dialog for adding exercise
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Exercise")
        dialog.geometry("450x350")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Style the dialog to match the main app
        dialog_frame = ttk.Frame(dialog, padding=20)
        dialog_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add option to choose between preset and custom exercise
        entry_mode_var = tk.StringVar(value="preset")
        
        preset_radio = ttk.Radiobutton(dialog_frame, text="Select from presets", variable=entry_mode_var, value="preset")
        preset_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        custom_radio = ttk.Radiobutton(dialog_frame, text="Enter custom exercise", variable=entry_mode_var, value="custom")
        custom_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Create frames for preset and custom entry
        preset_frame = ttk.Frame(dialog_frame)
        preset_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        custom_frame = ttk.Frame(dialog_frame)
        custom_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # === PRESET EXERCISE SECTION ===
        
        # Combobox with exercise options
        ttk.Label(preset_frame, text="Exercise Type:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        exercise_options = list(self.data_manager.exercise_database.keys())
        exercise_var = tk.StringVar()
        exercise_combo = ttk.Combobox(
            preset_frame, 
            textvariable=exercise_var, 
            values=exercise_options, 
            width=25, 
            style="TCombobox"
        )
        exercise_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        exercise_combo.current(0)  # Set default selection
        
        # Show calories per minute for selected exercise
        ttk.Label(preset_frame, text="Calories/min:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        cal_per_min_var = tk.StringVar(value=str(self.data_manager.exercise_database[exercise_options[0]]))
        ttk.Label(preset_frame, textvariable=cal_per_min_var, font=("Roboto", 12, "bold")).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # === CUSTOM EXERCISE SECTION ===
        
        # Custom exercise name entry
        ttk.Label(custom_frame, text="Exercise Name:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        custom_exercise_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=custom_exercise_var, width=25).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Custom calories per minute
        ttk.Label(custom_frame, text="Calories/min:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        custom_cal_per_min_var = tk.StringVar()
        ttk.Entry(custom_frame, textvariable=custom_cal_per_min_var, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Option to save custom exercise to database
        save_custom_var = tk.BooleanVar(value=False)
        save_custom_check = ttk.Checkbutton(
            custom_frame,
            text="Save to exercise database for future use",
            variable=save_custom_var
        )
        save_custom_check.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        
        # === COMMON FIELDS ===
        
        # Duration field (shared between both modes)
        duration_frame = ttk.Frame(dialog_frame)
        duration_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ttk.Label(duration_frame, text="Duration (minutes):", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        duration_var = tk.StringVar(value="30")
        ttk.Entry(duration_frame, textvariable=duration_var, width=10).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Preview calories burnt
        ttk.Label(duration_frame, text="Calories Burnt:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        calories_var = tk.StringVar(value="0")
        ttk.Label(duration_frame, textvariable=calories_var, font=("Roboto", 12, "bold"), foreground="#5cb85c").grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Toggle between preset and custom frames based on selection
        def toggle_entry_mode(*args):
            if entry_mode_var.get() == "preset":
                preset_frame.grid()
                custom_frame.grid_remove()
                update_calories()  # Update calories based on preset selection
            else:
                preset_frame.grid_remove()
                custom_frame.grid()
                update_custom_calories()  # Update calories based on custom entry
        
        entry_mode_var.trace_add("write", toggle_entry_mode)
        
        # Update calories when exercise or duration changes for preset
        def update_calories(*args):
            if entry_mode_var.get() != "preset":
                return
                
            exercise = exercise_var.get()
            try:
                duration = float(duration_var.get())
                if exercise in self.data_manager.exercise_database:
                    calories_per_min = self.data_manager.exercise_database[exercise]
                    cal_per_min_var.set(str(calories_per_min))
                    burnt = int(calories_per_min * duration)
                    calories_var.set(str(burnt))
                else:
                    calories_var.set("0")
            except ValueError:
                calories_var.set("0")
        
        # Update calories for custom exercise
        def update_custom_calories(*args):
            if entry_mode_var.get() != "custom":
                return
                
            try:
                cal_per_min = float(custom_cal_per_min_var.get() or "0")
                duration = float(duration_var.get())
                burnt = int(cal_per_min * duration)
                calories_var.set(str(burnt))
            except ValueError:
                calories_var.set("0")
        
        # Connect update functions to variables
        exercise_var.trace_add("write", update_calories)
        duration_var.trace_add("write", lambda *args: update_calories() if entry_mode_var.get() == "preset" else update_custom_calories())
        custom_cal_per_min_var.trace_add("write", update_custom_calories)
        
        # Update exercise combobox selection to show calories per minute
        def update_cal_per_min(*args):
            exercise = exercise_var.get()
            if exercise in self.data_manager.exercise_database:
                cal_per_min_var.set(str(self.data_manager.exercise_database[exercise]))
        
        exercise_var.trace_add("write", update_cal_per_min)
        
        # Initial setup
        toggle_entry_mode()
        update_calories()  # Initial update
        
        # Buttons
        def save_entry():
            try:
                duration = float(duration_var.get())
                if duration <= 0:
                    messagebox.showerror("Error", "Duration must be greater than 0")
                    return
                    
                if entry_mode_var.get() == "preset":
                    # Get values from preset selection
                    exercise = exercise_var.get()
                    if not exercise or exercise not in self.data_manager.exercise_database:
                        messagebox.showerror("Error", "Please select a valid exercise")
                        return
                        
                    # Calculate calories burnt
                    calories_per_min = self.data_manager.exercise_database[exercise]
                    calories_burnt = int(calories_per_min * duration)
                else:
                    # Get values from custom entry
                    exercise = custom_exercise_var.get().strip()
                    if not exercise:
                        messagebox.showerror("Error", "Please enter an exercise name")
                        return
                        
                    try:
                        cal_per_min = float(custom_cal_per_min_var.get())
                        if cal_per_min <= 0:
                            messagebox.showerror("Error", "Calories per minute must be greater than 0")
                            return
                    except ValueError:
                        messagebox.showerror("Error", "Please enter valid calories per minute")
                        return
                        
                    calories_burnt = int(cal_per_min * duration)
                    
                    # Save custom exercise to database if option is selected
                    if save_custom_var.get():
                        if self.data_manager.save_custom_exercise(exercise, cal_per_min):
                            self.status_var.set(f"Added and saved {exercise} to exercise database")
                        else:
                            messagebox.showwarning("Warning", "Could not save exercise to database, but it will be added to today's log")
                
                # Add to data manager
                self.data_manager.add_exercise_entry(
                    self.date_var.get(),
                    exercise,
                    duration,
                    calories_burnt
                )
                
                # Add to exercise tree
                self.exercise_tree.insert("", "end", values=(
                    exercise,
                    f"{duration:.1f}",
                    calories_burnt
                ))
                
                # Update summaries
                self.update_exercise_summary()
                self.update_totals()  # Update main tab as well
                
                # Check for achievements and challenges
                new_achievements = self.gamification_manager.check_achievements()
                new_daily, new_weekly = self.gamification_manager.check_challenges()
                
                # Show notifications for new unlocks
                for achievement in new_achievements:
                    self.show_achievement_notification(achievement)
                    
                for challenge in new_daily + new_weekly:
                    self.show_challenge_notification(challenge)
                
                self.status_var.set(f"Added {exercise} for {duration} minutes")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
        
        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", style="Success.TButton", command=save_entry).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
    
    def delete_food(self):
        """Delete selected food entries."""
        # Get selected items
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an entry to delete")
            return
        
        # Get indices of selected items
        indices = [self.tree.index(item) for item in selected]
        
        # Delete from data manager
        self.data_manager.delete_food_entries(self.date_var.get(), indices)
        
        # Remove from tree
        for item in selected:
            self.tree.delete(item)
        
        # Update totals
        self.update_totals()
        self.status_var.set(f"Deleted {len(selected)} food entries")
    
    def delete_exercise(self):
        """Delete selected exercise entries."""
        # Get selected items
        selected = self.exercise_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an exercise to delete")
            return
        
        # Get indices of selected items
        indices = [self.exercise_tree.index(item) for item in selected]
        
        # Delete from data manager
        self.data_manager.delete_exercise_entries(self.date_var.get(), indices)
        
        # Remove from tree
        for item in selected:
            self.exercise_tree.delete(item)
        
        # Update totals
        day_data = self.data_manager.get_day_data(self.date_var.get())
        self.update_exercise_summary(day_data.get("exercise", []))
        self.update_totals()  # Also update main tab
        self.status_var.set(f"Deleted {len(selected)} exercise entries")
    
    def clear_all(self):
        """Clear all food entries for the selected date."""
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Clear all food entries for this date?"):
            return
        
        # Clear in data manager
        self.data_manager.clear_food_entries(self.date_var.get())
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Update totals
        self.update_totals()
        self.status_var.set(f"Cleared all food entries for {self.date_var.get()}")
    
    def clear_all_exercises(self):
        """Clear all exercise entries for the selected date."""
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Clear all exercise entries for this date?"):
            return
        
        # Clear in data manager
        self.data_manager.clear_exercise_entries(self.date_var.get())
        
        # Clear treeview
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
        
        # Update totals
        self.update_exercise_summary([])
        self.update_totals()  # Also update main tab
        self.status_var.set(f"Cleared all exercise entries for {self.date_var.get()}")
    
    def clear_today(self):
        """Clear all entries for today."""
        # Clear today's entries
        if not messagebox.askyesno("Confirm", "Clear all entries for today?"):
            return
        
        self.data_manager.clear_today()
        
        # If today is selected, update display
        if self.date_var.get() == self.data_manager.current_date:
            # Clear food treeview
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Clear exercise treeview
            for item in self.exercise_tree.get_children():
                self.exercise_tree.delete(item)
                
            self.update_totals()
            self.update_exercise_summary([])
        
        self.status_var.set("Cleared today's entries")
    
    def delete_history(self):
        """Delete all history data."""
        # Delete all history
        if not messagebox.askyesno("Confirm", "Delete ALL history data? This cannot be undone!"):
            return
        
        self.data_manager.delete_all_history()
        
        # Update display
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
            
        self.update_totals()
        self.update_exercise_summary([])
        
        self.status_var.set("All history has been deleted")
    
    def show_stats(self):
        """Show the statistics tab."""
        # Show statistics - now we show the stats tab
        self.notebook.select(self.stats_tab)
        
        # Generate chart for the current selection
        self.generate_chart()
    
    def show_about(self):
        """Show the about dialog."""
        # Show about dialog
        about_window = tk.Toplevel(self.root)
        about_window.title("About Jacob Burger Tracker")
        about_window.geometry("600x450")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Content frame
        about_frame = ttk.Frame(about_window, padding=20)
        about_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo (hamburger emoji)
        logo_label = ttk.Label(about_frame, text="🍔", font=("Arial", 48))
        logo_label.pack(pady=10)
        
        # Display ASCII art
        ascii_label = ttk.Label(about_frame, text=self.ascii_art, font=("Courier", 8), justify="left")
        ascii_label.pack(pady=10)
        
        # About text
        about_text = ttk.Label(
            about_frame, 
            text=f"Jacob Burger Tracker v{self.app_version}",
            font=("Roboto", 16, "bold")
        )
        about_text.pack(pady=5)
        
        # Description
        desc_text = ttk.Label(
            about_frame, 
            text="I got hella burgers nigga",
            font=("Roboto", 12)
        )
        desc_text.pack(pady=5)
        
        # Features
        features_frame = ttk.LabelFrame(about_frame, text="Features")
        features_frame.pack(fill=tk.X, pady=10, padx=10)
        
        features_text = ttk.Label(
            features_frame,
            text="• Modern UI\n• Track burgers, sides, and drinks\n• Exercise tracking\n• Kyle Tax\n• Calorie tracking\n• Data visualization\n• Custom food and exercise entries\n• Achievements and challenges\n• Level progression system",
            font=("Roboto", 10),
            justify="left"
        )
        features_text.pack(pady=10, padx=10, anchor="w")
        
        # Credits
        credits_text = ttk.Label(
            about_frame, 
            text="Created by Chaka and Draco and DinoDog",
            font=("Roboto", 10)
        )
        credits_text.pack(pady=10)
        
        # Close button
        ttk.Button(
            about_frame, 
            text="Close", 
            style="Info.TButton",
            command=about_window.destroy
        ).pack(pady=10)
    
    def manage_custom_database(self):
        """Open a window to manage custom foods and exercises."""
        # Create management window
        mgmt_window = tk.Toplevel(self.root)
        mgmt_window.title("Manage Custom Database")
        mgmt_window.geometry("700x500")
        mgmt_window.transient(self.root)
        mgmt_window.grab_set()
        
        # Create notebook for foods and exercises
        notebook = ttk.Notebook(mgmt_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        food_tab = ttk.Frame(notebook)
        exercise_tab = ttk.Frame(notebook)
        
        notebook.add(food_tab, text="Custom Foods")
        notebook.add(exercise_tab, text="Custom Exercises")
        
        # === FOOD TAB ===
        # Filter frame
        food_filter_frame = ttk.Frame(food_tab)
        food_filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(food_filter_frame, text="Filter by category:").pack(side=tk.LEFT, padx=5)
        
        food_categories = ["All Categories"] + ["Burgers", "Sides", "Drinks", "Other"]
        food_filter_var = tk.StringVar(value="All Categories")
        food_filter_combo = ttk.Combobox(
            food_filter_frame,
            textvariable=food_filter_var,
            values=food_categories,
            state="readonly",
            width=15
        )
        food_filter_combo.pack(side=tk.LEFT, padx=5)
        
        # Create treeview for foods
        food_tree_frame = ttk.Frame(food_tab)
        food_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Food Name", "Calories", "Category")
        food_tree = ttk.Treeview(food_tree_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            food_tree.heading(col, text=col)
        
        food_tree.column("Food Name", width=200)
        food_tree.column("Calories", width=100)
        food_tree.column("Category", width=150)
        
        # Add scrollbar
        food_scrollbar = ttk.Scrollbar(food_tree_frame, orient="vertical", command=food_tree.yview)
        food_tree.configure(yscrollcommand=food_scrollbar.set)
        
        food_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        food_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        food_button_frame = ttk.Frame(food_tab)
        food_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Function to filter custom foods
        def filter_custom_foods():
            # Clear tree
            for item in food_tree.get_children():
                food_tree.delete(item)
            
            # Load custom foods
            custom_foods = {}
            if os.path.exists(self.data_manager.custom_food_file):
                try:
                    with open(self.data_manager.custom_food_file, "r") as f:
                        custom_foods = json.load(f)
                except Exception as e:
                    print(f"Error loading custom foods: {e}")
            
            # Add to tree with filter
            category_filter = food_filter_var.get()
            for name, data in custom_foods.items():
                if category_filter == "All Categories" or data.get("category", "Other") == category_filter:
                    food_tree.insert("", "end", values=(
                        name,
                        data["calories"],
                        data.get("category", "Other")
                    ))
        
        # Function to delete custom food
        def delete_custom_food():
            selected = food_tree.selection()
            if not selected:
                messagebox.showinfo("Info", "Please select a food to delete")
                return
            
            # Get food name
            food_name = food_tree.item(selected[0], "values")[0]
            
            if not messagebox.askyesno("Confirm", f"Delete custom food '{food_name}'?"):
                return
            
            # Load custom foods
            custom_foods = {}
            if os.path.exists(self.data_manager.custom_food_file):
                try:
                    with open(self.data_manager.custom_food_file, "r") as f:
                        custom_foods = json.load(f)
                except Exception as e:
                    print(f"Error loading custom foods: {e}")
            
            # Remove the food
            if food_name in custom_foods:
                del custom_foods[food_name]
                
                # Save back to file
                try:
                    with open(self.data_manager.custom_food_file, "w") as f:
                        json.dump(custom_foods, f, indent=4)
                    
                    # Also remove from main database
                    if food_name in self.data_manager.food_database:
                        del self.data_manager.food_database[food_name]
                    
                    # Update tree
                    food_tree.delete(selected[0])
                    messagebox.showinfo("Success", f"Deleted '{food_name}' from custom database")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete: {e}")
        
        # Function to edit custom food
        def edit_custom_food():
            selected = food_tree.selection()
            if not selected:
                messagebox.showinfo("Info", "Please select a food to edit")
                return
            
            # Get food data
            item_id = selected[0]
            values = food_tree.item(item_id, "values")
            food_name = values[0]
            calories = values[1]
            category = values[2]
            
            # Create edit dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Edit {food_name}")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Create form
            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Food Name:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            name_var = tk.StringVar(value=food_name)
            ttk.Entry(frame, textvariable=name_var, width=25).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            ttk.Label(frame, text="Calories:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
            calories_var = tk.StringVar(value=calories)
            ttk.Entry(frame, textvariable=calories_var, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")
            
            ttk.Label(frame, text="Category:", font=("Roboto", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
            
            categories = ["Burgers", "Sides", "Drinks", "Other"]
            category_var = tk.StringVar(value=category)
            category_combo = ttk.Combobox(
                frame, 
                textvariable=category_var, 
                values=categories, 
                width=15,
                state="readonly"
            )
            category_combo.grid(row=2, column=1, padx=10, pady=10, sticky="w")
            
            # Save function
            def save_edit():
                try:
                    new_name = name_var.get().strip()
                    new_calories = int(calories_var.get())
                    new_category = category_var.get()
                    
                    if not new_name or new_calories <= 0:
                        messagebox.showerror("Error", "Please enter valid values")
                        return
                    
                    # Load custom foods
                    custom_foods = {}
                    if os.path.exists(self.data_manager.custom_food_file):
                        try:
                            with open(self.data_manager.custom_food_file, "r") as f:
                                custom_foods = json.load(f)
                        except Exception as e:
                            print(f"Error loading custom foods: {e}")
                    
                    # Remove old entry and add new
                    if food_name in custom_foods:
                        del custom_foods[food_name]
                    
                    custom_foods[new_name] = {
                        "calories": new_calories,
                        "category": new_category
                    }
                    
                    # Save back to file
                    with open(self.data_manager.custom_food_file, "w") as f:
                        json.dump(custom_foods, f, indent=4)
                    
                    # Update main database
                    if food_name in self.data_manager.food_database:
                        del self.data_manager.food_database[food_name]
                    
                    self.data_manager.food_database[new_name] = {
                        "calories": new_calories,
                        "category": new_category
                    }
                    
                    # Update tree
                    food_tree.item(item_id, values=(new_name, new_calories, new_category))
                    messagebox.showinfo("Success", "Food updated successfully")
                    dialog.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid calories")
            
            # Button frame
            button_frame = ttk.Frame(frame)
            button_frame.grid(row=3, column=0, columnspan=2, pady=20)
            
            ttk.Button(button_frame, text="Save", style="Success.TButton", command=save_edit).pack(side="left", padx=10)
            ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
        
        ttk.Button(
            food_filter_frame,
            text="Apply Filter",
            command=filter_custom_foods
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            food_button_frame,
            text="Delete Selected",
            style="Danger.TButton",
            command=delete_custom_food
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            food_button_frame,
            text="Edit Selected",
            style="Info.TButton",
            command=edit_custom_food
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            food_button_frame,
            text="Refresh List",
            command=filter_custom_foods
        ).pack(side=tk.RIGHT, padx=5)
        
        # === EXERCISE TAB ===
        # Create treeview for exercises
        exercise_tree_frame = ttk.Frame(exercise_tab)
        exercise_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Exercise Name", "Calories/min")
        exercise_tree = ttk.Treeview(exercise_tree_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            exercise_tree.heading(col, text=col)
        
        exercise_tree.column("Exercise Name", width=200)
        exercise_tree.column("Calories/min", width=150)
        
        # Add scrollbar
        exercise_scrollbar = ttk.Scrollbar(exercise_tree_frame, orient="vertical", command=exercise_tree.yview)
        exercise_tree.configure(yscrollcommand=exercise_scrollbar.set)
        
        exercise_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        exercise_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        exercise_button_frame = ttk.Frame(exercise_tab)
        exercise_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Function to populate custom exercises
        def populate_custom_exercises():
            # Clear tree
            for item in exercise_tree.get_children():
                exercise_tree.delete(item)
            
            # Load custom exercises
            custom_exercises = {}
            if os.path.exists(self.data_manager.custom_exercise_file):
                try:
                    with open(self.data_manager.custom_exercise_file, "r") as f:
                        custom_exercises = json.load(f)
                except Exception as e:
                    print(f"Error loading custom exercises: {e}")
            
            # Add to tree
            for name, cal_per_min in custom_exercises.items():
                exercise_tree.insert("", "end", values=(
                    name,
                    cal_per_min
                ))
        
        # Function to delete custom exercise
        def delete_custom_exercise():
            selected = exercise_tree.selection()
            if not selected:
                messagebox.showinfo("Info", "Please select an exercise to delete")
                return
            
            # Get exercise name
            exercise_name = exercise_tree.item(selected[0], "values")[0]
            
            if not messagebox.askyesno("Confirm", f"Delete custom exercise '{exercise_name}'?"):
                return
            
            # Load custom exercises
            custom_exercises = {}
            if os.path.exists(self.data_manager.custom_exercise_file):
                try:
                    with open(self.data_manager.custom_exercise_file, "r") as f:
                        custom_exercises = json.load(f)
                except Exception as e:
                    print(f"Error loading custom exercises: {e}")
            
            # Remove the exercise
            if exercise_name in custom_exercises:
                del custom_exercises[exercise_name]
                
                # Save back to file
                try:
                    with open(self.data_manager.custom_exercise_file, "w") as f:
                        json.dump(custom_exercises, f, indent=4)
                    
                    # Also remove from main database
                    if exercise_name in self.data_manager.exercise_database:
                        del self.data_manager.exercise_database[exercise_name]
                    
                    # Update tree
                    exercise_tree.delete(selected[0])
                    messagebox.showinfo("Success", f"Deleted '{exercise_name}' from custom database")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to delete: {e}")
        
        # Function to edit custom exercise
        def edit_custom_exercise():
            selected = exercise_tree.selection()
            if not selected:
                messagebox.showinfo("Info", "Please select an exercise to edit")
                return
            
            # Get exercise data
            item_id = selected[0]
            values = exercise_tree.item(item_id, "values")
            exercise_name = values[0]
            cal_per_min = values[1]
            
            # Create edit dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Edit {exercise_name}")
            dialog.geometry("400x250")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Create form
            frame = ttk.Frame(dialog, padding=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Exercise Name:", font=("Roboto", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            name_var = tk.StringVar(value=exercise_name)
            ttk.Entry(frame, textvariable=name_var, width=25).grid(row=0, column=1, padx=10, pady=10, sticky="w")
            
            ttk.Label(frame, text="Calories/min:", font=("Roboto", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
            cal_var = tk.StringVar(value=cal_per_min)
            ttk.Entry(frame, textvariable=cal_var, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")
            
            # Save function
            def save_edit():
                try:
                    new_name = name_var.get().strip()
                    new_cal = float(cal_var.get())
                    
                    if not new_name or new_cal <= 0:
                        messagebox.showerror("Error", "Please enter valid values")
                        return
                    
                    # Load custom exercises
                    custom_exercises = {}
                    if os.path.exists(self.data_manager.custom_exercise_file):
                        try:
                            with open(self.data_manager.custom_exercise_file, "r") as f:
                                custom_exercises = json.load(f)
                        except Exception as e:
                            print(f"Error loading custom exercises: {e}")
                    
                    # Remove old entry and add new
                    if exercise_name in custom_exercises:
                        del custom_exercises[exercise_name]
                    
                    custom_exercises[new_name] = new_cal
                    
                    # Save back to file
                    with open(self.data_manager.custom_exercise_file, "w") as f:
                        json.dump(custom_exercises, f, indent=4)
                    
                    # Update main database
                    if exercise_name in self.data_manager.exercise_database:
                        del self.data_manager.exercise_database[exercise_name]
                    
                    self.data_manager.exercise_database[new_name] = new_cal
                    
                    # Update tree
                    exercise_tree.item(item_id, values=(new_name, new_cal))
                    messagebox.showinfo("Success", "Exercise updated successfully")
                    dialog.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid calories per minute")
            
            # Button frame
            button_frame = ttk.Frame(frame)
            button_frame.grid(row=2, column=0, columnspan=2, pady=20)
            
            ttk.Button(button_frame, text="Save", style="Success.TButton", command=save_edit).pack(side="left", padx=10)
            ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
        
        ttk.Button(
            exercise_button_frame,
            text="Delete Selected",
            style="Danger.TButton",
            command=delete_custom_exercise
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            exercise_button_frame,
            text="Edit Selected",
            style="Info.TButton",
            command=edit_custom_exercise
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            exercise_button_frame,
            text="Refresh List",
            command=populate_custom_exercises
        ).pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        filter_custom_foods()
        populate_custom_exercises()
        
        # Close button
        ttk.Button(
            mgmt_window,
            text="Close",
            command=mgmt_window.destroy
        ).pack(pady=10)
    
    def show_calendar(self, parent_widget=None):
        """Show calendar dialog for date selection."""
        # Create calendar dialog
        calendar_dialog = CalendarDialog(
            self.root,
            self.date_var,
            self.data_manager.history,
            self.on_date_selected
        )
    
    def on_date_selected(self, date_str):
        """Handle date selection from calendar."""
        # Load entries for the selected date
        self.load_entries()
        self.load_exercises()
        
        # Update weight data if weight_var exists
        if hasattr(self, 'weight_var'):
            day_data = self.data_manager.get_day_data(date_str)
            current_weight = day_data.get("weight")
            
            if current_weight is not None:
                self.weight_var.set(str(current_weight))
            else:
                self.weight_var.set("")
    
    def on_tab_changed(self, event):
        """Handle tab change event."""
        # Refresh the current tab's content when tab is changed
        current_tab = self.notebook.index('current')
        
        if current_tab == 0:  # Daily Tracking
            self.load_entries()
        elif current_tab == 1:  # Exercise Log
            self.load_exercises()
        elif current_tab == 2:  # Weight Tracker
            self.load_weight_history()
        elif current_tab == 3:  # Statistics
            self.generate_chart()
            self.update_stats_text()
        elif current_tab == 4:  # Achievements
            self.refresh_achievements()
    
    def on_window_resize(self, event):
        """Handle window resize event."""
        # This method is called when the window is resized
        # Update UI elements that need to be adjusted on resize
        
        # Check if the event is for the main window
        if event.widget == self.root:
            width = event.width
            height = event.height
            
            # Scale font sizes based on window dimensions
            base_size = min(max(int(width / 80), 8), 14)  # Limit font size between 8 and 14
            
            # Update font configurations
            self.style.configure("TButton", font=("Roboto", base_size))
            self.style.configure("TLabel", font=("Roboto", base_size))
            self.style.configure("Heading.TLabel", font=("Roboto", base_size + 2, "bold"))
            
            # Update tree column widths
            if hasattr(self, 'tree'):
                # Calculate proportional widths
                food_width = int(width * 0.3)
                quantity_width = int(width * 0.1)
                category_width = int(width * 0.2)
                calories_width = int(width * 0.15)
                kyle_width = int(width * 0.15)
                
                self.tree.column("Food", width=food_width)
                self.tree.column("Quantity", width=quantity_width)
                self.tree.column("Category", width=category_width)
                self.tree.column("Calories", width=calories_width)
                self.tree.column("Kyle Tax", width=kyle_width)
            
            # Update exercise tree column widths
            if hasattr(self, 'exercise_tree'):
                exercise_width = int(width * 0.4)
                duration_width = int(width * 0.2)
                calories_burnt_width = int(width * 0.2)
                
                self.exercise_tree.column("Exercise", width=exercise_width)
                self.exercise_tree.column("Duration (min)", width=duration_width)
                self.exercise_tree.column("Calories Burnt", width=calories_burnt_width)
            
            # Update weight tree column widths
            if hasattr(self, 'weight_tree'):
                date_width = int(width * 0.5)
                weight_width = int(width * 0.4)
                
                self.weight_tree.column("Date", width=date_width)
                self.weight_tree.column("Weight (lb)", width=weight_width)
            
            # Regenerate current chart if on stats tab
            if hasattr(self, 'notebook') and self.notebook.index('current') == 3:  # Stats tab index
                self.generate_chart()
    
    def show_weight_tracker(self):
        """Show the weight tracker tab."""
        self.notebook.select(2)  # Index 2 is the weight tab
    
    def save_history(self):
        """Save history to file."""
        if self.data_manager.save_history():
            # Also save gamification data
            self.gamification_manager.save_gamification_data()
            
            # Check for new achievements and challenges
            new_achievements = self.gamification_manager.check_achievements()
            new_daily, new_weekly = self.gamification_manager.check_challenges()
            
            # Show notifications for new unlocks
            for achievement in new_achievements:
                self.show_achievement_notification(achievement)
                
            for challenge in new_daily + new_weekly:
                self.show_challenge_notification(challenge)
                
            self.status_var.set("Data saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save history")


# Run the application
if __name__ == "__main__":
    try:
        print("Starting Jacob Burger Tracker...")
        root = tk.Tk()
        app = BurgerTracker(root)
        print("Application initialized. Starting main loop...")
        root.mainloop()
        print("Application closed normally.")
    except Exception as e:
        print(f"Error running application: {e}")