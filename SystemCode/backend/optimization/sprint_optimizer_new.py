from pulp import *
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime, timedelta
import collections

# Assume a default daily capacity if not specified for a developer/day
DEFAULT_DAILY_CAPACITY = 8.0 # Points or hours equivalent per developer per working day

# A large number for Big M constraints - must be larger than any possible sum it's used with
# For precedence, it needs to be larger than max task points.
BIG_M = 1000.0

class SprintOptimizer:
    def __init__(self):
        self.problem = None
        self.task_vars = {}        # y_t
        self.assignment_vars = {}  # x_ta
        self.work_vars = {}        # w_tad (Binary: developer a works on task t on day d)
        self.points_vars = {}      # p_tad (Continuous: points of task t worked by a on day d)
        self._tasks = []
        self._developers = []
        self._days = [] # List of working days (YYYY-MM-DD strings)
        self._task_points = {}
        self._developer_total_capacity = {} # Total sprint capacity (can be derived from daily, but useful to store)
        self._developer_daily_capacity = {} # Daily capacity per developer per day {dev: {day: capacity}}
        self._task_dependencies = {}
        self._task_priorities = {}

    def create_optimization_model(
        self,
        tasks: List[str],
        developers: List[str],
        task_priorities: Dict[str, int],
        task_points: Dict[str, float],
        developer_total_capacity: Dict[str, float], # This is total sprint capacity (optional if daily is provided)
        task_dependencies: Dict[str, List[str]],
        task_skills: Dict[str, List[str]],
        developer_skills: Dict[str, List[str]],
        sprint_start_date: str,
        sprint_end_date: str,
        # NEW: developer_daily_capacity is now required and detailed per day
        developer_daily_capacity: Dict[str, Dict[str, float]]
    ) -> None:
        """
        Create the MILP optimization model for sprint planning, including
        task selection, assignment, and daily scheduling with dependencies.
        Accepts detailed daily capacity per developer per day.
        """
        print("Creating time-aware optimization model with integrated scheduling and detailed daily capacity...")

        # Store inputs for later use in summary
        self._tasks = tasks
        self._developers = developers
        self._task_priorities = task_priorities
        self._task_points = task_points
        self._developer_total_capacity = developer_total_capacity # Store total capacity as well
        self._task_dependencies = task_dependencies

        # Determine working days based on sprint dates
        self._days = self._get_working_days_list(sprint_start_date, sprint_end_date)
        if not self._days:
            raise ValueError("No working days found in the specified sprint range.")
        num_days = len(self._days)
        day_index = {day: i for i, day in enumerate(self._days)} # Map day string to index

        # Store the provided detailed daily capacity
        # Validate that daily capacity is provided for all developers and relevant days
        self._developer_daily_capacity = {}
        for dev in developers:
            if dev not in developer_daily_capacity:
                 raise ValueError(f"Daily capacity not provided for developer: {dev}")
            self._developer_daily_capacity[dev] = {}
            for day in self._days:
                 if day not in developer_daily_capacity[dev]:
                      # Assume 0 capacity if a specific day is missing for a developer, or use default?
                      # Let's raise an error to ensure explicit capacity is provided for all sprint days.
                      raise ValueError(f"Daily capacity not provided for developer {dev} on day {day}")
                 self._developer_daily_capacity[dev][day] = developer_daily_capacity[dev][day]

        # Create the optimization problem
        self.problem = LpProblem("SprintPlanningWithScheduling", LpMaximize)

        # --- Decision Variables ---

        # y_t: Binary variable indicating whether task t is selected
        self.task_vars = LpVariable.dicts("task_selected", tasks, cat='Binary')

        # x_t,a: Binary variable indicating if task t is assigned to developer a (overall sprint assignment)
        # This variable links task selection to who is responsible for the task.
        self.assignment_vars = LpVariable.dicts("task_assigned", ((t, a) for t in tasks for a in developers), cat='Binary')

        # w_tad: Binary variable indicating if developer a works on task t on day d
        self.work_vars = LpVariable.dicts("work_on_task_day", ((t, a, d) for t in tasks for a in developers for d in self._days), cat='Binary')

        # p_tad: Continuous variable for points of task t worked on by developer a on day d
        self.points_vars = LpVariable.dicts("points_worked_day", ((t, a, d) for t in tasks for a in developers for d in self._days), lowBound=0, cat='Continuous')

        # --- Objective Function ---

        # Maximize the sum of selected tasks weighted by priority
        self.problem += lpSum(
            self.task_vars[t] * task_priorities.get(t, 0)
            for t in tasks
        ), "Maximize_Total_Priority"

        # --- Constraints ---

        # 1. Task Selection and Assignment Link:
        # If a task is selected (y_t=1), it must be assigned to exactly one developer (sum(x_ta)=1).
        # If a task is not selected (y_t=0), it cannot be assigned (sum(x_ta)=0).
        for t in tasks:
            self.problem += lpSum(self.assignment_vars[t, a] for a in developers) == self.task_vars[t], f"Assign_Selected_Task_{t}"

        # 2. Assignment and Daily Work Link:
        # Developer 'a' can only work on task 't' on day 'd' (w_tad=1) if task 't' is assigned to 'a' (x_ta=1).
        for t in tasks:
            for a in developers:
                for d in self._days:
                    # If w_tad = 1, then x_ta must be 1
                    self.problem += self.work_vars[t, a, d] <= self.assignment_vars[t, a], f"Work_Requires_Assignment_{t}_{a}_{d}"

        # 3. Points Worked and Daily Work Link (Big M):
        # Points p_tad can only be positive if w_tad is 1.
        # If w_tad is 1, p_tad can be up to the daily capacity or remaining task points.
        # Use the maximum possible daily capacity across all developers and days as a safe M
        max_possible_daily_points = max(
            self._developer_daily_capacity[dev].get(d, DEFAULT_DAILY_CAPACITY)
            for dev in developers for d in self._days
        ) if developers and self._developer_daily_capacity else DEFAULT_DAILY_CAPACITY

        for t in tasks:
            task_pt = task_points.get(t, 0)
            M_points = max(task_pt, max_possible_daily_points, 1.0) # Ensure M is large enough and at least 1

            for a in developers:
                for d in self._days:
                    # If w_tad = 0, p_tad must be 0
                    self.problem += self.points_vars[t, a, d] <= M_points * self.work_vars[t, a, d], f"Points_Requires_Work_{t}_{a}_{d}"
                    # If w_tad = 1, p_tad can be > 0. No lower bound needed if total points constraint is active.

        # 4. Developer Daily Capacity:
        # Total points worked by developer 'a' on day 'd' cannot exceed their specific daily capacity for that day.
        for a in developers:
            for d in self._days:
                daily_cap = self._developer_daily_capacity[a].get(d, 0.0) # Use the specific daily capacity
                self.problem += lpSum(self.points_vars[t, a, d] for t in tasks) <= daily_cap, f"Daily_Capacity_{a}_{d}"

        # 5. Developer Total Sprint Capacity (Optional but good practice if total capacity is also a hard constraint)
        # Total points worked by developer 'a' over the sprint cannot exceed their total capacity.
        # This can be derived from daily capacity sum, but keeping it adds robustness.
        for a in developers:
             self.problem += lpSum(self.points_vars[t, a, d] for t in tasks for d in self._days) <= self._developer_total_capacity.get(a, 0), f"Total_Sprint_Capacity_{a}"


        # 6. Task Completion:
        # If a task 't' is selected (y_t=1), the total points worked on it across all days and its assigned developer must equal its total points.
        # If y_t=0, total points worked must be 0.
        for t in tasks:
            # Sum points for task t across all developers and days. Due to constraint 2, only the assigned developer will have p_tad > 0.
            self.problem += lpSum(self.points_vars[t, a, d] for a in developers for d in self._days) == task_points.get(t, 0) * self.task_vars[t], f"Task_Total_Points_{t}"


        # 7. Skill Matching Constraints (Applied to daily work):
        # Developer 'a' cannot work on task 't' on day 'd' (w_tad=0) if developer 'a' lacks skills for task 't'.
        for t in tasks:
            task_req_skills = task_skills.get(t, [])
            for a in developers:
                developer_has_skills = developer_skills.get(a, [])
                if task_req_skills and not all(skill in developer_has_skills for skill in task_req_skills):
                    for d in self._days:
                        self.problem += self.work_vars[t, a, d] == 0, f"Skill_Constraint_Work_{t}_{a}_{d}"
                        self.problem += self.points_vars[t, a, d] == 0, f"Skill_Constraint_Points_{t}_{a}_{d}"


        # 8. Time-Based Dependency Constraints (Precedence):
        # If task t2 depends on task t1 (t1 -> t2), and both are selected,
        # t2 cannot be worked on day 'd' unless t1 is completed by the end of day 'd-1'.
        # Completion of t1 by day d-1 means total points worked on t1 up to d-1 equals task_points[t1].
        # Constraint: If w_t2_a2_d = 1, then sum(p_t1_a1_d' for all a1, d' < d) >= task_points[t1]
        # This constraint is applied for every day 'd' from the second day of the sprint onwards.

        for t2 in tasks:
            dependencies = task_dependencies.get(t2, [])
            for t1 in dependencies:
                if t1 in tasks: # Ensure dependency is also in the list of tasks being considered
                    # If t2 is selected, t1 must be selected (already handled by constraint 1 in previous version, let's keep it)
                    # Note: This is implicitly handled by the time-based constraint too - if t1 isn't selected, its points are 0, and the precedence constraint becomes trivial.
                    # But keeping it makes the model structure clearer.
                    self.problem += self.task_vars[t2] <= self.task_vars[t1], f"Dependency_Selection_{t2}_on_{t1}"

                    # Time-based precedence constraint:
                    # For every day d from the second day onwards (index 1 to num_days-1):
                    # task_points[t1] * (sum of w_t2_a_d for all a) <= (sum of p_t1_a_d_prime for all a, d_prime < d) + BIG_M * (1 - task_vars[t1]) + BIG_M * (1 - task_vars[t2])
                    # This constraint states: If t1 and t2 are selected, and t2 is worked on day d (by any developer),
                    # THEN the total points worked on t1 (by any developer) up to day d-1 must be at least task_points[t1].
                    # The BIG_M terms deactivate the constraint if t1 or t2 are not selected.

                    for d_idx in range(1, num_days):
                        current_day = self._days[d_idx]
                        previous_days = self._days[:d_idx]
                        self.problem += task_points.get(t1, 0) * lpSum(self.work_vars[t2, a, current_day] for a in developers) <= lpSum(self.points_vars[t1, a_prime, prev_day] for a_prime in developers for prev_day in previous_days) + BIG_M * (1 - self.task_vars[t1]) + BIG_M * (1 - self.task_vars[t2]), f"Precedence_{t1}_before_{t2}_Day_{current_day}"


        print("Optimization model created with integrated scheduling constraints.")
        # Optional: write model to file for debugging
        # self.problem.writeMPS("sprint_planning_scheduled.mps")


    def _get_working_days_list(self, start_date_str, end_date_str):
        """Helper to get working days (Mon-Fri) as YYYY-MM-DD strings."""
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        working_days = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5: # Monday to Friday
                working_days.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        return working_days


    def solve(self) -> Tuple[Dict[str, bool], Dict[Tuple[str, str], bool], Dict[Tuple[str, str, str], bool], Dict[Tuple[str, str, str], float]]:
        """Solve the optimization problem and return the results."""
        if self.problem is None:
            raise ValueError("Optimization model not created. Call create_optimization_model first.")

        print("Solving time-aware optimization problem...")
        # Solve the problem using the default solver
        # For larger problems, consider using a more powerful solver (if available)
        # and potentially setting a time limit:
        # self.problem.solve(PULP_CBC_CMD(timeLimit=300)) # Example: 300 second limit

        status = self.problem.solve()

        status_map = {
            LpStatusOptimal: "Optimal",
            LpStatusNotSolved: "Not Solved",
            LpStatusInfeasible: "Infeasible",
            LpStatusUnbounded: "Unbounded",
            LpStatusUndefined: "Undefined"
        }
        print(f"Solver Status: {status_map.get(status, 'Unknown Status')}")

        if status != LpStatusOptimal:
            raise ValueError(f"Optimization failed to find an optimal solution. Status: {status_map.get(status, 'Unknown')}")

        print("Optimization solved successfully.")

        # Extract results
        task_selection = {
            t: bool(value(self.task_vars[t]))
            for t in self.task_vars
        }

        task_assignments = {
            (t, a): bool(value(self.assignment_vars[t, a]))
            for t, a in self.assignment_vars
        }

        work_schedule = {
            (t, a, d): bool(value(self.work_vars[t, a, d]))
            for t, a, d in self.work_vars
        }

        points_schedule = {
            (t, a, d): value(self.points_vars[t, a, d])
            for t, a, d in self.points_vars
        }

        return task_selection, task_assignments, work_schedule, points_schedule

    def get_optimization_summary(
        self,
        task_selection: Dict[str, bool],
        task_assignments: Dict[Tuple[str, str], bool],
        work_schedule: Dict[Tuple[str, str, str], bool],
        points_schedule: Dict[Tuple[str, str, str], float]
    ) -> Dict:
        """
        Generate a summary of the optimization results, extracting the daily schedule
        directly from the solved MILP variables.
        """
        if not self._task_points or not self._developer_total_capacity or not self._days or not self._developer_daily_capacity:
             raise ValueError("Optimization model inputs not stored. Ensure create_optimization_model was called.")

        selected_tasks = [t for t, selected in task_selection.items() if selected]

        # Calculate total story points selected (based on the optimizer's selection)
        total_points_selected = sum(
            self._task_points.get(t, 0)
            for t in selected_tasks
        )

        # Calculate total points actually scheduled (should match total_points_selected for selected tasks in an optimal feasible solution)
        total_points_scheduled = sum(value for value in points_schedule.values())


        # Build the daily schedule structure from the points_vars results
        developer_daily_schedule = collections.defaultdict(lambda: collections.defaultdict(list))
        developer_total_scheduled_points = collections.defaultdict(float)


        for (t, a, d), points in points_schedule.items():
            if points > 1e-6: # Only include if points worked is significant (handle floating point inaccuracies)
                 developer_daily_schedule[a][d].append({
                     "task": t,
                     "points": points
                 })
                 developer_total_scheduled_points[a] += points

        # Sort tasks within each day by points (or another criteria if desired) for consistent output
        for dev in developer_daily_schedule:
             for day in developer_daily_schedule[dev]:
                 developer_daily_schedule[dev][day].sort(key=lambda item: item['points'], reverse=True)


        # Calculate developer utilization based on total scheduled points against total sprint capacity
        # Also calculate utilization against the sum of their daily capacities
        developer_utilization = {}
        developer_tasks_assigned_by_optimizer = collections.defaultdict(list)

        for (t, a), assigned in task_assignments.items():
             if assigned:
                 developer_tasks_assigned_by_optimizer[a].append(t)


        for dev in self._developers:
            total_scheduled = developer_total_scheduled_points.get(dev, 0.0)
            total_sprint_capacity_input = self._developer_total_capacity.get(dev, 0)
            # Calculate total capacity from the sum of daily capacities
            total_daily_sum_capacity = sum(self._developer_daily_capacity.get(dev, {}).values())


            developer_utilization[dev] = {
                'total_sprint_capacity_input': total_sprint_capacity_input, # The total capacity provided as input
                'total_daily_sum_capacity': total_daily_sum_capacity, # Sum of daily capacities
                'total_points_scheduled': total_scheduled,
                # Utilization can be reported against either total input capacity or sum of daily capacity
                # Using sum of daily capacity is likely more relevant for scheduling feasibility
                'utilization_rate_vs_daily_sum': total_scheduled / total_daily_sum_capacity if total_daily_sum_capacity > 0 else 0,
                'tasks_assigned_by_optimizer': developer_tasks_assigned_by_optimizer[dev]
            }

        # Format the output schedule, ensuring days are sorted
        formatted_schedule = {}
        for dev, daily_data in developer_daily_schedule.items():
            formatted_schedule[dev] = {}
            # Sort days chronologically
            sorted_days = sorted(daily_data.keys())
            for day_str in sorted_days:
                 formatted_schedule[dev][day_str] = daily_data[day_str]


        return {
            'total_tasks_considered': len(self._tasks),
            'total_tasks_selected': len(selected_tasks),
            'total_story_points_selected': total_points_selected,
            'total_story_points_scheduled': total_points_scheduled, # Should be very close to selected points if feasible
            'objective_value': value(self.problem.objective) if self.problem else 0,
            'developer_utilization': developer_utilization,
            'sprint_working_days': self._days,
            'developer_daily_schedule': formatted_schedule
        }

