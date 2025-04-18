import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
import os

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

# Import our modules
from data_ingestion.data_loader import DataLoader
from data_ingestion.dummy_data_generator import DummyDataGenerator
from optimization.sprint_optimizer import SprintOptimizer
from nlp.sprint_summarizer import SprintSummarizer
from visualization.visualizer import SprintVisualizer

# Create data directory if it doesn't exist
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Sprint Planning Assistant",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize components
data_loader = DataLoader()
optimizer = SprintOptimizer()
summarizer = SprintSummarizer()
visualizer = SprintVisualizer()

def main():
    st.title("AI-Driven Sprint Planning Assistant")
    st.markdown("""
    This application helps optimize sprint planning by analyzing historical data,
    product backlogs, and team information to create efficient sprint plans.
    """)

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["Data Management", "Data Visualization", "Sprint Planning", "Results"]
    )

    if page == "Data Management":
        show_data_management()
    elif page == "Data Visualization":
        show_data_visualization()
    elif page == "Sprint Planning":
        show_sprint_planning()
    else:
        show_results()

def show_data_management():
    st.header("Data Management")
    
    # File upload section
    st.subheader("Upload Data Files")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        backlog_file = st.file_uploader(
            "Product Backlog (CSV)",
            type=["csv"],
            help="Upload your product backlog CSV file"
        )
        if backlog_file:
            data_loader.load_backlog(backlog_file)
            st.session_state.backlog_data = data_loader.backlog_data
    
    with col2:
        sprint_file = st.file_uploader(
            "Historical Sprint Data (CSV)",
            type=["csv"],
            help="Upload your historical sprint data CSV file"
        )
        if sprint_file:
            data_loader.load_sprint_data(sprint_file)
            st.session_state.sprint_data = data_loader.sprint_data
    
    with col3:
        team_file = st.file_uploader(
            "Team Data (CSV)",
            type=["csv"],
            help="Upload your team data CSV file"
        )
        if team_file:
            data_loader.load_team_data(team_file)
            st.session_state.team_data = data_loader.team_data
    
    # Generate dummy data option
    st.subheader("Generate Dummy Data")
    if st.button("Generate Sample Data"):
        generator = DummyDataGenerator()
        dummy_data = generator.save_dummy_data()
        st.success("Dummy data generated successfully!")
        
        # Store dummy data in session state
        st.session_state.backlog_data = dummy_data["backlog"]
        st.session_state.sprint_data = dummy_data["sprint_data"]
        st.session_state.team_data = dummy_data["team_data"]
    
    # Data Management Section
    st.subheader("Manage Data")
    
    # Backlog Management
    st.markdown("### Backlog Management")
    if hasattr(st.session_state, 'backlog_data'):
        st.dataframe(st.session_state.backlog_data)
        
        # Add new task
        with st.expander("Add New Task"):
            with st.form("add_task_form"):
                task_data = {
                    'issue_key': st.text_input("Issue Key"),
                    'summary': st.text_input("Summary"),
                    'description': st.text_area("Description"),
                    'priority': st.selectbox("Priority", [3, 2, 1]),  # High = 3, Medium = 2, Low = 1
                    'story_points': st.number_input("Story Points", min_value=1, max_value=13),
                    'dependencies': st.text_input("Dependencies (comma-separated)"),
                    'pre_mapped_skills': st.text_input("Required Skills (comma-separated)")
                }
                if st.form_submit_button("Add Task"):
                    try:
                        data_loader.add_task(task_data)
                        st.session_state.backlog_data = data_loader.backlog_data
                        st.success("Task added successfully!")
                    except Exception as e:
                        st.error(f"Error adding task: {str(e)}")
        
        # Edit task
        with st.expander("Edit Task"):
            task_key = st.selectbox("Select Task to Edit", st.session_state.backlog_data['issue_key'])
            if task_key:
                task = st.session_state.backlog_data[st.session_state.backlog_data['issue_key'] == task_key].iloc[0]
                updates = {}
                for col in st.session_state.backlog_data.columns:
                    if col != 'issue_key':
                        if col in ['dependencies', 'pre_mapped_skills']:
                            updates[col] = st.text_input(col, value=','.join(task[col]) if isinstance(task[col], list) else task[col])
                        elif col == 'priority':
                            updates[col] = st.selectbox(col, [3, 2, 1], index=[3, 2, 1].index(task[col]))  # High = 3, Medium = 2, Low = 1
                        elif col == 'story_points':
                            updates[col] = st.number_input(col, min_value=1, max_value=13, value=int(task[col]))
                        else:
                            updates[col] = st.text_input(col, value=task[col])
                
                if st.button("Update Task"):
                    try:
                        data_loader.update_task(task_key, updates)
                        st.session_state.backlog_data = data_loader.backlog_data
                        st.success("Task updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating task: {str(e)}")
        
        # Delete task
        with st.expander("Delete Task"):
            task_to_delete = st.selectbox("Select Task to Delete", st.session_state.backlog_data['issue_key'])
            if st.button("Delete Task"):
                try:
                    data_loader.delete_task(task_to_delete)
                    st.session_state.backlog_data = data_loader.backlog_data
                    st.success("Task deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting task: {str(e)}")
    
    # Team Management
    st.markdown("### Team Management")
    if hasattr(st.session_state, 'team_data'):
        st.dataframe(st.session_state.team_data)
        
        # Add new developer
        with st.expander("Add New Developer"):
            with st.form("add_developer_form"):
                dev_data = {
                    'developer_name': st.text_input("Developer Name"),
                    'role': st.text_input("Role"),
                    'capacity': st.number_input("Capacity (story points)", min_value=1),
                    'skill_sets': st.text_input("Skills (semicolon-separated)"),
                    'preferences': st.text_input("Preferences (semicolon-separated)")
                }
                if st.form_submit_button("Add Developer"):
                    try:
                        data_loader.add_developer(dev_data)
                        st.session_state.team_data = data_loader.team_data
                        st.success("Developer added successfully!")
                    except Exception as e:
                        st.error(f"Error adding developer: {str(e)}")
        
        # Edit developer
        with st.expander("Edit Developer"):
            dev_name = st.selectbox("Select Developer to Edit", st.session_state.team_data['developer_name'])
            if dev_name:
                dev = st.session_state.team_data[st.session_state.team_data['developer_name'] == dev_name].iloc[0]
                updates = {}
                for col in st.session_state.team_data.columns:
                    if col != 'developer_name':
                        if col in ['skill_sets', 'preferences']:
                            updates[col] = st.text_input(col, value=';'.join(dev[col]))
                        elif col == 'capacity':
                            updates[col] = st.number_input(col, min_value=1, value=int(dev[col]))
                        else:
                            updates[col] = st.text_input(col, value=dev[col])
                
                if st.button("Update Developer"):
                    try:
                        data_loader.update_developer(dev_name, updates)
                        st.session_state.team_data = data_loader.team_data
                        st.success("Developer updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating developer: {str(e)}")
        
        # Delete developer
        with st.expander("Delete Developer"):
            dev_to_delete = st.selectbox("Select Developer to Delete", st.session_state.team_data['developer_name'])
            if st.button("Delete Developer"):
                try:
                    data_loader.delete_developer(dev_to_delete)
                    st.session_state.team_data = data_loader.team_data
                    st.success("Developer deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting developer: {str(e)}")
    
    # Sprint Data Management
    st.markdown("### Sprint Data Management")
    if hasattr(st.session_state, 'sprint_data'):
        st.dataframe(st.session_state.sprint_data)
        
        # Add new sprint
        with st.expander("Add New Sprint"):
            with st.form("add_sprint_form"):
                sprint_data = {
                    'sprint_id': st.text_input("Sprint ID"),
                    'task_ids': st.text_input("Task IDs (semicolon-separated)"),
                    'story_points_committed': st.number_input("Story Points Committed", min_value=0),
                    'story_points_completed': st.number_input("Story Points Completed", min_value=0),
                    'slippage': st.number_input("Slippage", min_value=0)
                }
                if st.form_submit_button("Add Sprint"):
                    try:
                        data_loader.add_sprint(sprint_data)
                        st.session_state.sprint_data = data_loader.sprint_data
                        st.success("Sprint added successfully!")
                    except Exception as e:
                        st.error(f"Error adding sprint: {str(e)}")
        
        # Edit sprint
        with st.expander("Edit Sprint"):
            sprint_id = st.selectbox("Select Sprint to Edit", st.session_state.sprint_data['sprint_id'])
            if sprint_id:
                sprint = st.session_state.sprint_data[st.session_state.sprint_data['sprint_id'] == sprint_id].iloc[0]
                updates = {}
                for col in st.session_state.sprint_data.columns:
                    if col != 'sprint_id':
                        if col == 'task_ids':
                            updates[col] = st.text_input(col, value=';'.join(sprint[col]))
                        elif col in ['story_points_committed', 'story_points_completed', 'slippage']:
                            updates[col] = st.number_input(col, min_value=0, value=int(sprint[col]))
                
                if st.button("Update Sprint"):
                    try:
                        data_loader.update_sprint(sprint_id, updates)
                        st.session_state.sprint_data = data_loader.sprint_data
                        st.success("Sprint updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating sprint: {str(e)}")
        
        # Delete sprint
        with st.expander("Delete Sprint"):
            sprint_to_delete = st.selectbox("Select Sprint to Delete", st.session_state.sprint_data['sprint_id'])
            if st.button("Delete Sprint"):
                try:
                    data_loader.delete_sprint(sprint_to_delete)
                    st.session_state.sprint_data = data_loader.sprint_data
                    st.success("Sprint deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting sprint: {str(e)}")
    
    # Save Data
    st.subheader("Save Data")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if hasattr(st.session_state, 'backlog_data') and st.session_state.backlog_data is not None:
            if st.button("Save Backlog"):
                try:
                    data_loader.save_data('backlog', 'data/backlog.csv')
                    st.success("Backlog saved successfully!")
                except Exception as e:
                    st.error(f"Error saving backlog: {str(e)}")
        else:
            st.info("No backlog data to save")
    
    with col2:
        if hasattr(st.session_state, 'sprint_data') and st.session_state.sprint_data is not None:
            if st.button("Save Sprint Data"):
                try:
                    data_loader.save_data('sprint', 'data/sprint_data.csv')
                    st.success("Sprint data saved successfully!")
                except Exception as e:
                    st.error(f"Error saving sprint data: {str(e)}")
        else:
            st.info("No sprint data to save")
    
    with col3:
        if hasattr(st.session_state, 'team_data') and st.session_state.team_data is not None:
            if st.button("Save Team Data"):
                try:
                    data_loader.save_data('team', 'data/team_data.csv')
                    st.success("Team data saved successfully!")
                except Exception as e:
                    st.error(f"Error saving team data: {str(e)}")
        else:
            st.info("No team data to save")

