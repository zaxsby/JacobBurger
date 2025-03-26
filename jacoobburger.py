import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font, simpledialog
import datetime
import os
import json
import matplotlib
# Use Agg backend for better performance
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # For visualizing consumption
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk  # Modern UI elements
import calendar  # Standard Python calendar module
import sv_ttk  # Import sv-ttk instead of ttkbootstrap

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
        
        # File paths
        self.data_file = "burger_tracker_data.json"
        self.custom_food_db = "custom_food_database.json"
        self.custom_exercise_db = "custom_exercise_database.json"
        
        # Initialize variables
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.today_entries = {"food": [], "exercise": [], "water": []}
        self.kyle_tax_enabled = tk.BooleanVar(value=False)
        self.date_var = tk.StringVar(value=self.current_date)
        self.goal_var = tk.StringVar(value="2000")
        self.weight_var = tk.StringVar(value="")
        self.water_progress_var = tk.DoubleVar(value=0)
        self.daily_water_goal = tk.StringVar(value="8")
        self.progress_var = tk.DoubleVar(value=0)
        self.total_var = tk.StringVar(value="Total Calories: 0")
        self.burnt_var = tk.StringVar(value="Calories Burnt: 0")
        self.net_var = tk.StringVar(value="Net Calories: 0")
        self.remaining_var = tk.StringVar(value="Remaining: 0")
        self.total_exercise_var = tk.StringVar(value="Total Exercise Time: 0 minutes")
        self.total_burnt_var = tk.StringVar(value="Total Calories Burnt: 0")
        self.status_var = tk.StringVar(value="Ready")
        
        # Add window resize event handler with debouncing
        self.resize_timer = None
        self.root.bind("<Configure>", self.on_window_resize)
        
        # Initialize theme settings once
        self._initialize_theme()
        
        # Configure global styling
        self.configure_styles()
        
        # App version
        self.app_version = "1.7"  # Updated version number for sv-ttk UI update
        
        # Theme names for menu
        self.theme_names = ["light", "dark"]
        
        # Load history data
        self.history = self.load_history()
        self.today_entries = self.history.get(self.current_date, {"food": [], "exercise": [], "weight": None, "water": []})
        
        # ASCII art for the app
        self.ascii_art = r"""
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
        self.water_tab = ttk.Frame(self.notebook)  # New tab for water tracking
        
        # Configure tab frames for responsive behavior
        for tab in [self.tracking_tab, self.stats_tab, self.exercise_tab, self.weight_tab, self.water_tab]:
            for i in range(5):  # Generous number of columns
                tab.columnconfigure(i, weight=1)
            for i in range(5):  # Generous number of rows
                tab.rowconfigure(i, weight=1)
        
        self.notebook.add(self.tracking_tab, text="Daily Tracking")
        self.notebook.add(self.exercise_tab, text="Exercise Log")  # New exercise tab
        self.notebook.add(self.weight_tab, text="Weight Tracker")  # New weight tracking tab
        self.notebook.add(self.water_tab, text="Water Tracker")  # New water tracking tab
        self.notebook.add(self.stats_tab, text="Statistics")
        
        # Setup tracking tab
        self.setup_tracking_tab()

        # Setup exercise tab
        self.setup_exercise_tab()
        
        # Setup weight tracking tab
        self.setup_weight_tab()
        
        # Setup water tracking tab
        self.setup_water_tab()
        
        # Setup stats tab
        self.setup_stats_tab()
        
        # Load today's entries
        self.load_entries()
        self.load_exercises()  # Load exercises
        
        # Status bar
        status_bar = ttk.Frame(self.main_frame)
        status_bar.pack(fill=tk.X, pady=5)
        
        status_label = ttk.Label(status_bar, textvariable=self.status_var, anchor=tk.W)
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Version info
        version_label = ttk.Label(status_bar, text=f"v{self.app_version}", anchor=tk.E)  # Updated version number
        version_label.pack(side=tk.RIGHT, padx=10)
    
    def configure_styles(self):
        """Configure global styles once instead of repeatedly"""
        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Heading.TLabel", font=("Segoe UI", 12, "bold"))
    
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
        
        # Add separator between upper controls and food log
        ttk.Separator(self.tracking_tab, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
        # Create the food log frame
        log_frame = ttk.LabelFrame(self.tracking_tab, text="Food Log")  # Changed from "Burger Log" to "Food Log"
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for food entries
        columns = ("Food", "Quantity", "Category", "Calories", "Kyle Tax")  # Added Category column
        self.tree = ttk.Treeview(log_frame, columns=columns, show="headings")
        
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
        
        # Add separator between buttons and progress section
        ttk.Separator(self.tracking_tab, orient='horizontal').pack(fill='x', padx=10, pady=5)
        
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
        
        # Add separator between date controls and exercise log
        ttk.Separator(exercise_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Exercise log
        log_frame = ttk.LabelFrame(exercise_frame, text="Exercise Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create treeview for exercise entries
        columns = ("Exercise", "Duration (min)", "Calories Burnt")
        self.exercise_tree = ttk.Treeview(log_frame, columns=columns, show="headings")
        
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
        
        # Add separator between buttons and summary
        ttk.Separator(exercise_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
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
        
        # Add separator between date controls and weight entry
        ttk.Separator(weight_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
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
        
        # Add separator between weight entry and history
        ttk.Separator(weight_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # History section
        history_frame = ttk.LabelFrame(weight_frame, text="Weight History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create treeview for weight entries
        columns = ("Date", "Weight (lb)")
        self.weight_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
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
        """Optimize loading weight history"""
        # Clear the weight treeview
        for item in self.weight_tree.get_children():
            self.weight_tree.delete(item)
            
        # Batch update
        self.weight_tree.update_idletasks()
        
        # Get all weight entries from history
        weights = []
        for date, data in self.history.items():
            if "weight" in data:
                weights.append((date, data["weight"]))
                
        # Sort by date (most recent first)
        weights.sort(reverse=True)
        
        # Add entries to weight treeview
        for date, weight in weights:
            self.weight_tree.insert("", "end", values=(date, weight))
    
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
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Chart options
        options_frame = ttk.LabelFrame(stats_frame, text="Chart Options")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.chart_type = tk.StringVar(value="weekly")
        
        charts = [
            ("Weekly Calories", "weekly"),
            ("Food Distribution", "distribution"),
            ("Food Types", "food_types"),
            ("Calories In/Out", "calories_io"),
            ("Weight Tracking", "weight"),
            ("Water Intake", "water")  # New water tracking chart option
        ]
        
        for i, (text, value) in enumerate(charts):
            ttk.Radiobutton(
                options_frame, 
                text=text, 
                value=value, 
                variable=self.chart_type,
                command=self.generate_chart
            ).grid(row=i // 3, column=i % 3, padx=10, pady=5, sticky="w")
        
        # Chart frame
        self.chart_frame = ttk.Frame(stats_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary stats
        summary_frame = ttk.LabelFrame(stats_frame, text="Summary Statistics")
        summary_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.stats_text = tk.Text(summary_frame, height=6, width=40, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.stats_text.config(state=tk.DISABLED)
        
        # Generate chart on startup
        self.generate_chart()
    
    def create_menu(self):
        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        
        # Add File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Export Report", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Add Edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Clear Today", command=self.clear_today)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        edit_menu.add_command(label="Delete History", command=self.delete_history)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        
        # Add View menu with themes
        view_menu = tk.Menu(menu_bar, tearoff=0)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme in self.theme_names:
            theme_menu.add_command(
                label=theme.capitalize(),
                command=lambda t=theme: self.change_theme(t)
            )
        view_menu.add_cascade(label="Theme", menu=theme_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Add Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Show Stats", command=self.show_stats)
        tools_menu.add_command(label="Show Weight Tracker", command=self.show_weight_tracker)
        tools_menu.add_command(label="Manage Custom Database", command=self.manage_custom_database)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        
        # Add Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Guide", command=self.show_guide)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        # Set the menu bar to the root window
        self.root.config(menu=menu_bar)
    
    def change_theme(self, theme_name):
        """Apply theme change with optimized performance"""
        # Set sv-ttk theme
        sv_ttk.set_theme(theme_name)
        
        # Update status bar
        self.status_var.set(f"Theme changed to {theme_name}")
        
        # Only regenerate chart if stats tab is visible
        if hasattr(self, 'notebook') and self.notebook.index('current') == 3:
            self.generate_chart()
    
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
        """Generate charts with optimization"""
        # Clear the current chart if it exists
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.get_tk_widget().destroy()
            plt.close('all')  # Close all existing matplotlib figures to prevent memory leaks
            
        # Create figure with optimized DPI settings
        chart_type = self.chart_type.get()
        fig = plt.figure(figsize=(10, 6), dpi=80)  # Lower DPI for better performance
        
        # Use tight_layout to optimize space
        fig.tight_layout(pad=3.0)
        
        # Create a single axis with optimized settings
        ax = fig.add_subplot(111)
        
        # Create different charts based on selection
        if chart_type == "weekly":
            self.create_weekly_chart(ax)
        elif chart_type == "distribution":
            self.create_distribution_chart(ax)
        elif chart_type == "food_types":
            self.create_food_types_chart(ax)
        elif chart_type == "calories_io":
            self.create_calories_in_out_chart(ax)
        elif chart_type == "weight":
            self.create_weight_tracking_chart(ax)
        elif chart_type == "water":
            self.create_water_tracking_chart(ax)
        
        # Create the canvas - use 'nearest' for faster image resampling
        self.canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        self.canvas.draw()
        
        # Pack the canvas but use fill and expand for better layout performance
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Update stats once after chart is drawn
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
        
        # Total tracking days
        total_days = len(self.history)
        
        # Total items logged
        food_entries = sum(len(data.get("food", [])) for data in self.history.values())
        exercise_entries = sum(len(data.get("exercise", [])) for data in self.history.values())
        water_entries = sum(len(data.get("water", [])) for data in self.history.values())
        
        # Total calories
        total_calories = 0
        total_burnt = 0
        total_water = 0
        
        for date, data in self.history.items():
            # Food calories
            for entry in data.get("food", []):
                calories = entry.get("calories", 0)
                if entry.get("kyle_tax", False):
                    calories = int(calories * 0.85)
                total_calories += calories
            
            # Exercise calories
            for entry in data.get("exercise", []):
                total_burnt += entry.get("calories_burnt", 0)
                
            # Water glasses
            for entry in data.get("water", []):
                total_water += entry.get("amount", 0)
        
        # Format stats
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        # Calculate averages
        avg_daily_calories = total_calories / total_days if total_days > 0 else 0
        avg_daily_burnt = total_burnt / total_days if total_days > 0 else 0
        avg_daily_water = total_water / total_days if total_days > 0 else 0
        
        # Calculate net
        net_calories = total_calories - total_burnt
        
        # Display stats
        stats = f"""• Total Days Tracked: {total_days}
