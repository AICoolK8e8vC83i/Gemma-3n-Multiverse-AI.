#!/usr/bin/env python3
"""
🧠 Gemma 3n Multiverse - Streamlit Interface
Amazon Bedrock-inspired AI Brain UI
"""

import streamlit as st
import time
import base64
import json
from datetime import datetime
from PIL import Image
import io
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from typing import Dict, List

from main import gemma_system
from config_agents import HACKATHON_AGENTS, UI_CONFIG, BRAIN_VIZ_CONFIG
from speech_to_text import speech_interface
import requests

# 🎨 CUSTOM CSS WITH AI BRAIN STYLING
def inject_custom_css():
    st.markdown("""
    <style>
    /* 🎨 Main App Styling */
    .stApp {
        background: linear-gradient(135deg, #0F1419 0%, #1E2A3A 50%, #2D3F5F 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 🧠 Brain Header */
    .brain-header {
        background: linear-gradient(90deg, #4A90E2, #7B68EE, #00CED1);
        background-size: 200% 200%;
        animation: gradient-shift 3s ease infinite;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(74, 144, 226, 0.3);
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .brain-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
    }
    
    .brain-subtitle {
        font-size: 1.1rem;
        color: rgba(255, 255, 255, 0.9);
        margin-top: 5px;
    }
    
    /* 🌐 Neural Network Visualization */
    .neural-viz {
        position: relative;
        background: rgba(26, 35, 47, 0.8);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border: 1px solid rgba(74, 144, 226, 0.3);
        overflow: hidden;
    }
    
    .neural-node {
        width: 8px;
        height: 8px;
        background: #4A90E2;
        border-radius: 50%;
        position: absolute;
        box-shadow: 0 0 10px #4A90E2;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
    }
    
    /* 💬 Chat Interface */
    .chat-container {
        background: rgba(26, 35, 47, 0.6);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(74, 144, 226, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .user-message {
        background: linear-gradient(135deg, #4A90E2, #5BA3F5);
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        color: white;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
        animation: slideInRight 0.3s ease;
    }
    
    .agent-message {
        background: linear-gradient(135deg, #2A2A2A, #3A3A3A);
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        color: #E0E0E0;
        border-left: 4px solid #7B68EE;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        animation: slideInLeft 0.3s ease;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-30px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    /* 🎯 Agent Selector */
    .agent-card {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.1), rgba(123, 104, 238, 0.1));
        border-radius: 12px;
        padding: 15px;
        margin: 8px;
        border: 1px solid rgba(74, 144, 226, 0.3);
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    
    .agent-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(74, 144, 226, 0.4);
        border-color: #4A90E2;
    }
    
    .agent-emoji {
        font-size: 2rem;
        margin-bottom: 8px;
    }
    
    .agent-name {
        font-weight: 600;
        color: #E0E0E0;
        margin-bottom: 5px;
    }
    
    .agent-desc {
        font-size: 0.85rem;
        color: #B0B0B0;
        line-height: 1.3;
    }
    
    /* 🎯 Goals Interface */
    .goal-card {
        background: linear-gradient(135deg, rgba(0, 206, 209, 0.1), rgba(152, 251, 152, 0.1));
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #00CED1;
        animation: fadeInUp 0.4s ease;
    }
    
    @keyframes fadeInUp {
        from { transform: translateY(20px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    .goal-title {
        color: #00CED1;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .goal-progress {
        background: rgba(0, 206, 209, 0.2);
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
        margin: 8px 0;
    }
    
    .goal-progress-bar {
        background: linear-gradient(90deg, #00CED1, #98FB98);
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }
    
    /* 💡 Goal Suggestions */
    .suggestion-card {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 165, 0, 0.1));
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        border: 1px dashed rgba(255, 107, 107, 0.4);
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .suggestion-card:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.3);
    }
    
    .suggestion-card::before {
        content: "✨";
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 1.2rem;
        animation: sparkle 1.5s infinite;
    }
    
    @keyframes sparkle {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.2) rotate(180deg); }
    }
    
    /* 📷 Camera Interface */
    .camera-interface {
        background: rgba(26, 35, 47, 0.8);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 2px dashed rgba(74, 144, 226, 0.5);
        margin: 15px 0;
    }
    
    .camera-button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E8E);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    .camera-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
    }
    
    /* 🚀 Action Buttons */
    .action-button {
        background: linear-gradient(135deg, #7B68EE, #9A84FF);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 5px;
        box-shadow: 0 3px 10px rgba(123, 104, 238, 0.4);
    }
    
    .action-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 5px 15px rgba(123, 104, 238, 0.6);
    }
    
    /* 📊 Stats Dashboard */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.15), rgba(123, 104, 238, 0.15));
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(74, 144, 226, 0.3);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #4A90E2;
        margin-bottom: 5px;
    }
    
    .stat-label {
        color: #B0B0B0;
        font-size: 0.9rem;
    }
    
    /* 🔮 Proactive Follow-up */
    .follow-up {
        background: linear-gradient(135deg, rgba(123, 104, 238, 0.2), rgba(147, 112, 219, 0.2));
        border-radius: 15px;
        padding: 18px;
        margin: 15px 0;
        border-left: 4px solid #7B68EE;
        animation: glow 2s infinite alternate;
        position: relative;
    }
    
    @keyframes glow {
        from { box-shadow: 0 0 5px rgba(123, 104, 238, 0.3); }
        to { box-shadow: 0 0 20px rgba(123, 104, 238, 0.6); }
    }
    
    .follow-up::before {
        content: "🤖";
        position: absolute;
        top: -5px;
        right: 15px;
        font-size: 1.5rem;
        animation: bounce 1s infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
    }
    
    /* 🧠 Animated Neural Logo */
    .neural-loader {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        margin-right: 12px;
        position: relative;
        vertical-align: middle;
    }
    
    .neural-core {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        background: radial-gradient(circle, #4A90E2 0%, #7B68EE 50%, #00CED1 100%);
        position: relative;
        animation: neuralPulse 1.8s ease-in-out infinite;
        box-shadow: 0 0 15px rgba(74, 144, 226, 0.6);
    }
    
    .neural-core::before {
        content: '';
        position: absolute;
        top: -4px;
        left: -4px;
        right: -4px;
        bottom: -4px;
        border-radius: 50%;
        background: linear-gradient(45deg, transparent 40%, rgba(74, 144, 226, 0.3) 50%, transparent 60%);
        animation: neuralSpin 3s linear infinite;
    }
    
    .neural-core::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 2px;
        right: 2px;
        bottom: 2px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.8) 0%, transparent 70%);
        animation: neuralGlow 2s ease-in-out infinite alternate;
    }
    
    @keyframes neuralPulse {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 0 15px rgba(74, 144, 226, 0.6);
        }
        50% { 
            transform: scale(1.15);
            box-shadow: 0 0 25px rgba(74, 144, 226, 0.9);
        }
    }
    
    @keyframes neuralSpin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes neuralGlow {
        0% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    
    /* 💬 Advanced Streaming Text Effects */
    .streaming-text {
        position: relative;
    }
    
    /* Claude-style animated dots loading */
    .ai-thinking {
        display: inline-flex;
        align-items: center;
        margin-left: 8px;
    }
    
    .thinking-dots {
        display: inline-flex;
        gap: 4px;
        align-items: center;
    }
    
    .thinking-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: linear-gradient(45deg, #4A90E2, #7B68EE);
        animation: thinkingBounce 1.4s infinite ease-in-out;
        opacity: 0.7;
    }
    
    .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
    .thinking-dot:nth-child(2) { animation-delay: -0.16s; }
    .thinking-dot:nth-child(3) { animation-delay: 0s; }
    
    @keyframes thinkingBounce {
        0%, 80%, 100% {
            transform: scale(0.8);
            opacity: 0.5;
        }
        40% {
            transform: scale(1.2);
            opacity: 1;
        }
    }
    
    /* Advanced typing cursor with smooth fade */
    .typing-cursor {
        display: inline-block;
        width: 2px;
        height: 1.2em;
        background: linear-gradient(180deg, #4A90E2 0%, #7B68EE 100%);
        margin-left: 3px;
        animation: smoothBlink 1.2s ease-in-out infinite;
        vertical-align: text-bottom;
        border-radius: 1px;
        box-shadow: 0 0 4px rgba(74, 144, 226, 0.4);
    }
    
    @keyframes smoothBlink {
        0%, 45% { 
            opacity: 1;
            transform: scaleY(1);
        }
        50%, 95% { 
            opacity: 0.3;
            transform: scaleY(0.8);
        }
        100% { 
            opacity: 1;
            transform: scaleY(1);
        }
    }
    
    /* OpenAI-style pulsing loader */
    .openai-loader {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        margin-left: 8px;
        margin-right: 8px;
    }
    
    .pulse-ring {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: radial-gradient(circle, #4A90E2 30%, transparent 70%);
        position: relative;
        animation: pulseRing 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
    }
    
    .pulse-ring::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        border-radius: 50%;
        border: 1px solid rgba(74, 144, 226, 0.4);
        animation: pulseRingOuter 2s cubic-bezier(0.455, 0.03, 0.515, 0.955) infinite;
    }
    
    @keyframes pulseRing {
        0% {
            transform: scale(0.8);
            opacity: 1;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.7;
        }
        100% {
            transform: scale(0.8);
            opacity: 1;
        }
    }
    
    @keyframes pulseRingOuter {
        0% {
            transform: scale(0.8);
            opacity: 0.6;
        }
        50% {
            transform: scale(1.2);
            opacity: 0.2;
        }
        100% {
            transform: scale(0.8);
            opacity: 0.6;
        }
    }
    
    .stream-container {
        position: relative;
    }
    
    .agent-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        font-weight: 600;
        color: #E0E0E0;
    }
    
    .streaming-placeholder {
        min-height: 50px;
        background: linear-gradient(135deg, #2A2A2A, #3A3A3A);
        border-radius: 20px 20px 20px 5px;
        padding: 15px 20px;
        border-left: 4px solid #7B68EE;
        position: relative;
        overflow: hidden;
    }
    
    .streaming-placeholder::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(74, 144, 226, 0.1), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* 📱 Mobile Responsive */
    @media (max-width: 768px) {
        .brain-title { font-size: 2rem; }
        .agent-card { margin: 5px; padding: 12px; }
        .stats-container { grid-template-columns: repeat(2, 1fr); }
        .neural-loader { width: 24px; height: 24px; }
        .neural-core { width: 16px; height: 16px; }
    }
    
    /* 🎭 Animations */
    .fadeIn {
        animation: fadeIn 0.5s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 🧠 O1-STYLE KNOWLEDGE THINKING DISPLAY */
    .knowledge-thinking {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border: 1px solid #3498db;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        position: relative;
        overflow: hidden;
    }
    
    .knowledge-thinking::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -100%;
        width: 100%;
        height: calc(100% + 4px);
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.4),
            transparent
        );
        animation: shine 2s infinite;
    }
    
    @keyframes shine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .knowledge-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: 600;
        color: #3498db;
    }
    
    .knowledge-pulse {
        width: 8px;
        height: 8px;
        background: #3498db;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.7; }
    }
    
    .knowledge-query {
        background: rgba(52, 152, 219, 0.1);
        border: 1px solid rgba(52, 152, 219, 0.3);
        border-radius: 8px;
        padding: 8px 12px;
        margin: 8px 0;
        font-style: italic;
        color: #85c1e9;
    }
    
    .knowledge-chunk {
        background: rgba(39, 174, 96, 0.1);
        border-left: 3px solid #27ae60;
        border-radius: 0 8px 8px 0;
        padding: 10px 12px;
        margin: 6px 0;
        font-size: 0.9rem;
        line-height: 1.4;
        color: #a9dfbf;
        position: relative;
        overflow: hidden;
    }
    
    .knowledge-chunk::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.1),
            transparent
        );
        animation: chunkShine 3s infinite;
        animation-delay: 0.5s;
    }
    
    @keyframes chunkShine {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .knowledge-score {
        font-size: 0.7rem;
        color: #f39c12;
        font-weight: bold;
        margin-right: 8px;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton { display: none; }
    footer { visibility: hidden; }
    .stApp > header { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 🧠 NEURAL NETWORK VISUALIZATION
def create_neural_network_viz():
    """Create animated neural network visualization"""
    
    # Generate random neural network nodes
    nodes = BRAIN_VIZ_CONFIG["nodes"]
    connections = BRAIN_VIZ_CONFIG["connections"]
    colors = BRAIN_VIZ_CONFIG["colors"]
    
    # Create nodes
    x = np.random.rand(nodes)
    y = np.random.rand(nodes)
    node_colors = [colors[i % len(colors)] for i in range(nodes)]
    
    # Create connections
    x_connections = []
    y_connections = []
    
    for _ in range(connections):
        i, j = np.random.choice(nodes, 2, replace=False)
        x_connections.extend([x[i], x[j], None])
        y_connections.extend([y[i], y[j], None])
    
    # Create the plot
    fig = go.Figure()
    
    # Add connections
    fig.add_trace(go.Scatter(
        x=x_connections,
        y=y_connections,
        mode='lines',
        line=dict(color='rgba(74, 144, 226, 0.3)', width=1),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(
            size=8,
            color=node_colors,
            opacity=0.8,
            line=dict(color='white', width=1)
        ),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        width=800,
        height=300,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, showticklabels=False, showline=False),
        yaxis=dict(showgrid=False, showticklabels=False, showline=False),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    return fig

# 🎨 UI COMPONENTS
def render_brain_header():
    """Render the main brain header"""
    st.markdown("""
    <div class="brain-header">
        <h1 class="brain-title">🧠 Gemma 3n Multiverse</h1>
        <p class="brain-subtitle">AI Agents for Real-World Impact • Powered by Advanced Neural Architecture</p>
    </div>
    """, unsafe_allow_html=True)

def render_agent_selector():
    """Render agent selection interface"""
    st.markdown("### 🤖 Choose Your AI Agent")
    
    agents = gemma_system.get_agent_list()
    
    # Create columns for agent cards
    cols = st.columns(4)
    selected_agent = None
    
    for i, (agent_id, agent_info) in enumerate(agents.items()):
        with cols[i % 4]:
            if st.button(
                f"{agent_info['emoji']}\n{agent_info['name']}\n{agent_info['description'][:50]}...",
                key=f"agent_{agent_id}",
                help=agent_info['description']
            ):
                selected_agent = agent_id
    
    return selected_agent

def render_goals_dashboard():
    """Render goals dashboard with entry form"""
    st.markdown("### 🎯 Your Active Goals")
    
    # Goal creation form
    with st.expander("➕ Create New Goal", expanded=False):
        with st.form("create_goal_form"):
            goal_title = st.text_input(
                "Goal Title*", 
                placeholder="e.g., Learn Python Programming"
            )
            
            goal_description = st.text_area(
                "Description", 
                placeholder="Brief description of what you want to achieve..."
            )
            
            col1, col2 = st.columns(2)
            with col1:
                goal_category = st.selectbox(
                    "Category",
                    options=["general", "education", "health_fitness", "career", "creativity", 
                           "mental_health", "productivity", "relationships", "cooking", 
                           "ai_ml_datascience", "environmental_sustainability"],
                    format_func=lambda x: x.replace("_", " ").title()
                )
            
            with col2:
                goal_priority = st.selectbox(
                    "Priority",
                    options=["high", "medium", "low"],
                    index=1  # Default to medium
                )
            
            target_date = st.date_input(
                "Target Date (Optional)",
                value=None,
                help="When do you want to achieve this goal?"
            )
            
            # Milestones section
            st.markdown("**🎯 Milestones (Optional)**")
            milestone1 = st.text_input("Milestone 1", placeholder="e.g., Complete basic course")
            milestone2 = st.text_input("Milestone 2", placeholder="e.g., Build first project")
            milestone3 = st.text_input("Milestone 3", placeholder="e.g., Deploy to production")
            
            # Daily routines section
            st.markdown("**🔄 Daily Routines (Optional)**")
            routine1 = st.text_input("Daily Routine 1", placeholder="e.g., Study for 30 minutes")
            routine2 = st.text_input("Daily Routine 2", placeholder="e.g., Practice coding")
            routine3 = st.text_input("Daily Routine 3", placeholder="e.g., Review progress")
            
            submitted = st.form_submit_button("🚀 Create Goal")
            
            if submitted and goal_title:
                target_date_str = target_date.isoformat() if target_date else None
                
                # Collect milestones and routines
                milestones = []
                if milestone1:
                    milestones.append({"title": milestone1, "status": "pending", "progress_percentage": 0})
                if milestone2:
                    milestones.append({"title": milestone2, "status": "pending", "progress_percentage": 0})
                if milestone3:
                    milestones.append({"title": milestone3, "status": "pending", "progress_percentage": 0})
                
                routines = []
                if routine1:
                    routines.append({"title": routine1, "frequency": "daily", "streak_count": 0, "longest_streak": 0})
                if routine2:
                    routines.append({"title": routine2, "frequency": "daily", "streak_count": 0, "longest_streak": 0})
                if routine3:
                    routines.append({"title": routine3, "frequency": "daily", "streak_count": 0, "longest_streak": 0})
                
                success = gemma_system.create_goal_from_suggestion(
                    goal_title, goal_category, goal_description, goal_priority, target_date_str, milestones, routines
                )
                
                if success:
                    st.success("🎉 Goal created successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to create goal. Please try again.")
            elif submitted and not goal_title:
                st.error("⚠️ Please enter a goal title.")
    
    # Display active goals
    active_goals = gemma_system.get_active_goals()
    print(f"🎯 SIDEBAR: Retrieved {len(active_goals)} active goals")
    
    if not active_goals:
        st.markdown("""
        <div class="goal-card">
            <div style="text-align: center; color: #B0B0B0;">
                <h3>🌟 No goals yet!</h3>
                <p>Create your first goal above or chat with an agent for suggestions.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display goals with progress controls
    for i, goal in enumerate(active_goals):
        st.markdown(f"""
        <div class="goal-card">
            <div class="goal-title">{goal['title']}</div>
            <div style="color: #B0B0B0; font-size: 0.9rem; margin-bottom: 5px;">
                {goal.get('description', 'No description')}
            </div>
            <div class="goal-progress">
                <div class="goal-progress-bar" style="width: {goal['progress']}%"></div>
            </div>
            <div style="color: #B0B0B0; font-size: 0.9rem; margin-bottom: 10px;">
                Progress: {goal['progress']}% • Category: {goal['category']} • Priority: {goal.get('priority', 'medium')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress update controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            new_progress = st.slider(
                f"Update Progress", 
                min_value=0, 
                max_value=100, 
                value=goal['progress'],
                key=f"progress_{i}",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("💾 Update", key=f"update_{i}"):
                success = gemma_system.goals_manager.update_goal_progress(
                    goal['id'], new_progress
                )
                if success:
                    st.success("Updated!")
                    st.rerun()
        
        with col3:
            if goal['progress'] < 100:
                if st.button("✅ Complete", key=f"complete_{i}"):
                    success = gemma_system.goals_manager.update_goal_progress(
                        goal['id'], 100
                    )
                    if success:
                        st.success("Completed! 🎉")
                        st.rerun()
        
        # 🎯 MILESTONES SECTION
        if goal.get('milestones') and len(goal['milestones']) > 0:
            with st.expander(f"🎯 Milestones ({len(goal['milestones'])} total)", expanded=False):
                for j, milestone in enumerate(goal['milestones']):
                    # Handle both dict and string formats
                    if isinstance(milestone, str):
                        milestone_title = milestone
                        milestone_status = 'pending'
                        milestone_progress = 0
                        milestone_completed = None
                    else:
                        milestone_title = milestone.get('title', 'Unknown')
                        milestone_status = milestone.get('status', 'pending')
                        milestone_progress = milestone.get('progress_percentage', 0)
                        milestone_completed = milestone.get('completed_date')
                    
                    status_emoji = "✅" if milestone_status == 'completed' else "⏳"
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **{status_emoji} {milestone_title}**
                        - Status: {milestone_status}
                        - Progress: {milestone_progress}%
                        """)
                        if milestone_completed:
                            st.markdown(f"*Completed: {milestone_completed}*")
                    
                    with col2:
                        if milestone_status != 'completed':
                            if st.button("✅ Complete", key=f"milestone_{i}_{j}"):
                                success = gemma_system.goals_manager.complete_milestone(
                                    goal['id'], milestone.get('id', str(j))
                                )
                                if success:
                                    st.success("Milestone completed! 🎉")
                                    st.rerun()
        
        # 🔄 DAILY ROUTINES SECTION
        if goal.get('daily_routines') and len(goal['daily_routines']) > 0:
            with st.expander(f"🔄 Daily Routines ({len(goal['daily_routines'])} total)", expanded=False):
                for k, routine in enumerate(goal['daily_routines']):
                    # Handle both dict and string formats
                    if isinstance(routine, str):
                        routine_title = routine
                        routine_streak = 0
                        routine_longest = 0
                        routine_frequency = 'daily'
                        routine_last = None
                    else:
                        routine_title = routine.get('title', 'Unknown')
                        routine_streak = routine.get('streak_count', 0)
                        routine_longest = routine.get('longest_streak', 0)
                        routine_frequency = routine.get('frequency', 'daily')
                        routine_last = routine.get('last_completed')
                    
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **🔥 {routine_title}**
                        - Current Streak: {routine_streak} days
                        - Longest Streak: {routine_longest} days
                        - Frequency: {routine_frequency}
                        """)
                        if routine_last:
                            st.markdown(f"*Last completed: {routine_last[:10]}*")
                    
                    with col2:
                        if st.button("✅ Check Today", key=f"routine_{i}_{k}"):
                            success = gemma_system.goals_manager.check_daily_routine(
                                goal['id'], routine.get('id', str(k))
                            )
                            if success:
                                st.success("Routine checked! 🔥")
                                st.rerun()
        
        st.markdown("---")

def render_goal_suggestions(suggested_goals: List[str]):
    """Render AI goal suggestions with click-to-add (fixed bottom position)"""
    if not suggested_goals:
        return
    
    # Create a container that stays at the bottom
    st.markdown("""
    <div style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); 
                background: linear-gradient(135deg, rgba(255, 107, 107, 0.95), rgba(255, 165, 0, 0.95)); 
                border-radius: 15px; padding: 20px; z-index: 1000; 
                box-shadow: 0 8px 32px rgba(255, 107, 107, 0.4);
                max-width: 600px; width: 90%;">
        <h4 style="color: white; margin: 0 0 15px 0; text-align: center;">
            ✨ AI Goal Suggestions
        </h4>
        <p style="color: rgba(255, 255, 255, 0.9); margin: 0 0 15px 0; text-align: center; font-size: 0.9rem;">
            Click to add these intelligent suggestions to your goals
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Use a special container for the goal buttons that appears above main content
    with st.container():
        st.markdown("### 💡 AI Goal Suggestions")
        st.markdown("*Intelligent suggestions based on your conversation - Click to add instantly*")
        
        for i, goal in enumerate(suggested_goals):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="suggestion-card">
                    <strong>{goal}</strong>
                    <br>
                    <small style="color: #B0B0B0;">AI suggested from proactive analysis</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✅ Add", key=f"add_goal_{i}_{time.time()}"):  # Unique key
                    # Handle both string and dict formats
                    try:
                        if isinstance(goal, str):
                            print(f"🎯 ADDING STRING GOAL: {goal}")
                            success = gemma_system.create_goal_from_suggestion(
                                goal_title=goal,
                                category="general",
                                description="AI suggested goal",
                                priority="medium"
                            )
                        else:
                            # Extract data from goal dictionary
                            goal_title = goal.get("title", "")
                            category = goal.get("category", "general")
                            milestones = goal.get("milestones", [])
                            routines = goal.get("routines", [])
                            
                            print(f"🎯 ADDING DICT GOAL: {goal_title} with {len(milestones)} milestones and {len(routines)} routines")
                            
                            # Convert string lists to dict format for milestones and routines
                            milestone_dicts = [{"title": m, "status": "pending", "progress_percentage": 0} for m in milestones]
                            routine_dicts = [{"title": r, "frequency": "daily", "streak_count": 0, "longest_streak": 0} for r in routines]
                            
                            success = gemma_system.create_goal_from_suggestion(
                                goal_title=goal_title,
                                category=category,
                                description="AI suggested goal with milestones and routines",
                                priority="medium",
                                target_date=None,
                                milestones=milestone_dicts,
                                routines=routine_dicts
                            )
                        
                        if success:
                            st.success("🎉 Goal added to your list! Check the sidebar.")
                            print(f"✅ GOAL ADDED SUCCESSFULLY - Triggering rerun")
                            # Force a full page refresh to ensure sidebar updates
                            time.sleep(0.1)  # Small delay to ensure database write completes
                            st.rerun()
                        else:
                            st.error("❌ Failed to add goal. Please try again.")
                            print(f"❌ GOAL ADDITION FAILED")
                    
                    except Exception as e:
                        st.error(f"❌ Error adding goal: {str(e)}")
                        print(f"❌ EXCEPTION ADDING GOAL: {e}")
                        import traceback
                        traceback.print_exc()
        
        # Add some bottom spacing so goals are always visible
        st.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

