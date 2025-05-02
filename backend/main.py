import pandas as pd
from fastapi import FastAPI, HTTPException, Request # Import Request if needed, though not strictly for body access here
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth
# Remove Flask imports: from flask import Flask, render_template, request, jsonify, session
import json
import re
from openai import OpenAI
from pydantic import BaseModel # For request body validation


# --- Define Helper Functions (Replace with your actual implementations) ---
# These functions were used in your Flask code and are needed for FastAPI too.
# Assuming they are in a file like `utils.py` and imported, or defined here.

PLAN_FILE = "current_sprint_plan.json" # Example file name

def load_updated_plan():
    """Loads the current sprint plan from a file."""
    try:
        if os.path.exists(PLAN_FILE):
            with open(PLAN_FILE, 'r') as f:
                return json.load(f)
        return {} # Return empty plan if file doesn't exist
    except Exception as e:
        print(f"Error loading sprint plan: {e}")
        return {}

def save_updated_plan(plan_data):
    """Saves the updated sprint plan to a file."""
    try:
        with open(PLAN_FILE, 'w') as f:
            json.dump(plan_data, f, indent=4)
        print("Sprint plan saved successfully.")
    except Exception as e:
        print(f"Error saving sprint plan: {e}")


def extract_sprint_plan_from_response(response_text: str):
    """Extracts a JSON sprint plan from the AI's response text."""
    # This regex looks for a json code block wrapped in ```json ... ```
    json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
    if json_match:
        try:
            # Attempt to parse the extracted string as JSON
            plan_json_str = json_match.group(1)
            return json.loads(plan_json_str)
        except json.JSONDecodeError as e:
            print(f"Could not decode JSON from AI response: {e}")
            return None # Return None if JSON is invalid
    return None # Return None if no JSON block is found
# --- End Helper Functions ---


# Load environment variables
load_dotenv()

# Import backend modules
from data_ingestion.data_loader import DataLoader
from data_ingestion.dummy_data_generator import DummyDataGenerator
from visualization.visualizer import SprintVisualizer
from optimization.sprint_optimizer import SprintOptimizer

# Remove Flask app initialization: flaskapp = Flask(__name__)
# Remove Flask secret key: flaskapp.secret_key = os.urandom(24) # Not needed for FastAPI sessions

# Initialize OpenAI client (can remain global)
client = OpenAI(api_key="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") # Use environment variable for API key

# Initialize FastAPI app
app = FastAPI(title="Sprint Spark AI Planner API")

# Configure CORS
# NOTE: Correct the origin string format. It should be a simple URL string.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"], # Use actual URL strings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend components.
data_loader = DataLoader()
dummy_generator = DummyDataGenerator()
visualizer = SprintVisualizer()
optimizer = SprintOptimizer()

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if (frontend_path.exists()):
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

# Define Pydantic model for chat request body
class ChatRequest(BaseModel):
    message: str

# --- New FastAPI Chat Endpoint ---
@app.post("/api/chat")
async def chat_endpoint(request_data: ChatRequest): # Use Pydantic model for validation and data access
    user_message = request_data.message # Access message directly from the model

    try:
        # Always get the latest plan from file (replaces Flask session loading)
        #current_plan = load_updated_plan()
        #if not current_plan:
            # Handle case where plan isn't loaded - maybe return an error or default?
            # For now, proceed with empty plan, but good practice to handle this.
         #   print("Warning: No sprint plan loaded.")
         #   current_plan = {}


        # Prepare the system prompt (remains the same)
        system_prompt = """SYSTEM PROMPT: Sprint Plan AI Assistant
Role & Purpose
You are SprintBot, an expert AI assistant for Agile sprint planning. You have access to the entire current sprint plan, including all tasks, story points, developer assignments, schedules, and utilization rates. Your job is to:
Answer any question about the sprint plan in a clear, structured, and insightful manner.
Allow the user to request changes to the plan using natural language, intelligently interpret their intent, and return the updated plan reflecting those changes.
Suggest and guide possible actions the user can take to optimize or modify the sprint.

Data Context
You will always be provided with the full, up-to-date sprint plan data in JSON format. Use this as the single source of truth for all answers and modifications.

Output Structure
For every user query, respond with:
Answer (mandatory): A direct, structured answer to the user's question, referencing the sprint plan data.
Actionable Suggestions (mandatory): If the user's query is about changing the plan, list the possible actions they can take, or confirm the action you will perform.
Updated Sprint Plan (if a change is requested): Return the full, updated sprint plan JSON reflecting the requested change.Please ensure the json developer_daily_schedule is definitely changed. If change requested is to remove a task named Leave then do not make the change and in response just send an apology that Leaves cannot be changed during sprint planning.
Summary: A brief summary of what was changed or answered.

IMPORTANT: When making changes to the sprint plan, ALWAYS return the complete updated plan in JSON format, wrapped in ```json ... ``` markers."""


        # Prepare messages array with system prompt and current sprint plan
        # Note: We are NOT including chat history from a session here.
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current Sprint Plan: {json.dumps(data_loader.sprint_task_distribution)}"}, # Use loaded plan
            {"role": "user", "content": user_message} # Add the current user message
        ]

        # Get response from OpenAI
        #response = client.chat.completions.create(
        #    model="gpt-4o-mini", # Using a potentially cheaper/faster model example, adjust as needed
        #    messages=messages,
        #    temperature=0.7,
        #    max_tokens=16384
        #)

        print(f"Sending request to OpenAI with messages: {messages}")

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.7,
            max_tokens=32768
        )

        assistant_response = response.choices[0].message.content
        print(f"Assistant response: {assistant_response}")

        # Check if the response contains an updated sprint plan
        updated_plan = extract_sprint_plan_from_response(assistant_response)

        plan_was_updated = False
        if updated_plan is not None: # Check against None because extract might return {}
            print("Updating sprint plan with new data")
            # Save the updated plan to the file
            save_updated_plan(updated_plan)
            print("Sprint plan updated successfully")
            plan_was_updated = True
        else:
             print("No updated sprint plan found in AI response.")

        # Return a dictionary directly; FastAPI converts it to JSON response
        return {
            'response': assistant_response,
            'sprint_plan_updated': plan_was_updated,
            'sprint_plan': updated_plan # Return the potentially updated plan
        }

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        # Use FastAPI's HTTPException for errors
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# --- End New FastAPI Chat Endpoint ---

