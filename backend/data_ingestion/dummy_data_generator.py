import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import openai
from openai import OpenAI
import os
from dotenv import load_dotenv
import streamlit as st
from typing import Dict, List, Any

class DummyDataGenerator:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client with API key from environment variable
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not found in environment variables")
            self.client = OpenAI(api_key=api_key)
        except Exception as e:
            st.error(f"Error initializing OpenAI client: {str(e)}")
            self.client = None
        
        # Define common data
        self.priorities = ["High", "Medium", "Low"]
        self.skills = [
            "Python", "Java", "JavaScript", "React", "Angular", "Node.js",
            "SQL", "MongoDB", "AWS", "Docker", "Kubernetes", "CI/CD",
            "Machine Learning", "Data Analysis", "UI/UX Design", "DevOps"
        ]
        self.roles = [
            "Backend Developer", "Frontend Developer", "Full Stack Developer",
            "DevOps Engineer", "Data Engineer", "ML Engineer", "UI/UX Designer"
        ]
        self.features = [
            "User Authentication", "Database Migration", "API Integration",
            "UI Component", "Performance Optimization", "Security Feature",
            "Monitoring System", "Deployment Pipeline", "Testing Framework",
            "Documentation", "Code Refactoring", "Feature Enhancement",
            "Bug Fix", "Infrastructure Setup", "Data Processing"
        ]
        
        self.tasks = []
        self.sprints = []
        self.developers = []
        self.future_capacity = []
    
    def generate_task_descriptions(self, task_types):
        """Generate multiple task descriptions in a single API call."""
        if not self.client:
            return [f"Detailed description for {task_type} feature. This task involves various aspects of development." 
                   for task_type in task_types]
            
        prompt = f"""Generate detailed technical task descriptions for the following features in a software development project.
        For each task, include:
        1. Technical requirements
        2. Implementation details
        3. Testing requirements
        4. Acceptance criteria
        
        Format each task as a proper user story.
        Keep each description concise (max 100 words) but informative and technical.
        
        Tasks to describe:
        {', '.join(task_types)}
        
        Provide the descriptions in a numbered list format."""
        
        try:
            with st.spinner("Generating task descriptions..."):
                response = self.client.chat.completions.create(
                    model="gpt-4-0125-preview",  # Using the latest GPT-4 model
                    messages=[
                        {"role": "system", "content": "You are a technical product owner creating detailed user stories and tasks for a software development team."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                # Split the response into individual descriptions
                descriptions = response.choices[0].message.content.strip().split('\n')
                # Clean up the descriptions
                descriptions = [desc.strip().lstrip('1234567890.)') for desc in descriptions if desc.strip()]
                return descriptions[:len(task_types)]  # Ensure we return exactly the number of descriptions we need
        except Exception as e:
            st.error(f"Error generating task descriptions: {str(e)}")
            return [f"Detailed description for {task_type} feature. This task involves various aspects of development." 
                   for task_type in task_types]
    
    def generate_backlog_data(self):
        """Generate dummy product backlog data with realistic tasks."""
        with st.spinner("Generating backlog data..."):
            tasks = []
            num_tasks = 50
            
            # Define common task types
            task_types = [
                "User Authentication", "Database Migration", "API Integration",
                "UI Component", "Performance Optimization", "Security Feature",
                "Monitoring System", "Deployment Pipeline", "Testing Framework",
                "Documentation", "Code Refactoring", "Feature Enhancement",
                "Bug Fix", "Infrastructure Setup", "Data Processing"
            ]
            
            # Generate all task descriptions in one API call
            descriptions = self.generate_task_descriptions(task_types)
            
            progress_bar = st.progress(0)
            for i in range(num_tasks):
                # Update progress
                progress_bar.progress((i + 1) / num_tasks)
                
                # Generate dependencies (some tasks depend on others)
                dependencies = []
                if i > 0 and np.random.random() < 0.3:  # 30% chance of having dependencies
                    num_deps = np.random.randint(1, min(4, i + 1))
                    dependencies = [f"PROJ-{j+1}" for j in np.random.choice(i, num_deps, replace=False)]
                
                # Generate required skills
                num_skills = np.random.randint(1, 5)
                required_skills = np.random.choice(self.skills, num_skills, replace=False)
                
                # Generate story points (Fibonacci-like sequence)
                story_points = np.random.choice([1, 2, 3, 5, 8, 13])
                
                # Determine if task is completed or in backlog
                status = np.random.choice(["Completed", "Backlog"], p=[0.4, 0.6])
                sprint_id = f"SPRINT-{np.random.randint(1, 4)}" if status == "Completed" else ""
                
                # Generate task type and description
                task_type = np.random.choice(task_types)
                description = descriptions[task_types.index(task_type)]
                
                task = {
                    'issue_key': f"PROJ-{i+1}",
                    'summary': f"{task_type} - {np.random.choice(['Implement', 'Design', 'Test', 'Review', 'Document'])}",
                    'description': description,
                    'priority': np.random.choice(self.priorities),
                    'story_points': story_points,
                    'dependencies': ','.join(dependencies),
                    'pre_mapped_skills': ';'.join(required_skills),
                    'status': status,
                    'sprint_id': sprint_id
                }
                tasks.append(task)
            
            progress_bar.empty()
            return pd.DataFrame(tasks)
    
    def generate_sprint_data(self):
        """Generate dummy sprint data."""
        sprints = []
        num_sprints = 5
        
        for i in range(num_sprints):
            start_date = datetime.now() - timedelta(days=70) + timedelta(days=i*14)
            end_date = start_date + timedelta(days=13)
            
            # Generate story points
            total_points = np.random.randint(20, 40)
            completed_points = np.random.randint(15, total_points + 1)
            
            # Determine sprint status
            if i < 2:  # First two sprints are completed
                status = "Completed"
            elif i == 2:  # Current sprint is in progress
                status = "In Progress"
            else:  # Future sprints
                status = "Not Started"
            
            sprint = {
                'sprint_id': f"SPRINT-{i+1}",
                'sprint_name': f"Sprint {i+1}",
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'status': status,
                'completed_story_points': completed_points,
                'total_story_points': total_points
            }
            sprints.append(sprint)
        
        return pd.DataFrame(sprints)
    
    def generate_team_data(self):
        """Generate dummy team data."""
        developers = []
        num_developers = 8
        
        for i in range(num_developers):
            # Generate skills (2-5 skills per developer)
            num_skills = np.random.randint(2, 6)
            developer_skills = np.random.choice(self.skills, num_skills, replace=False)
            
            # Generate preferences (1-2 preferences per developer)
            num_prefs = np.random.randint(1, 3)
            preferences = np.random.choice(['Frontend', 'Backend', 'Full Stack', 'DevOps'], num_prefs, replace=False)
            
            # Generate capacity (based on role)
            role = np.random.choice(self.roles)
            if "Senior" in role or "Lead" in role:
                capacity = np.random.randint(15, 20)
            elif "Junior" in role:
                capacity = np.random.randint(5, 10)
            else:
                capacity = np.random.randint(10, 15)
            
            developer = {
                'developer_name': f"Developer {i+1}",
                'role': role,
                'capacity': capacity,
                'skill_sets': ';'.join(developer_skills),
                'preferences': ';'.join(preferences)
            }
            developers.append(developer)
        
        return pd.DataFrame(developers)
    
    def generate_future_capacity(self):
        """Generate future capacity data for developers."""
        future_capacity = []
        
        # Get future sprints (SPRINT-5 and beyond)
        future_sprints = self.sprints[self.sprints['sprint_id'].str.startswith('SPRINT-5')]
        
        for _, sprint in future_sprints.iterrows():
            for _, dev in self.team_data.iterrows():
                # Generate base capacity between 5 and 20 story points
                base_capacity = np.random.randint(5, 21)  # Changed from 5,20 to 5,21 to include 20
                
                # Generate availability between 80% and 100%
                availability = np.random.uniform(0.8, 1.0)
                
                # Calculate actual capacity
                actual_capacity = int(base_capacity * availability)
                
                future_capacity.append({
                    'sprint_id': sprint['sprint_id'],
                    'developer_name': dev['developer_name'],
                    'capacity': actual_capacity,
                    'availability': round(availability, 2)  # Round to 2 decimal places
                })
        
        return pd.DataFrame(future_capacity)
    
    def generate_dummy_data(self) -> Dict[str, pd.DataFrame]:
        """Generate all dummy data."""
        # Generate sprints first
        self.sprints = self.generate_sprint_data()
        
        # Generate team data
        self.team_data = self.generate_team_data()
        
        # Generate tasks
        self.backlog_data = self.generate_backlog_data()
        
        # Generate future capacity
        self.future_capacity_data = self.generate_future_capacity()
        
        return {
            'sprint_data': self.sprints,
            'team_data': self.team_data,
            'backlog_data': self.backlog_data,
            'future_capacity_data': self.future_capacity_data
        }
    
    def _generate_developers(self):
        """Generate dummy developer data."""
        developer_names = [
            "John Smith", "Emma Wilson", "Michael Chen", "Sarah Johnson",
            "David Brown", "Lisa Anderson", "James Wilson", "Maria Garcia"
        ]
        
        for name in developer_names:
            # Randomly select 3-5 skills
            num_skills = np.random.randint(3, 6)
            selected_skills = np.random.choice(self.skills, num_skills, replace=False)
            
            # Randomly select a role
            role = np.random.choice(self.roles)
            
            # Generate capacity between 10 and 20 story points
            capacity = np.random.randint(10, 21)
            
            # Generate preferences (randomly select 2-3 skills they prefer to work with)
            num_preferences = np.random.randint(2, 4)
            preferences = np.random.choice(selected_skills, num_preferences, replace=False)
            
            self.developers.append({
                "developer_name": name,
                "role": role,
                "capacity": capacity,
                "skill_sets": ";".join(selected_skills),
                "preferences": ";".join(preferences)
            })
    
    def _generate_sprints(self):
        """Generate dummy sprint data."""
        # Generate 5 sprints
        for i in range(5):
            sprint_id = f"SPRINT-{i+1}"
            start_date = datetime.now() + timedelta(days=i*14)
            end_date = start_date + timedelta(days=13)
            
            # Generate random story points
            total_points = np.random.randint(30, 51)
            completed_points = np.random.randint(20, total_points + 1)
            
            self.sprints.append({
                "sprint_id": sprint_id,
                "sprint_name": f"Sprint {i+1}",
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "status": "Completed" if i < 3 else "In Progress" if i == 3 else "Not Started",
                "completed_story_points": completed_points,
                "total_story_points": total_points
            })
    
    def _generate_tasks(self):
        """Generate dummy tasks with realistic data."""
        tasks = []
        task_types = {
            "Feature": (3, 8),  # Medium complexity features
            "Bug": (1, 5),      # Bug fixes
            "Enhancement": (2, 6),  # Small improvements
            "Integration": (4, 10),  # Integration work
            "Testing": (2, 5),  # Testing tasks
            "Deployment": (3, 7),  # Deployment tasks
            "Security": (3, 8),  # Security tasks
            "Documentation": (1, 4)  # Documentation tasks
        }
        
        # Generate 100 tasks
        for i in range(100):
            # Select task type and generate story points
            task_type = np.random.choice(list(task_types.keys()))
            min_points, max_points = task_types[task_type]
            story_points = np.random.randint(min_points, max_points + 1)  # Add 1 to include max_points
            
            # Generate dependencies (0-2 dependencies per task)
            num_dependencies = np.random.randint(0, 3)
            dependencies = []
            if num_dependencies > 0:
                # Only depend on tasks with lower indices
                possible_deps = [f"TASK-{j+1}" for j in range(i)]
                if possible_deps:
                    dependencies = np.random.choice(possible_deps, size=min(num_dependencies, len(possible_deps)), replace=False).tolist()
            
            # Generate required skills (2-4 skills per task)
            num_skills = np.random.randint(2, 5)
            required_skills = np.random.choice(self.skills, size=num_skills, replace=False).tolist()
            
            # Generate priority (weighted towards Medium)
            priority = np.random.choice(
                ["High", "Medium", "Low"],
                p=[0.2, 0.5, 0.3]
            )
            
            # Create task
            task = {
                'issue_key': f"TASK-{i+1}",
                'summary': f"{task_type}: {np.random.choice(['Implement', 'Design', 'Test', 'Review', 'Document'])} {np.random.choice(self.features)}",
                'description': f"Detailed description for {task_type} task {i+1}",
                'priority': priority,
                'story_points': story_points,
                'dependencies': ','.join(dependencies),
                'pre_mapped_skills': ';'.join(required_skills),
                'status': 'Backlog',
                'sprint_id': ''
            }
            tasks.append(task)
        
        # Assign tasks to sprints (70% in backlog, 30% in sprints)
        num_sprint_tasks = int(len(tasks) * 0.3)
        sprint_tasks = np.random.choice(tasks, size=num_sprint_tasks, replace=False)
        
        for task in sprint_tasks:
            # Assign to a random sprint (SPRINT-1 to SPRINT-4)
            sprint_num = np.random.randint(1, 5)
            task['sprint_id'] = f"SPRINT-{sprint_num}"
            task['status'] = np.random.choice(['Not Started', 'In Progress', 'Completed'])
        
        return pd.DataFrame(tasks)
    
    def _generate_team_data(self):
        """Generate dummy team data."""
        developers = []
        num_developers = 8
        
        for i in range(num_developers):
            # Generate skills (2-5 skills per developer)
            num_skills = np.random.randint(2, 6)
            developer_skills = np.random.choice(self.skills, num_skills, replace=False)
            
            # Generate preferences (1-2 preferences per developer)
            num_prefs = np.random.randint(1, 3)
            preferences = np.random.choice(['Frontend', 'Backend', 'Full Stack', 'DevOps'], num_prefs, replace=False)
            
            # Generate capacity (based on role)
            role = np.random.choice(self.roles)
            if "Senior" in role or "Lead" in role:
                capacity = np.random.randint(15, 20)
            elif "Junior" in role:
                capacity = np.random.randint(5, 10)
            else:
                capacity = np.random.randint(10, 15)
            
            developer = {
                'developer_name': f"Developer {i+1}",
                'role': role,
                'capacity': capacity,
                'skill_sets': ';'.join(developer_skills),
                'preferences': ';'.join(preferences)
            }
            developers.append(developer)
        
        return pd.DataFrame(developers)
    
    def save_dummy_data(self) -> Dict[str, pd.DataFrame]:
        """Generate and save dummy data to CSV files."""
        data = self.generate_dummy_data()
        
        # Save to CSV files
        data['backlog_data'].to_csv(self.data_dir / "backlog.csv", index=False)
        data['sprint_data'].to_csv(self.data_dir / "sprint_data.csv", index=False)
        data['team_data'].to_csv(self.data_dir / "team_data.csv", index=False)
        data['future_capacity_data'].to_csv(self.data_dir / "future_capacity.csv", index=False)
        
        return data 