def render_camera_interface():
    """Render camera interface for multimodal input"""
    st.markdown("### 📷 Multimodal Input")
    
    # Camera status check
    st.markdown("**📸 Camera Status:**")
    col_status1, col_status2 = st.columns(2)
    with col_status1:
        if st.button("🔍 Test Camera", help="Test if camera is accessible"):
            try:
                # Try to create a camera input to test
                test_cam = st.empty()
                with test_cam:
                    st.camera_input("Test", key="test_camera_check")
                st.success("✅ Camera accessible!")
            except Exception as e:
                st.error(f"❌ Camera issue: {str(e)[:50]}...")
    
    with col_status2:
        st.info("💡 Camera not working? Use upload below!")
    
    # Camera troubleshooting
    with st.expander("🔧 Camera Troubleshooting", expanded=False):
        st.markdown("""
        **Common Issues & Solutions:**
        
        1. **Browser Permissions**
           - Click the camera icon in your browser address bar
           - Select "Allow" for camera access
           - Refresh the page after allowing
        
        2. **Browser Compatibility**
           - ✅ Best: Chrome, Edge, Firefox
           - ❌ Issues: Safari, IE
        
        3. **Technical Issues**
           - Clear browser cache and cookies
           - Disable browser extensions
           - Try incognito/private mode
           - Restart browser
        
        4. **Windows Issues**
           - Check Windows camera privacy settings
           - Ensure no other apps are using camera
           - Update camera drivers
        
        5. **Alternative Solutions**
           - Use file upload instead
           - Take photo with phone and upload
           - Use screenshot tools
        """)
    
    # File upload (primary method)
    st.markdown("### 📁 **Recommended: File Upload**")
    uploaded_file = st.file_uploader(
        "Upload an image for AI analysis",
        type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'tiff'],
        help="Drag & drop or click to select an image file"
    )
    
    if uploaded_file is not None:
        # Process uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_container_width=True)
        
        # Show image details
        st.info(f"📊 Image: {image.size[0]}x{image.size[1]} pixels, Format: {image.format}")
        
        # Convert to base64 for processing
        buffered = io.BytesIO()
        # Convert to RGB if necessary (for JPEG)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        st.session_state.captured_image = img_base64
        st.success("✅ Image ready for AI analysis!")
    
    # Camera input (secondary method)
    st.markdown("### 📸 **Alternative: Camera Capture**")
    try:
        camera_image = st.camera_input(
            "Take a photo with your camera",
            help="Allow camera permissions when prompted"
        )
        
        if camera_image is not None:
            st.success("📷 Camera photo captured!")
            # Convert camera image to base64
            img_base64 = base64.b64encode(camera_image.getvalue()).decode()
            st.session_state.captured_image = img_base64
            
    except Exception as e:
        st.error(f"🚫 Camera Error: {str(e)}")
        st.markdown("""
        **Camera not working?** Try these quick fixes:
        - 🔄 Refresh the page and allow camera permissions
        - 🌐 Try a different browser (Chrome recommended)
        - 📁 Use the file upload option above instead
        """)