@app.post("/api/chatSummary")
async def chat_endpoint(request_data: ChatRequest): # Use Pydantic model for validation and data access
    user_message = request_data.message # Access message directly from the model

    try:
        # Always get the latest plan from file (replaces Flask session loading)
        #current_plan = load_updated_plan()
        #if not current_plan:
            # Handle case where plan isn't loaded - maybe return an error or default?
            # For now, proceed with empty plan, but good practice to handle this.
         #   print("Warning: No sprint plan loaded.")
         #   current_plan = {}


        # Prepare the system prompt (remains the same)
        system_prompt = """SYSTEM PROMPT: Sprint Plan AI Assistant
Role & Purpose
You are SprintBot, an expert AI assistant for Agile sprint planning. You have access to the entire current sprint plan, including all tasks, story points, developer assignments, schedules, and utilization rates. Your job is to:
Provide a detailed sprint summary based on thre inputs provided.

Data Context
You will always be provided with the full, up-to-date sprint plan data in JSON format. Use this as the single source of truth for all answers.

Output Structure
Output in a professional manner, with a summary of the sprint plan. The target audience are senior management and stakeholders. The summary should include:
1. Overview of the sprint plan
2. Key metrics (e.g., total story points, number of tasks, team capacity)
3. Team member assignments
4. Any potential risks or issues identified
5. Recommendations for the next steps

Also include how the optization was done correctly highlighting the positive aspects."""

        # Prepare messages array with system prompt and current sprint plan
        # Note: We are NOT including chat history from a session here.
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current Sprint Plan: {json.dumps(data_loader.sprint_task_distribution)}"}, # Use loaded plan
            #{"role": "user", "content": user_message} # Add the current user message
        ]

        # Get response from OpenAI
        #response = client.chat.completions.create(
        #    model="gpt-4o-mini", # Using a potentially cheaper/faster model example, adjust as needed
        #    messages=messages,
        #    temperature=0.7,
        #    max_tokens=16384
        #)

        print(f"Sending request to OpenAI with messages: {messages}")

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            temperature=0.7,
            max_tokens=32768
        )

        assistant_response = response.choices[0].message.content
        print(f"Assistant response: {assistant_response}")

        # Check if the response contains an updated sprint plan
        updated_plan = extract_sprint_plan_from_response(assistant_response)

        plan_was_updated = False
        if updated_plan is not None: # Check against None because extract might return {}
            print("Updating sprint plan with new data")
            # Save the updated plan to the file
            save_updated_plan(updated_plan)
            print("Sprint plan updated successfully")
            plan_was_updated = True
        else:
             print("No updated sprint plan found in AI response.")

        # Return a dictionary directly; FastAPI converts it to JSON response
        return {
            'response': assistant_response,
            'sprint_plan_updated': plan_was_updated,
            'sprint_plan': updated_plan # Return the potentially updated plan
        }

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        # Use FastAPI's HTTPException for errors
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

# --- End New FastAPI Chat Endpoint ---