# --- Example Usage ---
if __name__ == "__main__":
    tasks = ["T1", "T2", "T3", "T4", "T5", "T6", "T7"]
    developers = ["Alice", "Bob", "Charlie"]

    task_priorities = {
        "T1": 5, "T2": 4, "T3": 3, "T4": 5, "T5": 2, "T6": 4, "T7": 1
    }
    task_points = {
        "T1": 8, "T2": 12, "T3": 5, "T4": 6, "T5": 10, "T6": 8, "T7": 3
    }
    # Developer capacity in total story points for the sprint
    # This is now less critical than daily capacity, but still used in constraint 5.
    developer_total_capacity = {
        "Alice": 20,
        "Bob": 25,
        "Charlie": 15
    }

    task_dependencies = {
        "T2": ["T1"],
        "T3": ["T1"],
        "T4": ["T2"],
        "T5": ["T3", "T4"],
        "T6": [],
        "T7": ["T6"]
    }

    task_skills = {
        "T1": ["Frontend"], "T2": ["Backend"], "T3": ["Database"],
        "T4": ["Backend", "Frontend"], "T5": ["Database", "Backend"],
        "T6": ["Frontend"], "T7": ["Backend"]
    }
    developer_skills = {
        "Alice": ["Frontend", "Backend"],
        "Bob": ["Backend", "Database"],
        "Charlie": ["Frontend"]
    }

    sprint_start = "2025-04-07" # A Monday
    sprint_end = "2025-04-18"   # A Friday (Two-week sprint = 10 working days)

    # --- Define Detailed Daily Capacity ---
    # This dictionary specifies capacity for each developer for each day.
    # Capacity 0 means they are unavailable that day.
    developer_daily_capacity = {
        "Alice": {
            "2025-04-07": 8.0, "2025-04-08": 8.0, "2025-04-09": 8.0, "2025-04-10": 8.0, "2025-04-11": 8.0, # Week 1
            "2025-04-14": 8.0, "2025-04-15": 8.0, "2025-04-16": 8.0, "2025-04-17": 8.0, "2025-04-18": 8.0  # Week 2
        },
        "Bob": {
            "2025-04-07": 8.0, "2025-04-08": 8.0, "2025-04-09": 8.0, "2025-04-10": 8.0, "2025-04-11": 8.0, # Week 1
            "2025-04-14": 8.0, "2025-04-15": 8.0, "2025-04-16": 8.0, "2025-04-17": 8.0, "2025-04-18": 8.0  # Week 2
        },
        "Charlie": {
            "2025-04-07": 8.0, "2025-04-08": 8.0, "2025-04-09": 0.0, "2025-04-10": 8.0, "2025-04-11": 8.0, # Charlie off on 2025-04-09
            "2025-04-14": 8.0, "2025-04-15": 8.0, "2025-04-16": 8.0, "2025-04-17": 8.0, "2025-04-18": 8.0
        }
    }
    # Note: The sum of daily capacities for Charlie is 8*9 = 72, which is much higher than his total sprint capacity input (15).
    # The MILP will respect *both* the daily capacity constraints AND the total sprint capacity constraint.
    # If the sum of daily capacities is less than the total sprint capacity input, the daily capacity constraints will be the binding ones.
    # If the sum of daily capacities is more than the total sprint capacity input, the total sprint capacity constraint will be binding.
    # Ensure consistency between total and daily capacities if you intend them to represent the same thing.
    # A simpler approach might be to only use the sum of daily capacities as the effective total capacity.

    optimizer = SprintOptimizer()

    try:
        optimizer.create_optimization_model(
            tasks, developers, task_priorities, task_points, developer_total_capacity,
            task_dependencies, task_skills, developer_skills,
            sprint_start_date=sprint_start,
            sprint_end_date=sprint_end,
            developer_daily_capacity=developer_daily_capacity # Pass the detailed daily capacity
        )

        task_selection, task_assignments, work_schedule, points_schedule = optimizer.solve()

        summary = optimizer.get_optimization_summary(
            task_selection, task_assignments, work_schedule, points_schedule
        )

        print("\n--- Optimization Summary (Time-Aware MILP with Detailed Daily Capacity) ---")
        print(f"Total Tasks Considered: {summary['total_tasks_considered']}")
        print(f"Total Tasks Selected: {summary['total_tasks_selected']}")
        print(f"Total Story Points Selected: {summary['total_story_points_selected']:.2f}")
        print(f"Total Story Points Scheduled: {summary['total_story_points_scheduled']:.2f}") # Should match selected points if feasible
        print(f"Objective Value (Total Priority): {summary['objective_value']:.2f}")
        print(f"Sprint Working Days: {len(summary['sprint_working_days'])}")
        print("-" * 20)
        print("Developer Utilization:")
        for dev, data in summary['developer_utilization'].items():
            print(f"  {dev}:")
            print(f"    Total Sprint Capacity Input: {data['total_sprint_capacity_input']:.2f} points")
            print(f"    Total Daily Sum Capacity: {data['total_daily_sum_capacity']:.2f} points")
            print(f"    Total Points Scheduled: {data['total_points_scheduled']:.2f} points")
            print(f"    Utilization Rate (vs Daily Sum): {data['utilization_rate_vs_daily_sum']:.2%}")
            print(f"    Tasks Assigned by Optimizer: {', '.join(data['tasks_assigned_by_optimizer']) if data['tasks_assigned_by_optimizer'] else 'None'}")
        print("-" * 20)
        print("Developer Daily Schedule:")
        for dev, schedule in summary['developer_daily_schedule'].items():
             print(f"  {dev}:")
             if schedule:
                 # Sort days for consistent output
                 sorted_days = sorted(schedule.keys())
                 for day_str in sorted_days:
                      # Get the capacity for this specific day for this developer
                      daily_cap = optimizer._developer_daily_capacity.get(dev, {}).get(day_str, 0.0)
                      print(f"    {day_str} (Capacity: {daily_cap:.2f}):")
                      # Sort tasks on the day by points
                      tasks_on_day = schedule[day_str]
                      tasks_on_day.sort(key=lambda item: item['points'], reverse=True)
                      for item in tasks_on_day:
                           print(f"      - {item['task']}: {item['points']:.2f} points")
             else:
                 print("    No tasks scheduled for this developer.")

        print("\n--- Detailed Assignment Results (from Optimizer) ---")
        selected_tasks_list = [t for t, selected in task_selection.items() if selected]
        if selected_tasks_list:
            print("Selected Tasks and Assignments:")
            for t in selected_tasks_list:
                assigned_dev = None
                for dev in developers:
                    if task_assignments.get((t, dev), False):
                        assigned_dev = dev
                        break
                print(f"  - {t} (Priority: {task_priorities.get(t,0)}, Points: {task_points.get(t,0)}) assigned to {assigned_dev}")
        else:
            print("No tasks were selected by the optimizer.")


    except ValueError as e:
        print(f"\nError during optimization or summary: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