def render_streaming_response(response_stream, placeholder):
    """Render streaming response with neural animation"""
    
    metadata = None
    full_response = ""
    agent_info = {}
    proactive_messages = []
    
    # Show initial loading with advanced neural animation
    placeholder.markdown(f"""
    <div class="stream-container">
        <div class="agent-header">
            <div class="neural-loader">
                <div class="neural-core"></div>
            </div>
            🧠 AI is thinking
            <div class="ai-thinking">
                <div class="thinking-dots">
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                    <div class="thinking-dot"></div>
                </div>
            </div>
        </div>
        <div class="streaming-placeholder">
            <div class="openai-loader">
                <div class="pulse-ring"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for chunk in response_stream:
        if chunk["type"] == "metadata":
            metadata = chunk
            agent_info = {
                "agent_name": chunk["agent_name"],
                "agent_emoji": chunk["agent_emoji"],
                "relevant_goals": chunk["relevant_goals"],
                "knowledge_source": chunk.get("knowledge_source")
            }
            
            # Update header with agent info and thinking animation
            placeholder.markdown(f"""
            <div class="stream-container">
                <div class="agent-header">
                    <div class="neural-loader">
                        <div class="neural-core"></div>
                    </div>
                    <strong>{chunk["agent_emoji"]} {chunk["agent_name"]} is responding</strong>
                    <div class="knowledge-indicator" style="font-size: 0.8rem; opacity: 0.8; margin-left: 10px;">
                        🧠 {(chunk.get("knowledge_source") or {}).get("type", "general").upper()} knowledge
                    </div>
                    <div class="ai-thinking">
                        <div class="thinking-dots">
                            <div class="thinking-dot"></div>
                            <div class="thinking-dot"></div>
                            <div class="thinking-dot"></div>
                        </div>
                    </div>
                </div>
                <div class="streaming-placeholder">
                    <div class="openai-loader">
                        <div class="pulse-ring"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif chunk["type"] == "thinking":
            # Handle Qwen 3:0.6b thinking display
            full_thinking = chunk["full_thinking"]
            
            # Show thinking in dedicated UI section
            placeholder.markdown(f"""
            <div class="stream-container">
                <div class="agent-header">
                    <div class="neural-loader">
                        <div class="neural-core"></div>
                    </div>
                    <strong>🧠 Qwen 3 is thinking strategically...</strong>
                </div>
                <div style="background: rgba(74, 144, 226, 0.1); border-left: 4px solid #4A90E2; 
                            border-radius: 8px; padding: 15px; margin: 10px 0; font-style: italic;">
                    <div style="color: #4A90E2; font-weight: 600; margin-bottom: 8px;">💭 Strategic Thinking:</div>
                    <div style="color: #E0E0E0; line-height: 1.6;">
                        {full_thinking}<span class="typing-cursor"></span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        elif chunk["type"] == "knowledge_thinking":
            # Simplified knowledge display - no complex HTML
            if chunk["status"] == "searching":
                placeholder.markdown(f"""
                <div class="stream-container">
                    <div class="agent-header">
                        <div class="neural-loader">
                            <div class="neural-core"></div>
                        </div>
                        <strong>{agent_info.get("agent_emoji", "🧠")} {agent_info.get("agent_name", "AI Agent")} is thinking</strong>
                    </div>
                    <div style="color: #85c1e9; font-style: italic; padding: 15px;">
                        🔍 Accessing knowledge base...
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            elif chunk["status"] == "retrieved":
                placeholder.markdown(f"""
                <div class="stream-container">
                    <div class="agent-header">
                        <div class="neural-loader">
                            <div class="neural-core"></div>
                        </div>
                        <strong>{agent_info.get("agent_emoji", "🧠")} {agent_info.get("agent_name", "AI Agent")} is responding</strong>
                    </div>
                    <div style="color: #85c1e9; font-style: italic; padding: 15px;">
                        ✨ Knowledge retrieved, generating response...
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
        elif chunk["type"] == "text":
            full_response = chunk["full_content"]
            
            # Show streaming text with cursor
            placeholder.markdown(f"""
            <div class="agent-message">
                <div class="agent-header">
                    <div class="neural-loader">
                        <div class="neural-core"></div>
                    </div>
                    <strong>{agent_info.get("agent_emoji", "🤖")} {agent_info.get("agent_name", "AI Agent")}:</strong>
                </div>
                <div class="streaming-text">
                    {full_response}<span class="typing-cursor"></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Small delay for smooth streaming effect
            time.sleep(0.01)
            
        elif chunk["type"] == "proactive_round":
            # Add proactive round immediately as it's generated
            round_indicator = "🔥" if chunk.get("extended", False) else "💫"
            proactive_msg = {
                "round": chunk["round"],
                "content": chunk["content"],
                "extended": chunk.get("extended", False)
            }
            proactive_messages.append(proactive_msg)
            
            # IMMEDIATELY DISPLAY PROACTIVE DISPLAY WITH STOP BUTTON!
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                ## 🧠 Proactive AI Intelligence - Round {chunk["round"]}
                
                <div style="background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%); 
                            border-radius: 15px; padding: 25px; margin: 20px 0; border: 3px solid #3498db;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <h3 style="color: #3498db; margin: 0;">
                            💫 Proactive Round {chunk["round"]}/{chunk.get("total_rounds", 4)} • ⏰ {chunk.get("timestamp", datetime.now().strftime("%H:%M:%S"))}
                        </h3>
                    </div>
                    <div style="background: rgba(52, 152, 219, 0.2); border-left: 5px solid #3498db; 
                                padding: 20px; margin: 15px 0; border-radius: 10px;">
                        <div style="color: #ffffff; font-size: 1.1rem; line-height: 1.6;">
                            {chunk["content"]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # STOP BUTTON FOR PROACTIVE THREAD
                if st.button("🛑 Stop", key=f"stop_proactive_{chunk['round']}", 
                           help="Stop generating more proactive rounds"):
                    st.session_state.stop_proactive = True
                    st.success("⏹️ Stopped proactive generation")
                    st.rerun()
            
            # If this is the last proactive round, show goal suggestions immediately
            if chunk["round"] == chunk.get("total_rounds", 4):
                st.markdown("---")
                st.markdown("## 🎯 AI GOAL SUGGESTIONS (Generated from Proactive Analysis)")
                st.markdown("**Based on our conversation and your goals, I suggest:**")
                
                # Placeholder for upcoming goal suggestions
                goal_placeholder = st.empty()
                goal_placeholder.markdown("""
                <div style="text-align: center; padding: 20px; color: #85c1e9;">
                    🔄 Generating personalized goal suggestions...
                </div>
                """, unsafe_allow_html=True)
            
            # Don't update main display during proactive rounds - let the big displays be prominent!
            # Store in session state for persistence
            st.session_state.current_proactive_messages = proactive_messages
            
        elif chunk["type"] == "complete":
            # Final response without cursor - use proactive_messages collected during streaming
            goal_aware = len(agent_info.get("relevant_goals", [])) > 0
            
            # Store goal suggestions for stylized display later
            proactive_result = chunk.get("proactive_result", {})
            suggested_goals = proactive_result.get("suggested_goals", [])
            print(f"🎯 COMPLETE: Processing {len(suggested_goals)} goal suggestions")
            
            # REMOVED DUPLICATE - Goal suggestions will be shown by render_goal_suggestions only
            
            # CLEAN FINAL DISPLAY - No proactive duplication!
            placeholder.markdown(f"""
            <div class="agent-message fadeIn">
                <strong>{agent_info.get("agent_emoji", "🤖")} {agent_info.get("agent_name", "AI Agent")}:</strong>
                <br>
                {full_response}
                <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 8px;">
                    ⚡ {chunk["response_time"]:.2f}s • {datetime.now().strftime("%H:%M:%S")}
                    {f" • 🎯 Goal-aware" if goal_aware else ""}
                    {f" • 🧠 {len(proactive_messages)} rounds" if proactive_messages else ""}
                    {f" • 📚 {(agent_info.get('knowledge_source') or {}).get('type', 'general').upper()} knowledge" if agent_info.get('knowledge_source') else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Text-to-speech disabled for demo performance
            
            # Return final data for history with collected proactive messages
            proactive_result = chunk.get("proactive_result", {})
            suggested_goals = proactive_result.get("suggested_goals", [])
            
            return {
                "role": "assistant",
                "content": full_response,
                "agent_name": agent_info.get("agent_name", "AI Agent"),
                "agent_emoji": agent_info.get("agent_emoji", "🤖"),
                "response_time": chunk["response_time"],
                "goal_aware": goal_aware,
                "worldview_enhanced": False,  # Using thinking model instead
                "knowledge_source": agent_info.get("knowledge_source"),  # Include knowledge source
                "proactive_result": {
                    "proactive_messages": proactive_messages,  # Use collected messages
                    "suggested_goals": suggested_goals,
                    "thread_complete": True,
                    "rounds_completed": len(proactive_messages)
                }
            }
            
        elif chunk["type"] == "error":
            placeholder.markdown(f"""
            <div class="agent-message">
                <strong>{chunk.get("agent_emoji", "🤖")} {chunk.get("agent_name", "AI Agent")}:</strong>
                <br>
                <span style="color: #FF6B6B;">Sorry, I encountered an error: {chunk["error"]}</span>
            </div>
            """, unsafe_allow_html=True)
            
            return {
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {chunk['error']}",
                "agent_name": chunk.get("agent_name", "AI Agent"),
                "agent_emoji": chunk.get("agent_emoji", "🤖"),
                "response_time": 0,
                "goal_aware": False,
                "worldview_enhanced": False,
                "proactive_result": {
                    "proactive_messages": [],
                    "suggested_goals": [],
                    "thread_complete": True,
                    "rounds_completed": 0
                }
            }

def render_chat_interface():
    """Render the main chat interface with streaming support"""
    st.markdown("### 💬 Chat with Your AI Agent")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history with proactive rounds
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Display main AI response
            st.markdown(f"""
            <div class="agent-message">
                <strong>{message.get("agent_emoji", "🤖")} {message.get("agent_name", "AI Agent")}:</strong>
                <br>
                {message["content"]}
                <div style="font-size: 0.8rem; opacity: 0.7; margin-top: 8px;">
                    {f"🎯 Goal-aware" if message.get("goal_aware") else ""}
                    {f" • 🧠 Thinking-enhanced" if message.get("thinking_enhanced") else ""}
                    {f" • 🧠 Memory-enhanced" if message.get("memory_enhanced") else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display proactive rounds in chat history (like ChatGPT)
            proactive_result = message.get("proactive_result", {})
            proactive_messages = proactive_result.get("proactive_messages", [])
            
            if proactive_messages:
                st.markdown("### 💫 Proactive Intelligence Rounds")
                for i, proactive_msg in enumerate(proactive_messages):
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #2d1b69 0%, #8b1a1a 100%); 
                                border-radius: 15px; padding: 20px; margin: 10px 0; border: 2px solid #ff6b6b;">
                        <div style="text-align: center; margin-bottom: 15px;">
                            <h4 style="color: #ff6b6b; margin: 0;">
                                🔥 Proactive Round {i+1} - {proactive_msg.get("timestamp", "")}
                            </h4>
                        </div>
                        <div style="background: rgba(255, 107, 107, 0.2); border-left: 4px solid #ff6b6b; 
                                    padding: 15px; border-radius: 8px;">
                            <div style="color: #ffffff; font-size: 1rem; line-height: 1.5;">
                                {proactive_msg.get("content", "")}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Goal suggestions removed from chat history to avoid duplicates
            # They will only show once after the latest message
    
    # 🧠 PROACTIVE INTELLIGENCE SECTION + AUTO-CONTINUATION
    st.markdown("### 🧠 Proto-AGI Proactive Intelligence")
    proactive_container = st.container()
    with proactive_container:
        proactive_placeholder = st.empty()
        
        # Clear previous proactive messages when starting new conversation
        if st.session_state.get("clear_proactive", False):
            st.session_state.current_proactive_messages = []
            st.session_state.clear_proactive = False
        
        # Check for auto-continuation (every minute)
        auto_messages = gemma_system.agent_system.check_auto_continuation(st.session_state)
        if auto_messages:
            # Add auto-continuation messages to display
            for auto_msg in auto_messages:
                st.markdown(f"""
                ## 🔥 Auto-Continuation - Round {auto_msg["round"]}
                
                <div style="background: linear-gradient(135deg, #2d1b69 0%, #8b1a1a 100%); 
                            border-radius: 15px; padding: 25px; margin: 20px 0; border: 3px solid #ff6b6b;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <h3 style="color: #ff6b6b; margin: 0;">
                            🔥 Auto-Generated - {auto_msg["timestamp"]}
                        </h3>
                    </div>
                    <div style="background: rgba(255, 107, 107, 0.2); border-left: 5px solid #ff6b6b; 
                                padding: 20px; margin: 15px 0; border-radius: 10px;">
                        <div style="color: #ffffff; font-size: 1.1rem; line-height: 1.6;">
                            {auto_msg["content"]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # REMOVED REDUNDANT DEDICATED SECTION - Proactive displays happen during streaming!
        # The big prominent displays during generation are the main UX
        proactive_placeholder.markdown("""
        <div style="padding: 25px; background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%); 
                    border-radius: 15px; text-align: center; border: 2px solid #3498db; margin: 20px 0;">
            <h4 style="color: #3498db; margin-bottom: 10px;">💫 Proto-AGI Proactive Intelligence</h4>
            <p style="color: #85c1e9; margin: 0; font-size: 1.1rem;">
                After each main response, proactive rounds appear above with big prominent displays.<br/>
                ⏰ Auto-continues every 60 seconds with deeper insights!
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 📷 MULTIMODAL INPUT SECTION
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Chat input
        user_input = st.chat_input("Type your message here...")
    
    with col2:
        # Speech-to-text input
        st.markdown("**🎤 Voice**")
        voice_text = speech_interface.render_speech_interface()
        if voice_text and not user_input:
            user_input = voice_text
    
    with col3:
        # Camera input for images - improved implementation
        st.markdown("**📸 Camera**")
        
        # Add help text for camera issues
        with st.expander("📷 Camera Not Working?", expanded=False):
            st.markdown("""
            **Try these steps:**
            1. **Refresh the page** and allow camera permissions
            2. **Use Chrome/Edge** (best compatibility)
            3. **Check browser settings** - ensure camera is allowed
            4. **Try HTTPS**: Run with `streamlit run streamlit.py --server.enableCORS=false`
            5. **Alternative**: Use the file upload instead
            """)
        
        # Try the camera input with better error handling
        try:
            camera_image = st.camera_input("📸 Take Photo", 
                                         help="Allow camera permissions in your browser",
                                         key="main_camera")
        except Exception as e:
            st.error(f"Camera error: {e}")
            st.info("💡 Try using the file upload below instead")
            camera_image = None
    
    with col4:
        # File upload for images only (video disabled for performance)
        uploaded_file = st.file_uploader(
            "📁 Upload Image",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
            help="Upload image for AI analysis"
        )
    
    # Determine image data source
    image_data = None
    multimodal_type = None
    
    if camera_image is not None:
        image_data = camera_image
        multimodal_type = "camera"
        st.success("📷 Camera image captured! Ready to analyze.")
        
        # Show preview
        with st.expander("🔍 Image Preview", expanded=False):
            st.image(camera_image, caption="Camera capture", use_container_width=True)
    elif uploaded_file is not None:
        image_data = uploaded_file
        multimodal_type = "image"
        st.success("🖼️ Image uploaded! Ready to analyze.")
        
        # Show preview
        with st.expander("🔍 Image Preview", expanded=False):
            st.image(uploaded_file, caption="Uploaded image", use_container_width=True)
    
    # Selected agent from sidebar
    selected_agent = st.session_state.get("selected_agent", None)
    
    if user_input:
        # Clear previous proactive messages for new conversation
        st.session_state.current_proactive_messages = []
        st.session_state.clear_proactive = True
        # Reset stop flag for new conversation
        st.session_state.stop_proactive = False
        
        # Prepare user message with multimodal context
        user_message_content = user_input
        if image_data:
            if multimodal_type == "camera":
                user_message_content += " 📷 [Camera image attached]"
            else:
                user_message_content += " 🖼️ [Image attached]"
        
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_message_content,
            "image_data": image_data,
            "multimodal_type": multimodal_type
        })
        
        # Send to local sync server for mobile app
        try:
            requests.post(f"{st.session_state.sync_server_url}/messages", json={
                "timestamp": datetime.now().isoformat(),
                "type": "user",
                "message": user_message_content,
                "agent": selected_agent,
                "status": "pending"
            }, timeout=2)
        except:
            pass  # Don't break if sync server is down
        
        # Store image data for processing
        if image_data:
            st.session_state.current_image_data = image_data
            st.session_state.current_multimodal_type = multimodal_type
        
        # Rerun to show user message immediately
        st.rerun()
        
    # Check if we need to generate a response (last message is from user)
    if (st.session_state.messages and 
        st.session_state.messages[-1]["role"] == "user" and
        not st.session_state.get("generating_response", False)):
        
        # Mark as generating to prevent duplicate responses
        st.session_state.generating_response = True
        
        # Get the last user message
        last_user_message = st.session_state.messages[-1]["content"]
        
        # Get image data if available from current session or message
        current_image_data = st.session_state.get("current_image_data", None)
        multimodal_type = st.session_state.get("current_multimodal_type", None)
        
        # Clear image data after use to prevent reuse in next messages
        if current_image_data:
            st.session_state.current_image_data = None
            st.session_state.current_multimodal_type = None
        
        # Create placeholder for streaming response
        response_placeholder = st.empty()
        
        try:
            # Get streaming response with multimodal support
            response_stream = gemma_system.process_message_stream(
                last_user_message,
                selected_agent=selected_agent,
                image_data=current_image_data,
                session_state=st.session_state  # Pass session state for stop signal
            )
            
            # Render streaming response
            final_message = render_streaming_response(response_stream, response_placeholder)
            
            if final_message:
                # Add to history
                st.session_state.messages.append(final_message)
                
                # Show goal suggestions using ONLY the stylized version
                proactive_result = final_message.get("proactive_result", {})
                suggested_goals = proactive_result.get("suggested_goals", [])
                print(f"🎯 UI: Got {len(suggested_goals)} goal suggestions to display")
                if suggested_goals:
                    # Use ONLY the stylized gradient box version with rotating stars
                    render_goal_suggestions(suggested_goals)
            
        except Exception as e:
            response_placeholder.markdown(f"""
            <div class="agent-message">
                <strong>🤖 AI Agent:</strong>
                <br>
                <span style="color: #FF6B6B;">Sorry, I encountered an error: {str(e)}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Add error to history
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Sorry, I encountered an error: {str(e)}",
                "agent_name": "AI Agent",
                "agent_emoji": "🤖",
                "response_time": 0,
                "goal_aware": False,
                "worldview_enhanced": False,
                "proactive_result": {
                    "proactive_messages": [],
                    "suggested_goals": [],
                    "thread_complete": True,
                    "rounds_completed": 0
                }
            })
        
        finally:
            # Clear generating flag and image data
            st.session_state.generating_response = False
            if "captured_image" in st.session_state:
                del st.session_state.captured_image

def render_stats_dashboard():
    """Render usage statistics"""
    st.markdown("### 📊 Your AI Stats")
    
    # Calculate stats from message history
    messages = st.session_state.get("messages", [])
    ai_messages = [m for m in messages if m["role"] == "assistant"]
    
    total_responses = len(ai_messages)
    avg_response_time = np.mean([m.get("response_time", 0) for m in ai_messages]) if ai_messages else 0
    goal_aware_responses = len([m for m in ai_messages if m.get("goal_aware", False)])
    thinking_enhanced = len([m for m in ai_messages if m.get("thinking_enhanced", False)])
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_responses}</div>
            <div class="stat-label">Total Responses</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{avg_response_time:.1f}s</div>
            <div class="stat-label">Avg Response Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{goal_aware_responses}</div>
            <div class="stat-label">Goal-Aware</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{thinking_enhanced}</div>
            <div class="stat-label">Thinking Enhanced</div>
        </div>
        """, unsafe_allow_html=True)

# 🚀 MAIN APP
def main():
    # Page config
    st.set_page_config(
        page_title="🧠 Gemma 3n Multiverse",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize local sync server connection
    if 'sync_server_url' not in st.session_state:
        st.session_state.sync_server_url = "http://192.168.1.40:8000"
    
    # Test sync server connection
    try:
        response = requests.get(f"{st.session_state.sync_server_url}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Local sync server connected!")
        else:
            st.warning("⚠️ Local sync server not responding")
    except:
        st.warning("⚠️ Local sync server not available - start with: python sync_server.py")
    
    # Inject custom CSS
    inject_custom_css()
    
    # Main header
    render_brain_header()
    
    # Neural network visualization
    if BRAIN_VIZ_CONFIG.get("neural_network_viz", True):
        st.plotly_chart(create_neural_network_viz(), use_container_width=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Control Center")
        
        # Agent selector
        agents = gemma_system.get_agent_list()
        agent_options = ["Auto-Select"] + [f"{info['emoji']} {info['name']}" 
                                         for info in agents.values()]
        
        selected_idx = st.selectbox(
            "🤖 Choose Agent",
            range(len(agent_options)),
            format_func=lambda x: agent_options[x]
        )
        
        if selected_idx == 0:
            st.session_state.selected_agent = None
        else:
            agent_id = list(agents.keys())[selected_idx - 1]
            st.session_state.selected_agent = agent_id
        
        st.markdown("---")
        
        # Goals dashboard in sidebar
        render_goals_dashboard()
        
        st.markdown("---")
        
        # Camera interface
        render_camera_interface()
        
        st.markdown("---")
        
        # Stats
        render_stats_dashboard()
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    # Main chat interface
    render_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        🧠 Powered by Gemma 3n • Built for Hackathon Excellence • 
        <a href="https://github.com" style="color: #4A90E2;">View Source</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 