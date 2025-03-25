import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import json
import ttkthemes  # For better themes
from ttkbootstrap import Style  # For modern Bootstrap-like styling
import matplotlib.pyplot as plt  # For visualizing consumption
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk  # Modern UI elements
import calendar  # Standard Python calendar module

class BurgerTracker:
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
        
        # Apply modern theme
        self.style = Style(theme="superhero")
        
        # Configure global styling
        self.style.configure("TButton", font=("Roboto", 10))
        self.style.configure("TLabel", font=("Roboto", 10))
        self.style.configure("TFrame", background="#2b3e50")
        
        # App version
        self.app_version = "1.5"  # Updated version number for calendar feature
        
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
        
        # Food database - now with categories
        self.food_database = {
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
        
        # Exercise database - common activities and their calories burnt per minute
        self.exercise_database = {
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
        
        # Data files
        self.data_file = "burger_tracker_data.json"
        self.custom_food_file = "custom_foods.json"  # New file for custom foods
        self.custom_exercise_file = "custom_exercises.json"  # New file for custom exercises
        
        # Load custom databases if they exist
        self.load_custom_databases()
        
        # History by date
        self.history = self.load_history()
        
        # Today's date string
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Today's entries
        self.today_entries = self.history.get(self.current_date, {"food": [], "exercise": [], "weight": None})
        
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
        
        # Create tabs for different views
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure notebook for responsive behavior
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Create tab for daily tracking
        self.tracking_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        self.exercise_tab = ttk.Frame(self.notebook)  # New tab for exercise tracking
        self.weight_tab = ttk.Frame(self.notebook)  # New tab for weight tracking
        
        # Configure tab frames for responsive behavior
        for tab in [self.tracking_tab, self.stats_tab, self.exercise_tab, self.weight_tab]:
            for i in range(5):  # Generous number of columns
                tab.columnconfigure(i, weight=1)
            for i in range(5):  # Generous number of rows
                tab.rowconfigure(i, weight=1)
        
        self.notebook.add(self.tracking_tab, text="Daily Tracking")
        self.notebook.add(self.exercise_tab, text="Exercise Log")  # New exercise tab
        self.notebook.add(self.weight_tab, text="Weight Tracker")  # New weight tracking tab
        self.notebook.add(self.stats_tab, text="Statistics")
        
        # Setup tracking tab
        self.setup_tracking_tab()

        # Setup exercise tab
        self.setup_exercise_tab()
        
        # Setup weight tracking tab
        self.setup_weight_tab()
        
        # Setup stats tab
        self.setup_stats_tab()
        
        # Load today's entries
        self.load_entries()
        self.load_exercises()  # Load exercises
        
        # Status bar
        status_bar = ttk.Frame(self.main_frame)
        status_bar.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_bar, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Version info
        version_label = ttk.Label(status_bar, text=f"v{self.app_version}", anchor=tk.E)  # Updated version number
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def setup_tracking_tab(self):
        # Upper section with date and goal controls
        control_frame = ttk.Frame(self.tracking_tab)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Left side - Date selection
        date_frame = ttk.LabelFrame(control_frame, text="Date Selection")
        date_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        
        date_controls = ttk.Frame(date_frame)
        date_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(date_controls, text="Date:").pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar(value=self.current_date)
        date_entry = ttk.Entry(date_controls, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        # Bind double-click and Enter key to show calendar
        date_entry.bind("<Double-1>", lambda e: self.show_calendar(date_entry))
        date_entry.bind("<Return>", lambda e: self.load_entries())
        
        # Calendar button with icon
        cal_button = ttk.Button(
            date_controls,
            text="📅",  # Calendar emoji
            width=2,
            command=lambda: self.show_calendar(date_entry)
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
        log_frame = ttk.LabelFrame(self.tracking_tab, text="Food Log")  # Changed from "Burger Log" to "Food Log"
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for food entries
        columns = ("Food", "Quantity", "Category", "Calories", "Kyle Tax")  # Added Category column
        self.tree = ttk.Treeview(log_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Food", width=150)
        self.tree.column("Quantity", width=60)
        self.tree.column("Category", width=80)  # New category column
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
        self.burnt_var = tk.StringVar(value="Calories Burnt: 0")  # New variable for burned calories
        self.net_var = tk.StringVar(value="Net Calories: 0")  # New variable for net calories
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
        date_entry.bind("<Double-1>", lambda e: self.show_calendar(date_entry))
        date_entry.bind("<Return>", lambda e: self.load_exercises())
        
        # Calendar button with icon
        cal_button = ttk.Button(
            date_controls,
            text="📅",  # Calendar emoji
            width=2,
            command=lambda: self.show_calendar(date_entry)
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
        date_entry.bind("<Double-1>", lambda e: self.show_calendar(date_entry))
        date_entry.bind("<Return>", lambda e: self.load_weight_history())
        
        # Calendar button with icon
        cal_button = ttk.Button(
            date_controls,
            text="📅",  # Calendar emoji
            width=2,
            command=lambda: self.show_calendar(date_entry)
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
    
    def load_weight_history(self):
        # Clear the weight treeview
        for item in self.weight_tree.get_children():
            self.weight_tree.delete(item)
        
        # Load weight history from all dates
        weights = []
        for date, data in self.history.items():
            weight = data.get("weight")
            if weight is not None:
                weights.append((date, weight))
        
        # Sort by date (newest first)
        weights.sort(reverse=True)
        
        # Add to treeview
        for date, weight in weights:
            self.weight_tree.insert("", "end", values=(date, weight))
        
        # Load current date's weight if it exists
        selected_date = self.date_var.get()
        day_data = self.get_day_data(selected_date)
        current_weight = day_data.get("weight")
        
        if current_weight is not None:
            self.weight_var.set(str(current_weight))
        else:
            self.weight_var.set("")
    
    def save_weight(self):
        # Get the weight value
        try:
            weight = float(self.weight_var.get())
            if weight <= 0:
                messagebox.showerror("Error", "Weight must be a positive number")
                return
                
            # Get the selected date
            selected_date = self.date_var.get()
            
            # Update the weight for this date
            day_data = self.get_day_data(selected_date)
            day_data["weight"] = weight
            
            # If it's today, update today_entries
            if selected_date == self.current_date:
                self.today_entries["weight"] = weight
            
            # Update history
            self.history[selected_date] = day_data
            
            # Save to file
            self.save_history()
            
            # Refresh the weight history display
            self.load_weight_history()
            
            # Show confirmation
            self.status_var.set(f"Weight for {selected_date} saved: {weight} lb")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid weight value")
    
    def delete_weight(self):
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
        if item_date in self.history:
            self.history[item_date]["weight"] = None
            
            # If it's today, update today_entries
            if item_date == self.current_date:
                self.today_entries["weight"] = None
            
            # Save to file
            self.save_history()
            
            # Refresh the weight history display
            self.load_weight_history()
            
            # Show confirmation
            self.status_var.set(f"Weight for {item_date} deleted")
        
    def edit_weight(self):
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
                if item_date in self.history:
                    self.history[item_date]["weight"] = new_weight
                    
                    # If it's today, update today_entries
                    if item_date == self.current_date:
                        self.today_entries["weight"] = new_weight
                    
                    # Save to file
                    self.save_history()
                    
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
    
    def setup_stats_tab(self):
        # Create frames for stats display
        chart_frame = ttk.Frame(self.stats_tab)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(chart_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Select Chart:").pack(side=tk.LEFT, padx=5)
        
        chart_options = ["Weekly Calories", "Daily Distribution", "Food Types", "Calories In vs Out", "Weight Tracking"]  # Added weight tracking chart
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
    
    def create_menu(self):
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
        tools_menu.add_command(label="Food Statistics", command=self.show_stats)  # Changed from "Burger Statistics"
        tools_menu.add_command(label="Weight Tracker", command=self.show_weight_tracker)  # Added menu item for weight tracking
        tools_menu.add_command(label="Refresh Charts", command=self.generate_chart)
        tools_menu.add_separator()
        tools_menu.add_command(label="Manage Custom Database", command=self.manage_custom_database)
        
        # Create View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        
        themes = ["Draco", "Justin", "Mason", "William", "Chaka"]
        for theme in themes:
            theme_menu.add_command(
                label=theme.capitalize(),
                command=lambda t=theme: self.change_theme(t)
            )
        
        # Create Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_guide)
    
    def change_theme(self, theme_name):
        self.style = Style(theme=theme_name)
        self.style.configure("TButton", font=("Roboto", 10))
        self.style.configure("TLabel", font=("Roboto", 10))
        self.status_var.set(f"Theme changed to {theme_name.capitalize()}")
    
    def export_report(self):
        filename = f"burger_report_{self.current_date}.txt"
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
                day_data = self.get_day_data(selected_date)
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
        # Clear the current chart
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#2b3e50')  # Match background
        ax.set_facecolor('#2b3e50')
        ax.tick_params(colors='white')  # White ticks
        
        # Set title text color to white
        plt.rcParams['text.color'] = 'white'
        plt.rcParams['axes.labelcolor'] = 'white'
        plt.rcParams['xtick.color'] = 'white'
        plt.rcParams['ytick.color'] = 'white'
        
        # Create the selected chart
        selected_chart = self.chart_var.get()
        
        if selected_chart == "Weekly Calories":
            self.create_weekly_chart(ax)
        elif selected_chart == "Daily Distribution":
            self.create_distribution_chart(ax)
        elif selected_chart == "Food Types":
            self.create_food_types_chart(ax)
        elif selected_chart == "Calories In vs Out":
            self.create_calories_in_out_chart(ax)
        elif selected_chart == "Weight Tracking":
            self.create_weight_tracking_chart(ax)
        
        # Create canvas for chart
        self.canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Update stats text
        self.update_stats_text()
    
    def create_weekly_chart(self, ax):
        # Get the last 7 days
        end_date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
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
        try:
            goal = int(self.goal_var.get())
            ax.axhline(y=goal, color='r', linestyle='--', label=f'Goal ({goal} cal)')
            ax.legend()
        except ValueError:
            pass
    
    def create_distribution_chart(self, ax):
        # Get entries for selected date
        selected_date = self.date_var.get()
        day_data = self.get_day_data(selected_date)
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
        ax.set_title(f'Calorie Distribution - {selected_date}')
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    def create_food_types_chart(self, ax):
        # Collect all food types from all dates, now with categories
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
    
    def create_calories_in_out_chart(self, ax):
        # Get the last 7 days
        end_date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
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
    
    def update_stats_text(self):
        # Calculate stats
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
        
        # Generate stats text
        stats_text = f"Total days tracked: {total_days}\n"
        stats_text += f"Total food entries: {total_foods}\n"
        stats_text += f"Total exercise entries: {total_exercises}\n"
        stats_text += f"Total calories consumed: {total_calories}\n"
        stats_text += f"Total calories burned: {total_burned}\n"
        stats_text += f"Net calories: {total_calories - total_burned}\n"
        
        # Add weight stats if available
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
    
    def get_day_data(self, date_str):
        """Get food and exercise data for a specific day."""
        # If it's today and not in history, use today's entries
        if date_str == self.current_date and date_str not in self.history:
            return self.today_entries
        # Otherwise get from history
        return self.history.get(date_str, {"food": [], "exercise": [], "weight": None})
    
    def load_history(self):
        # Load history from file
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
                messagebox.showerror("Error", f"Failed to load history: {e}")
                return {}
        return {}
    
    def save_history(self):
        # Save current entries to today's date
        self.history[self.current_date] = self.today_entries
        
        # Save history to file
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.history, f, indent=4)
            self.status_var.set("Data saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {e}")
    
    def change_date(self, days):
        # Change the selected date
        try:
            date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
            new_date = date + datetime.timedelta(days=days)
            self.date_var.set(new_date.strftime("%Y-%m-%d"))
            self.load_entries()
            self.load_exercises()  # Also load exercises for the new date
            
            # Also update weight data for the selected date
            if hasattr(self, 'weight_var'):
                selected_date = self.date_var.get()
                day_data = self.get_day_data(selected_date)
                current_weight = day_data.get("weight")
                
                if current_weight is not None:
                    self.weight_var.set(str(current_weight))
                else:
                    self.weight_var.set("")
                    
        except ValueError:
            self.go_to_today()
    
    def go_to_today(self):
        # Set date to today
        self.date_var.set(self.current_date)
        
        # Show the calendar popup
        self.show_calendar(None)
        
        # Load entries and exercises
        self.load_entries()
        self.load_exercises()  # Also load exercises
        
        # Also update weight data for today
        if hasattr(self, 'weight_var'):
            day_data = self.get_day_data(self.current_date)
            current_weight = day_data.get("weight")
            
            if current_weight is not None:
                self.weight_var.set(str(current_weight))
            else:
                self.weight_var.set("")
    
    def load_entries(self):
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get selected date
        selected_date = self.date_var.get()
        
        # Get data for the selected date
        day_data = self.get_day_data(selected_date)
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
                entry.get("category", "Food"),  # Add category
                adjusted_calories,
                kyle_status
            ))
        
        # Update totals
        self.update_totals()
    
    def load_exercises(self):
        # Clear the exercise treeview
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
        
        # Get selected date
        selected_date = self.date_var.get()
        
        # Get data for the selected date
        day_data = self.get_day_data(selected_date)
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
        # Calculate exercise statistics
        if exercises is None:
            day_data = self.get_day_data(self.date_var.get())
            exercises = day_data.get("exercise", [])
        
        total_time = sum(ex["duration"] for ex in exercises)
        total_burnt = sum(ex["calories_burnt"] for ex in exercises)
        
        # Update display
        self.total_exercise_var.set(f"Total Exercise Time: {total_time} minutes")
        self.total_burnt_var.set(f"Total Calories Burnt: {total_burnt}")
    
    def update_totals(self):
        # Get food entries
        day_data = self.get_day_data(self.date_var.get())
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
        # Re-load entries to apply or remove Kyle Tax
        self.load_entries()
        
        if self.kyle_tax_enabled.get():
            self.status_var.set("Kyle Tax applied: 15% calorie reduction")
        else:
            self.status_var.set("Kyle Tax removed")
    
    def set_goal(self):
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
        # Create a modern dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Food Item")  # Changed from "Add Burger"
        dialog.geometry("500x450")  # Made larger for custom entry fields
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
            food_options = [food for food, data in self.food_database.items() 
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
                if food in self.food_database:
                    original_cal = self.food_database[food]["calories"] * amount
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
                    if not (food and food in self.food_database and amount > 0):
                        messagebox.showerror("Error", "Please select a valid food and amount")
                        return
                        
                    calories = self.food_database[food]["calories"] * amount
                    category = self.food_database[food]["category"]
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
                        if self.save_custom_food(food, int(cal_per_unit), category):
                            self.status_var.set(f"Added and saved {food} to database")
                        else:
                            messagebox.showwarning("Warning", "Could not save food to database, but it will be added to today's log")
                
                # Add to tree
                display_calories = int(calories * 0.85) if apply_kyle else int(calories)
                self.tree.insert("", "end", values=(
                    food,
                    f"{amount:.1f}",
                    category,
                    display_calories,
                    "Applied" if apply_kyle else "No"
                ))
                
                # Add to entries if it's today
                if self.date_var.get() == self.current_date:
                    if "food" not in self.today_entries:
                        self.today_entries["food"] = []
                        
                    self.today_entries["food"].append({
                        "food": food,
                        "amount": amount,
                        "calories": int(calories),
                        "category": category,
                        "kyle_tax": apply_kyle
                    })
                else:
                    # Add to history for selected date
                    selected_date = self.date_var.get()
                    if selected_date not in self.history:
                        self.history[selected_date] = {"food": [], "exercise": []}
                    
                    if "food" not in self.history[selected_date]:
                        self.history[selected_date]["food"] = []
                        
                    self.history[selected_date]["food"].append({
                        "food": food,
                        "amount": amount,
                        "calories": int(calories),
                        "category": category,
                        "kyle_tax": apply_kyle
                    })
                
                # Update total
                self.update_totals()
                self.status_var.set(f"Added {amount} {food}")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
        
        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", style="Success.TButton", command=save_entry).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
    
    def add_exercise(self):
        # Create dialog for adding exercise
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Exercise")
        dialog.geometry("450x350")  # Made bigger for custom options
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
        
        exercise_options = list(self.exercise_database.keys())
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
        cal_per_min_var = tk.StringVar(value=str(self.exercise_database[exercise_options[0]]))
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
                if exercise in self.exercise_database:
                    calories_per_min = self.exercise_database[exercise]
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
            if exercise in self.exercise_database:
                cal_per_min_var.set(str(self.exercise_database[exercise]))
        
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
                    if not exercise or exercise not in self.exercise_database:
                        messagebox.showerror("Error", "Please select a valid exercise")
                        return
                        
                    # Calculate calories burnt
                    calories_per_min = self.exercise_database[exercise]
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
                        if self.save_custom_exercise(exercise, cal_per_min):
                            self.status_var.set(f"Added and saved {exercise} to exercise database")
                        else:
                            messagebox.showwarning("Warning", "Could not save exercise to database, but it will be added to today's log")
                
                # Add to exercise tree
                self.exercise_tree.insert("", "end", values=(
                    exercise,
                    f"{duration:.1f}",
                    calories_burnt
                ))
                
                # Add to data structure
                exercise_entry = {
                    "exercise": exercise,
                    "duration": duration,
                    "calories_burnt": calories_burnt
                }
                
                # Add to entries if it's today
                if self.date_var.get() == self.current_date:
                    if "exercise" not in self.today_entries:
                        self.today_entries["exercise"] = []
                        
                    self.today_entries["exercise"].append(exercise_entry)
                else:
                    # Add to history for selected date
                    selected_date = self.date_var.get()
                    if selected_date not in self.history:
                        self.history[selected_date] = {"food": [], "exercise": []}
                    
                    if "exercise" not in self.history[selected_date]:
                        self.history[selected_date]["exercise"] = []
                        
                    self.history[selected_date]["exercise"].append(exercise_entry)
                
                # Update summaries
                self.update_exercise_summary()
                self.update_totals()  # Update main tab as well
                
                self.status_var.set(f"Added {exercise} for {duration} minutes")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid values")
        
        button_frame = ttk.Frame(dialog_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", style="Success.TButton", command=save_entry).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
    
    def delete_food(self):
        # Get selected item
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an entry to delete")
            return
        
        # Get selected date
        selected_date = self.date_var.get()
        day_data = self.get_day_data(selected_date)
        food_entries = day_data.get("food", [])
        
        # Build new list without deleted items
        new_entries = []
        deleted_indices = []
        
        for item in selected:
            idx = self.tree.index(item)
            deleted_indices.append(idx)
        
        for i, entry in enumerate(food_entries):
            if i not in deleted_indices:
                new_entries.append(entry)
        
        # Update entries
        if selected_date == self.current_date and selected_date not in self.history:
            self.today_entries["food"] = new_entries
        else:
            if selected_date not in self.history:
                self.history[selected_date] = {"food": [], "exercise": []}
            self.history[selected_date]["food"] = new_entries
        
        # Remove from tree
        for item in selected:
            self.tree.delete(item)
        
        # Update totals
        self.update_totals()
        self.status_var.set(f"Deleted {len(selected)} food entries")
    
    def delete_exercise(self):
        # Get selected item
        selected = self.exercise_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an exercise to delete")
            return
        
        # Get selected date
        selected_date = self.date_var.get()
        day_data = self.get_day_data(selected_date)
        exercise_entries = day_data.get("exercise", [])
        
        # Build new list without deleted items
        new_entries = []
        deleted_indices = []
        
        for item in selected:
            idx = self.exercise_tree.index(item)
            deleted_indices.append(idx)
        
        for i, entry in enumerate(exercise_entries):
            if i not in deleted_indices:
                new_entries.append(entry)
        
        # Update entries
        if selected_date == self.current_date and selected_date not in self.history:
            self.today_entries["exercise"] = new_entries
        else:
            if selected_date not in self.history:
                self.history[selected_date] = {"food": [], "exercise": []}
            self.history[selected_date]["exercise"] = new_entries
        
        # Remove from tree
        for item in selected:
            self.exercise_tree.delete(item)
        
        # Update totals
        self.update_exercise_summary(new_entries)
        self.update_totals()  # Also update main tab
        self.status_var.set(f"Deleted {len(selected)} exercise entries")
    
    def clear_all(self):
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Clear all food entries for this date?"):
            return
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear entries
        selected_date = self.date_var.get()
        if selected_date == self.current_date and selected_date not in self.history:
            self.today_entries["food"] = []
        else:
            if selected_date in self.history:
                self.history[selected_date]["food"] = []
        
        # Update totals
        self.update_totals()
        self.status_var.set(f"Cleared all food entries for {selected_date}")
    
    def clear_all_exercises(self):
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Clear all exercise entries for this date?"):
            return
        
        # Clear treeview
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
        
        # Clear entries
        selected_date = self.date_var.get()
        if selected_date == self.current_date and selected_date not in self.history:
            self.today_entries["exercise"] = []
        else:
            if selected_date in self.history:
                self.history[selected_date]["exercise"] = []
        
        # Update totals
        self.update_exercise_summary([])
        self.update_totals()  # Also update main tab
        self.status_var.set(f"Cleared all exercise entries for {selected_date}")
    
    def clear_today(self):
        # Clear today's entries
        if not messagebox.askyesno("Confirm", "Clear all entries for today?"):
            return
        
        self.today_entries = {"food": [], "exercise": []}
        
        # If today is selected, update display
        if self.date_var.get() == self.current_date:
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
        # Delete all history
        if not messagebox.askyesno("Confirm", "Delete ALL history data? This cannot be undone!"):
            return
        
        self.history = {}
        self.today_entries = {"food": [], "exercise": []}
        
        # Update display
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
            
        self.update_totals()
        self.update_exercise_summary([])
        
        self.status_var.set("All history has been deleted")
    
    def show_stats(self):
        # Show statistics - now we show the stats tab
        self.notebook.select(self.stats_tab)
        
        # Generate chart for the current selection
        self.generate_chart()
    
    def show_about(self):
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
            text="Jacob Burger Tracker v1.5",  # Updated version
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
            text="• Modern UI\n• Track burgers, sides, and drinks\n• Exercise tracking\n• Kyle Tax\n• Calorie tracking\n• Data visualization\n• Custom food and exercise entries",
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
    
    def load_custom_databases(self):
        """Load custom foods and exercises from files"""
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
    
    def save_custom_food(self, name, calories, category):
        """Save a custom food to the database"""
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
    
    def save_custom_exercise(self, name, calories_per_min):
        """Save a custom exercise to the database"""
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
    
    def manage_custom_database(self):
        """Open a window to manage custom foods and exercises"""
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
        
        ttk.Button(
            food_filter_frame,
            text="Apply Filter",
            command=lambda: self.filter_custom_foods(food_tree, food_filter_var.get())
        ).pack(side=tk.LEFT, padx=5)
        
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
        
        ttk.Button(
            food_button_frame,
            text="Delete Selected",
            style="Danger.TButton",
            command=lambda: self.delete_custom_food(food_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            food_button_frame,
            text="Edit Selected",
            style="Info.TButton",
            command=lambda: self.edit_custom_food(food_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            food_button_frame,
            text="Refresh List",
            command=lambda: self.populate_custom_foods(food_tree)
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
        
        ttk.Button(
            exercise_button_frame,
            text="Delete Selected",
            style="Danger.TButton",
            command=lambda: self.delete_custom_exercise(exercise_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            exercise_button_frame,
            text="Edit Selected",
            style="Info.TButton",
            command=lambda: self.edit_custom_exercise(exercise_tree)
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            exercise_button_frame,
            text="Refresh List",
            command=lambda: self.populate_custom_exercises(exercise_tree)
        ).pack(side=tk.RIGHT, padx=5)
        
        # Load initial data
        self.populate_custom_foods(food_tree)
        self.populate_custom_exercises(exercise_tree)
        
        # Close button
        ttk.Button(
            mgmt_window,
            text="Close",
            command=mgmt_window.destroy
        ).pack(pady=10)
    
    def populate_custom_foods(self, tree):
        """Populate the custom foods treeview"""
        # Clear tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Load custom foods
        custom_foods = {}
        if os.path.exists(self.custom_food_file):
            try:
                with open(self.custom_food_file, "r") as f:
                    custom_foods = json.load(f)
            except Exception as e:
                print(f"Error loading custom foods: {e}")
        
        # Add to tree
        for name, data in custom_foods.items():
            tree.insert("", "end", values=(
                name,
                data["calories"],
                data.get("category", "Other")
            ))
    
    def filter_custom_foods(self, tree, category):
        """Filter custom foods by category"""
        # Clear tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Load custom foods
        custom_foods = {}
        if os.path.exists(self.custom_food_file):
            try:
                with open(self.custom_food_file, "r") as f:
                    custom_foods = json.load(f)
            except Exception as e:
                print(f"Error loading custom foods: {e}")
        
        # Add to tree with filter
        for name, data in custom_foods.items():
            if category == "All Categories" or data.get("category", "Other") == category:
                tree.insert("", "end", values=(
                    name,
                    data["calories"],
                    data.get("category", "Other")
                ))
    
    def delete_custom_food(self, tree):
        """Delete selected custom food"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a food to delete")
            return
        
        # Get food name
        food_name = tree.item(selected[0], "values")[0]
        
        if not messagebox.askyesno("Confirm", f"Delete custom food '{food_name}'?"):
            return
        
        # Load custom foods
        custom_foods = {}
        if os.path.exists(self.custom_food_file):
            try:
                with open(self.custom_food_file, "r") as f:
                    custom_foods = json.load(f)
            except Exception as e:
                print(f"Error loading custom foods: {e}")
        
        # Remove the food
        if food_name in custom_foods:
            del custom_foods[food_name]
            
            # Save back to file
            try:
                with open(self.custom_food_file, "w") as f:
                    json.dump(custom_foods, f, indent=4)
                
                # Also remove from main database
                if food_name in self.food_database:
                    del self.food_database[food_name]
                
                # Update tree
                tree.delete(selected[0])
                messagebox.showinfo("Success", f"Deleted '{food_name}' from custom database")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
    
    def edit_custom_food(self, tree):
        """Edit selected custom food"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a food to edit")
            return
        
        # Get food data
        item_id = selected[0]
        values = tree.item(item_id, "values")
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
                if os.path.exists(self.custom_food_file):
                    try:
                        with open(self.custom_food_file, "r") as f:
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
                with open(self.custom_food_file, "w") as f:
                    json.dump(custom_foods, f, indent=4)
                
                # Update main database
                if food_name in self.food_database:
                    del self.food_database[food_name]
                
                self.food_database[new_name] = {
                    "calories": new_calories,
                    "category": new_category
                }
                
                # Update tree
                tree.item(item_id, values=(new_name, new_calories, new_category))
                messagebox.showinfo("Success", "Food updated successfully")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid calories")
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", style="Success.TButton", command=save_edit).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
    
    def populate_custom_exercises(self, tree):
        """Populate the custom exercises treeview"""
        # Clear tree
        for item in tree.get_children():
            tree.delete(item)
        
        # Load custom exercises
        custom_exercises = {}
        if os.path.exists(self.custom_exercise_file):
            try:
                with open(self.custom_exercise_file, "r") as f:
                    custom_exercises = json.load(f)
            except Exception as e:
                print(f"Error loading custom exercises: {e}")
        
        # Add to tree
        for name, cal_per_min in custom_exercises.items():
            tree.insert("", "end", values=(
                name,
                cal_per_min
            ))
    
    def delete_custom_exercise(self, tree):
        """Delete selected custom exercise"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an exercise to delete")
            return
        
        # Get exercise name
        exercise_name = tree.item(selected[0], "values")[0]
        
        if not messagebox.askyesno("Confirm", f"Delete custom exercise '{exercise_name}'?"):
            return
        
        # Load custom exercises
        custom_exercises = {}
        if os.path.exists(self.custom_exercise_file):
            try:
                with open(self.custom_exercise_file, "r") as f:
                    custom_exercises = json.load(f)
            except Exception as e:
                print(f"Error loading custom exercises: {e}")
        
        # Remove the exercise
        if exercise_name in custom_exercises:
            del custom_exercises[exercise_name]
            
            # Save back to file
            try:
                with open(self.custom_exercise_file, "w") as f:
                    json.dump(custom_exercises, f, indent=4)
                
                # Also remove from main database
                if exercise_name in self.exercise_database:
                    del self.exercise_database[exercise_name]
                
                # Update tree
                tree.delete(selected[0])
                messagebox.showinfo("Success", f"Deleted '{exercise_name}' from custom database")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")
    
    def edit_custom_exercise(self, tree):
        """Edit selected custom exercise"""
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an exercise to edit")
            return
        
        # Get exercise data
        item_id = selected[0]
        values = tree.item(item_id, "values")
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
                if os.path.exists(self.custom_exercise_file):
                    try:
                        with open(self.custom_exercise_file, "r") as f:
                            custom_exercises = json.load(f)
                    except Exception as e:
                        print(f"Error loading custom exercises: {e}")
                
                # Remove old entry and add new
                if exercise_name in custom_exercises:
                    del custom_exercises[exercise_name]
                
                custom_exercises[new_name] = new_cal
                
                # Save back to file
                with open(self.custom_exercise_file, "w") as f:
                    json.dump(custom_exercises, f, indent=4)
                
                # Update main database
                if exercise_name in self.exercise_database:
                    del self.exercise_database[exercise_name]
                
                self.exercise_database[new_name] = new_cal
                
                # Update tree
                tree.item(item_id, values=(new_name, new_cal))
                messagebox.showinfo("Success", "Exercise updated successfully")
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid calories per minute")
        
        # Button frame
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", style="Success.TButton", command=save_edit).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side="left", padx=10)
    
    def create_weight_tracking_chart(self, ax):
        # Get weight entries from history
        weights = []
        dates = []
        
        # Collect all weights with their dates
        for date, data in self.history.items():
            weight = data.get("weight")
            if weight is not None:
                weights.append(weight)
                dates.append(date)
        
        # Sort by date
        sorted_data = sorted(zip(dates, weights), key=lambda x: x[0])
        if not sorted_data:
            ax.text(0.5, 0.5, "No weight data available", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   color='white',
                   fontsize=14)
            return
        
        dates, weights = zip(*sorted_data)
        
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
    
    def on_window_resize(self, event):
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
                self.tree.column("Quantity", width=quantity_width)  # Changed from "Amount" to "Quantity"
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
    
    def on_tab_changed(self, event):
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
    
    def show_weight_tracker(self):
        # Show the weight tracker tab
        self.notebook.select(2)  # Index 2 is the weight tab
    
    def show_calendar(self, parent_widget):
        # Create a toplevel window for the calendar
        cal_window = tk.Toplevel(self.root)
        cal_window.title("Select Date")
        cal_window.geometry("300x320")
        cal_window.resizable(False, False)
        cal_window.transient(self.root)  # Make it transient to the main window
        cal_window.grab_set()  # Modal dialog
        
        # Center window
        cal_window.update_idletasks()
        width = cal_window.winfo_width()
        height = cal_window.winfo_height()
        x = (cal_window.winfo_screenwidth() // 2) - (width // 2)
        y = (cal_window.winfo_screenheight() // 2) - (height // 2)
        cal_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # Get the current date from the date_var
        try:
            current_date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            current_date = datetime.datetime.now()
        
        # Create variables to store selected date
        self.cal_year = tk.IntVar(value=current_date.year)
        self.cal_month = tk.IntVar(value=current_date.month)
        self.cal_day = tk.IntVar(value=current_date.day)
        
        # Month and year selection
        nav_frame = ttk.Frame(cal_window)
        nav_frame.pack(fill="x", padx=10, pady=5)
        
        # Previous month button
        prev_btn = ttk.Button(
            nav_frame, 
            text="◀", 
            width=2,
            command=lambda: self.change_calendar_month(-1, cal_window)
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
            textvariable=tk.StringVar(value=months[current_date.month-1])
        )
        month_combo.pack(side="left", padx=5)
        month_combo.bind("<<ComboboxSelected>>", 
                         lambda e: [self.cal_month.set(month_combo.current()+1), 
                                    self.update_calendar_days(cal_window)])
        
        # Year spinbox
        year_spin = ttk.Spinbox(
            nav_frame, 
            from_=1900, 
            to=2100, 
            width=6,
            textvariable=self.cal_year
        )
        year_spin.pack(side="left", padx=5)
        year_spin.bind("<Return>", lambda e: self.update_calendar_days(cal_window))
        
        # Next month button
        next_btn = ttk.Button(
            nav_frame, 
            text="▶", 
            width=2,
            command=lambda: self.change_calendar_month(1, cal_window)
        )
        next_btn.pack(side="left", padx=5)
        
        # Days of the week
        days_frame = ttk.Frame(cal_window)
        days_frame.pack(fill="x", padx=10, pady=2)
        
        for i, day in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            label = ttk.Label(days_frame, text=day, width=3, anchor="center")
            label.grid(row=0, column=i, padx=1, pady=1)
        
        # Days frame where we'll add the day buttons
        self.days_frame = ttk.Frame(cal_window)
        self.days_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Update the calendar
        self.update_calendar_days(cal_window)
        
        # Button frame
        button_frame = ttk.Frame(cal_window)
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
                self.update_calendar_days(cal_window)
            ]
        ).pack(side="left", padx=10)
        
        # Select button
        ttk.Button(
            button_frame, 
            text="Select", 
            style="Success.TButton",
            command=lambda: self.select_date_from_calendar(cal_window)
        ).pack(side="right", padx=10)
        
        # Cancel button
        ttk.Button(
            button_frame, 
            text="Cancel", 
            style="Secondary.TButton",
            command=cal_window.destroy
        ).pack(side="right", padx=10)
    
    def update_calendar_days(self, cal_window):
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
                        command=lambda d=day: [self.cal_day.set(d), self.select_date_from_calendar(cal_window)]
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
    
    def change_calendar_month(self, delta, cal_window):
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
        self.update_calendar_days(cal_window)
    
    def select_date_from_calendar(self, cal_window):
        # Get the selected date from our custom calendar
        year = self.cal_year.get()
        month = self.cal_month.get()
        day = self.cal_day.get()
        
        # Format the date as YYYY-MM-DD
        formatted_date = f"{year}-{month:02d}-{day:02d}"
        
        # Set the date variable
        self.date_var.set(formatted_date)
        
        # Close the calendar window
        cal_window.destroy()
        
        # Load entries for the selected date
        self.load_entries()
        self.load_exercises()
        
        # Update weight data if weight_var exists
        if hasattr(self, 'weight_var'):
            day_data = self.get_day_data(formatted_date)
            current_weight = day_data.get("weight")
            
            if current_weight is not None:
                self.weight_var.set(str(current_weight))
            else:
                self.weight_var.set("")
    
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
