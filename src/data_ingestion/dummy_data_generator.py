import pandas as pd
import numpy as np
from typing import List, Dict
import random

class DummyDataGenerator:
    def __init__(self):
        self.skills = [
            "Python", "JavaScript", "Java", "SQL", "React", "Angular", "Node.js",
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Machine Learning",
            "Data Analysis", "UI/UX Design", "DevOps", "CI/CD", "Git", "Agile",
            "Project Management", "System Architecture", "Microservices", "REST APIs",
            "GraphQL", "MongoDB", "PostgreSQL", "Redis", "Elasticsearch", "Kafka",
            "RabbitMQ", "Jenkins", "Terraform", "Ansible", "Prometheus", "Grafana"
        ]
        
        self.roles = [
            "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
            "Backend Developer", "Frontend Developer", "DevOps Engineer", "Data Engineer",
            "ML Engineer", "UI/UX Designer", "Product Manager", "Scrum Master",
            "Technical Lead", "Architect", "QA Engineer", "Security Engineer"
        ]
        
        self.priorities = [3, 2, 1]  # High = 3, Medium = 2, Low = 1
        
    def generate_backlog(self, num_tasks: int = 200) -> pd.DataFrame:
        """Generate dummy product backlog data."""
        tasks = []
        
        for i in range(num_tasks):
            task = {
                'issue_key': f'TSK-{i+1:03d}',
                'summary': f'Task {i+1}: {random.choice(["Feature", "Bug", "Enhancement", "Documentation"])}',
                'description': f'Detailed description for task {i+1}. This is a {random.choice(["user story", "bug fix", "technical task", "documentation update"])}.',
                'priority': random.choice(self.priorities),
                'story_points': random.choice([1, 2, 3, 5, 8, 13]),
                'dependencies': ','.join(random.sample([f'TSK-{j+1:03d}' for j in range(num_tasks) if j != i], random.randint(0, 3))),
                'pre_mapped_skills': ','.join(random.sample(self.skills, random.randint(1, 4)))
            }
            tasks.append(task)
        
        return pd.DataFrame(tasks)
    
    def generate_sprint_data(self, num_sprints: int = 10, num_tasks: int = 200) -> pd.DataFrame:
        """Generate dummy historical sprint data."""
        sprints = []
        
        for i in range(num_sprints):
            # Generate random tasks for this sprint
            num_sprint_tasks = random.randint(5, 15)
            sprint_tasks = random.sample([f'TSK-{j+1:03d}' for j in range(num_tasks)], num_sprint_tasks)
            
            # Calculate story points
            committed_points = random.randint(20, 40)
            completed_points = random.randint(15, committed_points)
            slippage = committed_points - completed_points
            
            sprint = {
                'sprint_id': f'SPRINT-{i+1:03d}',
                'task_ids': ';'.join(sprint_tasks),
                'story_points_committed': committed_points,
                'story_points_completed': completed_points,
                'slippage': slippage
            }
            sprints.append(sprint)
        
        return pd.DataFrame(sprints)
    
    def generate_team_data(self, num_developers: int = 10) -> pd.DataFrame:
        """Generate dummy team data."""
        developers = []
        
        for i in range(num_developers):
            # Generate random skills for the developer
            num_skills = random.randint(3, 8)
            dev_skills = random.sample(self.skills, num_skills)
            
            # Generate random preferences
            preferences = random.sample([
                "Backend Development", "Frontend Development", "DevOps",
                "Data Engineering", "Machine Learning", "UI/UX Design",
                "Architecture", "Testing", "Documentation"
            ], random.randint(1, 3))
            
            # Generate capacity based on role
            role = random.choice(self.roles)
            if "Senior" in role or "Lead" in role or "Architect" in role:
                capacity = random.randint(25, 35)
            else:
                capacity = random.randint(15, 25)
            
            developer = {
                'developer_name': f'Developer {i+1}',
                'role': role,
                'capacity': capacity,
                'skill_sets': ';'.join(dev_skills),
                'preferences': ';'.join(preferences)
            }
            developers.append(developer)
        
        return pd.DataFrame(developers)
    
    def save_dummy_data(self, output_dir: str = "data/dummy"):
        """Save generated dummy data to CSV files."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate and save backlog data
        backlog_df = self.generate_backlog()
        backlog_df.to_csv(os.path.join(output_dir, "backlog.csv"), index=False)
        
        # Generate and save sprint data
        sprint_df = self.generate_sprint_data()
        sprint_df.to_csv(os.path.join(output_dir, "sprint_data.csv"), index=False)
        
        # Generate and save team data
        team_df = self.generate_team_data()
        team_df.to_csv(os.path.join(output_dir, "team_data.csv"), index=False)
        
        return {
            "backlog": backlog_df,
            "sprint_data": sprint_df,
            "team_data": team_df
        }