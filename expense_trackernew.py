"""
STUDENT EXPENSE TRACKER
-----------------------
A simple console program that helps a student record daily expenses,
set a monthly budget, and see where the money is going.


"""

from datetime import date

DATA_FILE = "expenses.txt"
BUDGET_FILE = "budget.txt"


ESSENTIAL_CATEGORIES = ("Food", "Travel", "Study", "Rent")
LEISURE_CATEGORIES = ("Entertainment", "Shopping", "Other")
ALL_CATEGORIES = ESSENTIAL_CATEGORIES + LEISURE_CATEGORIES



class InvalidAmountError(Exception):
   
    pass



class Expense:
   

    def __init__(self, amount, category, description, exp_date=None):
        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero.")
        self.amount = amount
        self.category = category
        self.description = description
        if exp_date is None:
            exp_date = str(date.today())
        self.date = exp_date

    def expense_type(self):
        return "General"

    def to_line(self):
        
        return f"{self.date}|{self.category}|{self.description}|{self.amount}"

    def __str__(self):
        return (f"{self.date} | {self.category:<13} | {self.description:<20} | "
                f"Rs. {self.amount:>8.2f} | {self.expense_type()}")


class EssentialExpense(Expense):
   

    def expense_type(self):          
        return "Essential"


class LeisureExpense(Expense):
   

    def expense_type(self):          
        return "Leisure"


def create_expense(amount, category, description, exp_date=None):
   
    if category in ESSENTIAL_CATEGORIES:
        return EssentialExpense(amount, category, description, exp_date)
    return LeisureExpense(amount, category, description, exp_date)