def show_data_visualization():
    st.header("Data Visualization")
    
    # Check if data is available
    if not hasattr(st.session_state, 'backlog_data') or \
       not hasattr(st.session_state, 'sprint_data') or \
       not hasattr(st.session_state, 'team_data'):
        st.warning("Please upload data or generate dummy data first.")
        return
    
    # Set data for visualizer
    visualizer.set_data(
        st.session_state.backlog_data,
        st.session_state.sprint_data,
        st.session_state.team_data
    )
    
    # Show visualizations
    visualizer.show_backlog_analysis()
    visualizer.show_sprint_history()
    visualizer.show_team_capacity()
    visualizer.show_task_dependency_graph()
    visualizer.show_skill_matching_matrix()

def show_sprint_planning():
    st.header("Sprint Planning")
    
    # Check if data is available
    if not hasattr(st.session_state, 'backlog_data') or \
       not hasattr(st.session_state, 'sprint_data') or \
       not hasattr(st.session_state, 'team_data'):
        st.warning("Please upload data or generate dummy data first.")
        return
    
    # Get data from session state
    backlog_data = st.session_state.backlog_data
    sprint_data = st.session_state.sprint_data
    team_data = st.session_state.team_data
    
    # Prepare data for optimization
    tasks = backlog_data['issue_key'].tolist()
    
    
    developers = team_data['developer_name'].tolist()
    
    task_priorities = dict(zip(backlog_data['issue_key'], backlog_data['priority']))
    
    task_points = dict(zip(backlog_data['issue_key'], backlog_data['story_points'].astype(int)))  # Ensure integers
    
    
    # Use effective capacity if available, otherwise use regular capacity
    if 'effective_capacity' in team_data.columns:
        developer_capacity = dict(zip(team_data['developer_name'], team_data['effective_capacity'].astype(int)))  # Ensure integers
    else:
        developer_capacity = dict(zip(team_data['developer_name'], team_data['capacity'].astype(int)))  # Ensure integers
    
    
    task_dependencies = dict(zip(backlog_data['issue_key'], backlog_data['dependencies'].apply(lambda x: x.split(',') if isinstance(x, str) else [])))
    
    task_skills = dict(zip(backlog_data['issue_key'], backlog_data['pre_mapped_skills'].apply(lambda x: x.split(',') if isinstance(x, str) else [])))
    
    
    developer_skills = dict(zip(team_data['developer_name'], team_data['skill_sets'].apply(lambda x: x.split(';') if isinstance(x, str) else [])))
    
    #print(backlog_data['dependencies'].tolist())
    #print(task_dependencies)
    #print("Contents of pre_mapped_skills column:", backlog_data['pre_mapped_skills'])
    
    # Create and solve optimization model
    if st.button("Generate Sprint Plan"):
        with st.spinner("Generating optimal sprint plan..."):
            try:
                print("Clicked")

                # Debugging: Check data types
                print("Checking data types...")
                
                assert isinstance(tasks, list) and all(isinstance(t, str) for t in tasks), "Tasks must be List[str]"
                
                assert isinstance(developers, list) and all(isinstance(d, str) for d in developers), "Developers must be List[str]"
                
                assert isinstance(task_priorities, dict) and all(isinstance(k, str) and isinstance(v, int) for k, v in task_priorities.items()), "Task priorities must be Dict[str, int]"
                
                assert isinstance(task_points, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in task_points.items()), "Task points must be Dict[str, float]"
                
                assert isinstance(developer_capacity, dict) and all(isinstance(k, str) and isinstance(v, (int, float)) for k, v in developer_capacity.items()), "Developer capacity must be Dict[str, float]"
                
                
                assert isinstance(task_dependencies, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(dep, str) for dep in v) for k, v in task_dependencies.items()), "Task dependencies must be Dict[str, List[str]]"
                
                print(task_skills)
                assert isinstance(task_skills, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(skill, str) for skill in v) for k, v in task_skills.items()), "Task skills must be Dict[str, List[str]]"
                print(developer_skills)
                assert isinstance(developer_skills, dict) and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(skill, str) for skill in v) for k, v in developer_skills.items()), "Developer skills must be Dict[str, List[str]]"
                print("All data types are correct.")
                
                #print("Data types in pre_mapped_skills column:", backlog_data['pre_mapped_skills'].apply(type).tolist())
                #print("Entries in pre_mapped_skills column:", backlog_data['pre_mapped_skills'].tolist())
                
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
                task_selection, task_assignments = optimizer.solve()
                print("Optimisation Summary")
                optimization_summary = optimizer.get_optimization_summary(
                    task_selection,
                    task_assignments,
                    task_points,
                    developer_capacity
                )
                print("Store results in session state")
                # Store results in session state
                st.session_state.task_selection = task_selection
                st.session_state.task_assignments = task_assignments
                st.session_state.optimization_summary = optimization_summary
                
                st.success("Sprint plan generated successfully!")
                
                # Generate AI summary
                with st.spinner("Generating AI summary..."):
                    summary = summarizer.generate_summary(
                        task_selection,
                        task_assignments,
                        task_points,
                        developer_capacity,
                        task_priorities,
                        task_dependencies,
                        task_skills,
                        developer_skills
                    )
                    st.session_state.ai_summary = summary
                    
                    st.markdown("### AI-Generated Summary")
                    st.write(summary)
            except Exception as e:
                st.error(f"Error generating sprint plan: {str(e)}")

