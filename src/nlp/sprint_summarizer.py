from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Dict, List, Tuple
import json

class SprintSummarizer:
    def __init__(self):
        self.model_name = "meta-llama/Llama-2-7b-chat-hf"
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_model(self):
        """Load the Llama 3.2 model and tokenizer."""
        if self.tokenizer is None or self.model is None:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
    
    def generate_summary(
        self,
        task_selection: Dict[str, bool],
        task_assignments: Dict[Tuple[str, str], bool],
        task_points: Dict[str, float],
        developer_capacity: Dict[str, float],
        task_priorities: Dict[str, int],
        task_dependencies: Dict[str, List[str]],
        task_skills: Dict[str, List[str]],
        developer_skills: Dict[str, List[str]]
    ) -> str:
        """Generate a human-readable summary of the sprint plan."""
        self.load_model()
        
        # Prepare the input data for the model
        input_data = self._prepare_input_data(
            task_selection,
            task_assignments,
            task_points,
            developer_capacity,
            task_priorities,
            task_dependencies,
            task_skills,
            developer_skills
        )
        
        # Create the prompt
        prompt = self._create_prompt(input_data)
        
        # Generate the summary
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_length=1000,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Decode and return the generated text
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
    
    def _prepare_input_data(
        self,
        task_selection: Dict[str, bool],
        task_assignments: Dict[Tuple[str, str], bool],
        task_points: Dict[str, float],
        developer_capacity: Dict[str, float],
        task_priorities: Dict[str, int],
        task_dependencies: Dict[str, List[str]],
        task_skills: Dict[str, List[str]],
        developer_skills: Dict[str, List[str]]
    ) -> Dict:
        """Prepare the input data for the model."""
        # Get selected tasks and their assignments
        selected_tasks = [t for t, selected in task_selection.items() if selected]
        task_developer_map = {
            t: [a for (task, a), assigned in task_assignments.items() if task == t and assigned]
            for t in selected_tasks
        }
        
        # Calculate utilization rates
        developer_utilization = {}
        for a in developer_capacity:
            assigned_points = sum(
                task_points[t]
                for (t, dev), assigned in task_assignments.items()
                if dev == a and assigned
            )
            developer_utilization[a] = assigned_points / developer_capacity[a]
        
        return {
            'selected_tasks': selected_tasks,
            'task_developer_map': task_developer_map,
            'task_points': task_points,
            'developer_capacity': developer_capacity,
            'task_priorities': task_priorities,
            'task_dependencies': task_dependencies,
            'task_skills': task_skills,
            'developer_skills': developer_skills,
            'developer_utilization': developer_utilization
        }
    
    def _create_prompt(self, input_data: Dict) -> str:
        """Create the prompt for the model."""
        prompt = """You are an expert sprint planning assistant. Please analyze the following sprint plan and provide a detailed summary explaining the decisions made and potential risks.

Sprint Plan Details:
1. Selected Tasks and Assignments:
"""
        
        # Add task assignments
        for task in input_data['selected_tasks']:
            developers = input_data['task_developer_map'][task]
            prompt += f"- {task} (Points: {input_data['task_points'][task]}, Priority: {input_data['task_priorities'][task]})"
            prompt += f" → Assigned to: {', '.join(developers)}\n"
        
        # Add developer utilization
        prompt += "\n2. Developer Utilization:\n"
        for dev, util in input_data['developer_utilization'].items():
            prompt += f"- {dev}: {util:.1%} of capacity utilized\n"
        
        # Add dependencies
        prompt += "\n3. Task Dependencies:\n"
        for task in input_data['selected_tasks']:
            deps = input_data['task_dependencies'][task]
            if deps:
                prompt += f"- {task} depends on: {', '.join(deps)}\n"
        
        # Add skill matching
        prompt += "\n4. Skill Matching:\n"
        for task in input_data['selected_tasks']:
            required_skills = input_data['task_skills'][task]
            assigned_devs = input_data['task_developer_map'][task]
            for dev in assigned_devs:
                dev_skills = input_data['developer_skills'][dev]
                prompt += f"- {task} → {dev}: Required skills: {', '.join(required_skills)}, Developer skills: {', '.join(dev_skills)}\n"
        
        prompt += "\nPlease provide a comprehensive summary that includes:\n"
        prompt += "1. Overall sprint scope and capacity utilization\n"
        prompt += "2. Key decisions made in task selection and assignment\n"
        prompt += "3. Potential risks and challenges\n"
        prompt += "4. Recommendations for successful sprint execution\n"
        
        return prompt 