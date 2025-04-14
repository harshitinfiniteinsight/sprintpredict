import pandas as pd
import numpy as np
from typing import Tuple, Dict, List, Any, Optional, Union
from pathlib import Path

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
    
    def load_backlog(self, file_path: Union[str, Path]) -> bool:
        """Load product backlog data."""
        try:
            df = pd.read_csv(file_path)
            
            # Ensure required columns exist
            required_columns = ['issue_key', 'summary', 'description', 'priority', 'story_points', 
                              'dependencies', 'pre_mapped_skills', 'status', 'sprint_id']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert string representations of lists to actual lists
            df['dependencies'] = df['dependencies'].apply(lambda x: x.split(',') if pd.notna(x) else [])
            df['pre_mapped_skills'] = df['pre_mapped_skills'].apply(lambda x: x.split(';') if pd.notna(x) else [])
            
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
        task_data['pre_mapped_skills'] = ';'.join(task_data.get('pre_mapped_skills', []))
        
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
        if 'pre_mapped_skills' in updates:
            updates['pre_mapped_skills'] = ';'.join(updates['pre_mapped_skills'])
        
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
    
    def get_task_dependencies(self) -> Dict[str, List[str]]:
        """Get the dependencies for each task."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        return dict(zip(self.backlog_data['issue_key'], self.backlog_data['dependencies']))
    
    def get_task_skills(self) -> Dict[str, List[str]]:
        """Get the required skills for each task."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        return dict(zip(self.backlog_data['issue_key'], self.backlog_data['pre_mapped_skills']))
    
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