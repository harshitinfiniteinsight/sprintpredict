from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend modules
from data_ingestion.data_loader import DataLoader
from data_ingestion.dummy_data_generator import DummyDataGenerator
from visualization.visualizer import DataVisualizer
from optimization.optimizer import SprintOptimizer

# Initialize FastAPI app
app = FastAPI(title="Sprint Spark AI Planner API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize backend components
data_loader = DataLoader()
dummy_generator = DummyDataGenerator()
visualizer = DataVisualizer()
optimizer = SprintOptimizer()

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_path.exists():
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
        return {"tasks": tasks.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/backlog/tasks")
async def add_task(task_data: dict):
    try:
        data_loader.add_task(task_data)
        return {"message": "Task added successfully"}
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
        return {"members": team_data.to_dict(orient="records")}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("BACKEND_HOST", "localhost"),
        port=int(os.getenv("BACKEND_PORT", 8000)),
        reload=True
    ) 