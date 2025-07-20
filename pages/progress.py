import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.connection import db_manager
from database.models import Journal, Plan
from utils.display import display_plan
import logging

logger = logging.getLogger(__name__)

def display_progress_page(username: str):
    """Display the progress page with user data visualizations"""
    st.subheader("📊 Progress Tracking")
    
    # Check if user has sufficient data for visualization
    with db_manager.session_scope() as session:
        journal_entries = session.query(Journal).filter_by(name=username).all()
        plans = session.query(Plan).filter_by(name=username).all()
        
        if not journal_entries:
            st.warning("No journal entries found. Please log some entries to track your progress.")
            if st.button("Go to Journal"):
                st.session_state.nav = "journal"
                st.rerun()
            return
    
    # Convert journal entries to dataframe for visualization
    data = []
    for entry in journal_entries:
        data.append({
            'date': entry.entry_date,
            'weight': entry.weight,
            'workout_adherence': entry.workout_adherence,
            'diet_adherence': entry.diet_adherence,
            'mood': entry.mood,
            'energy': entry.energy
        })
    
    df = pd.DataFrame(data)
    df = df.sort_values(by='date')
    
    # Weight tracking chart
    st.markdown("### Weight Progress")
    
    # Create weight chart with trendline
    fig_weight = px.line(df, x='date', y='weight', markers=True, title='Weight Over Time (kg)')
    fig_weight.update_layout(xaxis_title='Date', yaxis_title='Weight (kg)')
    
    # Add trendline if enough data points
    if len(df) >= 3:
        fig_weight.add_trace(go.Scatter(
            x=df['date'],
            y=df['weight'].rolling(window=3, min_periods=1).mean(),
            mode='lines',
            line=dict(color='rgba(0,128,0,0.5)', width=2, dash='dash'),
            name='Trend'
        ))
    
    st.plotly_chart(fig_weight, use_container_width=True)
    
    # Adherence tracking
    st.markdown("### Plan Adherence")
    
    # Create adherence chart
    fig_adherence = go.Figure()
    fig_adherence.add_trace(go.Bar(
        x=df['date'],
        y=df['workout_adherence'],
        name='Workout Adherence',
        marker_color='blue'
    ))
    fig_adherence.add_trace(go.Bar(
        x=df['date'],
        y=df['diet_adherence'],
        name='Diet Adherence',
        marker_color='green'
    ))
    
    fig_adherence.update_layout(
        title='Weekly Plan Adherence (%)',
        xaxis_title='Date',
        yaxis_title='Adherence (%)',
        barmode='group',
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig_adherence, use_container_width=True)
    
    # Mood and energy tracking
    st.markdown("### Mood & Energy Tracking")
    
    # Convert categorical to numerical for plotting
    mood_mapping = {
        'Excellent': 5,
        'Good': 4,
        'Average': 3,
        'Poor': 2,
        'Terrible': 1
    }
    
    energy_mapping = {
        'Very High': 5,
        'High': 4,
        'Average': 3,
        'Low': 2,
        'Very Low': 1
    }
    
    df['mood_score'] = df['mood'].map(mood_mapping)
    df['energy_score'] = df['energy'].map(energy_mapping)
    
    # Create combined mood/energy chart
    fig_wellbeing = go.Figure()
    fig_wellbeing.add_trace(go.Scatter(
        x=df['date'],
        y=df['mood_score'],
        mode='lines+markers',
        name='Mood',
        line=dict(color='purple')
    ))
    fig_wellbeing.add_trace(go.Scatter(
        x=df['date'],
        y=df['energy_score'],
        mode='lines+markers',
        name='Energy',
        line=dict(color='orange')
    ))
    
    fig_wellbeing.update_layout(
        title='Mood & Energy Levels',
        xaxis_title='Date',
        yaxis_title='Level',
        yaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4, 5],
            ticktext=['Very Low', 'Low', 'Average', 'High', 'Very High'],
            range=[0.5, 5.5]
        )
    )
    
    st.plotly_chart(fig_wellbeing, use_container_width=True)
    
    # Plan history
    st.markdown("### Plan History")
    
    for i, plan in enumerate(plans):
        with st.expander(f"Plan {i+1} - Created on {plan.created_date.strftime('%Y-%m-%d')}"):
            st.write(f"Goal: {plan.goal}")
            st.write(f"Weight at time of plan: {plan.weight} kg")
            st.markdown("**Plan Details:**")
            display_plan(plan.plan)