def show_results():
    st.header("Results")
    
    # Check if optimization results are available
    if not hasattr(st.session_state, 'task_selection') or \
       not hasattr(st.session_state, 'task_assignments') or \
       not hasattr(st.session_state, 'optimization_summary'):
        st.warning("Please generate a sprint plan first.")
        return
    
    # Display optimization results
    st.subheader("Optimization Results")
    
    # Show developer utilization
    visualizer.set_data(
        st.session_state.backlog_data,
        st.session_state.sprint_data,
        st.session_state.team_data,
        st.session_state.optimization_summary
    )
    visualizer.show_optimization_results()
    
    # Display AI summary
    if hasattr(st.session_state, 'ai_summary'):
        st.subheader("AI-Generated Summary")
        st.write(st.session_state.ai_summary)
    
    # Download results
    st.subheader("Download Results")
    
    # Create results DataFrame
    results_data = []
    for task, selected in st.session_state.task_selection.items():
        if selected:
            assigned_devs = [
                dev for (t, dev), assigned in st.session_state.task_assignments.items()
                if t == task and assigned
            ]
            results_data.append({
                'Task': task,
                'Assigned To': ', '.join(assigned_devs),
                'Story Points': st.session_state.backlog_data[
                    st.session_state.backlog_data['issue_key'] == task
                ]['story_points'].iloc[0],
                'Priority': st.session_state.backlog_data[
                    st.session_state.backlog_data['issue_key'] == task
                ]['priority'].iloc[0]
            })
    
    results_df = pd.DataFrame(results_data)
    
    # Download button
    st.download_button(
        "Download Sprint Plan (CSV)",
        data=results_df.to_csv(index=False),
        file_name="sprint_plan.csv",
        mime="text/csv"
    )

if __name__ == "__main__":
    main()