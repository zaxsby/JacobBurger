import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os
import json

class BurgerTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Jacob Burger Tracker")
        self.root.geometry("700x500")
        
        # ASCII art for the app
        self.ascii_art = """
       ▐▄▄▄ ▄▄▄·  ▄▄·       ▄▄▄▄·     ▄▄▄▄· ▄• ▄▌▄▄▄   ▄▄ • ▄▄▄ .▄▄▄          
        ·██▐█ ▀█ ▐█ ▌▪▪     ▐█ ▀█▪    ▐█ ▀█▪█▪██▌▀▄ █·▐█ ▀ ▪▀▄.▀·▀▄ █·        
      ▪▄ ██▄█▀▀█ ██ ▄▄ ▄█▀▄ ▐█▀▀█▄    ▐█▀▀█▄█▌▐█▌▐▀▀▄ ▄█ ▀█▄▐▀▀▪▄▐▀▀▄         
      ▐▌▐█▌▐█ ▪▐▌▐███▌▐█▌.▐▌██▄▪▐█    ██▄▪▐█▐█▄█▌▐█•█▌▐█▄▪▐█▐█▄▄▌▐█•█▌        
       ▀▀▀• ▀  ▀ ·▀▀▀  ▀█▄▀▪·▀▀▀▀     ·▀▀▀▀  ▀▀▀ .▀  ▀·▀▀▀▀  ▀▀▀ .▀  ▀        
                ▄▄▄▄▄▄▄▄   ▄▄▄·  ▄▄· ▄ •▄ ▄▄▄ .▄▄▄                      
                •██  ▀▄ █·▐█ ▀█ ▐█ ▌▪█▌▄▌▪▀▄.▀·▀▄ █·                    
                 ▐█.▪▐▀▀▄ ▄█▀▀█ ██ ▄▄▐▀▀▄·▐▀▀▪▄▐▀▀▄                     
                 ▐█▌·▐█•█▌▐█ ▪▐▌▐███▌▐█.█▌▐█▄▄▌▐█•█▌                    
                 ▀▀▀ .▀  ▀ ▀  ▀ ·▀▀▀ ·▀  ▀ ▀▀▀ .▀  ▀                          
        """
        
        # Simple food database
        self.food_database = {
            "Single Patty Burger": 500,
            "Double Patty Burger": 700,
            "Single Patty Cheeseburger": 775,
            "Double Patty Cheeseburger": 850,
            "Big Smasher Burger": 1500,
            "Floyd Burger": 1000,
            "Beef Tallow Fries": 800,
            "Southwestern Eggrolls": 1200,
            "The Biggest Burger": 10000,
            "Iftar Burger": 3000,
        }
        
        # Data file for saving history
        self.data_file = "burger_tracker_data.json"
        
        # History by date
        self.history = self.load_history()
        
        # Today's date string
        self.current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Today's entries
        self.today_entries = self.history.get(self.current_date, [])
        
        # Create menu
        self.create_menu()
        
        # Create the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a label
        ttk.Label(
            main_frame, 
            text="Jacob Burger Tracker", 
            font=("Arial", 16, "bold")
        ).pack(pady=10)
        
        # Create date selection
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        
        self.date_var = tk.StringVar(value=self.current_date)
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
        date_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            date_frame, 
            text="←", 
            width=2,
            command=lambda: self.change_date(-1)
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            date_frame, 
            text="Today", 
            command=self.go_to_today
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            date_frame, 
            text="→", 
            width=2,
            command=lambda: self.change_date(1)
        ).pack(side=tk.LEFT)
        
        # Calorie goal
        goal_frame = ttk.Frame(main_frame)
        goal_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(goal_frame, text="Daily Calorie Goal:").pack(side=tk.LEFT, padx=5)
        
        self.goal_var = tk.StringVar(value="2000")
        goal_entry = ttk.Entry(goal_frame, textvariable=self.goal_var, width=8)
        goal_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            goal_frame, 
            text="Set Goal", 
            command=self.set_goal
        ).pack(side=tk.LEFT, padx=5)
        
        # Create the food log frame
        log_frame = ttk.LabelFrame(main_frame, text="Burger Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview for food entries
        columns = ("Food", "Quantity", "Calories")
        self.tree = ttk.Treeview(log_frame, columns=columns, show="headings")
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column("Food", width=200)
        self.tree.column("Quantity", width=100)
        self.tree.column("Calories", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Add buttons
        ttk.Button(
            button_frame, 
            text="Add Burger", 
            command=self.add_food
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Delete Selected", 
            command=self.delete_food
        ).pack(side="left", padx=5)
        
        ttk.Button(
            button_frame, 
            text="Clear All", 
            command=self.clear_all
        ).pack(side="left", padx=5)
        
        # Total calories display and remaining
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.total_var = tk.StringVar(value="Total Calories: 0")
        self.remaining_var = tk.StringVar(value="Remaining: 2000")
        
        ttk.Label(
            stats_frame, 
            textvariable=self.total_var,
            font=("Arial", 12, "bold")
        ).pack(side="left", padx=20)
        
        ttk.Label(
            stats_frame, 
            textvariable=self.remaining_var,
            font=("Arial", 12, "bold")
        ).pack(side="right", padx=20)
        
        # Load today's entries
        self.load_entries()
    
    def create_menu(self):
        # Create a menu bar
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # Create File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Data", command=self.save_history)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Create Tools menu
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Today's Log", command=self.clear_today)
        tools_menu.add_command(label="Delete All History", command=self.delete_history)
        tools_menu.add_separator()
        tools_menu.add_command(label="Burger Statistics", command=self.show_stats)
        
        # Create Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def load_history(self):
        # Load history from file
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    return json.load(f)
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
            messagebox.showinfo("Success", "Data saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save history: {e}")
    
    def change_date(self, days):
        # Change the selected date
        try:
            date = datetime.datetime.strptime(self.date_var.get(), "%Y-%m-%d")
            new_date = date + datetime.timedelta(days=days)
            self.date_var.set(new_date.strftime("%Y-%m-%d"))
            self.load_entries()
        except ValueError:
            self.go_to_today()
    
    def go_to_today(self):
        # Set date to today
        self.date_var.set(self.current_date)
        self.load_entries()
    
    def load_entries(self):
        # Clear the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get selected date
        selected_date = self.date_var.get()
        
        # If it's today, use today_entries
        if selected_date == self.current_date:
            entries = self.today_entries
        else:
            # Otherwise load from history
            entries = self.history.get(selected_date, [])
        
        # Add entries to treeview
        for entry in entries:
            self.tree.insert("", "end", values=(
                entry["food"],
                entry["amount"],
                entry["calories"]
            ))
        
        # Update totals
        self.update_totals(entries)
    
    def update_totals(self, entries=None):
        if entries is None:
            if self.date_var.get() == self.current_date:
                entries = self.today_entries
            else:
                entries = self.history.get(self.date_var.get(), [])
        
        # Calculate total calories
        total = sum(entry["calories"] for entry in entries)
        
        # Update display
        self.total_var.set(f"Total Calories: {total}")
        
        # Get goal
        try:
            goal = int(self.goal_var.get())
        except ValueError:
            goal = 2000
        
        # Update remaining
        remaining = max(0, goal - total)
        self.remaining_var.set(f"Remaining: {remaining}")
    
    def set_goal(self):
        try:
            goal = int(self.goal_var.get())
            if goal <= 0:
                messagebox.showerror("Error", "Goal must be positive")
                return
            
            # Update display
            self.update_totals()
            messagebox.showinfo("Success", f"Calorie goal set to {goal}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
    
    def add_food(self):
        # Create a simple dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Burger")
        dialog.geometry("350x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Form fields
        ttk.Label(dialog, text="Select Burger:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Combobox with food options
        food_options = list(self.food_database.keys())
        food_var = tk.StringVar()
        food_combo = ttk.Combobox(dialog, textvariable=food_var, values=food_options, width=25)
        food_combo.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(dialog, text="Quantity:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        amount_var = tk.StringVar(value="1")
        ttk.Entry(dialog, textvariable=amount_var, width=10).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Preview calories
        ttk.Label(dialog, text="Calories:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        calories_var = tk.StringVar(value="0")
        ttk.Label(dialog, textvariable=calories_var).grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Update calories when food or amount changes
        def update_calories(*args):
            food = food_var.get()
            try:
                amount = float(amount_var.get())
                if food in self.food_database:
                    cal = self.food_database[food] * amount
                    calories_var.set(str(int(cal)))
                else:
                    calories_var.set("0")
            except ValueError:
                calories_var.set("0")
        
        food_var.trace_add("write", update_calories)
        amount_var.trace_add("write", update_calories)
        
        # Buttons
        def save_entry():
            food = food_var.get()
            try:
                amount = float(amount_var.get())
                if food and food in self.food_database and amount > 0:
                    calories = self.food_database[food] * amount
                    
                    # Add to tree
                    self.tree.insert("", "end", values=(
                        food,
                        f"{amount:.1f}",
                        f"{int(calories)}"
                    ))
                    
                    # Add to entries if it's today
                    if self.date_var.get() == self.current_date:
                        self.today_entries.append({
                            "food": food,
                            "amount": amount,
                            "calories": int(calories)
                        })
                    else:
                        # Add to history for selected date
                        selected_date = self.date_var.get()
                        if selected_date not in self.history:
                            self.history[selected_date] = []
                        
                        self.history[selected_date].append({
                            "food": food,
                            "amount": amount,
                            "calories": int(calories)
                        })
                    
                    # Update total
                    self.update_totals()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Please select a valid food and amount")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
        
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Add", command=save_entry).pack(side="left", padx=10)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=10)
    
    def delete_food(self):
        # Get selected item
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select an entry to delete")
            return
        
        # Get selected date
        selected_date = self.date_var.get()
        is_today = selected_date == self.current_date
        
        # Get entries
        entries = self.today_entries if is_today else self.history.get(selected_date, [])
        
        # Build new list without deleted items
        new_entries = []
        deleted_indices = []
        
        for item in selected:
            idx = self.tree.index(item)
            deleted_indices.append(idx)
        
        for i, entry in enumerate(entries):
            if i not in deleted_indices:
                new_entries.append(entry)
        
        # Update entries
        if is_today:
            self.today_entries = new_entries
        else:
            self.history[selected_date] = new_entries
        
        # Remove from tree
        for item in selected:
            self.tree.delete(item)
        
        # Update totals
        self.update_totals(new_entries)
    
    def clear_all(self):
        # Ask for confirmation
        if not messagebox.askyesno("Confirm", "Clear all entries for this date?"):
            return
        
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Clear entries
        selected_date = self.date_var.get()
        if selected_date == self.current_date:
            self.today_entries = []
        else:
            self.history[selected_date] = []
        
        # Update totals
        self.update_totals([])
    
    def clear_today(self):
        # Clear today's entries
        if not messagebox.askyesno("Confirm", "Clear all entries for today?"):
            return
        
        self.today_entries = []
        
        # If today is selected, update display
        if self.date_var.get() == self.current_date:
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.update_totals([])
    
    def delete_history(self):
        # Delete all history
        if not messagebox.askyesno("Confirm", "Delete ALL history data? This cannot be undone!"):
            return
        
        self.history = {}
        self.today_entries = []
        
        # Update display
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.update_totals([])
        
        messagebox.showinfo("Success", "All history has been deleted")
    
    def show_stats(self):
        # Show statistics
        if not self.history:
            messagebox.showinfo("Statistics", "No data available for statistics")
            return
        
        # Calculate stats
        total_burgers = 0
        total_calories = 0
        biggest_day = (None, 0)
        
        for date, entries in self.history.items():
            day_calories = sum(entry["calories"] for entry in entries)
            day_burgers = sum(entry["amount"] for entry in entries)
            
            total_burgers += day_burgers
            total_calories += day_calories
            
            if day_calories > biggest_day[1]:
                biggest_day = (date, day_calories)
        
        # Include today's entries if not already in history
        if self.current_date not in self.history and self.today_entries:
            today_calories = sum(entry["calories"] for entry in self.today_entries)
            today_burgers = sum(entry["amount"] for entry in self.today_entries)
            
            total_burgers += today_burgers
            total_calories += today_calories
            
            if today_calories > biggest_day[1]:
                biggest_day = (self.current_date, today_calories)
        
        # Create stats window
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Burger Stats")
        stats_window.geometry("400x300")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Add stats
        ttk.Label(
            stats_window, 
            text="Burger Stats", 
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        stats_frame = ttk.Frame(stats_window, padding=20)
        stats_frame.pack(fill="both", expand=True)
        
        ttk.Label(
            stats_frame, 
            text=f"Total Burgers Consumed: {total_burgers:.1f}",
            font=("Arial", 12)
        ).pack(anchor="w", pady=5)
        
        ttk.Label(
            stats_frame, 
            text=f"Total Calories Consumed: {total_calories:,}",
            font=("Arial", 12)
        ).pack(anchor="w", pady=5)
        
        if biggest_day[0]:
            ttk.Label(
                stats_frame, 
                text=f"Biggest Day: {biggest_day[0]} ({biggest_day[1]:,} calories)",
                font=("Arial", 12)
            ).pack(anchor="w", pady=5)
        
        # Close button
        ttk.Button(
            stats_window, 
            text="Close", 
            command=stats_window.destroy
        ).pack(pady=20)
    
    def show_about(self):
        # Show about dialog
        about_window = tk.Toplevel(self.root)
        about_window.title("Chaka")
        about_window.geometry("600x400")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Display ASCII art
        ascii_label = tk.Label(about_window, text=self.ascii_art, font=("Courier", 10), justify="left")
        ascii_label.pack(pady=20)
        
        # About text
        about_text = tk.Label(
            about_window, 
            text="Jacob Burger Tracker v1.0\nCreated by Chaka and Draco", 
            font=("Arial", 14)
        )
        about_text.pack(pady=10)
        
        # Additional info
        info_text = tk.Label(
            about_window, 
            text="southwestern egg rolls and a big smasher burger meal\nNo, I want steak and shake", 
            font=("Arial", 12)
        )
        info_text.pack(pady=10)
        
        # Close button
        ttk.Button(
            about_window, 
            text="Close", 
            command=about_window.destroy
        ).pack(pady=20)

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