• Total Food Items: {food_entries}
• Total Exercises: {exercise_entries}
• Total Water Entries: {water_entries}

• Average Daily Calories: {avg_daily_calories:.1f}
• Average Daily Calories Burnt: {avg_daily_burnt:.1f}
• Average Daily Water: {avg_daily_water:.1f} glasses

• Total Calories Consumed: {total_calories}
• Total Calories Burnt: {total_burnt}
• Net Calories: {net_calories}
• Total Water: {total_water:.1f} glasses"""
        
        self.stats_text.insert(tk.END, stats)
        self.stats_text.config(state=tk.DISABLED)
    
    def get_day_data(self, date_str):
        """Get food and exercise data for a specific day."""
        # If it's today and not in history, use today's entries
        if date_str == self.current_date and date_str not in self.history:
            return self.today_entries
        # Otherwise get from history
        return self.history.get(date_str, {"food": [], "exercise": [], "weight": None, "water": []})
    
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
            self.load_water_history()  # Also load water data for the new date
            
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
        self.load_water_history()  # Also load water data
        
        # Also update weight data for today
        if hasattr(self, 'weight_var'):
            day_data = self.get_day_data(self.current_date)
            current_weight = day_data.get("weight")
            
            if current_weight is not None:
                self.weight_var.set(str(current_weight))
            else:
                self.weight_var.set("")
    
    def load_entries(self):
        """Optimize loading entries into the treeview"""
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Get entries for the selected date
        day_data = self.get_day_data(self.date_var.get())
        food_entries = day_data.get("food", [])
        
        # Batch update with temporary detachment for better performance
        self.tree.update_idletasks()
        
        # Add entries to treeview
        for entry in food_entries:
            # Check if Kyle tax is applied
            kyle_tax = "Yes" if entry.get("kyle_tax", False) or self.kyle_tax_enabled.get() else "No"
            
            # Calculate calories with Kyle Tax if needed
            calories = entry["calories"]
            if kyle_tax == "Yes":
                display_calories = int(calories * 0.85)
            else:
                display_calories = calories
                
            # Get category
            category = entry.get("category", "Food")
            
            self.tree.insert(
                "", 
                "end", 
                values=(
                    entry["food"], 
                    entry["amount"], 
                    category,
                    display_calories,
                    kyle_tax
                )
            )
            
        # Update totals
        self.update_totals()
        
        # Update status bar
        self.status_var.set(f"Loaded entries for {self.date_var.get()}")
    
    def load_exercises(self):
        """Optimize loading exercises into the treeview"""
        # Clear the exercise treeview
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)
            
        # Get entries for the selected date
        day_data = self.get_day_data(self.date_var.get())
        exercise_entries = day_data.get("exercise", [])
        
        # Batch update
        self.exercise_tree.update_idletasks()
        
        # Add entries to exercise treeview
        for entry in exercise_entries:
            self.exercise_tree.insert(
                "", 
                "end", 
                values=(
                    entry["exercise"], 
                    entry["duration"], 
                    entry["calories_burnt"]
                )
            )
            
        # Update exercise summary
        self.update_exercise_summary(exercise_entries)
        
        # Update totals
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
        
        # Update progress bar color - use default sv-ttk styling
        if progress_pct < 75:
            # Using default progressbar style
            pass
        elif progress_pct < 100:
            # Using default progressbar style
            pass
        else:
            # Using default progressbar style
            pass
    
    def calculate_goal(self):
        try:
            return int(self.goal_var.get())
        except ValueError:
            return 2000
    
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
            text="Jacob Burger Tracker v1.6",  # Updated version
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
            text="• Modern UI\n• Track burgers, sides, and drinks\n• Exercise tracking\n• Kyle Tax\n• Calorie tracking\n• Data visualization\n• Custom food and exercise entries\n• Water tracking",
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
        """Debounced resize handler to prevent excessive updates"""
        # Only process events from the main window
        if event.widget != self.root:
            return
            
        # Cancel previous timer if it exists
        if self.resize_timer is not None:
            self.root.after_cancel(self.resize_timer)
            
        # Set a new timer for 150ms
        self.resize_timer = self.root.after(150, lambda: self.update_ui_for_resize(event.width, event.height))
    
    def update_ui_for_resize(self, width, height):
        """Apply UI updates after resize with optimized performance"""
        # Scale font sizes based on window dimensions
        base_size = min(max(int(width / 80), 8), 14)  # Limit font size between 8 and 14
        
        # Only update fonts if size changed
        if hasattr(self, '_last_font_size') and self._last_font_size == base_size:
            # Skip font updates if size hasn't changed
            pass
        else:
            # Update font configurations
            style = ttk.Style()
            style.configure("TButton", font=("Segoe UI", base_size))
            style.configure("TLabel", font=("Segoe UI", base_size))
            style.configure("Heading.TLabel", font=("Segoe UI", base_size + 2, "bold"))
            self._last_font_size = base_size
        
        # Update tree column widths efficiently
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
        
        # Only regenerate charts if on stats tab to avoid unnecessary processing
        if hasattr(self, 'notebook') and self.notebook.index('current') == 3:  # Stats tab index
            self.generate_chart()
    
    def on_tab_changed(self, event):
        # Refresh the current tab's content when tab is changed
        tab_id = self.notebook.select()
        tab_name = self.notebook.tab(tab_id, "text")
        
        if tab_name == "Daily Tracking":
            self.load_entries()
        elif tab_name == "Exercise Log":
            self.load_exercises()
        elif tab_name == "Weight Tracker":
            self.load_weight_history()
        elif tab_name == "Water Tracker":
            self.load_water_history()
        elif tab_name == "Statistics":
            self.generate_chart()
            self.update_stats_text()
    
    def show_weight_tracker(self):
        # Show the weight tracker tab
        self.notebook.select(2)  # Index 2 is the weight tab
    
    def show_calendar(self, parent_widget):
        """Optimized calendar implementation"""
        # Check if calendar already exists and is visible
        if hasattr(self, 'cal_window') and self.cal_window and self.cal_window.winfo_exists():
            # Just raise existing calendar window
            self.cal_window.focus_set()
            return
            
        # Create a toplevel window for the calendar
        self.cal_window = tk.Toplevel(self.root)
        self.cal_window.title("Date Selector")
        self.cal_window.geometry("320x300")
        self.cal_window.resizable(False, False)
        
        # Apply the same theme
        sv_ttk.set_theme(sv_ttk.get_theme())
        
        # Make dialog modal
        self.cal_window.transient(self.root)
        self.cal_window.grab_set()
        
        # Parse the current date
        try:
            current_date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
        except ValueError:
            current_date = datetime.datetime.now()
            
        # Set calendar variables
        self.cal_year = tk.IntVar(value=current_date.year)
        self.cal_month = tk.IntVar(value=current_date.month)
        self.cal_day = tk.IntVar(value=current_date.day)
        
        # Create header frame
        header_frame = ttk.Frame(self.cal_window)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Navigation buttons with optimal spacing
        ttk.Button(
            header_frame, 
            text="◄", 
            width=3,
            command=lambda: self.change_calendar_month(-1, self.cal_window)
        ).pack(side=tk.LEFT, padx=2)
        
        # Month and year label in the center
        self.month_year_label = ttk.Label(
            header_frame, 
            text=f"{calendar.month_name[self.cal_month.get()]} {self.cal_year.get()}",
            font=("Segoe UI", 12)
        )
        self.month_year_label.pack(side=tk.LEFT, expand=True, padx=10)
        
        ttk.Button(
            header_frame, 
            text="►", 
            width=3,
            command=lambda: self.change_calendar_month(1, self.cal_window)
        ).pack(side=tk.RIGHT, padx=2)
        
        # Weekday names, use abbreviated to save space
        days_frame = ttk.Frame(self.cal_window)
        days_frame.pack(fill=tk.X, padx=5)
        
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            ttk.Label(
                days_frame, 
                text=day, 
                width=5, 
                anchor="center",
                font=("Segoe UI", 9, "bold")
            ).grid(row=0, column=i, padx=1, pady=1)
            
        # Days grid
        self.days_frame = ttk.Frame(self.cal_window)
        self.days_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button frame at bottom
        button_frame = ttk.Frame(self.cal_window)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Button(
            button_frame, 
            text="Today",
            style="Info.TButton",
            command=lambda: [
                self.cal_day.set(datetime.datetime.now().day),
                self.cal_month.set(datetime.datetime.now().month),
                self.cal_year.set(datetime.datetime.now().year),
                self.update_calendar_days(self.cal_window),
                self.update_selected_date(self.cal_window)
            ]
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Select",
            style="Success.TButton",
            command=lambda: self.select_date_from_calendar(self.cal_window)
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel",
            style="Secondary.TButton",
            command=self.cal_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Fill the calendar with days
        self.update_calendar_days(self.cal_window)
        
        # Cleanup on window close
        self.cal_window.protocol("WM_DELETE_WINDOW", lambda: self._cleanup_calendar())
    
    def _cleanup_calendar(self):
        """Clean up calendar resources"""
        if hasattr(self, 'cal_window') and self.cal_window:
            self.cal_window.destroy()
            self.cal_window = None
    
    def update_calendar_days(self, cal_window):
        """Optimized calendar days rendering"""
        # Store button references to prevent garbage collection
        if not hasattr(self, 'day_buttons'):
            self.day_buttons = []
            
        # Clear existing day buttons
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        self.day_buttons = []
        
        # Get the number of days in the selected month
        year = self.cal_year.get()
        month = self.cal_month.get()
        
        # Get the first day of the month (0 = Monday, 6 = Sunday in the calendar module)
        first_day, num_days = calendar.monthrange(year, month)
        
        # Adjust for Sunday as first day of week (calendar.monthrange returns 0 for Monday)
        first_day = (first_day + 1) % 7
        
        # Update the month/year label
        self.month_year_label.config(text=f"{calendar.month_name[month]} {year}")
        
        # Create day buttons with minimal styling
        btn_style = ttk.Style()
        btn_style.configure("Cal.TButton", font=("Segoe UI", 9))
        
        # Cache today's date for comparison
        today = datetime.datetime.now()
        today_is_day = today.day
        today_is_month = today.month
        today_is_year = today.year
        
        # Cache selected date from data
        selected_date = self.date_var.get()
        try:
            selected_parts = selected_date.split('-')
            selected_year = int(selected_parts[0])
            selected_month = int(selected_parts[1])
            selected_day = int(selected_parts[2])
        except (ValueError, IndexError):
            selected_year, selected_month, selected_day = 0, 0, 0
            
        # Generate all buttons at once
        day = 1
        for row in range(6):  # 6 weeks max
            if day > num_days:
                break
                
            for col in range(7):  # 7 days per week
                if row == 0 and col < first_day:
                    # Empty cell before first day
                    spacer = ttk.Label(self.days_frame, text="", width=3)
                    spacer.grid(row=row, column=col, padx=1, pady=1)
                elif day <= num_days:
                    # Create the day button
                    btn = ttk.Button(
                        self.days_frame, 
                        text=str(day), 
                        width=3,
                        style="Cal.TButton",
                        command=lambda d=day: [
                            self.cal_day.set(d), 
                            self.update_selected_date(cal_window)
                        ]
                    )
                    
                    # Store reference
                    self.day_buttons.append(btn)
                    
                    # Highlight today
                    if day == today_is_day and month == today_is_month and year == today_is_year:
                        btn.configure(style="Primary.TButton")
                    
                    # Highlight selected day from calendar variables
                    elif day == self.cal_day.get() and month == self.cal_month.get() and year == self.cal_year.get():
                        btn.configure(style="Primary.TButton")
                        
                    # Check if there's data for this date
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    if date_str in self.history:
                        data = self.history[date_str]
                        has_food = len(data.get("food", [])) > 0
                        has_exercise = len(data.get("exercise", [])) > 0
                        
                        if has_food and has_exercise:
                            btn.configure(style="Success.TButton", text=f"{day}**")
                        elif has_food:
                            btn.configure(style="Success.TButton", text=f"{day}*")
                        elif has_exercise:
                            btn.configure(style="Info.TButton", text=f"{day}*")
                    
                    # Check if it matches the originally selected date
                    elif day == selected_day and month == selected_month and year == selected_year:
                        btn.configure(style="Success.TButton")
                        
                    btn.grid(row=row, column=col, padx=1, pady=1)
                    day += 1
    
    def update_selected_date(self, cal_window):
        """Update the selected_date attribute in the calendar window."""
        year = self.cal_year.get()
        month = self.cal_month.get()
        day = self.cal_day.get()
        cal_window.selected_date = f"{year}-{month:02d}-{day:02d}"
    
    def change_calendar_month(self, delta, cal_window):
        # Update the month and year when navigating
        month = self.cal_month.get() + delta
        year = self.cal_year.get()
        
        # Handle year change if needed
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        
        # Update the variables
        self.cal_month.set(month)
        self.cal_year.set(year)
        
        # Make sure the day is valid in the new month
        _, days_in_month = calendar.monthrange(year, month)
        if self.cal_day.get() > days_in_month:
            self.cal_day.set(days_in_month)
        
        # Update the calendar UI
        self.update_calendar_days(cal_window)
        
        # Update the selected_date attribute
        self.update_selected_date(cal_window)
    
    def select_date_from_calendar(self, cal_window):
        # Get the selected date from our custom calendar
        try:
            selected_date = cal_window.selected_date
            
            # Set the date
            self.date_var.set(selected_date)
            
            # Destroy the calendar window
            cal_window.destroy()
            
            # Load entries for the new date
            self.load_entries()
            self.load_exercises()
            self.load_water_history()
            
            # Also update weight data for the selected date
            if hasattr(self, 'weight_var'):
                day_data = self.get_day_data(selected_date)
                current_weight = day_data.get("weight")
                
                if current_weight is not None:
                    self.weight_var.set(str(current_weight))
                else:
                    self.weight_var.set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to select date: {e}")
    
    def setup_water_tab(self):
        # Water tracking tab main container
        water_frame = ttk.Frame(self.water_tab)
        water_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Upper controls - same date selector as in tracking tab
        control_frame = ttk.Frame(water_frame)
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
        date_entry.bind("<Return>", lambda e: self.load_water_history())
        
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
        
        # Goal setting frame
        goal_frame = ttk.LabelFrame(control_frame, text="Daily Water Goal")
        goal_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.X, expand=True)
        
        goal_controls = ttk.Frame(goal_frame)
        goal_controls.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Label(goal_controls, text="Goal (glasses):").pack(side=tk.LEFT, padx=5)
        
        water_goal_entry = ttk.Entry(goal_controls, textvariable=self.daily_water_goal, width=5)
        water_goal_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            goal_controls, 
            text="Set Goal", 
            style="Accent.TButton",
            command=self.set_water_goal
        ).pack(side=tk.LEFT, padx=5)
        
        # Add separator between controls and water tracking
        ttk.Separator(water_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Add water tracking UI
        tracking_frame = ttk.Frame(water_frame)
        tracking_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Quick add buttons
        quick_add_frame = ttk.LabelFrame(tracking_frame, text="Quick Add Water")
        quick_add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        quick_buttons_frame = ttk.Frame(quick_add_frame)
        quick_buttons_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Create a row of water glass buttons for quick adding
        for amount in [1, 2, 3]:
            btn = ttk.Button(
                quick_buttons_frame,
                text=f"{amount} Glass{'es' if amount > 1 else ''}",
                style="Info.TButton",
                command=lambda a=amount: self.add_water(a)
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Custom amount entry
        custom_frame = ttk.Frame(quick_buttons_frame)
        custom_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(custom_frame, text="Custom:").pack(side=tk.LEFT, padx=5)
        
        self.custom_water_var = tk.StringVar(value="1")
        custom_entry = ttk.Entry(custom_frame, textvariable=self.custom_water_var, width=5)
        custom_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            custom_frame,
            text="Add",
            style="Success.TButton",
            command=self.add_custom_water
        ).pack(side=tk.LEFT, padx=5)
        
        # Add separator between quick add and history
        ttk.Separator(water_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # Water progress visualization
        progress_frame = ttk.LabelFrame(water_frame, text="Today's Progress")
        progress_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Create a frame for the glasses visualization
        self.glasses_frame = ttk.Frame(progress_frame)
        self.glasses_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Progress bar for water intake
        self.water_progress_var = tk.DoubleVar(value=0)
        progress_bar_frame = ttk.Frame(progress_frame)
        progress_bar_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(progress_bar_frame, text="Progress:").pack(side=tk.LEFT, padx=5)
        
        self.water_progress_bar = ttk.Progressbar(
            progress_bar_frame,
            orient="horizontal",
            length=300,
            mode="determinate",
            variable=self.water_progress_var,
            style="info.Horizontal.TProgressbar"
        )
        self.water_progress_bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Summary labels
        self.water_summary_var = tk.StringVar(value="0 / 8 glasses consumed")
        self.water_percentage_var = tk.StringVar(value="0% of daily goal")
        
        summary_frame = ttk.Frame(progress_frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            summary_frame,
            textvariable=self.water_summary_var,
            font=("Segoe UI", 12, "bold")
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Label(
            summary_frame,
            textvariable=self.water_percentage_var,
            font=("Segoe UI", 12, "bold"),
            foreground="#5bc0de"  # Info blue color
        ).pack(side=tk.RIGHT, padx=10)
        
        # Add separator between progress and history
        ttk.Separator(water_frame, orient='horizontal').pack(fill='x', padx=5, pady=5)
        
        # History section
        history_frame = ttk.LabelFrame(water_frame, text="Water Intake History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create treeview for water entries
        columns = ("Time", "Amount (glasses)", "Notes")
        self.water_tree = ttk.Treeview(history_frame, columns=columns, show="headings", style="Treeview")
        
        # Define headings
        for col in columns:
            self.water_tree.heading(col, text=col)
        
        self.water_tree.column("Time", width=100)
        self.water_tree.column("Amount (glasses)", width=120)
        self.water_tree.column("Notes", width=200)
        
        # Add scrollbar
        water_scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.water_tree.yview)
        self.water_tree.configure(yscrollcommand=water_scrollbar.set)
        
        self.water_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        water_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame for water history
        water_button_frame = ttk.Frame(water_frame)
        water_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            water_button_frame,
            text="Delete Selected",
            style="Danger.TButton",
            command=self.delete_water
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            water_button_frame,
            text="Clear All",
            style="Warning.TButton",
            command=self.clear_all_water
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            water_button_frame,
            text="Add with Notes",
            style="Success.TButton",
            command=self.add_water_with_notes
        ).pack(side=tk.RIGHT, padx=5)
        
        # Load water history
        self.load_water_history()
    
    def set_water_goal(self):
        try:
            goal = int(self.daily_water_goal.get())
            if goal <= 0:
                messagebox.showerror("Error", "Goal must be a positive number")
                return
                
            # Update the progress display
            self.update_water_progress()
            
            # Update status
            self.status_var.set(f"Water goal set to {goal} glasses")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_water(self, amount):
        # Add water entry with current time
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        # Get selected date
        selected_date = self.date_var.get()
        
        # Create a new water entry
        water_entry = {
            "time": current_time,
            "amount": amount,
            "notes": ""
        }
        
        # Get the day data
        day_data = self.get_day_data(selected_date)
        
        # Initialize water list if not present
        if "water" not in day_data:
            day_data["water"] = []
        
        # Add the entry
        day_data["water"].append(water_entry)
        
        # Update history
        self.history[selected_date] = day_data
        
        # If it's today, update today_entries
        if selected_date == self.current_date:
            self.today_entries = day_data
        
        # Save to file
        self.save_history()
        
        # Refresh the water history
        self.load_water_history()
        
        # Update status
        self.status_var.set(f"Added {amount} glass{'es' if amount > 1 else ''} of water")
    
    def add_custom_water(self):
        try:
            amount = float(self.custom_water_var.get())
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be a positive number")
                return
                
            self.add_water(amount)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_water_with_notes(self):
        # Create a dialog for adding water with notes
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Water with Notes")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Apply the same theme
        dialog.tk.call("source", "azure.tcl")
        dialog.tk.call("set_theme", sv_ttk.get_theme())
        
        # Make dialog modal
        dialog.grab_set()
        dialog.focus_set()
        
        # Amount frame
        amount_frame = ttk.Frame(dialog, padding=10)
        amount_frame.pack(fill=tk.X)
        
        ttk.Label(amount_frame, text="Amount (glasses):").pack(side=tk.LEFT, padx=5)
        
        amount_var = tk.StringVar(value="1")
        amount_entry = ttk.Entry(amount_frame, textvariable=amount_var, width=5)
        amount_entry.pack(side=tk.LEFT, padx=5)
        
        # Notes frame
        notes_frame = ttk.Frame(dialog, padding=10)
        notes_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(notes_frame, text="Notes:").pack(anchor=tk.W, padx=5)
        
        notes_var = tk.StringVar()
        notes_entry = ttk.Entry(notes_frame, textvariable=notes_var, width=40)
        notes_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Suggestions frame
        suggestions_frame = ttk.LabelFrame(dialog, text="Quick Notes", padding=10)
        suggestions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Common notes suggestions
        suggestions = ["Morning hydration", "With meal", "After workout", "Before bed"]
        
        for suggestion in suggestions:
            btn = ttk.Button(
                suggestions_frame,
                text=suggestion,
                command=lambda s=suggestion: notes_var.set(s)
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Button frame
        button_frame = ttk.Frame(dialog, padding=10)
        button_frame.pack(fill=tk.X)
        
        def save_water_entry():
            try:
                amount = float(amount_var.get())
                notes = notes_var.get()
                
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be a positive number")
                    return
                
                # Current time
                current_time = datetime.datetime.now().strftime("%H:%M")
                
                # Get selected date
                selected_date = self.date_var.get()
                
                # Create the water entry
                water_entry = {
                    "time": current_time,
                    "amount": amount,
                    "notes": notes
                }
                
                # Get the day data
                day_data = self.get_day_data(selected_date)
                
                # Initialize water list if not present
                if "water" not in day_data:
                    day_data["water"] = []
                
                # Add the entry
                day_data["water"].append(water_entry)
                
                # Update history
                self.history[selected_date] = day_data
                
                # If it's today, update today_entries
                if selected_date == self.current_date:
                    self.today_entries = day_data
                
                # Save to file
                self.save_history()
                
                # Close the dialog
                dialog.destroy()
                
                # Refresh the water history
                self.load_water_history()
                
                # Update status
                self.status_var.set(f"Added {amount} glass{'es' if amount > 1 else ''} of water with notes")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for amount")
        
        ttk.Button(
            button_frame,
            text="Cancel",
            style="Secondary.TButton",
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Save",
            style="Success.TButton",
            command=save_water_entry
        ).pack(side=tk.RIGHT, padx=5)
        
        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def delete_water(self):
        # Get selected item
        selected = self.water_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a water entry to delete")
            return
        
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Delete selected water entry?"):
            return
        
        # Get the selected date
        selected_date = self.date_var.get()
        day_data = self.get_day_data(selected_date)
        
        # Get the index to delete (based on the row selection)
        idx = self.water_tree.index(selected[0])
        
        # Remove the entry
        if 0 <= idx < len(day_data.get("water", [])):
            day_data["water"].pop(idx)
            
            # Update history
            self.history[selected_date] = day_data
            
            # If it's today, update today_entries
            if selected_date == self.current_date:
                self.today_entries = day_data
            
            # Save to file
            self.save_history()
            
            # Refresh the display
            self.load_water_history()
            
            # Update status
            self.status_var.set("Water entry deleted")
        else:
            messagebox.showerror("Error", "Failed to delete entry")
    
    def clear_all_water(self):
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Clear all water entries for this date?"):
            return
        
        # Get the selected date
        selected_date = self.date_var.get()
        day_data = self.get_day_data(selected_date)
        
        # Clear water entries
        day_data["water"] = []
        
        # Update history
        self.history[selected_date] = day_data
        
        # If it's today, update today_entries
        if selected_date == self.current_date:
            self.today_entries = day_data
        
        # Save to file
        self.save_history()
        
        # Refresh the display
        self.load_water_history()
        
        # Update status
        self.status_var.set("All water entries cleared")
    
    def load_water_history(self):
        """Optimize loading water history"""
        # Clear the water treeview
        for item in self.water_tree.get_children():
            self.water_tree.delete(item)
            
        # Batch update
        self.water_tree.update_idletasks()
        
        # Get entries for the selected date
        day_data = self.get_day_data(self.date_var.get())
        water_entries = day_data.get("water", [])
        
        # Add entries to treeview
        for entry in water_entries:
            self.water_tree.insert(
                "", 
                "end", 
                values=(
                    entry["time"], 
                    entry["amount"], 
                    entry.get("notes", "")
                )
            )
        
        # Update water progress
        self.update_water_progress()
    
    def update_water_progress(self):
        # Get selected date
        selected_date = self.date_var.get()
        
        # Get data for the selected date
        day_data = self.get_day_data(selected_date)
        water_entries = day_data.get("water", [])
        
        # Calculate total glasses
        total_glasses = sum(entry["amount"] for entry in water_entries)
        
        # Get the goal
        try:
            goal = int(self.daily_water_goal.get())
        except ValueError:
            goal = 8  # Default goal
        
        # Calculate percentage
        percentage = min(100, (total_glasses / goal * 100) if goal > 0 else 0)
        
        # Update the progress bar
        self.water_progress_var.set(percentage)
        
        # Update summary text
        self.water_summary_var.set(f"{total_glasses:.1f} / {goal} glasses consumed")
        self.water_percentage_var.set(f"{percentage:.1f}% of daily goal")
        
        # Update the glasses visualization
        self.update_glasses_visualization(total_glasses, goal)
    
    def update_glasses_visualization(self, total, goal):
        # Clear the glasses frame
        for widget in self.glasses_frame.winfo_children():
            widget.destroy()
        
        # Calculate how many full and empty glasses to show
        full_glasses = int(total)
        partial_glass = total - full_glasses
        empty_glasses = max(0, goal - full_glasses - (1 if partial_glass > 0 else 0))
        
        # Create full glasses
        for i in range(full_glasses):
            if i < 10:  # Only show max 10 to prevent overflow
                ttk.Label(self.glasses_frame, text="🥛", font=("Segoe UI Emoji", 24)).pack(side=tk.LEFT, padx=2)
        
        # Create partial glass if needed
        if partial_glass > 0 and full_glasses < 10:
            ttk.Label(self.glasses_frame, text="🥛", font=("Segoe UI Emoji", 20)).pack(side=tk.LEFT, padx=2)
        
        # Create empty glasses
        for i in range(empty_glasses):
            if full_glasses + i < 10:  # Only show max 10 to prevent overflow
                ttk.Label(self.glasses_frame, text="⚪", font=("Segoe UI Emoji", 24)).pack(side=tk.LEFT, padx=2)
    
    def create_water_tracking_chart(self, ax):
        # Get water entries from the last 7 days
        today = datetime.datetime.now().date()
        dates = []
        water_amounts = []
        
        for i in range(6, -1, -1):  # Last 7 days, from oldest to newest
            date = today - datetime.timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            dates.append(date.strftime("%m-%d"))  # Short date format for x-axis
            
            # Get water data for this date
            day_data = self.get_day_data(date_str)
            water_entries = day_data.get("water", [])
            
            # Sum all water intake for this day
            total_water = sum(entry["amount"] for entry in water_entries)
            water_amounts.append(total_water)
        
        # Plot the water intake
        bars = ax.bar(dates, water_amounts, color='#5bc0de')
        
        # Add data labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height + 0.1, 
                f'{height:.1f}', 
                ha='center', 
                va='bottom',
                color='white'
            )
        
        # Get the goal for reference line
        try:
            goal = int(self.daily_water_goal.get())
        except ValueError:
            goal = 8  # Default goal
        
        # Add a horizontal line for the daily goal
        ax.axhline(y=goal, color='r', linestyle='--', alpha=0.7, label=f'Daily Goal ({goal} glasses)')
        
        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Glasses of Water')
        ax.set_title('Water Intake - Last 7 Days')
        
        # Add legend
        ax.legend()
        
        # Set y-axis to start at 0
        ax.set_ylim(bottom=0)
        
        # Adjust grid for better readability
        ax.grid(axis='y', alpha=0.3)
    
    def _initialize_theme(self):
        """Initialize sv-ttk theme settings once at startup"""
        # Apply sv-ttk theme
        sv_ttk.set_theme("dark")
        
        # Preload both themes to avoid lag when switching
        self.root.after(100, lambda: sv_ttk.set_theme("light"))
        self.root.after(200, lambda: sv_ttk.set_theme("dark"))
        
        # Cache for chart data to avoid frequent recomputation
        self._chart_cache = {}
        
        # Optimize matplotlib for better performance
        plt.rcParams['figure.dpi'] = 80
        plt.rcParams['savefig.dpi'] = 80
        plt.rcParams['path.simplify'] = True
        plt.rcParams['path.simplify_threshold'] = 1.0
        plt.rcParams['agg.path.chunksize'] = 10000
    
    def change_theme(self, theme_name):
        """Apply theme change with optimized performance"""
        # Set sv-ttk theme
        sv_ttk.set_theme(theme_name)
        
        # Update status bar
        self.status_var.set(f"Theme changed to {theme_name}")
        
        # Only regenerate chart if stats tab is visible
        if hasattr(self, 'notebook') and self.notebook.index('current') == 3:
            self.generate_chart()
    
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
