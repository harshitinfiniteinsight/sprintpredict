from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables
load_dotenv()

# Import backend modules
from data_ingestion.data_loader import DataLoader
from data_ingestion.dummy_data_generator import DummyDataGenerator
from visualization.visualizer import SprintVisualizer
from optimization.sprint_optimizer import SprintOptimizer

# Initialize FastAPI app
app = FastAPI(title="Sprint Spark AI Planner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("http://localhost:8080", "http://localhost:8080")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend components
data_loader = DataLoader()
dummy_generator = DummyDataGenerator()
visualizer = SprintVisualizer()
optimizer = SprintOptimizer()

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if (frontend_path.exists()):
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

# API Routes
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

# Visualization endpoints
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
    jira_url = "https://nusgroup7project.atlassian.net/rest/api/3/search?jql=project=SCRUM&fields=summary,description,status"
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
            "Java", "Oracle"
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
                issue_info['dependencies'] = ','.join(
                    random.sample(
                        [f'SCRUM-{j+1}' for j in range(13) if j != i],  # Exclude the current task
                        random.randint(0, min(3, 12))  # Ensure the sample size is within bounds
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "localhost"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    )