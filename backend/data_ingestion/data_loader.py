import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Any, Optional, Union
from pathlib import Path
from optimization.sprint_optimizer import SprintOptimizer
from optimization.sprint_optimizer_5 import SprintOptimizerNew
from regression.sprint_velocity_forecast4 import VelocityForecaster

optimizer = SprintOptimizer()
optimizerNew = SprintOptimizerNew()
forecaster = VelocityForecaster(num_historical_sprints=52, num_sprints_to_forecast=52)

class DataLoader:
    def __init__(self):
        """Initialize the data loader."""
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize data attributes
        self.backlog_data = None
        self.sprint_data = None
        self.team_data = None
        self.future_capacity_data = None
        self.sprint_history_data = None
        self.forecasted_velocity = None
        self.leaves= None
        self.holidays= None
        self.sprint_task_distribution = None

        self.load_team_data(self.data_dir / "dummy" / "team_data.csv")  # Load team data during initialization
        self.load_sprint_history_data(self.data_dir / "dummy" / "sprint_data.csv")
        self.load_forecast_velocity()
        self.load_leaves(self.data_dir / "dummy" / "leaves.csv")
        self.load_holidays(self.data_dir / "dummy" / "holiday.csv")
    
    def load_backlog(self, file_path: Union[str, Path]) -> bool:
        """Load product backlog data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['issue_key', 'summary', 'description', 'priority', 'story_points', 
                              'dependencies', 'skills', 'status', 'sprint_id']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert string representations of lists to actual lists
            df['dependencies'] = df['dependencies'].apply(lambda x: x.split(',') if pd.notna(x) else [])
            df['skills'] = df['skills'].apply(lambda x: x.split(';') if pd.notna(x) else [])
            
            self.backlog_data = df
            return True
        except Exception as e:
            print(f"Error loading backlog data: {str(e)}")
            return False
    
    def load_sprint_data(self, file_path: Union[str, Path]) -> bool:
        """Load sprint data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['sprint_id', 'sprint_name', 'start_date', 'end_date', 'status', 
                              'completed_story_points', 'total_story_points']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            self.sprint_data = df
            return True
        except Exception as e:
            print(f"Error loading sprint data: {str(e)}")
            return False
    
    def load_team_data(self, file_path: Union[str, Path]) -> bool:
        """Load team data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['developer_name', 'role', 'capacity', 'skill_sets', 'preferences']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert string representations of lists to actual lists
            df['skill_sets'] = df['skill_sets'].apply(lambda x: x.split(';') if pd.notna(x) else [])
            df['preferences'] = df['preferences'].apply(lambda x: x.split(';') if pd.notna(x) else [])
            
            self.team_data = df
            return True
        except Exception as e:
            print(f"Error loading team data: {str(e)}")
            return False
    
    def load_sprint_history_data(self, file_path: Union[str, Path]) -> bool:
        """Load team data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['sprint_number','start_date','end_date','team_size','committed_story_points','completed_story_points','planned_leave_days_team','unplanned_leave_days_team','major_impediment','backlog_well_refined_percentage','sprint_duration_days','available_person_days','lagged_velocity']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            df['status'] = 'Completed'  # Mark all records as completed
            
            self.sprint_history_data = df
            return True
        except Exception as e:
            print(f"Error loading team data: {str(e)}")
            return False
        
    def load_leaves(self, file_path: Union[str, Path]) -> bool:
        """Load Leaves data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['developer','date']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            
            
            self.leaves = df
            return True
        except Exception as e:
            print(f"Error loading Leave data: {str(e)}")
            return False
        
    def load_holidays(self, file_path: Union[str, Path]) -> bool:
        """Load Holidays data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['date','holidayName']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            
            
            self.holidays = df
            return True
        except Exception as e:
            print(f"Error loading Leave data: {str(e)}")
            return False
    
    def load_future_capacity(self, file_path: Union[str, Path]) -> bool:
        """Load future capacity data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['sprint_id', 'developer_name', 'base_capacity', 'availability']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            self.future_capacity_data = df
            return True
        except Exception as e:
            print(f"Error loading future capacity data: {str(e)}")
            return False
    
    def get_team_data(self) -> pd.DataFrame:
        """Get team data."""
        if self.team_data is None or self.team_data.empty:
            return pd.DataFrame()
        
        team_members = [
            {
                "name": row["developer_name"],
                "role": row["role"],
                "capacity": row["capacity"],
                "skills": ", ".join(row["skill_sets"]),
                "email": row.get("email", "")
            }
            for _, row in self.team_data.iterrows()  
        ]
        return team_members
    
    def get_backlog_tasks(self) -> pd.DataFrame:
        """Get tasks that are available for planning (in backlog or future sprints)."""
        if self.backlog_data is None or self.backlog_data.empty:
            return pd.DataFrame()
        
        # Filter tasks that are either:
        # 1. Marked as "Backlog" status
        # 2. Have no sprint_id
        # 3. Have an empty sprint_id
        # 4. Have "None" as sprint_id
        # 5. Are assigned to future sprints
        available_tasks = self.backlog_data[
            (self.backlog_data['status'] == 'Backlog') |
            (self.backlog_data['sprint_id'].isna()) |
            (self.backlog_data['sprint_id'] == '') |
            (self.backlog_data['sprint_id'] == 'None') |
            (self.backlog_data['sprint_id'].str.startswith('SPRINT-5', na=False))
        ]
        
        return available_tasks
    
    def get_completed_sprint_tasks(self) -> pd.DataFrame:
        """Get tasks that are completed in sprints."""
        if self.backlog_data is None:
            return pd.DataFrame()
        return self.backlog_data[self.backlog_data['status'] == 'Completed']
    
    def get_in_progress_sprint_tasks(self) -> pd.DataFrame:
        """Get tasks that are in progress in sprints."""
        if self.backlog_data is None:
            return pd.DataFrame()
        return self.backlog_data[self.backlog_data['status'] == 'In Progress']
    
    def get_future_sprints(self) -> pd.DataFrame:
        """Get sprints that are available for planning."""
        if self.sprint_data is None or self.sprint_data.empty:
            return pd.DataFrame()
        
        # Filter sprints that are not started or in progress
        future_sprints = self.sprint_data[
            (self.sprint_data['status'] == 'Not Started') |
            (self.sprint_data['status'] == 'In Progress')
        ]
        
        return future_sprints
    
    def get_sprint_capacity(self, sprint_id: str) -> pd.DataFrame:
        """Get developer capacity for a specific sprint."""
        if self.future_capacity_data is None or self.future_capacity_data.empty:
            return pd.DataFrame()
        
        # Filter capacity data for the specified sprint
        sprint_capacity = self.future_capacity_data[
            self.future_capacity_data['sprint_id'] == sprint_id
        ]
        
        return sprint_capacity
    
    def get_available_tasks_for_planning(self) -> pd.DataFrame:
        """Get tasks that are available for sprint planning."""
        if self.backlog_data is None:
            return pd.DataFrame()
        
        # Get tasks that are either in backlog or assigned to future sprints
        backlog_tasks = self.get_backlog_tasks()
        
        # Filter out any tasks that are already assigned to in-progress or completed sprints
        if self.sprint_data is not None:
            active_sprints = self.sprint_data[
                (self.sprint_data['status'] == 'In Progress') |
                (self.sprint_data['status'] == 'Completed')
            ]['sprint_id'].tolist()
            
            available_tasks = backlog_tasks[
                ~backlog_tasks['sprint_id'].isin(active_sprints)
            ]
        else:
            available_tasks = backlog_tasks
        
        return available_tasks
    
    def assign_task_to_sprint(self, task_key: str, sprint_id: str, developer_name: str) -> None:
        """Assign a task to a sprint and developer."""
        if self.backlog_data is None or self.backlog_data.empty:
            raise ValueError("No backlog data available")
        
        # Update task status and sprint assignment
        task_mask = self.backlog_data['issue_key'] == task_key
        if not any(task_mask):
            raise ValueError(f"Task {task_key} not found")
        
        self.backlog_data.loc[task_mask, 'status'] = 'In Progress'
        self.backlog_data.loc[task_mask, 'sprint_id'] = sprint_id
        self.backlog_data.loc[task_mask, 'assigned_to'] = developer_name
    
    def add_task(self, task_data: Dict[str, Any]) -> None:
        """Add a new task to the backlog."""
        if self.backlog_data is None:
            self.backlog_data = pd.DataFrame()
        
        # Convert dependencies and skills to strings
        task_data['dependencies'] = ','.join(task_data.get('dependencies', []))
        task_data['skills'] = ','.join(task_data.get('skills', []))

        print(task_data)
        
        # Add the task
        self.backlog_data = pd.concat([
            self.backlog_data,
            pd.DataFrame([task_data])
        ], ignore_index=True)

    def deleteAll_task(self) -> None:
        """Add a new task to the backlog."""
        self.backlog_data = None
        

    def add_rep_task(self, task_data: Dict[str, Any]) -> None:
        """Add a new task to the backlog."""
        if self.backlog_data is None:
            self.backlog_data = pd.DataFrame()
        
        # Convert dependencies and skills to strings
        print(task_data)
        
        # Add the task
        self.backlog_data = pd.concat([
            self.backlog_data,
            pd.DataFrame([task_data])
        ], ignore_index=True)
    
    def update_task(self, task_key: str, updates: Dict[str, Any]) -> None:
        """Update an existing task."""
        if self.backlog_data is None:
            raise Exception("No backlog data available")
        
        # Find the task
        task_idx = self.backlog_data[self.backlog_data['issue_key'] == task_key].index
        if len(task_idx) == 0:
            raise Exception(f"Task {task_key} not found")
        
        # Convert dependencies and skills to strings if present
        if 'dependencies' in updates:
            updates['dependencies'] = ','.join(updates['dependencies'])
        if 'skills' in updates:
            updates['skills'] = ';'.join(updates['skills'])
        
        # Update the task
        for key, value in updates.items():
            self.backlog_data.loc[task_idx[0], key] = value
    
    def delete_task(self, task_key: str) -> None:
        """Delete a task from the backlog."""
        if self.backlog_data is None:
            raise Exception("No backlog data available")
        
        # Find and remove the task
        task_idx = self.backlog_data[self.backlog_data['issue_key'] == task_key].index
        if len(task_idx) == 0:
            raise Exception(f"Task {task_key} not found")
        
        self.backlog_data = self.backlog_data.drop(task_idx)
    
    def add_developer(self, dev_data: Dict[str, Any]) -> None:
        """Add a new developer to the team."""
        if self.team_data is None:
            self.team_data = pd.DataFrame()
        
        # Convert skills and preferences to strings
        dev_data['skill_sets'] = ';'.join(dev_data.get('skill_sets', []))
        dev_data['preferences'] = ';'.join(dev_data.get('preferences', []))
        
        # Add the developer
        self.team_data = pd.concat([
            self.team_data,
            pd.DataFrame([dev_data])
        ], ignore_index=True)
    
    def update_developer(self, dev_name: str, updates: Dict[str, Any]) -> None:
        """Update an existing developer."""
        if self.team_data is None:
            raise Exception("No team data available")
        
        # Find the developer
        dev_idx = self.team_data[self.team_data['developer_name'] == dev_name].index
        if len(dev_idx) == 0:
            raise Exception(f"Developer {dev_name} not found")
        
        # Convert skills and preferences to strings if present
        if 'skill_sets' in updates:
            updates['skill_sets'] = ';'.join(updates['skill_sets'])
        if 'preferences' in updates:
            updates['preferences'] = ';'.join(updates['preferences'])
        
        # Update the developer
        for key, value in updates.items():
            self.team_data.loc[dev_idx[0], key] = value
    
    def delete_developer(self, dev_name: str) -> None:
        """Delete a developer from the team."""
        if self.team_data is None:
            raise Exception("No team data available")
        
        # Find and remove the developer
        dev_idx = self.team_data[self.team_data['developer_name'] == dev_name].index
        if len(dev_idx) == 0:
            raise Exception(f"Developer {dev_name} not found")
        
        self.team_data = self.team_data.drop(dev_idx)
    
    def add_sprint(self, sprint_data: Dict[str, Any]) -> None:
        """Add a new sprint."""
        if self.sprint_data is None:
            self.sprint_data = pd.DataFrame()
        
        # Convert dates to datetime
        sprint_data['start_date'] = pd.to_datetime(sprint_data['start_date'])
        sprint_data['end_date'] = pd.to_datetime(sprint_data['end_date'])
        
        # Add the sprint
        self.sprint_data = pd.concat([
            self.sprint_data,
            pd.DataFrame([sprint_data])
        ], ignore_index=True)
    
    def update_sprint(self, sprint_id: str, updates: Dict[str, Any]) -> None:
        """Update an existing sprint."""
        if self.sprint_data is None:
            raise Exception("No sprint data available")
        
        # Find the sprint
        sprint_idx = self.sprint_data[self.sprint_data['sprint_id'] == sprint_id].index
        if len(sprint_idx) == 0:
            raise Exception(f"Sprint {sprint_id} not found")
        
        # Convert dates to datetime if present
        if 'start_date' in updates:
            updates['start_date'] = pd.to_datetime(updates['start_date'])
        if 'end_date' in updates:
            updates['end_date'] = pd.to_datetime(updates['end_date'])
        
        # Update the sprint
        for key, value in updates.items():
            self.sprint_data.loc[sprint_idx[0], key] = value
    
    def delete_sprint(self, sprint_id: str) -> None:
        """Delete a sprint."""
        if self.sprint_data is None:
            raise Exception("No sprint data available")
        
        # Find and remove the sprint
        sprint_idx = self.sprint_data[self.sprint_data['sprint_id'] == sprint_id].index
        if len(sprint_idx) == 0:
            raise Exception(f"Sprint {sprint_id} not found")
        
        self.sprint_data = self.sprint_data.drop(sprint_idx)
    
    def save_data(self, data_type: str, file_path: Union[str, Path]) -> bool:
        """Save data to a CSV file."""
        try:
            if data_type == 'backlog' and self.backlog_data is not None:
                self.backlog_data.to_csv(file_path, index=False)
            elif data_type == 'sprint' and self.sprint_data is not None:
                self.sprint_data.to_csv(file_path, index=False)
            elif data_type == 'team' and self.team_data is not None:
                self.team_data.to_csv(file_path, index=False)
            return True
        except Exception as e:
            print(f"Error saving {data_type} data: {str(e)}")
            return False
        

    def load_forecast_velocity(self):
        """Load forecast velocity data."""
        try:
            # Load the forecasted velocity data
            forecaster.simulate_historical_data()
            forecaster.prepare_data(test_data_percentage=0.2)
            forecaster.train_model()
            mae, y_pred_test = forecaster.evaluate_model() # You can use MAE here if needed
            forecaster.forecast_velocity()
            forecaster.prepare_plotting_data()
            # Get and print the JSON output
            json_output = forecaster.to_json()
            self.forecasted_velocity = json_output
            return True
        except Exception as e:
            print(f"Error loading forecast velocity data: {str(e)}")
            return False
    
    def get_task_dependencies(self) -> Dict[str, List[str]]:
        """Get the dependencies for each task."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        return dict(zip(self.backlog_data['issue_key'], self.backlog_data['dependencies']))
    
    def get_task_skills(self) -> Dict[str, List[str]]:
        """Get the required skills for each task."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        return dict(zip(self.backlog_data['issue_key'], self.backlog_data['skills']))
    
    def get_developer_skills(self) -> Dict[str, List[str]]:
        """Get the skills for each developer."""
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        return dict(zip(self.team_data['developer_name'], self.team_data['skill_sets']))
    
    def get_task_priorities(self) -> Dict[str, int]:
        """Get the priority for each task."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        return dict(zip(self.backlog_data['issue_key'], self.backlog_data['priority']))
    
    def get_task_points(self) -> Dict[str, float]:
        """Get the story points for each task."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        return dict(zip(self.backlog_data['issue_key'], self.backlog_data['story_points']))
    
    def get_sprint_tasks(self, sprint_id):
        """Get all tasks assigned to a specific sprint."""
        if self.backlog_data is None:
            return pd.DataFrame()
        
        return self.backlog_data[self.backlog_data['sprint_id'] == sprint_id]
    
    def get_developer_capacity(self) -> Dict[str, float]:
        """Get the effective capacity for each developer."""
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        return dict(zip(self.team_data['developer_name'], self.team_data['effective_capacity']))
    
    def get_task_distribution(self) -> Dict[str, List[str]]:
        """Get the distribution of tasks across sprints."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        tasks = self.backlog_data['issue_key'].tolist()

       

        
    
    
        developers = self.team_data['developer_name'].tolist()
        

        task_priorities = dict(zip(self.backlog_data['issue_key'], self.backlog_data['priority']))
        
    
        task_points = dict(zip(self.backlog_data['issue_key'], self.backlog_data['story_points'].astype(int)))  # Ensure integers
        
    
    
        # Use effective capacity if available, otherwise use regular capacity

        if 'effective_capacity' in self.team_data.columns:
            developer_capacity = dict(zip(self.team_data['developer_name'], self.team_data['effective_capacity'].astype(int)))  # Ensure integers
        else:
            developer_capacity = dict(zip(self.team_data['developer_name'], self.team_data['capacity'].astype(int)))  # Ensure integers
        
        
    
        
        task_dependencies = dict(zip(self.backlog_data['issue_key'], self.backlog_data['dependencies'].apply(lambda x: x.split(',') if isinstance(x, str) else [])))

        
    
        task_skills = dict(zip(self.backlog_data['issue_key'], self.backlog_data['skills'].apply(lambda x: x.split(',') if isinstance(x, str) else [])))

        
    
        
        developer_skills = dict(zip(self.team_data['developer_name'], self.team_data['skill_sets']))

        

        assert isinstance(tasks, list) and all(isinstance(t, str) for t in tasks), "Tasks must be List[str]"
                
        assert isinstance(developers, list) and all(isinstance(d, str) for d in developers), "Developers must be List[str]"
                
        assert isinstance(task_priorities, dict) and all(isinstance(k, str) and isinstance(v, int) for k, v in task_priorities.items()), "Task priorities must be Dict[str, int]"
                
        assert isinstance(task_points, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in task_points.items()), "Task points must be Dict[str, float]"
                
        assert isinstance(developer_capacity, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in developer_capacity.items()), "Developer capacity must be Dict[str, float]"
                
                
        assert isinstance(task_dependencies, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(dep, str) for dep in v) for k, v in task_dependencies.items()), "Task dependencies must be Dict[str, List[str]]"
                
       
        assert isinstance(task_skills, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(skill, str) for skill in v) for k, v in task_skills.items()), "Task skills must be Dict[str, List[str]]"
        
        assert isinstance(developer_skills, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(skill, str) for skill in v) for k, v in developer_skills.items()), "Developer skills must be Dict[str, List[str]]"
        
        print("Task Priorities")
        print(task_priorities)
        print("Task Points")
        print(task_points)
        print("Developer Capacity")
        print(developer_capacity)
        print("Task Dependencies")
        print(task_dependencies)
        print("Task Skills")
        print(task_skills)
        print("Developer Skills")
        print(developer_skills)
        
        
        print("All data types are correct.")
        print("Task Length",developer_capacity)

        optimizer.create_optimization_model(
                    tasks,
                    developers,
                    task_priorities,
                    task_points,
                    developer_capacity,
                    task_dependencies,
                    task_skills,
                    developer_skills
                )
        print("Solve")
        #task_selection, task_assignments = optimizer.solve(time_limit=5.0)
        task_selection, task_assignments = optimizer.solve()
        print("Task Selection")
        print(task_selection)
        print("Task Assignments")
        print(task_assignments)
        print("Optimisation Summary")
        optimization_summary = optimizer.get_optimization_summary(
                    task_selection,
                    task_assignments,
                    task_points,
                    developer_capacity
                )
        
        print(optimization_summary)
        
        
        return optimization_summary
    
    def get_forecasted_velocity_value(self) -> dict:
        """Return the value of forecasted velocity stored in self.forecasted_velocity as JSON."""
        try:
            if hasattr(self, 'forecasted_velocity') and self.forecasted_velocity is not None:
                return {"forecasted_velocity": self.forecasted_velocity}
            else:
                raise ValueError("Forecasted velocity is not available.")
        except Exception as e:
            print(f"Error retrieving forecasted velocity: {str(e)}")
            return {"error": str(e)}
    
    def get_holidays_and_leaves(self) -> dict:
        """Return the values of holidays and leaves in JSON format."""
        try:
            holidays_json = self.holidays.to_dict(orient='records') if self.holidays is not None else []
            leaves_json = self.leaves.to_dict(orient='records') if self.leaves is not None else []
            return {"holidays": holidays_json, "leaves": leaves_json}
        except Exception as e:
            print(f"Error retrieving holidays and leaves: {str(e)}")
            return {"error": str(e)}
        
    def get_task_distribution_new(self) -> Dict[str, List[str]]:
        """Get the distribution of tasks across sprints."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        if self.team_data is None:
            raise ValueError("Team data not loaded")

        tasks = self.backlog_data['issue_key'].tolist()
        developers = self.team_data['developer_name'].tolist()
        print("developers",developers)

        # Calculate daily capacity for each developer
        developer_daily_capacity = {}
        holidays_set = set(self.holidays['date'].tolist()) if self.holidays is not None else set()
        leaves_grouped = self.leaves.groupby('developer') if self.leaves is not None else {}

        print("Holidays Set",holidays_set)
        print("Leaves Grouped",leaves_grouped)

        try:
            for developer in developers:
                developer_daily_capacity[developer] = {}
                developer_leaves = set(leaves_grouped.get_group(developer)['date'].tolist()) if developer in leaves_grouped.groups else set()

                print("Developer Leaves", developer_leaves)
                for day in pd.date_range(start="2025-05-01", end="2025-05-14"):
                    day_str = day.strftime('%Y-%m-%d')
                    # Skip weekends
                    if day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                        continue
                    if day_str in holidays_set or day_str in developer_leaves:
                        developer_daily_capacity[developer][day_str] = 0.0
                    else:
                        developer_daily_capacity[developer][day_str] = 8.0
        except Exception as e:
            print(f"Error calculating developer daily capacity: {str(e)}")
            developer_daily_capacity = {developer: 8.0 for developer in developers}

        print("Developer Daily Capacity:", developer_daily_capacity)

        # Existing logic for task distribution
        task_priorities = dict(zip(self.backlog_data['issue_key'], self.backlog_data['priority']))
        task_points = dict(zip(self.backlog_data['issue_key'], self.backlog_data['story_points'].astype(int)))

        if 'effective_capacity' in self.team_data.columns:
            developer_capacity = dict(zip(self.team_data['developer_name'], self.team_data['effective_capacity'].astype(int)))
        else:
            developer_capacity = dict(zip(self.team_data['developer_name'], self.team_data['capacity'].astype(int)))

        task_dependencies = dict(zip(self.backlog_data['issue_key'], self.backlog_data['dependencies'].apply(lambda x: x.split(',') if isinstance(x, str) else [])))
        task_skills = dict(zip(self.backlog_data['issue_key'], self.backlog_data['skills'].apply(lambda x: x.split(',') if isinstance(x, str) else [])))
        developer_skills = dict(zip(self.team_data['developer_name'], self.team_data['skill_sets']))

        assert isinstance(tasks, list) and all(isinstance(t, str) for t in tasks), "Tasks must be List[str]"
                
        assert isinstance(developers, list) and all(isinstance(d, str) for d in developers), "Developers must be List[str]"
                
        assert isinstance(task_priorities, dict) and all(isinstance(k, str) and isinstance(v, int) for k, v in task_priorities.items()), "Task priorities must be Dict[str, int]"
                
        assert isinstance(task_points, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in task_points.items()), "Task points must be Dict[str, float]"
                
        assert isinstance(developer_capacity, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in developer_capacity.items()), "Developer capacity must be Dict[str, float]"
                
                
        assert isinstance(task_dependencies, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(dep, str) for dep in v) for k, v in task_dependencies.items()), "Task dependencies must be Dict[str, List[str]]"
                
       
        assert isinstance(task_skills, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(skill, str) for skill in v) for k, v in task_skills.items()), "Task skills must be Dict[str, List[str]]"
        
        assert isinstance(developer_skills, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(skill, str) for skill in v) for k, v in developer_skills.items()), "Developer skills must be Dict[str, List[str]]"
        
        print("Task Priorities")
        print(task_priorities)
        print("Task Points")
        print(task_points)
        print("Developer Capacity")
        print(developer_capacity)
        print("Task Dependencies")
        print(task_dependencies)
        print("Task Skills")
        print(task_skills)
        print("Developer Skills")
        print(developer_skills)
        
        
        print("All data types are correct.")
        
        print(developer_daily_capacity)

        optimizerNew.create_optimization_model(
            tasks,
            developers,
            task_priorities,
            task_points,
            developer_capacity,
            task_dependencies,
            task_skills,
            developer_skills,
            sprint_start_date="2025-05-01",
            sprint_end_date="2025-05-14",
            developer_daily_capacity=developer_daily_capacity,
            penalty_workload_imbalance=0.5, # Higher penalty for imbalance
            penalty_context_switching=0.05, # Higher penalty for context switching
            penalty_late_completion=0.01   
        )

        task_selection, task_assignments, work_schedule, points_schedule = optimizerNew.solve()
        print("Task Selection")
        summary = optimizerNew.get_optimization_summary(
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
                      daily_cap = optimizerNew._developer_daily_capacity.get(dev, {}).get(day_str, 0.0)
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
        optimization_summary = optimizerNew.get_optimization_summary(
            task_selection, task_assignments, work_schedule, points_schedule
        )
        optimization_summary['optimization_details'] = {
            "total_tasks_considered": summary['total_tasks_considered'],
            "total_tasks_selected": summary['total_tasks_selected'],
            "total_story_points_selected": summary['total_story_points_selected'],
            "total_story_points_scheduled": summary['total_story_points_scheduled'],
            "objective_value": summary['objective_value'],
            "sprint_working_days": len(summary['sprint_working_days']),
            "developer_utilization": {
                dev: {
                    "total_sprint_capacity_input": data['total_sprint_capacity_input'],
                    "total_daily_sum_capacity": data['total_daily_sum_capacity'],
                    "total_points_scheduled": data['total_points_scheduled'],
                    "utilization_rate_vs_daily_sum": data['utilization_rate_vs_daily_sum'],
                    "tasks_assigned_by_optimizer": data['tasks_assigned_by_optimizer'] or []
                } for dev, data in summary['developer_utilization'].items()
            },
            "soft_constraint_metrics": {
                "workload_imbalance_deviation": metrics['workload_imbalance_deviation'],
                "max_developer_workload": metrics['max_developer_workload'],
                "min_developer_workload": metrics['min_developer_workload'],
                "total_context_switches": metrics['total_context_switches'],
                "total_late_completion_penalty_points": metrics['total_late_completion_penalty_points']
            },
            "developer_daily_schedule": {
                dev: [
                    {
                        "day": day_str,
                        "capacity": optimizerNew._developer_daily_capacity.get(dev, {}).get(day_str, 0.0),
                        "tasks": [
                            {"task": item['task'], "points": item['points']}
                            for item in sorted(schedule[day_str], key=lambda item: item['points'], reverse=True)
                        ]
                    } for day_str in sorted(schedule.keys())
                ] if schedule else []
                for dev, schedule in summary['developer_daily_schedule'].items()
            },
            "detailed_assignment_results": {
                "selected_tasks": [
                    {
                        "task": t,
                        "priority": task_priorities.get(t, 0),
                        "points": task_points.get(t, 0),
                        "assigned_to": next((dev for dev in developers if task_assignments.get((t, dev), False)), None)
                    } for t in task_selection if task_selection[t]
                ]
            }
        }
        self.sprint_task_distribution= optimization_summary
        return optimization_summary