class ExpenseTracker:
    
    def __init__(self):
        self.expenses = []     
        self.budget = 0.0
        self.load_data()

    
    def load_data(self):
        try:
            file = open(DATA_FILE, "r")
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split("|")
                exp = create_expense(float(parts[3]), parts[1], parts[2], parts[0])
                self.expenses.append(exp)
            file.close()
        except FileNotFoundError:
            pass   
        except (ValueError, IndexError):
            print("Warning: some data in the file was damaged and was skipped.")

        try:
            file = open(BUDGET_FILE, "r")
            self.budget = float(file.read().strip())
            file.close()
        except (FileNotFoundError, ValueError):
            self.budget = 0.0

    def save_data(self):
        file = open(DATA_FILE, "w")
        for exp in self.expenses:
            file.write(exp.to_line() + "\n")
        file.close()

        file = open(BUDGET_FILE, "w")
        file.write(str(self.budget))
        file.close()

    
    def add_expense(self, amount, category, description):
        exp = create_expense(amount, category, description)
        self.expenses.append(exp)
        self.save_data()

    def delete_expense(self, number):
        removed = self.expenses.pop(number - 1)
        self.save_data()
        return removed

    def set_budget(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Budget must be greater than zero.")
        self.budget = amount
        self.save_data()

    def total_spent(self):
        total = 0
        for exp in self.expenses:
            total += exp.amount
        return total

    def category_summary(self):
        
        summary = {}
        for exp in self.expenses:
            summary[exp.category] = summary.get(exp.category, 0) + exp.amount
        return summary

    def type_summary(self):
        
        summary = {"Essential": 0, "Leisure": 0}
        for exp in self.expenses:
            summary[exp.expense_type()] += exp.amount
        return summary



def show_menu():
    print("\n" + "=" * 40)
    print("     STUDENT EXPENSE TRACKER")
    print("=" * 40)
    print("1. Add an expense")
    print("2. View all expenses")
    print("3. View category-wise summary")
    print("4. Set monthly budget")
    print("5. Check budget status")
    print("6. Show highest expenses")
    print("7. Delete an expense")
    print("8. Exit")


def choose_category():
    print("\nCategories:")
    for i, cat in enumerate(ALL_CATEGORIES, 1):
        print(f"  {i}. {cat}")
    choice = int(input("Choose category number: "))
    if choice < 1 or choice > len(ALL_CATEGORIES):
        raise ValueError("Category number out of range")
    return ALL_CATEGORIES[choice - 1]


def add_expense_screen(tracker):
    try:
        category = choose_category()
        description = input("Description (e.g. Lunch, Bus pass): ").strip()
        description = description.replace("|", "-")   
        if description == "":
            description = "No description"
        amount = float(input("Amount (Rs.): "))
        tracker.add_expense(amount, category, description)
        print("Expense added successfully!")
    except InvalidAmountError as e:
        print("Error:", e)
    except ValueError:
        print("Invalid input! Please enter numbers where required.")


def view_all_screen(tracker):
    if len(tracker.expenses) == 0:
        print("\nNo expenses recorded yet.")
        return
    print("\n" + "-" * 80)
    print(f"{'No.':<4}{'Date':<10} | {'Category':<13} | {'Description':<20} | "
          f"{'Amount':<12} | Type")
    print("-" * 80)
    for i, exp in enumerate(tracker.expenses, 1):
        print(f"{i:<4}{exp}")
    print("-" * 80)
    print(f"Total spent: Rs. {tracker.total_spent():.2f}")


def summary_screen(tracker):
    if len(tracker.expenses) == 0:
        print("\nNo expenses recorded yet.")
        return
    total = tracker.total_spent()
    print("\n--- Category-wise Summary ---")
    summary = tracker.category_summary()
    for cat in summary:
        percent = summary[cat] / total * 100
        print(f"{cat:<15} Rs. {summary[cat]:>9.2f}  ({percent:.1f}%)")

    print("\n--- Essential vs Leisure ---")
    types = tracker.type_summary()
    for name, amt in types.items():
        print(f"{name:<15} Rs. {amt:>9.2f}")


def budget_screen(tracker):
    if tracker.budget == 0:
        print("\nYou have not set a budget yet. Choose option 4 first.")
        return
    spent = tracker.total_spent()
    remaining = tracker.budget - spent
    print(f"\nBudget      : Rs. {tracker.budget:.2f}")
    print(f"Spent       : Rs. {spent:.2f}")
    if remaining >= 0:
        print(f"Remaining   : Rs. {remaining:.2f}")
        used = spent / tracker.budget * 100
        if used >= 80:
            print(f"Careful! You have used {used:.1f}% of your budget.")
        else:
            print(f"Good going! You have used {used:.1f}% of your budget.")
    else:
        print(f"You have crossed your budget by Rs. {-remaining:.2f}!")


def top_expenses_screen(tracker):
    if len(tracker.expenses) == 0:
        print("\nNo expenses recorded yet.")
        return
    
    top = sorted(tracker.expenses, key=lambda e: e.amount, reverse=True)[:3]
    print("\n--- Top 3 Highest Expenses ---")
    for exp in top:
        print(exp)


def delete_screen(tracker):
    view_all_screen(tracker)
    if len(tracker.expenses) == 0:
        return
    try:
        number = int(input("\nEnter the number of the expense to delete: "))
        if number < 1 or number > len(tracker.expenses):
            print("There is no expense with that number.")
            return
        removed = tracker.delete_expense(number)
        print(f"Deleted: {removed.description} (Rs. {removed.amount:.2f})")
    except ValueError:
        print("Invalid input! Please enter a number.")



def main():
    tracker = ExpenseTracker()
    print("Welcome to the Student Expense Tracker!")

    while True:
        show_menu()
        choice = input("Enter your choice (1-8): ").strip()

        if choice == "1":
            add_expense_screen(tracker)
        elif choice == "2":
            view_all_screen(tracker)
        elif choice == "3":
            summary_screen(tracker)
        elif choice == "4":
            try:
                amount = float(input("Enter your monthly budget (Rs.): "))
                tracker.set_budget(amount)
                print("Budget saved!")
            except InvalidAmountError as e:
                print("Error:", e)
            except ValueError:
                print("Invalid input! Please enter a number.")
        elif choice == "5":
            budget_screen(tracker)
        elif choice == "6":
            top_expenses_screen(tracker)
        elif choice == "7":
            delete_screen(tracker)
        elif choice == "8":
            print("Thank you for using the Expense Tracker. Bye!")
            break
        else:
            print("Invalid choice! Please enter a number from 1 to 8.")


if __name__ == "__main__":
    main()
