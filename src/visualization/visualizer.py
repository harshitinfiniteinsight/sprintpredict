import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Tuple
import numpy as np

class SprintVisualizer:
    def __init__(self):
        self.backlog_data = None
        self.sprint_data = None
        self.team_data = None
        self.optimization_results = None
    
    def set_data(
        self,
        backlog_data: pd.DataFrame,
        sprint_data: pd.DataFrame,
        team_data: pd.DataFrame,
        optimization_results: Dict = None
    ):
        """Set the data for visualization."""
        self.backlog_data = backlog_data
        self.sprint_data = sprint_data
        self.team_data = team_data
        self.optimization_results = optimization_results
    
    def show_backlog_analysis(self):
        """Display backlog analysis visualizations."""
        st.subheader("Product Backlog Analysis")
        
        # Priority distribution
        if self.backlog_data is not None:
            priority_counts = self.backlog_data['priority'].value_counts()
            fig = px.pie(
                values=priority_counts.values,
                names=priority_counts.index.map({3: 'High', 2: 'Medium', 1: 'Low'}),
                title="Task Priority Distribution"
            )
            st.plotly_chart(fig)
            
            # Story points distribution
            fig = px.histogram(
                self.backlog_data,
                x='story_points',
                title="Story Points Distribution",
                nbins=20
            )
            st.plotly_chart(fig)
    
    def show_sprint_history(self):
        """Display sprint history visualizations."""
        st.subheader("Sprint History Analysis")
        
        if self.sprint_data is not None:
            # Previous Sprint Summary
            st.markdown("### Previous Sprint Summary")
            last_sprint = self.sprint_data.iloc[-1]
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Points Committed",
                    f"{last_sprint['story_points_committed']}",
                    f"{last_sprint['story_points_completed'] - last_sprint['story_points_committed']}"
                )
            
            with col2:
                st.metric(
                    "Points Completed",
                    f"{last_sprint['story_points_completed']}",
                    f"{last_sprint['story_points_completed'] - last_sprint['story_points_committed']}"
                )
            
            with col3:
                st.metric(
                    "Slippage",
                    f"{last_sprint['slippage']}",
                    f"{last_sprint['slippage']}"
                )
            
            # Sprint completion rates over time
            st.markdown("### Sprint Completion Trends")
            fig = px.line(
                self.sprint_data,
                x='sprint_id',
                y=['story_points_committed', 'story_points_completed'],
                title="Sprint Points Committed vs Completed Over Time",
                labels={
                    'value': 'Story Points',
                    'variable': 'Metric',
                    'sprint_id': 'Sprint ID'
                }
            )
            fig.update_layout(
                showlegend=True,
                legend_title_text='Metric',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Slippage analysis
            st.markdown("### Sprint Slippage Analysis")
            fig = px.bar(
                self.sprint_data,
                x='sprint_id',
                y='slippage',
                title="Sprint Slippage Over Time",
                labels={
                    'slippage': 'Story Points Slipped',
                    'sprint_id': 'Sprint ID'
                }
            )
            fig.update_layout(
                showlegend=False,
                yaxis_title="Story Points Slipped"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Sprint completion rate
            st.markdown("### Sprint Completion Rate")
            self.sprint_data['completion_rate'] = (
                self.sprint_data['story_points_completed'] / 
                self.sprint_data['story_points_committed'] * 100
            )
            fig = px.line(
                self.sprint_data,
                x='sprint_id',
                y='completion_rate',
                title="Sprint Completion Rate Over Time",
                labels={
                    'completion_rate': 'Completion Rate (%)',
                    'sprint_id': 'Sprint ID'
                }
            )
            fig.update_layout(
                showlegend=False,
                yaxis_title="Completion Rate (%)"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def show_team_capacity(self):
        """Display team capacity visualizations."""
        st.subheader("Team Capacity Analysis")
        
        if self.team_data is not None:
            # Developer capacity comparison
            capacity_data = self.team_data[['developer_name', 'capacity']].copy()
            if 'effective_capacity' in self.team_data.columns:
                capacity_data['effective_capacity'] = self.team_data['effective_capacity']
            
            capacity_data = capacity_data.melt(
                id_vars=['developer_name'],
                var_name='capacity_type',
                value_name='points'
            )
            
            fig = px.bar(
                capacity_data,
                x='developer_name',
                y='points',
                color='capacity_type',
                title="Developer Capacity vs Effective Capacity",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Skill distribution
            all_skills = []
            for skills in self.team_data['skill_sets']:
                all_skills.extend(skills)
            skill_counts = pd.Series(all_skills).value_counts()
            
            fig = px.bar(
                x=skill_counts.index,
                y=skill_counts.values,
                title="Team Skill Distribution"
            )
            st.plotly_chart(fig)
    
    def show_optimization_results(self):
        """Display optimization results visualizations."""
        if self.optimization_results is None:
            return
        
        st.subheader("Sprint Planning Results")
        
        # Developer utilization
        utilization_data = []
        for dev, util in self.optimization_results['developer_utilization'].items():
            utilization_data.append({
                'developer': dev,
                'assigned_points': util['assigned_points'],
                'capacity': util['capacity'],
                'utilization_rate': util['utilization_rate']
            })
        
        df_util = pd.DataFrame(utilization_data)
        
        # Utilization bar chart
        fig = px.bar(
            df_util,
            x='developer',
            y=['assigned_points', 'capacity'],
            title="Developer Capacity Utilization",
            barmode='group'
        )
        st.plotly_chart(fig)
        
        # Utilization rate gauge
        for dev_data in utilization_data:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=dev_data['utilization_rate'] * 100,
                title={'text': f"{dev_data['developer']} Utilization"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 90], 'color': "gray"},
                        {'range': [90, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': dev_data['utilization_rate'] * 100
                    }
                }
            ))
            st.plotly_chart(fig)
    
    def show_task_dependency_graph(self):
        """Display task dependency visualization."""
        if self.backlog_data is None:
            return
        
        st.subheader("Task Dependencies")
        
        # Create a directed graph of dependencies
        edges = []
        for _, row in self.backlog_data.iterrows():
            task = row['issue_key']
            for dep in row['dependencies']:
                edges.append((dep, task))
        
        # Create a network graph using Plotly
        if edges:
            source, target = zip(*edges)
            unique_nodes = list(set(source + target))
            node_indices = {node: idx for idx, node in enumerate(unique_nodes)}
            
            fig = go.Figure(data=[go.Sankey(
                node = dict(
                    pad = 15,
                    thickness = 20,
                    line = dict(color = "black", width = 0.5),
                    label = unique_nodes,
                    color = "blue"
                ),
                link = dict(
                    source = [node_indices[s] for s in source],
                    target = [node_indices[t] for t in target],
                    value = [1] * len(source)  # Create a list of 1s with the same length as source
                )
            )])
            
            fig.update_layout(title_text="Task Dependency Network")
            st.plotly_chart(fig, use_container_width=True)
    
    def show_skill_matching_matrix(self):
        """Display skill matching matrix visualization."""
        if self.backlog_data is None or self.team_data is None:
            return
        
        st.subheader("Skill Matching Matrix")
        
        # Create a matrix of task skills vs developer skills
        tasks = self.backlog_data['issue_key'].tolist()
        developers = self.team_data['developer_name'].tolist()
        
        matrix_data = []
        for task in tasks:
            task_skills = set(self.backlog_data[self.backlog_data['issue_key'] == task]['pre_mapped_skills'].iloc[0])
            for dev in developers:
                dev_skills = set(self.team_data[self.team_data['developer_name'] == dev]['skill_sets'].iloc[0])
                match_score = len(task_skills.intersection(dev_skills)) / len(task_skills) if task_skills else 0
                matrix_data.append({
                    'task': task,
                    'developer': dev,
                    'match_score': match_score
                })
        
        df_matrix = pd.DataFrame(matrix_data)
        
        # Create a heatmap
        pivot_matrix = df_matrix.pivot(index='task', columns='developer', values='match_score')
        fig = px.imshow(
            pivot_matrix,
            title="Skill Matching Heatmap",
            color_continuous_scale="RdYlGn"
        )
        st.plotly_chart(fig)