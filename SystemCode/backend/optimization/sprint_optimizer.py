from pulp import *
from typing import Dict, List, Tuple
import numpy as np
from datetime import datetime, timedelta

class SprintOptimizer:
    def __init__(self):
        self.problem = None
        self.task_vars = {}
        self.assignment_vars = {}
        
    def create_optimization_model(
        self,
        tasks: List[str],
        developers: List[str],
        task_priorities: Dict[str, int],
        task_points: Dict[str, float],
        developer_capacity: Dict[str, float],
        task_dependencies: Dict[str, List[str]],
        task_skills: Dict[str, List[str]],
        developer_skills: Dict[str, List[str]]
    ) -> None:
        """Create the MILP optimization model for sprint planning."""
        print("create_optimization_model called with tasks:", tasks)
        
        

        # Create the optimization problem
        self.problem = LpProblem("SprintPlanning", LpMaximize)
        
        # Create decision variables
        # y_t: Binary variable indicating whether task t is selected
        self.task_vars = LpVariable.dicts(
            "task_selected",
            tasks,
            cat='Binary'
        )
        
        # x_t,a: Binary variable indicating if task t is assigned to developer a
        self.assignment_vars = LpVariable.dicts(
            "task_assigned",
            ((t, a) for t in tasks for a in developers),
            cat='Binary'
        )
        
        # Objective function: Maximize the sum of selected tasks weighted by priority
        self.problem += lpSum(
            self.task_vars[t] * task_priorities[t]
            for t in tasks
        )
        
        # Constraints
        
        # 1. Each selected task must be assigned to exactly one developer
        for t in tasks:
            self.problem += lpSum(
                self.assignment_vars[t, a]
                for a in developers
            ) == self.task_vars[t]
        
        # 2. Developer capacity constraints
        for a in developers:
            self.problem += lpSum(
                self.assignment_vars[t, a] * task_points[t]
                for t in tasks
            ) <= developer_capacity[a]
        
        # 3. Task dependency constraints
        for t in tasks:
            for dep in task_dependencies[t]:
                if dep in tasks:  # Only consider dependencies that are in the task list
                    self.problem += self.task_vars[t] <= self.task_vars[dep]
        
        # 4. Skill matching constraints (optional)
        for t in tasks:
            for a in developers:
                # If task requires skills that developer doesn't have, prevent assignment
                if not all(skill in developer_skills[a] for skill in task_skills[t]):
                    self.problem += self.assignment_vars[t, a] == 0
    
    def solve(self) -> Tuple[Dict[str, bool], Dict[Tuple[str, str], bool]]:
        """Solve the optimization problem and return the results."""
        if self.problem is None:
            raise ValueError("Optimization model not created")
        
        # Solve the problem
        status = self.problem.solve()
        
        if status != 1:
            raise ValueError("Optimization failed to find a solution")
        
        # Extract results
        task_selection = {
            t: bool(value(self.task_vars[t]))
            for t in self.task_vars
        }
        
        task_assignments = {
            (t, a): bool(value(self.assignment_vars[t, a]))
            for t, a in self.assignment_vars
        }
        
        return task_selection, task_assignments
    
    def get_optimization_summary(
        self,
        task_selection: Dict[str, bool],
        task_assignments: Dict[Tuple[str, str], bool],
        task_points: Dict[str, float],
        developer_capacity: Dict[str, float]
    ) -> Dict:
        """Generate a summary of the optimization results."""
        try:
            # Debugging logs to inspect inputs
            #print("Debugging get_optimization_summary inputs:")
            #print("task_selection:", task_selection)
            #print("task_assignments:", task_assignments)
            #print("task_points:", task_points)
            #print("developer_capacity:", developer_capacity)

            # Calculate total story points selected
            total_points = sum(
                task_points[t]
                for t, selected in task_selection.items()
                if selected
            )

            task_dates = assign_task_dates(task_assignments, task_points, developer_capacity, "2025-04-05", "2025-04-18")

            # Calculate developer utilization
            developer_utilization = {}
            developer_tasks = {dev: [] for dev in developer_capacity}  # Initialize task lists for each developer

            for dev in developer_capacity:
                assigned_points = sum(
                    task_points[t]
                    for (t, d), assigned in task_assignments.items()
                    if d == dev and assigned
                )

                # Collect tasks assigned to the developer
                developer_tasks[dev] = [
                    t for (t, d), assigned in task_assignments.items()
                    if d == dev and assigned
                ]

                developer_utilization[dev] = {
                    'assigned_points': assigned_points,
                    'capacity': developer_capacity[dev],
                    'utilization_rate': assigned_points / developer_capacity[dev],
                    'tasks': developer_tasks[dev]  # Add the list of tasks
                }

            # Add developer schedules to developer_utilization
            for dev in developer_utilization:
                developer_utilization[dev]['schedule'] = task_dates.get(dev, {})

            
            

            return {
                'total_tasks_selected': sum(1 for selected in task_selection.values() if selected),
                'total_story_points': total_points,
                'developer_utilization': developer_utilization
               
            }
        except Exception as e:
            print(f"Error in get_optimization_summary: {e}")
            return {
                'total_tasks_selected': 0,
                'total_story_points': 0,
                'developer_utilization': {},
                'developer_schedules': {}
            }

def assign_task_dates(task_assignments, task_points, developer_capacity, sprint_start_date, sprint_end_date):
    sprint_start = datetime.strptime(sprint_start_date, "%Y-%m-%d")
    sprint_end = datetime.strptime(sprint_end_date, "%Y-%m-%d")

    # Helper function to get working days
    def get_working_days(start_date, end_date):
        current_date = start_date
        working_days = []
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday are working days
                working_days.append(current_date)
            current_date += timedelta(days=1)
        return working_days

    working_days = get_working_days(sprint_start, sprint_end)

    # Initialize developer schedules
    developer_schedules = {dev: {day: 0 for day in working_days} for dev in developer_capacity}
    developer_task_dates = {dev: {} for dev in developer_capacity}  # Initialize developer task dates

    for (task, developer), assigned in task_assignments.items():
        if assigned:
            remaining_points = task_points[task]

            for day in working_days:
                if remaining_points <= 0:
                    break

                available_capacity = 8 - developer_schedules[developer][day]

                if available_capacity > 0:
                    points_to_assign = min(remaining_points, available_capacity)
                    developer_schedules[developer][day] += points_to_assign
                    remaining_points -= points_to_assign

                    if day.strftime("%Y-%m-%d") not in developer_task_dates[developer]:
                        developer_task_dates[developer][day.strftime("%Y-%m-%d")] = []

                    developer_task_dates[developer][day.strftime("%Y-%m-%d")].append({
                        "task": task,
                        "points": points_to_assign
                    })

    return developer_task_dates
