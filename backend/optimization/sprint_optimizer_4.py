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

class SprintOptimizerNew:
    def __init__(self):
        self.problem = None
        self.task_vars = {}        # y_t
        self.assignment_vars = {}  # x_ta
        self.work_vars = {}        # w_tad (Binary: developer a works on task t on day d)
        self.points_vars = {}      # p_tad (Continuous: points of task t worked by a on day d)

        # Soft constraint variables
        self.dev_total_points = {} # Total points scheduled for each developer
        self.max_workload = None
        self.min_workload = None
        self.workload_deviation = None

        self._tasks = []
        self._developers = []
        self._days = [] # List of working days (YYYY-MM-DD strings)
        self._day_index = {} # Map day string to index
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
        developer_daily_capacity: Dict[str, Dict[str, float]], # Required: detailed daily capacity per day
        # NEW: Penalty costs for soft constraints
        penalty_workload_imbalance: float = 0.1, # Cost per unit of workload deviation
        penalty_context_switching: float = 0.01, # Cost per task worked on per day
        penalty_late_completion: float = 0.005 # Cost per point per day later in sprint
    ) -> None:
        """
        Create the MILP optimization model for sprint planning, including
        task selection, assignment, daily scheduling with dependencies,
        and soft constraints.
        """
        print("Creating time-aware optimization model with integrated scheduling and soft constraints...")

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
        self._day_index = {day: i for i, day in enumerate(self._days)} # Map day string to index

        # Store the provided detailed daily capacity and validate
        self._developer_daily_capacity = {}
        for dev in developers:
            if dev not in developer_daily_capacity:
                 raise ValueError(f"Daily capacity not provided for developer: {dev}")
            self._developer_daily_capacity[dev] = {}
            for day in self._days:
                 if day not in developer_daily_capacity[dev]:
                      raise ValueError(f"Daily capacity not provided for developer {dev} on day {day}")
                 self._developer_daily_capacity[dev][day] = developer_daily_capacity[dev][day]


        # Create the optimization problem
        # Initialize with the primary objective (Maximize Priority)
        self.problem = LpProblem("SprintPlanningWithSchedulingAndSoftConstraints", LpMaximize)

        # --- Decision Variables ---

        # y_t: Binary variable indicating whether task t is selected
        self.task_vars = LpVariable.dicts("task_selected", tasks, cat='Binary')

        # x_t,a: Binary variable indicating if task t is assigned to developer a (overall sprint assignment)
        self.assignment_vars = LpVariable.dicts("task_assigned", ((t, a) for t in tasks for a in developers), cat='Binary')

        # w_tad: Binary variable indicating if developer a works on task t on day d
        self.work_vars = LpVariable.dicts("work_on_task_day", ((t, a, d) for t in tasks for a in developers for d in self._days), cat='Binary')

        # p_tad: Continuous variable for points of task t worked on by developer a on day d
        self.points_vars = LpVariable.dicts("points_worked_day", ((t, a, d) for t in tasks for a in developers for d in self._days), lowBound=0, cat='Continuous')

        # --- Soft Constraint Variables ---

        # For Workload Imbalance
        self.dev_total_points = LpVariable.dicts("dev_total_points", developers, lowBound=0, cat='Continuous')
        self.max_workload = LpVariable("max_workload", lowBound=0, cat='Continuous')
        self.min_workload = LpVariable("min_workload", lowBound=0, cat='Continuous')
        self.workload_deviation = LpVariable("workload_deviation", lowBound=0, cat='Continuous')


        # --- Objective Function ---

        # Primary Objective: Maximize the sum of selected tasks weighted by priority
        primary_objective = lpSum(self.task_vars[t] * task_priorities.get(t, 0) for t in tasks)

        # Soft Constraint Penalties (to be subtracted)
        # Penalty for Workload Imbalance: Penalize the difference between max and min developer workload
        penalty_imbalance = penalty_workload_imbalance * self.workload_deviation

        # Penalty for Context Switching: Penalize the total number of (developer, task, day) tuples where work occurs
        penalty_context = penalty_context_switching * lpSum(self.work_vars[t, a, d] for t in tasks for a in developers for d in self._days)

        # Penalty for Late Completion: Penalize points worked later in the sprint (weighted by day index)
        penalty_late = penalty_late_completion * lpSum(
            self.points_vars[t, a, d] * self._day_index[d]
            for t in tasks for a in developers for d in self._days
        )

        # Combine objectives: Maximize Primary Objective - Penalties
        self.problem += primary_objective - penalty_imbalance - penalty_context - penalty_late, "Combined_Objective"


        # --- Hard Constraints ---

        # 1. Task Selection and Assignment Link:
        for t in tasks:
            self.problem += lpSum(self.assignment_vars[t, a] for a in developers) == self.task_vars[t], f"Assign_Selected_Task_{t}"

        # 2. Assignment and Daily Work Link:
        for t in tasks:
            for a in developers:
                for d in self._days:
                    self.problem += self.work_vars[t, a, d] <= self.assignment_vars[t, a], f"Work_Requires_Assignment_{t}_{a}_{d}"

        # 3. Points Worked and Daily Work Link (Big M):
        max_possible_daily_points = max(
            self._developer_daily_capacity[dev].get(d, DEFAULT_DAILY_CAPACITY)
            for dev in developers for d in self._days
        ) if developers and self._developer_daily_capacity else DEFAULT_DAILY_CAPACITY

        for t in tasks:
            task_pt = task_points.get(t, 0)
            M_points = max(task_pt, max_possible_daily_points, 1.0)

            for a in developers:
                for d in self._days:
                    self.problem += self.points_vars[t, a, d] <= M_points * self.work_vars[t, a, d], f"Points_Requires_Work_{t}_{a}_{d}"

        # 4. Developer Daily Capacity:
        for a in developers:
            for d in self._days:
                daily_cap = self._developer_daily_capacity[a].get(d, 0.0)
                self.problem += lpSum(self.points_vars[t, a, d] for t in tasks) <= daily_cap, f"Daily_Capacity_{a}_{d}"

        # 5. Developer Total Sprint Capacity (Optional but good practice)
        for a in developers:
             self.problem += lpSum(self.points_vars[t, a, d] for t in tasks for d in self._days) <= self._developer_total_capacity.get(a, 0), f"Total_Sprint_Capacity_{a}"

        # 6. Task Completion:
        for t in tasks:
            self.problem += lpSum(self.points_vars[t, a, d] for a in developers for d in self._days) == task_points.get(t, 0) * self.task_vars[t], f"Task_Total_Points_{t}"

        # 7. Skill Matching Constraints (Applied to daily work):
        for t in tasks:
            task_req_skills = task_skills.get(t, [])
            for a in developers:
                developer_has_skills = developer_skills.get(a, [])
                if task_req_skills and not all(skill in developer_has_skills for skill in task_req_skills):
                    for d in self._days:
                        self.problem += self.work_vars[t, a, d] == 0, f"Skill_Constraint_Work_{t}_{a}_{d}"
                        self.problem += self.points_vars[t, a, d] == 0, f"Skill_Constraint_Points_{t}_{a}_{d}"

        # 8. Time-Based Dependency Constraints (Precedence):
        # If task t2 depends on t1, t2 can only start after t1 is completed.
        # Completion of t1 means all its points are scheduled *up to* a certain day.
        # t2 can work on day d only if all points for t1 are scheduled on days before d.
        # We enforce this using Big M: sum(points_t1_days_before_d) >= task_points_t1 * work_on_t2_on_day_d - M*(1-y_t1) - M*(1-y_t2)
        # If y_t1 and y_t2 are 1, then sum(points_t1_days_before_d) >= task_points_t1 * work_on_t2_on_day_d.
        # If work_on_t2_on_day_d is 1, then sum(points_t1_days_before_d) must be >= task_points_t1.
        # This implies t1 must have been fully scheduled on previous days.
        for t2 in tasks:
            dependencies = task_dependencies.get(t2, [])
            for t1 in dependencies:
                if t1 in tasks:
                    # Dependency constraint 1: If t2 is selected, t1 must be selected.
                    self.problem += self.task_vars[t2] <= self.task_vars[t1], f"Dependency_Selection_{t2}_on_{t1}"

                    # Dependency constraint 2: Scheduling precedence
                    # Iterate through all days except the first one
                    for d_idx in range(1, num_days):
                        current_day = self._days[d_idx]
                        previous_days = self._days[:d_idx]

                        # Sum of points of t1 worked by any developer up to the day before current_day
                        points_t1_on_previous_days = lpSum(self.points_vars[t1, a, prev_day]
                                                          for a in developers
                                                          for prev_day in previous_days)

                        # Sum of work variables for t2 on the current_day (across all developers)
                        work_on_t2_on_current_day = lpSum(self.work_vars[t2, a, current_day] for a in developers)

                        # If t2 is worked on day 'current_day', then t1 must have been completed on previous days.
                        # This is enforced by: points_t1_on_previous_days >= task_points.get(t1, 0) * work_on_t2_on_current_day
                        # Using Big M to activate/deactivate based on task selection:
                        # points_t1_on_previous_days >= task_points.get(t1, 0) * work_on_t2_on_current_day - M * (1 - self.task_vars[t1]) - M * (1 - self.task_vars[t2])
                        # Rearranging: task_points.get(t1, 0) * work_on_t2_on_current_day - points_t1_on_previous_days <= M * (1 - self.task_vars[t1]) + M * (1 - self.task_vars[t2])
                        self.problem += task_points.get(t1, 0) * work_on_t2_on_current_day - points_t1_on_previous_days <= BIG_M * (1 - self.task_vars[t1]) + BIG_M * (1 - self.task_vars[t2]), f"Precedence_{t1}_before_{t2}_Day_{current_day}"


        # --- Soft Constraint Implementation Constraints ---

        # Workload Imbalance: Link dev_total_points to actual scheduled points
        for a in developers:
            self.problem += self.dev_total_points[a] == lpSum(self.points_vars[t, a, d] for t in tasks for d in self._days), f"Define_Dev_Total_Points_{a}"

        # Workload Imbalance: Define max_workload and min_workload
        for a in developers:
            self.problem += self.max_workload >= self.dev_total_points[a], f"Define_Max_Workload_{a}"
            self.problem += self.min_workload <= self.dev_total_points[a], f"Define_Min_Workload_{a}"

        # Workload Imbalance: Define workload_deviation
        self.problem += self.workload_deviation == self.max_workload - self.min_workload, "Define_Workload_Deviation"


        print("Optimization model created with integrated scheduling and soft constraints.")
        # Optional: write model to file for debugging
        # self.problem.writeMPS("sprint_planning_scheduled_soft.mps")


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

        print("Solving time-aware optimization problem with soft constraints...")
        # Solve the problem using the default solver
        # For larger problems, consider using a more powerful solver (if available)
        # and potentially setting a time limit:
        # self.problem.solve(PULP_CBC_CMD(timeLimit=300)) # Example: 300 second limit

        status = self.problem.solve(PULP_CBC_CMD(timeLimit=30))

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

        print("Task Selection Results:")
        # print(task_selection) # Comment out verbose printing
        # print(task_assignments) # Comment out verbose printing
        # print(work_schedule) # Comment out verbose printing
        # print(points_schedule) # Comment out verbose printing

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
        directly from the solved MILP variables, and including dependency status
        for selected tasks.
        """

        if not self._task_points or not self._developer_total_capacity or not self._days or not self._developer_daily_capacity or not self._task_dependencies:
             raise ValueError("Optimization model inputs not stored. Ensure create_optimization_model was called.")

        selected_tasks = [t for t, selected in task_selection.items() if selected]

        print("Generating optimization summary...")

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

        # Extract soft constraint violation values (if problem was solved)
        workload_deviation_value = value(self.workload_deviation) #if self.workload_deviation else 0
        max_workload_value = value(self.max_workload) #if self.max_workload else 0
        min_workload_value = value(self.min_workload) #if self.min_workload else 0

        # Calculate total context switches (sum of w_tad where w_tad = 1)
        total_context_switches = sum(1 for (t, a, d), worked in work_schedule.items() if worked)

        # Calculate total late completion penalty points (sum of p_tad * day_index)
        total_late_completion_penalty_points = sum(
            points_schedule.get((t, a, d), 0) * self._day_index.get(d, 0)
            for t in self._tasks for a in self._developers for d in self._days
        )

        # --- Add Task Selection with Dependency Status ---
        selected_tasks_with_dependency_status = {}
        for t in selected_tasks:
            dependencies = self._task_dependencies.get(t, [])
            dependency_status_list = []
            for dep in dependencies:
                dependency_status_list.append({
                    'dependency': dep,
                    'selected': task_selection.get(dep, False) # Check if the dependency was selected
                })
            selected_tasks_with_dependency_status[t] = dependency_status_list
        # ----------------------------------------------------


        return {
            'total_tasks_considered': len(self._tasks),
            'total_tasks_selected': len(selected_tasks),
            'total_story_points_selected': total_points_selected,
            'total_story_points_scheduled': total_points_scheduled, # Should be very close to selected points if feasible
            'objective_value': value(self.problem.objective) if self.problem and self.problem.objective else 0,
            'developer_utilization': developer_utilization,
            'sprint_working_days': self._days,
            'developer_daily_schedule': formatted_schedule,
            # Soft Constraint Metrics
            'soft_constraint_metrics': {
                'workload_imbalance_deviation': workload_deviation_value,
                'max_developer_workload': max_workload_value,
                'min_developer_workload': min_workload_value,
                'total_context_switches': total_context_switches,
                'total_late_completion_penalty_points': total_late_completion_penalty_points
            },
            # NEW: Task Selection with Dependency Status
            'selected_tasks_with_dependency_status': selected_tasks_with_dependency_status
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
        "Alice": 80, # Increased total capacity for example
        "Bob": 80,
        "Charlie": 80
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
    # Note: The sum of daily capacities for Charlie is 8*9 = 72.
    # The total sprint capacity input (80) is higher than the sum of daily capacity (72),
    # so the daily capacity constraints will be the binding ones for Charlie's total work.

    optimizer = SprintOptimizerNew()

    try:
        # Example with soft constraint penalties
        optimizer.create_optimization_model(
            tasks, developers, task_priorities, task_points, developer_total_capacity,
            task_dependencies, task_skills, developer_skills,
            sprint_start_date=sprint_start,
            sprint_end_date=sprint_end,
            developer_daily_capacity=developer_daily_capacity,
            penalty_workload_imbalance=0.5, # Higher penalty for imbalance
            penalty_context_switching=0.05, # Higher penalty for context switching
            penalty_late_completion=0.01    # Higher penalty for late completion
        )

        task_selection, task_assignments, work_schedule, points_schedule = optimizer.solve()

        summary = optimizer.get_optimization_summary(
            task_selection, task_assignments, work_schedule, points_schedule
        )

        print("\n--- Optimization Summary (Time-Aware MILP with Soft Constraints) ---")
        print(f"Total Tasks Considered: {summary['total_tasks_considered']}")
        print(f"Total Tasks Selected: {summary['total_tasks_selected']}")
        print(f"Total Story Points Selected: {summary['total_story_points_selected']:.2f}")
        print(f"Total Story Points Scheduled: {summary['total_story_points_scheduled']:.2f}") # Should be very close to selected points if feasible
        print(f"Objective Value (Total Priority - Penalties): {summary['objective_value']:.2f}")
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
        print("Soft Constraint Metrics:")
        metrics = summary['soft_constraint_metrics']
        print(f"  Workload Imbalance Deviation (Max - Min): {metrics['workload_imbalance_deviation']:.2f}")
        print(f"    (Max Workload: {metrics['max_developer_workload']:.2f}, Min Workload: {metrics['min_developer_workload']:.2f})")
        print(f"  Total Context Switches (Sum of w_tad=1): {metrics['total_context_switches']}")
        print(f"  Total Late Completion Penalty Points (Sum of p_tad * day_index): {metrics['total_late_completion_penalty_points']:.2f}")
        print("-" * 20)
        # NEW: Print Task Selection with Dependency Status
        print("Selected Tasks and Dependency Status:")
        selected_tasks_with_deps = summary['selected_tasks_with_dependency_status']
        if selected_tasks_with_deps:
            for task, deps_status in selected_tasks_with_deps.items():
                print(f"  - {task} (Priority: {task_priorities.get(task,0)}, Points: {task_points.get(task,0)})")
                if deps_status:
                    print("    Dependencies:")
                    for dep_info in deps_status:
                        status = "Selected" if dep_info['selected'] else "NOT Selected"
                        print(f"      - {dep_info['dependency']} ({status})")
                else:
                    print("    No dependencies.")
        else:
            print("No tasks were selected by the optimizer.")
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