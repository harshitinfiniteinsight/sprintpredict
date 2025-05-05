import streamlit as st
from transformers import pipeline
from typing import List, Dict, Any

class SprintSummarizer:
    def __init__(self):
        """Initialize the summarizer with GPT-2."""
        self.summarizer = pipeline("text-generation", model="gpt2")
    
    def generate_summary(
        self,
        selected_tasks: List[str],
        task_assignments: Dict[tuple, bool],
        task_points: Dict[str, float],
        developer_capacity: Dict[str, float],
        task_priorities: Dict[str, int],
        task_dependencies: Dict[str, List[str]],
        task_skills: Dict[str, List[str]],
        developer_skills: Dict[str, List[str]]
    ) -> str:
        """Generate a summary of the sprint plan."""
        # Prepare input text
        input_text = "Sprint Planning Summary:\n\n"
        
        # Add task selection summary
        input_text += "Selected Tasks:\n"
        for task in selected_tasks:
            assigned_devs = [
                dev for (t, dev), assigned in task_assignments.items()
                if t == task and assigned
            ]
            input_text += f"- {task} (Priority: {task_priorities[task]}, Points: {task_points[task]}, "
            input_text += f"Assigned to: {', '.join(assigned_devs)})\n"
        
        # Add developer workload summary
        input_text += "\nDeveloper Workload:\n"
        for dev in developer_capacity:
            assigned_points = sum(
                task_points[task]
                for task in selected_tasks
                if task_assignments.get((task, dev), False)
            )
            utilization = assigned_points / developer_capacity[dev]
            input_text += f"- {dev}: {assigned_points}/{developer_capacity[dev]} points "
            input_text += f"({utilization:.1%} utilization)\n"
        
        # Add skill matching summary
        input_text += "\nSkill Matching:\n"
        for task in selected_tasks:
            task_skill_set = set(task_skills[task])
            assigned_devs = [
                dev for (t, dev), assigned in task_assignments.items()
                if t == task and assigned
            ]
            for dev in assigned_devs:
                dev_skill_set = set(developer_skills[dev])
                common_skills = task_skill_set.intersection(dev_skill_set)
                match_score = len(common_skills) / len(task_skill_set) if task_skill_set else 0
                input_text += f"- {task} -> {dev}: {match_score:.1%} skill match "
                input_text += f"(Common skills: {', '.join(common_skills)})\n"
        
        # Generate summary using GPT-2
        summary = self.summarizer(
            input_text,
            max_length=500,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True
        )[0]['generated_text']
        
        return summary 