# API Routes (Your existing FastAPI endpoints remain here)
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Backlog endpoints
@app.get("/api/backlog/tasks")
async def get_backlog_tasks():
    try:
        tasks = data_loader.get_backlog_tasks()
        print(tasks)
        return {"tasks": tasks.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backlog/tasks")
async def add_task(task_data: dict):
    try:
        data_loader.add_task(task_data)
        return {"message": "Task added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sprint endpoints
@app.get("/api/sprints")
async def get_sprints():
    try:
        sprints = data_loader.get_future_sprints()
        return {"sprints": sprints.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sprints")
async def create_sprint(sprint_data: dict):
    try:
        data_loader.add_sprint(sprint_data)
        return {"message": "Sprint created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Team endpoints
@app.get("/api/team/members")
async def get_team_members():
    try:
        team_data = data_loader.team_data
        if team_data is None or team_data.empty:
            return []

        # Convert team data to the desired JSON format
        team_members = [
            {
                "name": row["developer_name"],
                "role": row["role"],
                "capacity": row["capacity"],
                "skills": ", ".join(row["skill_sets"]),
                "email": row.get("email", "")
            }
            for _, row in team_data.iterrows()
        ]

        return {"members":team_members}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/team/capacity/{sprint_id}")
async def get_team_capacity(sprint_id: str):
    try:
        capacity = data_loader.get_sprint_capacity(sprint_id)
        return {"capacity": capacity.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Planning endpoints
@app.get("/api/planning/tasks")
async def get_available_tasks():
    try:
        tasks = data_loader.get_backlog_tasks()
        return {"tasks": tasks.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/planning/assign")
async def assign_task(assignment: dict):
    try:
        data_loader.assign_task_to_sprint(
            assignment["taskId"],
            assignment["sprintId"],
            assignment["developerName"]
        )
        return {"message": "Task assigned successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Visualization endpoints
@app.get("/api/sprint/task-distribution")
async def generateSprintPlan():
    try:
        tasks = data_loader.get_backlog_tasks()
        tasks=tasks.to_dict(orient="records")
        team_data = data_loader.get_team_data()

        optimization_summary= data_loader.get_task_distribution()


        return {"optimization_summary": optimization_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sprint/task-distribution-new")
async def generateSprintPlanNew():
    try:
        tasks = data_loader.get_backlog_tasks()
        tasks=tasks.to_dict(orient="records")
        team_data = data_loader.get_team_data()

        optimization_summary= data_loader.get_task_distribution_new()


        return {"optimization_summary": optimization_summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Visualization endpoints (already in FastAPI)
@app.get("/api/visualization/task-distribution")
async def get_task_distribution():
    try:
        distribution = visualizer.show_task_distribution()
        return {"distribution": distribution}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/visualization/skill-matching")
async def get_skill_matching():
    try:
        matrix = visualizer.show_skill_matching_matrix()
        return {"matrix": matrix}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# JIRA sync endpoint
@app.get("/api/sync/jira")
async def sync_from_jira():
    jira_url = "https://nusgroup7project.atlassian.net/rest/api/3/search?jql=project=SCRUM&fields=summary,description,status&maxResults=80"
    username = "chitrarathb@gmail.com"  # Replace with your JIRA username
    password = "ATATT3xFfGF0tgagPgs9R0hhzh6YahiE_XNfkr4X1C95nRRQoWpGL2tciPzT0MVi4wBLZA07Blxn5KI_3BX6EM4UVOdImYNDo0TOuPgIap_7uPEbjVehZ82lboRcL7aRKMz_79gB_4IMdryd-YCSq8LeT-XXgFErCmxMORsdPNkLDRFgLV5kag0=F0E43FB0"  # Replace with your JIRA password

    try:
        response = requests.get(jira_url, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        extracted_issues = []

        import json  # Ensure json is imported
        import random
    
        # Parse the response JSON
        json_data = data.get("issues", [])  # Define json_data properly

        skills = [
            "Java", "Oracle", "Python", "JavaScript", "React", "Node.js"
        ]
        
        roles = [
            "Software Engineer", "Senior Software Engineer", "Full Stack Developer",
            "Backend Developer", "Frontend Developer", "DevOps Engineer", "Data Engineer",
            "ML Engineer", "UI/UX Designer", "Product Manager", "Scrum Master",
            "Technical Lead", "Architect", "QA Engineer", "Security Engineer"
        ]
        
        priorities = [3, 2, 1]  # High = 3, Medium = 2, Low = 1
    
        # Check if 'issues' key exists and is a list
        if isinstance(json_data, list):
            for issue in json_data:
                issue_info = {}
    
                # Get issue key
                issue_info['issue_key'] = issue.get('key')
    
                # Get fields
                fields = issue.get('fields', {})
    
                # Get summary
                issue_info['summary'] = fields.get('summary')
    
                # Get description text from the nested structure
                description_text = None
                description_obj = fields.get('description')
                if description_obj and isinstance(description_obj, dict) and 'content' in description_obj:
                    # Assuming the description is a document with paragraphs and text blocks
                    # This structure can vary, this handles the common case shown in the input
                    content_blocks = description_obj['content']
                    if content_blocks and isinstance(content_blocks, list):
                        # Concatenate text from all paragraph content blocks
                        description_parts = []
                        for block in content_blocks:
                            if isinstance(block, dict) and block.get('type') == 'paragraph' and 'content' in block:
                                inner_content = block['content']
                                if isinstance(inner_content, list):
                                    for inner_block in inner_content:
                                        if isinstance(inner_block, dict) and inner_block.get('type') == 'text' and 'text' in inner_block:
                                            description_parts.append(inner_block['text'])
    
                    description_text = "".join(description_parts) if description_parts else None
    
                issue_info['description'] = description_text

                issue_info['priority'] = random.choice(priorities)  # Ensure priority is a single integer value

                #issue_info['story_points'] = random.choice([1, 2, 3, 5, 8, 13])
                issue_info['story_points'] = random.choice([8, 13])
                i = int(issue.get('key').split('-')[1]),  # Extracts the part after the hyphen and converts it to an integer
                #issue_info['dependencies'] = ','.join(
                #    random.sample(
                #        [f'SCRUM-{j+1}' for j in range(13) if j != i],  # Exclude the current task
                #        random.randint(0, min(3, 12))  # Ensure the sample size is within bounds
                #    )
                #)

                num_dependencies_options = [0, 0, 0, 0, 1, 2]

                # --- Modified Code Line ---
                issue_info['dependencies'] = ','.join(
                    random.sample(
                        [f'SCRUM-{j}' for j in range(200, 231) if j != i], # Potential dependencies from 200-230, excluding self
                        random.choice(num_dependencies_options) # Randomly select the number of dependencies based on the weighted list
                    )
            )
                
                # Get status category name
                status_category_name = None
                status_obj = fields.get('status', {})
                if isinstance(status_obj, dict):
                    status_category_obj = status_obj.get('statusCategory', {})
                    if isinstance(status_category_obj, dict):
                        status_category_name = status_category_obj.get('name')

                issue_info['status'] = status_category_name # Add status category
                
                #issue_info['skills'] = ','.join(random.sample(skills, random.randint(1, 4)))
                issue_info['skills'] = ','.join(random.sample(skills, random.randint(2, 2)))
                issue_info['sprint_id'] = None  # Assign a null value to sprint_id
                extracted_issues.append(issue_info)
    
        # Print the resulting list of dictionaries
        print("Extracted Issues:")
        print(json.dumps(extracted_issues, indent=4))
        data_loader.add_rep_task(extracted_issues)
        data_loader.deleteAll_task()  # Delete all tasks before adding new ones

        # Loop through each issue in extracted_issues and call add_rep_task
        for issue in extracted_issues:
            try:
                data_loader.add_rep_task(issue)  # Call add_rep_task for each issue
            except Exception as e:
                print(f"Error adding issue {issue['issue_key']}: {e}")

        return extracted_issues  # Return the extracted issues
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sprint/history")
async def get_sprint_history():
    try:
        if data_loader.sprint_history_data is None or data_loader.sprint_history_data.empty:
            return {"history": []}

        return {"history": data_loader.sprint_history_data.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sprint/history")
async def add_sprint_history_record(new_record: dict):
    try:
        # Ensure the sprint history data is loaded
        if data_loader.sprint_history_data is None:
            data_loader.sprint_history_data = pd.DataFrame()

        # Append the new record to the sprint history data
        new_record_df = pd.DataFrame([new_record])
        data_loader.sprint_history_data = pd.concat([data_loader.sprint_history_data, new_record_df], ignore_index=True)

        return {"message": "New sprint history record added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding sprint history record: {str(e)}")

@app.get("/api/sprint/velocity-chart")
async def get_sprint_velocity_chart():
    try:
        forecasted_velocity = data_loader.get_forecasted_velocity_value()
        return forecasted_velocity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/holidays-leaves")
async def get_holidays_and_leaves():
    try:
        holidays_and_leaves = data_loader.get_holidays_and_leaves()
        return holidays_and_leaves
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-sprint-task-distribution")
async def update_sprint_task_distribution(updated_data: dict):
    try:
        # Update the sprint_task_distribution with the provided JSON data
        data_loader.sprint_task_distribution = updated_data
        return {"message": "Sprint task distribution updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating sprint task distribution: {str(e)}")

if __name__ == "__main__":
    # Remove Flask mounting and Flask app startup
    import uvicorn
    uvicorn.run(
        "main:app", # Now this runs only the FastAPI app
        host=os.getenv("BACKEND_HOST", "localhost"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )