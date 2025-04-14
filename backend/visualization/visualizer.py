import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class SprintVisualizer:
    def __init__(self):
        self.backlog_data = None
        self.sprint_data = None
        self.team_data = None
        self.optimization_data = None
    
    def set_data(self, backlog_data: pd.DataFrame, sprint_data: pd.DataFrame, 
                 team_data: pd.DataFrame, optimization_data: Dict[str, Any] = None):
        """Set the data for visualization."""
        self.backlog_data = backlog_data
        self.sprint_data = sprint_data
        self.team_data = team_data
        self.optimization_data = optimization_data
    
    def show_backlog_analysis(self):
        """Show backlog analysis visualizations."""
        st.subheader("Backlog Analysis")
        
        # Task distribution by priority
        priority_counts = self.backlog_data['priority'].value_counts()
        fig_priority = px.pie(
            values=priority_counts.values,
            names=priority_counts.index,
            title="Task Distribution by Priority"
        )
        st.plotly_chart(fig_priority)
        
        # Story points distribution
        fig_points = px.histogram(
            self.backlog_data,
            x='story_points',
            title="Story Points Distribution",
            nbins=20
        )
        st.plotly_chart(fig_points)
        
        # Task status distribution
        status_counts = self.backlog_data['status'].value_counts()
        fig_status = px.bar(
            x=status_counts.index,
            y=status_counts.values,
            title="Task Status Distribution"
        )
        st.plotly_chart(fig_status)
    
    def show_sprint_history(self):
        """Show sprint history visualizations."""
        st.subheader("Sprint History")
        
        # Sprint velocity
        fig_velocity = px.line(
            self.sprint_data,
            x='sprint_id',
            y=['completed_story_points', 'total_story_points'],
            title="Sprint Velocity"
        )
        st.plotly_chart(fig_velocity)
        
        # Sprint completion rate
        self.sprint_data['completion_rate'] = (
            self.sprint_data['completed_story_points'] / 
            self.sprint_data['total_story_points']
        )
        fig_completion = px.bar(
            self.sprint_data,
            x='sprint_id',
            y='completion_rate',
            title="Sprint Completion Rate"
        )
        st.plotly_chart(fig_completion)
    
    def show_team_capacity(self):
        """Show team capacity visualizations."""
        st.subheader("Team Capacity")
        
        # Developer capacity
        fig_capacity = px.bar(
            self.team_data,
            x='developer_name',
            y='capacity',
            title="Developer Capacity"
        )
        st.plotly_chart(fig_capacity)
        
        # Skill distribution
        all_skills = []
        for skills in self.team_data['skill_sets']:
            if isinstance(skills, str):
                all_skills.extend(skills.split(';'))
        skill_counts = pd.Series(all_skills).value_counts()
        
        fig_skills = px.bar(
            x=skill_counts.index,
            y=skill_counts.values,
            title="Team Skill Distribution"
        )
        st.plotly_chart(fig_skills)
    
    def show_task_dependency_graph(self):
        """Show task dependency visualization."""
        st.subheader("Task Dependencies")
        
        # Create dependency matrix
        tasks = self.backlog_data['issue_key'].unique()
        dep_matrix = np.zeros((len(tasks), len(tasks)))
        
        for i, task1 in enumerate(tasks):
            deps = self.backlog_data[
                self.backlog_data['issue_key'] == task1
            ]['dependencies'].iloc[0]
            
            if isinstance(deps, str):
                for dep in deps.split(','):
                    if dep in tasks:
                        j = np.where(tasks == dep)[0][0]
                        dep_matrix[i, j] = 1
        
        # Create heatmap
        fig_deps = go.Figure(data=go.Heatmap(
            z=dep_matrix,
            x=tasks,
            y=tasks,
            colorscale='Viridis'
        ))
        fig_deps.update_layout(
            title="Task Dependency Matrix",
            xaxis_title="Dependent Task",
            yaxis_title="Task"
        )
        st.plotly_chart(fig_deps)
    
    def show_skill_matching_matrix(self):
        """Show skill matching visualization."""
        st.subheader("Skill Matching")
        
        # Create skill matching matrix
        tasks = self.backlog_data['issue_key'].unique()
        developers = self.team_data['developer_name'].unique()
        match_matrix = np.zeros((len(tasks), len(developers)))
        
        for i, task in enumerate(tasks):
            task_skills = set(
                self.backlog_data[
                    self.backlog_data['issue_key'] == task
                ]['pre_mapped_skills'].iloc[0].split(';')
            )
            
            for j, dev in enumerate(developers):
                dev_skills = set(
                    self.team_data[
                        self.team_data['developer_name'] == dev
                    ]['skill_sets'].iloc[0].split(';')
                )
                
                # Calculate skill match score
                common_skills = task_skills.intersection(dev_skills)
                match_score = len(common_skills) / len(task_skills) if task_skills else 0
                match_matrix[i, j] = match_score
        
        # Create heatmap
        fig_match = go.Figure(data=go.Heatmap(
            z=match_matrix,
            x=developers,
            y=tasks,
            colorscale='Viridis'
        ))
        fig_match.update_layout(
            title="Skill Matching Matrix",
            xaxis_title="Developer",
            yaxis_title="Task"
        )
        st.plotly_chart(fig_match)
    
    def show_optimization_results(self):
        """Show optimization results visualization."""
        if not self.optimization_data:
            st.warning("No optimization results available.")
            return
        
        st.subheader("Optimization Results")
        
        # Overview metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_tasks = sum(1 for task, selected in self.optimization_data['task_selection'].items() if selected)
            st.metric("Total Tasks Selected", total_tasks)
        
        with col2:
            total_points = sum(
                self.backlog_data[
                    self.backlog_data['issue_key'] == task
                ]['story_points'].iloc[0]
                for task, selected in self.optimization_data['task_selection'].items()
                if selected
            )
            st.metric("Total Story Points", total_points)
        
        with col3:
            avg_utilization = np.mean([
                self.optimization_data['developer_utilization'][dev]
                for dev in self.optimization_data['developer_utilization']
            ])
            st.metric("Average Developer Utilization", f"{avg_utilization:.1%}")
        
        # Task distribution by priority
        selected_tasks = [
            task for task, selected in self.optimization_data['task_selection'].items()
            if selected
        ]
        selected_data = self.backlog_data[
            self.backlog_data['issue_key'].isin(selected_tasks)
        ]
        
        fig_priority = px.pie(
            selected_data,
            names='priority',
            title="Selected Tasks by Priority"
        )
        st.plotly_chart(fig_priority)
        
        # Task assignment matrix
        tasks = list(self.optimization_data['task_selection'].keys())
        developers = list(self.optimization_data['developer_utilization'].keys())
        assignment_matrix = np.zeros((len(tasks), len(developers)))
        
        for i, task in enumerate(tasks):
            for j, dev in enumerate(developers):
                if self.optimization_data['task_assignments'].get((task, dev), False):
                    assignment_matrix[i, j] = 1
        
        fig_assign = go.Figure(data=go.Heatmap(
            z=assignment_matrix,
            x=developers,
            y=tasks,
            colorscale='Viridis'
        ))
        fig_assign.update_layout(
            title="Task Assignment Matrix",
            xaxis_title="Developer",
            yaxis_title="Task"
        )
        st.plotly_chart(fig_assign)
        
        # Developer workload
        workload_data = []
        for dev in developers:
            assigned_points = sum(
                self.backlog_data[
                    self.backlog_data['issue_key'] == task
                ]['story_points'].iloc[0]
                for task in tasks
                if self.optimization_data['task_assignments'].get((task, dev), False)
            )
            capacity = self.team_data[
                self.team_data['developer_name'] == dev
            ]['capacity'].iloc[0]
            
            workload_data.append({
                'Developer': dev,
                'Assigned Points': assigned_points,
                'Capacity': capacity,
                'Utilization': assigned_points / capacity if capacity > 0 else 0
            })
        
        workload_df = pd.DataFrame(workload_data)
        
        fig_workload = go.Figure()
        fig_workload.add_trace(go.Bar(
            name='Assigned Points',
            x=workload_df['Developer'],
            y=workload_df['Assigned Points']
        ))
        fig_workload.add_trace(go.Bar(
            name='Capacity',
            x=workload_df['Developer'],
            y=workload_df['Capacity']
        ))
        fig_workload.update_layout(
            title="Developer Workload",
            barmode='group'
        )
        st.plotly_chart(fig_workload)
        
        # Utilization gauges
        st.subheader("Developer Utilization")
        cols = st.columns(len(developers))
        
        for i, dev in enumerate(developers):
            with cols[i]:
                utilization = workload_df[
                    workload_df['Developer'] == dev
                ]['Utilization'].iloc[0]
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=utilization * 100,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"{dev}'s Utilization"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 60], 'color': "lightgray"},
                            {'range': [60, 80], 'color': "gray"},
                            {'range': [80, 100], 'color': "darkgray"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': utilization * 100
                        }
                    }
                ))
                st.plotly_chart(fig_gauge) 