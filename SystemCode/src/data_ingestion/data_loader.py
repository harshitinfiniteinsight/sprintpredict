import pandas as pd
import numpy as np
from typing import Tuple, Dict, List
from pathlib import Path

class DataLoader:
    def __init__(self):
        self.backlog_data = None
        self.sprint_data = None
        self.team_data = None
        
    def load_backlog(self, file_path: str) -> pd.DataFrame:
        """Load and preprocess product backlog data."""
        df = pd.read_csv(file_path)
        
        # Standardize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Remove the priority mapping logic as priorities are now integers
        # df['priority'] = df['priority'].str.lower().map(priority_map)
        
        # Convert dependencies to list
        df['dependencies'] = df['dependencies'].fillna('').apply(
            lambda x: x.split(',') if isinstance(x, str) else []
        )
        
        # Convert pre-mapped skills to list
        df['pre_mapped_skills'] = df['pre_mapped_skills'].fillna('').apply(
            lambda x: [skill.strip() for skill in str(x).split(',') if skill.strip()]
        )
        
        # Ensure story points is numeric
        df['story_points'] = pd.to_numeric(df['story_points'], errors='coerce')
        
        self.backlog_data = df
        return df
    
    def load_sprint_data(self, file_path: str) -> pd.DataFrame:
        """Load and preprocess historical sprint data."""
        df = pd.read_csv(file_path)
        
        # Standardize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Convert task_ids to list
        df['task_ids'] = df['task_ids'].fillna('').apply(
            lambda x: [task.strip() for task in str(x).split(';') if task.strip()]
        )
        
        # Ensure numeric columns
        numeric_columns = ['story_points_committed', 'story_points_completed', 'slippage']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Calculate completion rate
        df['completion_rate'] = df['story_points_completed'] / df['story_points_committed']
        
        self.sprint_data = df
        return df
    
    def load_team_data(self, file_path: str) -> pd.DataFrame:
        """Load and preprocess team data."""
        df = pd.read_csv(file_path)
        
        # Standardize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Convert skill sets to list
        df['skill_sets'] = df['skill_sets'].fillna('').apply(
            lambda x: [skill.strip() for skill in str(x).split(';') if skill.strip()]
        )
        
        # Convert preferences to list
        df['preferences'] = df['preferences'].fillna('').apply(
            lambda x: [pref.strip() for pref in str(x).split(';') if pref.strip()]
        )
        
        # Ensure capacity is numeric
        df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')
        
        # Calculate effective capacity (80% of capacity)
        df['effective_capacity'] = df['capacity'] * 0.8
        
        self.team_data = df
        return df
    
    def get_developer_capacity(self) -> Dict[str, float]:
        """Get the effective capacity for each developer."""
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        return dict(zip(self.team_data['developer_name'], self.team_data['effective_capacity']))
    
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
    
    def save_data(self, data_type: str, filepath: str):
        """Save data to CSV file."""
        if data_type == 'backlog' and self.backlog_data is not None:
            self.backlog_data.to_csv(filepath, index=False)
        elif data_type == 'sprint' and self.sprint_data is not None:
            self.sprint_data.to_csv(filepath, index=False)
        elif data_type == 'team' and self.team_data is not None:
            self.team_data.to_csv(filepath, index=False)
        else:
            raise ValueError(f"No data available to save for type: {data_type}")
    
    def update_task(self, task_key: str, updates: Dict) -> None:
        """Update a task in the backlog."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        mask = self.backlog_data['issue_key'] == task_key
        if not mask.any():
            raise ValueError(f"Task not found: {task_key}")
        
        for key, value in updates.items():
            if key in self.backlog_data.columns:
                self.backlog_data.loc[mask, key] = value
    
    def update_developer(self, developer_name: str, updates: Dict) -> None:
        """Update a developer in the team data."""
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        mask = self.team_data['developer_name'] == developer_name
        if not mask.any():
            raise ValueError(f"Developer not found: {developer_name}")
        
        for key, value in updates.items():
            if key in self.team_data.columns:
                self.team_data.loc[mask, key] = value
    
    def add_task(self, task_data: Dict) -> None:
        """Add a new task to the backlog."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        # Ensure all required fields are present
        required_fields = ['issue_key', 'summary', 'description', 'priority', 'story_points']
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert lists to strings for CSV storage
        if 'dependencies' in task_data:
            task_data['dependencies'] = ','.join(task_data['dependencies'])
        if 'pre_mapped_skills' in task_data:
            task_data['pre_mapped_skills'] = ','.join(task_data['pre_mapped_skills'])
        
        # Add the new task
        self.backlog_data = pd.concat([self.backlog_data, pd.DataFrame([task_data])], ignore_index=True)
    
    def add_developer(self, developer_data: Dict) -> None:
        """Add a new developer to the team data."""
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        # Ensure all required fields are present
        required_fields = ['developer_name', 'role', 'capacity']
        for field in required_fields:
            if field not in developer_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert lists to strings for CSV storage
        if 'skill_sets' in developer_data:
            developer_data['skill_sets'] = ';'.join(developer_data['skill_sets'])
        if 'preferences' in developer_data:
            developer_data['preferences'] = ';'.join(developer_data['preferences'])
        
        # Calculate effective capacity
        developer_data['effective_capacity'] = float(developer_data['capacity']) * 0.8
        
        # Add the new developer
        self.team_data = pd.concat([self.team_data, pd.DataFrame([developer_data])], ignore_index=True)
    
    def delete_task(self, task_key: str) -> None:
        """Delete a task from the backlog."""
        if self.backlog_data is None:
            raise ValueError("Backlog data not loaded")
        
        mask = self.backlog_data['issue_key'] == task_key
        if not mask.any():
            raise ValueError(f"Task not found: {task_key}")
        
        self.backlog_data = self.backlog_data[~mask]
    
    def delete_developer(self, developer_name: str) -> None:
        """Delete a developer from the team data."""
        if self.team_data is None:
            raise ValueError("Team data not loaded")
        
        mask = self.team_data['developer_name'] == developer_name
        if not mask.any():
            raise ValueError(f"Developer not found: {developer_name}")
        
        self.team_data = self.team_data[~mask]
    
    def add_sprint(self, sprint_data: Dict):
        """Add a new sprint to the sprint data."""
        # Convert task_ids string to list
        sprint_data['task_ids'] = sprint_data['task_ids'].split(';')
        
        # Create new row
        new_row = pd.DataFrame([sprint_data])
        self.sprint_data = pd.concat([self.sprint_data, new_row], ignore_index=True)
    
    def update_sprint(self, sprint_id: str, updates: Dict):
        """Update an existing sprint."""
        # Convert task_ids string to list if present
        if 'task_ids' in updates:
            updates['task_ids'] = updates['task_ids'].split(';')
        
        # Update the sprint
        mask = self.sprint_data['sprint_id'] == sprint_id
        for col, value in updates.items():
            self.sprint_data.loc[mask, col] = value
    
    def delete_sprint(self, sprint_id: str):
        """Delete a sprint from the sprint data."""
        self.sprint_data = self.sprint_data[self.sprint_data['sprint_id'] != sprint_id]