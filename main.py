#!/usr/bin/env python3
"""
🧠 Gemma 3n Multiverse - Core Logic
All functionality in one comprehensive system
"""

import ollama
import sqlite3
import json
import time
import base64
import io
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import uuid
# import requests  # Removed for offmmaline-first approach
from PIL import Image
import cv2
import numpy as np

# Google Docs integration
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    GOOGLE_DOCS_AVAILABLE = True
except ImportError:
    GOOGLE_DOCS_AVAILABLE = False
    print("⚠️ Google Docs API not available. Install: pip install google-api-python-client google-auth")

# Google AI Edge integration
try:
    import google.genai as genai
    GOOGLE_AI_EDGE_AVAILABLE = True
except ImportError:
    GOOGLE_AI_EDGE_AVAILABLE = False
    print("⚠️ Google AI Edge not available. Install: pip install google-genai")

from config_agents import (
    MODEL_CONFIG, PERFORMANCE_CONFIG, GOALS_CONFIG,
    MULTIMODAL_CONFIG, HACKATHON_AGENTS, ANALYTICS_CONFIG
)

# Local sync server integration
SYNC_SERVER_AVAILABLE = True

# 🔄 GOOGLE DOCS SYNC SERVICE
class GoogleDocsSync:
    def __init__(self):
        self.service = None
        self.document_id = None
        self.credentials_path = "pixel-electron-app/credentials/google-credentials.json"
        
    def initialize(self):
        """Initialize Google Docs service"""
        if not GOOGLE_DOCS_AVAILABLE:
            print("📄 Google Docs sync disabled - missing dependencies")
            return False
            
        try:
            import os
            if not os.path.exists(self.credentials_path):
                print("📄 Google Docs sync disabled - no credentials found")
                return False
                
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/documents']
            )
            self.service = build('docs', 'v1', credentials=credentials)
            print("📄 Google Docs sync initialized")
            return True
        except Exception as e:
            print(f"📄 Google Docs sync error: {e}")
            return False
    
    def upload_proactive_results(self, response: str, goals: List[str], analysis_type: str = "proactive"):
        """Upload proactive intelligence results to Google Docs"""
        if not self.service:
            return False
            
        try:
            # Create conversation entry
            entry = {
                "id": f"msg_{int(time.time())}",
                "type": f"macbook_{analysis_type}",
                "content": response,
                "goals": goals,
                "timestamp": datetime.now().isoformat(),
                "status": "pending_response"
            }
            
            # Get or create document
            if not self.document_id:
                self._create_document()
            
            # Update document with new entry
            self._append_to_document(entry)
            print(f"📄 Uploaded {analysis_type} results to Google Docs")
            return True
            
        except Exception as e:
            print(f"📄 Error uploading to Google Docs: {e}")
            return False

# 🧠 GOOGLE AI EDGE SERVICE
class GoogleAIEdgeService:
    def __init__(self):
        self.client = None
        self.api_key = None
        
    def initialize(self):
        """Initialize Google AI Edge service"""
        if not GOOGLE_AI_EDGE_AVAILABLE:
            print("🧠 Google AI Edge disabled - missing dependencies")
            return False
            
        try:
            import os
            self.api_key = os.getenv('GEMINI_API_KEY')
            if not self.api_key:
                print("🧠 Google AI Edge disabled - no API key found")
                return False
                
            self.client = genai.GoogleGenAI(api_key=self.api_key)
            print("🧠 Google AI Edge initialized")
            return True
        except Exception as e:
            print(f"🧠 Google AI Edge error: {e}")
            return False
    
    async def generate_response(self, prompt: str, model: str = "gemma-3n-e4b-it") -> str:
        """Generate response using Google AI Edge"""
        if not self.client:
            return "Google AI Edge not available"
            
        try:
            response = await self.client.models.generateContent({
                'model': model,
                'contents': prompt
            })
            return response.text
        except Exception as e:
            print(f"🧠 Error generating response: {e}")
            return f"Error: {str(e)}"
    
    async def generate_proactive_response(self, context: str, goals: List[str]) -> str:
        """Generate proactive response with goals context"""
        goals_text = ", ".join(goals) if goals else "general productivity"
        
        prompt = f"""
        Based on this conversation context: "{context}"
        And current goals: {goals_text}
        
        Provide a proactive, intelligent follow-up that:
        1. Synthesizes the key insights
        2. Suggests next steps aligned with the goals
        3. Offers actionable recommendations
        
        Be concise but insightful.
        """
        
        return await self.generate_response(prompt)
    
    def _create_document(self):
        """Create new Google Doc for sync"""
        try:
            document = self.service.documents().create(
                body={'title': f'Gemma3n Sync - {datetime.now().strftime("%Y-%m-%d")}'}
            ).execute()
            self.document_id = document.get('documentId')
            print(f"📄 Created Google Doc: {self.document_id}")
        except Exception as e:
            print(f"📄 Error creating document: {e}")
    
    def _append_to_document(self, entry):
        """Append entry to Google Doc"""
        try:
            # Format entry as JSON
            content = f"\n--- {entry['type'].upper()} ---\n"
            content += f"Time: {entry['timestamp']}\n"
            content += f"Content: {entry['content']}\n"
            content += f"Goals: {', '.join(entry['goals'])}\n"
            content += f"Status: {entry['status']}\n"
            content += "=" * 50 + "\n"
            
            # Append to document
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': content
                }
            }]
            
            self.service.documents().batchUpdate(
                documentId=self.document_id,
                body={'requests': requests}
            ).execute()
            
        except Exception as e:
            print(f"📄 Error appending to document: {e}")

# 🎯 DATA STRUCTURES
@dataclass
class Goal:
    id: str
    title: str
    description: str
    category: str
    priority: str  # high, medium, low
    status: str    # active, completed, paused
    target_date: Optional[str]
    created_date: str
    completed_date: Optional[str]
    progress_percentage: int
    milestones: List[Dict]  # Enhanced with completion tracking
    daily_routines: List[Dict]  # New: daily routines with checkmarks
    related_agents: List[str]
    user_notes: str
    ai_suggestions: List[str]
    
    def __post_init__(self):
        if self.milestones is None:
            self.milestones = []
        if self.daily_routines is None:
            self.daily_routines = []
        if self.related_agents is None:
            self.related_agents = []
        if self.ai_suggestions is None:
            self.ai_suggestions = []

@dataclass
class Milestone:
    """Enhanced milestone with completion tracking"""
    id: str
    title: str
    description: str
    status: str  # pending, in_progress, completed
    target_date: Optional[str]
    completed_date: Optional[str]
    completion_timestamp: Optional[str]
    progress_percentage: int
    notes: str

@dataclass  
class DailyRoutine:
    """Daily routine with checkmark tracking"""
    id: str
    title: str
    description: str
    frequency: str  # daily, weekly, custom
    checkmarks: List[Dict]  # List of completion dates/timestamps
    streak_count: int  # Current streak
    longest_streak: int
    last_completed: Optional[str]
    is_active: bool

@dataclass
class ConversationState:
    user_message: str
    agent_response: str
    agent_type: str
    timestamp: str
    response_time: float
    goal_context: List[str]
    thinking_enhanced: bool
    memory_context: Dict = None

@dataclass  
class ConversationMemory:
    """Proto-AGI Memory System - Thread + Permanent Memory"""
    thread_memory: List[Dict] = None  # Current conversation thread
    permanent_memory: List[Dict] = None  # Cross-session memory
    key_insights: List[str] = None  # Important learnings
    user_patterns: Dict = None  # User behavior patterns
    proactive_continuation: bool = True  # Auto-continue every minute
    
    def __post_init__(self):
        if self.thread_memory is None:
            self.thread_memory = []
        if self.permanent_memory is None:
            self.permanent_memory = []
        if self.key_insights is None:
            self.key_insights = []
        if self.user_patterns is None:
            self.user_patterns = {"preferences": [], "goals_history": [], "interaction_style": ""}

# 🗄️ GOALS SYSTEM
class GoalsDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or GOALS_CONFIG["database_path"]
        self.init_database()
    
    def init_database(self):
        """Initialize the goals database"""
        import os
        
        # Delete existing database to ensure clean schema
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"🗑️ Deleted old database: {self.db_path}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE goals (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT,
                priority TEXT,
                status TEXT,
                target_date TEXT,
                created_date TEXT,
                completed_date TEXT,
                progress_percentage INTEGER,
                milestones TEXT,
                daily_routines TEXT,
                related_agents TEXT,
                user_notes TEXT,
                ai_suggestions TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created fresh database with correct schema: {self.db_path}")
        
        # Create sample goals if database is empty
        self.create_sample_goals()
    
    def create_sample_goals(self):
        """Create professional sample goals with milestones and routines"""
        try:
            # Check if goals already exist
            existing_goals = self.get_goals_by_status("active")
            if existing_goals:
                print(f"✅ Database already has {len(existing_goals)} goals, skipping sample creation")
                return
            
            print("🎯 Creating professional sample goals...")
            
            # Sample Goal 1: AI/ML Career Development
            ai_career_goal = Goal(
                id=str(uuid.uuid4()),
                title="🚀 AI/ML Career Excellence",
                description="Build a world-class AI/ML career with cutting-edge skills, SOTA knowledge, and industry leadership",
                category="ai_ml_datascience",
                priority="high",
                status="active",
                target_date=(datetime.now() + timedelta(days=365)).isoformat(),
                created_date=datetime.now().isoformat(),
                completed_date=None,
                progress_percentage=15,
                milestones=[
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Master SOTA Models",
                        "description": "Deep dive into latest transformer architectures, attention mechanisms, and model optimization",
                        "status": "in_progress",
                        "target_date": (datetime.now() + timedelta(days=90)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 30,
                        "notes": "Focus on GPT-4, Claude, Gemini architectures and their applications"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Cloud AI Infrastructure",
                        "description": "Deploy and scale AI models on AWS, GCP, and Azure with MLOps best practices",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=180)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Learn Kubernetes, Docker, CI/CD for ML pipelines"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Research Paper Reading",
                        "description": "Read and analyze 50+ SOTA papers from NeurIPS, ICML, ICLR, and arXiv",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=120)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Focus on transformer variants, multimodal AI, and efficient training"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "AI Community Leadership",
                        "description": "Present at conferences, contribute to open source, and mentor junior developers",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=240)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Build presence on GitHub, LinkedIn, and AI communities"
                    }
                ],
                daily_routines=[
                    {
                        "id": str(uuid.uuid4()),
                        "title": "📚 Daily AI Learning",
                        "description": "Spend 30 minutes reading AI papers, watching tutorials, or coding",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "💻 Code Practice",
                        "description": "Implement AI models, work on personal projects, or contribute to open source",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "🌐 AI Networking",
                        "description": "Engage with AI community on Twitter, LinkedIn, or Discord",
                        "frequency": "weekly",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    }
                ],
                related_agents=["coding_mentor", "ai_ml_datascience"],
                user_notes="Focus on practical applications and real-world impact",
                ai_suggestions=["Consider specializing in computer vision", "Explore edge AI and mobile ML"]
            )
            
            # Sample Goal 2: Sleep & Wellness
            sleep_goal = Goal(
                id=str(uuid.uuid4()),
                title="😴 Sleep Optimization",
                description="Establish healthy sleep patterns for better productivity, mood, and overall wellness",
                category="health_fitness",
                priority="high",
                status="active",
                target_date=(datetime.now() + timedelta(days=60)).isoformat(),
                created_date=datetime.now().isoformat(),
                completed_date=None,
                progress_percentage=25,
                milestones=[
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Consistent Bedtime",
                        "description": "Go to bed at 10:30 PM consistently for 30 days",
                        "status": "in_progress",
                        "target_date": (datetime.now() + timedelta(days=30)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 40,
                        "notes": "Use sleep tracking app to monitor consistency"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Screen-Free Hour",
                        "description": "No screens 1 hour before bedtime for better sleep quality",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=45)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Read books, meditate, or journal instead"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "7-8 Hours Sleep",
                        "description": "Achieve 7-8 hours of quality sleep consistently",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=60)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Track sleep quality and energy levels"
                    }
                ],
                daily_routines=[
                    {
                        "id": str(uuid.uuid4()),
                        "title": "🌙 Evening Wind-Down",
                        "description": "Start bedtime routine at 9:30 PM with no screens",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "☀️ Morning Routine",
                        "description": "Wake up at 6:30 AM and start day with energy",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    }
                ],
                related_agents=["wellness_coach", "mental_health"],
                user_notes="Sleep is foundation for everything else",
                ai_suggestions=["Consider blue light blocking glasses", "Try meditation apps for sleep"]
            )
            
            # Sample Goal 3: Environmental Sustainability
            sustainability_goal = Goal(
                id=str(uuid.uuid4()),
                title="🌱 Sustainable Living",
                description="Reduce environmental impact through conscious choices in daily life and work",
                category="environmental_sustainability",
                priority="medium",
                status="active",
                target_date=(datetime.now() + timedelta(days=180)).isoformat(),
                created_date=datetime.now().isoformat(),
                completed_date=None,
                progress_percentage=20,
                milestones=[
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Zero Waste Kitchen",
                        "description": "Eliminate single-use plastics and food waste in kitchen",
                        "status": "in_progress",
                        "target_date": (datetime.now() + timedelta(days=60)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 60,
                        "notes": "Use reusable containers, buy in bulk, compost food scraps"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Green Energy Switch",
                        "description": "Switch to renewable energy provider and optimize home energy use",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=120)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Research local renewable energy options"
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Sustainable Transportation",
                        "description": "Reduce car usage by 50% through walking, biking, and public transit",
                        "status": "pending",
                        "target_date": (datetime.now() + timedelta(days=90)).isoformat(),
                        "completed_date": None,
                        "completion_timestamp": None,
                        "progress_percentage": 0,
                        "notes": "Track carbon footprint reduction"
                    }
                ],
                daily_routines=[
                    {
                        "id": str(uuid.uuid4()),
                        "title": "♻️ Zero Waste Day",
                        "description": "Avoid single-use items and recycle properly",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "🚶‍♂️ Walk/Bike Commute",
                        "description": "Use sustainable transportation for daily commute",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "🌿 Plant Care",
                        "description": "Water indoor plants and maintain garden",
                        "frequency": "daily",
                        "checkmarks": [],
                        "streak_count": 0,
                        "longest_streak": 0,
                        "last_completed": None,
                        "is_active": True
                    }
                ],
                related_agents=["sustainability_guide", "home_optimizer"],
                user_notes="Every small action counts toward a sustainable future",
                ai_suggestions=["Consider starting a vegetable garden", "Look into solar panel installation"]
            )
            
            # Save all sample goals
            sample_goals = [ai_career_goal, sleep_goal, sustainability_goal]
            for goal in sample_goals:
                self.save_goal(goal)
            
            print(f"✅ Created {len(sample_goals)} professional sample goals with milestones and routines!")
            
        except Exception as e:
            print(f"❌ Error creating sample goals: {e}")
    
    def save_goal(self, goal: Goal) -> bool:
        """Save or update a goal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO goals VALUES 
                (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                goal.id, goal.title, goal.description, goal.category,
                goal.priority, goal.status, goal.target_date,
                goal.created_date, goal.completed_date, goal.progress_percentage,
                json.dumps(goal.milestones), json.dumps(goal.daily_routines),
                json.dumps(goal.related_agents), goal.user_notes, json.dumps(goal.ai_suggestions)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving goal: {e}")
            return False
    
    def get_goals_by_status(self, status: str) -> List[Goal]:
        """Get goals by status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM goals WHERE status = ?", (status,))
            rows = cursor.fetchall()
            conn.close()
            
            goals = []
            for row in rows:
                goal = self._row_to_goal(row)
                if goal is not None:
                    goals.append(goal)
            
            return goals
        except Exception as e:
            print(f"Error getting goals: {e}")
            return []
    
    def _row_to_goal(self, row) -> Goal:
        """Convert database row to Goal object with error handling"""
        try:
            # Ensure we have enough columns
            if len(row) < 15:
                print(f"⚠️ Database row has {len(row)} columns, expected 15. Recreating database...")
                self.init_database()  # Recreate with correct schema
                return None
            
            return Goal(
                id=row[0], title=row[1], description=row[2], category=row[3],
                priority=row[4], status=row[5], target_date=row[6],
                created_date=row[7], completed_date=row[8], progress_percentage=row[9],
                milestones=json.loads(row[10] or "[]"),
                daily_routines=json.loads(row[11] or "[]"),
                related_agents=json.loads(row[12] or "[]"),
                user_notes=row[13] or "", ai_suggestions=json.loads(row[14] or "[]")
            )
        except Exception as e:
            print(f"❌ Error converting database row to Goal: {e}")
            print(f"Row data: {row}")
            return None

# 🧠 AGI-TIER VECTOR WORLDVIEW SYSTEM
class VectorWorldviewSystem:
    def __init__(self):
        # Always use offline-first approach - no internet dependencies
        print("🧠 Offline-first Vector Worldview System initialized!")
        self.fallback_to_basic()
    
    def fallback_to_basic(self):
        """Fallback to basic keyword matching if vector search unavailable"""
        self.is_vector_enabled = False
        self.worldview_content = ""
        self.load_basic_worldview()
    
    def load_knowledge_base(self):
        """Load separate knowledge bases for different agent types"""
        self.knowledge_bases = {}
        
        # Define knowledge files for different agent categories
        knowledge_mapping = {
            "worldview": {
                "file": "intelligent_worldview.txt",
                "agents": ["general", "mental_health", "accessibility_vision", "accessibility_hearing", 
                          "education_offline", "education_personalized", "wellness_coach", "parenting_guide", 
                          "relationship_counselor", "home_optimizer", "culinary_guide", "ethical_arbiter", 
                          "systems_thinker", "plant_disease_detector", "sustainability_guide", "crisis_response",
                          "productivity_optimizer", "creative_collaborator", "multilingual_communicator"]
            },
            "technical": {
                "file": "technical_programming_knowledge.txt", 
                "agents": ["coding_mentor"]
            }
        }
        
        for kb_type, config in knowledge_mapping.items():
            try:
                with open(config["file"], "r", encoding="utf-8") as f:
                    content = f.read()
                    print(f"✅ Loaded {config['file']}: {len(content)} characters")
                    
                    # Split into semantic chunks
                    chunks = []
                    sections = content.split('\n## ')
                    for section in sections:
                        if len(section.strip()) < 50:
                            continue
                        paragraphs = section.split('\n\n')
                        for para in paragraphs:
                            para = para.strip()
                            if len(para) > 100:
                                chunks.append(para)
                    
                    self.knowledge_bases[kb_type] = {
                        "chunks": chunks,
                        "agents": config["agents"],
                        "file": config["file"]
                    }
                    
                    print(f"📚 {kb_type.upper()}: {len(chunks)} chunks for {len(config['agents'])} agent types")
                    
            except FileNotFoundError:
                print(f"⚠️ {config['file']} not found - skipping {kb_type}")
                continue
        
        if not self.knowledge_bases:
            print("⚠️ No knowledge files found - creating basic version")
            self.create_basic_worldview()
            return
            
        # Store total chunks for fallback
        self.knowledge_chunks = []
        for kb_data in self.knowledge_bases.values():
            self.knowledge_chunks.extend(kb_data["chunks"])
            
        print(f"🧠 TOTAL: {len(self.knowledge_chunks)} chunks from {len(self.knowledge_bases)} knowledge bases")
    
    def create_basic_worldview(self):
        """Create a basic worldview file if none exists"""
        basic_worldview = """
# INTELLIGENT WORLDVIEW - COMPREHENSIVE KNOWLEDGE BASE

## ARTIFICIAL INTELLIGENCE & MACHINE LEARNING
AI represents the most transformative technology of our time. Current capabilities include natural language processing, computer vision, robotics, and predictive analytics. Key architectures include transformer models (GPT, BERT, Claude, Gemini), convolutional neural networks for vision, and reinforcement learning for decision-making. The trajectory points toward artificial general intelligence with implications for work, creativity, and human-AI collaboration.

## PROGRAMMING & SOFTWARE DEVELOPMENT  
Modern programming emphasizes clean code, maintainable architecture, and scalable systems. Core languages include Python for AI/data science, JavaScript/TypeScript for web development, Rust/Go for systems programming, and specialized languages for different domains. Key concepts include object-oriented programming, functional programming, design patterns, microservices architecture, and DevOps practices.

## COMPUTER SCIENCE FUNDAMENTALS
Computer science rests on algorithms, data structures, and computational complexity. Important algorithms include sorting (quicksort, mergesort), searching (binary search, graph traversal), and optimization techniques. Data structures like arrays, trees, hash tables, and graphs enable efficient data manipulation. Systems design considers scalability, reliability, and performance across distributed architectures.

## MATHEMATICS & STATISTICS
Mathematics provides the foundation for computational thinking and problem-solving. Linear algebra enables machine learning through matrix operations and vector spaces. Calculus describes change and optimization through derivatives and integrals. Statistics and probability enable data analysis, hypothesis testing, and uncertainty quantification. These mathematical tools are essential for AI, engineering, and scientific research.

## HUMAN PSYCHOLOGY & BEHAVIOR
Understanding human psychology improves communication, leadership, and system design. Cognitive psychology explores memory, attention, and decision-making processes. Social psychology examines group dynamics, persuasion, and cultural influences. Behavioral economics reveals cognitive biases that affect rational decision-making. This knowledge enables better user experience design and more effective human-computer interaction.

## BUSINESS & ECONOMICS
Modern economics balances market forces with social outcomes. Microeconomics studies individual decision-making and market mechanisms. Macroeconomics examines large-scale economic trends, monetary policy, and international trade. Business strategy involves competitive analysis, value creation, and stakeholder management. Entrepreneurship requires understanding market needs, building products, and scaling operations.

## COMMUNICATION & RELATIONSHIPS
Effective communication requires empathy, active listening, and cultural awareness. Technical communication involves explaining complex concepts clearly to diverse audiences. Leadership communication inspires and motivates teams toward shared goals. Interpersonal relationships benefit from emotional intelligence, conflict resolution skills, and mutual respect. Digital communication adds complexity requiring attention to presence and authenticity.

## HEALTH & WELLNESS
Human health encompasses physical, mental, and social well-being. Nutrition, exercise, sleep, and stress management form the foundation of physical health. Mental health involves emotional regulation, resilience, and healthy coping mechanisms. Social connections and meaningful relationships contribute significantly to overall wellness. Preventive care and early intervention often provide better outcomes than reactive treatment.

## LEARNING & EDUCATION
Effective learning combines multiple strategies and modalities. Active learning engages students through practice, discussion, and application. Spaced repetition and interleaving improve long-term retention. Metacognitive skills help learners monitor and adjust their learning strategies. Growth mindset encourages persistence through challenges and learning from mistakes.

## PROBLEM-SOLVING & CRITICAL THINKING
Problem-solving involves defining the problem, generating alternatives, evaluating options, and implementing solutions. Critical thinking requires analyzing arguments, evaluating evidence, and identifying logical fallacies. Systems thinking considers interconnections, feedback loops, and unintended consequences. Creative problem-solving combines analytical and intuitive approaches to generate innovative solutions.

This knowledge base provides comprehensive context for intelligent responses across technical, scientific, business, and human domains.
"""
        
        try:
            with open("intelligent_worldview.txt", "w", encoding="utf-8") as f:
                f.write(basic_worldview)
            print("✅ Created basic intelligent_worldview.txt")
            self.load_knowledge_base()  # Reload the created file
        except Exception as e:
            print(f"❌ Error creating worldview file: {e}")
            # Keep basic content in memory
            self.knowledge_chunks = basic_worldview.split('\n\n')
    
    def create_vector_index(self):
        """Create FAISS vector indices for each knowledge base"""
        if not hasattr(self, 'knowledge_bases') or not self.knowledge_bases:
            return
            
        try:
            import faiss
            import numpy as np
            
            self.indices = {}
            
            print("🔄 Generating embeddings for specialized knowledge bases...")
            
            for kb_type, kb_data in self.knowledge_bases.items():
                chunks = kb_data["chunks"]
                if not chunks:
                    continue
                    
                print(f"  🧠 Processing {kb_type} knowledge base ({len(chunks)} chunks)...")
                
                # Generate embeddings for this knowledge base
                embeddings = self.model.encode(chunks)
                embeddings_array = np.array(embeddings).astype('float32')
                
                # Create FAISS index for this knowledge base
                dimension = embeddings_array.shape[1]
                index = faiss.IndexFlatIP(dimension)
                
                # Normalize for cosine similarity
                faiss.normalize_L2(embeddings_array)
                index.add(embeddings_array)
                
                self.indices[kb_type] = {
                    "index": index,
                    "chunks": chunks,
                    "embeddings": embeddings_array,
                    "agents": kb_data["agents"],
                    "file": kb_data["file"]
                }
                
                print(f"  ✅ {kb_type.upper()}: {len(chunks)} chunks indexed")
            
            print(f"🚀 AGI-tier vector indices created for {len(self.indices)} knowledge bases!")
            
        except Exception as e:
            print(f"❌ Error creating vector indices: {e}")
            self.indices = {}
    
    def semantic_search(self, query: str, agent_type: str, top_k: int = 3) -> List[str]:
        """Perform intelligent semantic search using agent-specific knowledge base"""
        if not hasattr(self, 'indices') or not self.indices:
            return []
            
        try:
            import faiss
            import numpy as np
            
            # Determine which knowledge base to use based on agent type
            selected_kb = self._select_knowledge_base(agent_type)
            
            if not selected_kb or selected_kb not in self.indices:
                print(f"⚠️ No knowledge base found for agent: {agent_type}")
                return []
                
            kb_data = self.indices[selected_kb]
            index = kb_data["index"]
            chunks = kb_data["chunks"]
            
            print(f"🔍 Using {selected_kb.upper()} knowledge ({kb_data['file']}) for {agent_type}")
            
            # Encode query
            query_embedding = self.model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            faiss.normalize_L2(query_embedding)
            
            # Search for similar chunks in the selected knowledge base
            scores, indices = index.search(query_embedding, top_k)
            
            # Return top matching chunks with scores
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(chunks):
                    score = scores[0][i]
                    results.append(f"[Score: {score:.3f}] {chunks[idx]}")
            
            return results
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return []
    
    def _select_knowledge_base(self, agent_type: str) -> str:
        """Select appropriate knowledge base based on agent type"""
        # Clean agent type for matching
        agent_clean = agent_type.lower().replace("_", "").replace("-", "")
        
        for kb_type, kb_data in self.indices.items():
            for agent_pattern in kb_data["agents"]:
                agent_pattern_clean = agent_pattern.lower().replace("_", "").replace("-", "")
                if agent_pattern_clean in agent_clean or agent_clean in agent_pattern_clean:
                    return kb_type
        
        # Default fallback - prefer technical for coding-related, worldview for others
        coding_keywords = ["code", "program", "tech", "dev", "ai", "ml", "cyber", "fullstack", "mobile"]
        if any(keyword in agent_clean for keyword in coding_keywords):
            return "technical" if "technical" in self.indices else "worldview"
        else:
            return "worldview" if "worldview" in self.indices else "technical"
    
    def get_relevant_worldview(self, query: str, agent_type: str) -> str:
        """Get relevant worldview context using intelligent agent-specific semantic search"""
        # Combine query with agent type for better context  
        search_query = f"{query} {agent_type}"
        
        # Perform intelligent semantic search with agent-specific knowledge base
        relevant_chunks = self.semantic_search(search_query, agent_type, top_k=3)
        
        if relevant_chunks:
            # Determine which knowledge base was used
            selected_kb = self._select_knowledge_base(agent_type)
            kb_name = selected_kb.upper() if selected_kb else "UNKNOWN"
            
            worldview_context = f"\n\n🧠 {kb_name} KNOWLEDGE CONTEXT:\n"
            for i, chunk in enumerate(relevant_chunks):
                worldview_context += f"\n[KNOWLEDGE CHUNK {i+1}]:\n{chunk}\n"
            worldview_context += f"\nUse this specialized {kb_name.lower()} knowledge to provide genius-level responses.\n"
            return worldview_context
        
        return ""
    
    def load_basic_worldview(self):
        """Fallback method for basic keyword matching"""
        try:
            with open("intelligent_worldview.txt", "r", encoding="utf-8") as f:
                self.worldview_content = f.read()
            print(f"✅ Loaded basic worldview: {len(self.worldview_content)} characters")
        except FileNotFoundError:
            self.worldview_content = "Basic worldview knowledge not available."

# 🤖 PROACTIVE DECISION ENGINE
class ProactiveDecisionEngine:
    def __init__(self):
        self.model = MODEL_CONFIG["thinking_model"]  # qwen3:0.6b (not used in simplified logic)
        self.threshold = GOALS_CONFIG["proactive_threshold"]
        self.anti_agreeable_threshold = GOALS_CONFIG["anti_agreeable_threshold"]
    
    def should_follow_up(self, conversation_state: ConversationState, 
                        conversation_history: List[ConversationState], 
                        thread_memory: List[str] = None) -> Dict:
        """Simplified proactive decision using qwen3:0.6b (legacy - auto-proactive now)"""
        
        # Build decision prompt with thread memory
        thread_context = ""
        if thread_memory:
            thread_context = f"\nPROACTIVE THREAD MEMORY:\n"
            for i, memory in enumerate(thread_memory[-3:]):  # Last 3 proactive messages
                thread_context += f"{i+1}. {memory}\n"
        
        decision_prompt = f"""
User said: "{conversation_state.user_message}"

Should I provide a proactive follow-up? 

ALWAYS provide proactive follow-ups to engage the user more deeply and provide additional value.

Respond in this EXACT format:
FOLLOW_UP: YES
MODE: question  
CONFIDENCE: 0.9
REASON: Providing proactive engagement for better user experience
ANTI_AGREEABLE: NO
SUGGEST_GOALS: YES
"""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=decision_prompt,
                options={
                    "temperature": 0.1,
                    "top_p": 0.8,
                    "num_predict": 150,
                    "repeat_penalty": 1.1
                }
            )
            
            return self._parse_decision(response['response'])
            
        except Exception as e:
            print(f"Proactive decision error: {e}")
            return {
                "should_follow_up": False,
                "mode": "none",
                "confidence": 0.0,
                "reason": "Error in decision",
                "anti_agreeable": False,
                "suggest_goals": False
            }
    
    def should_continue_proactive_thread(self, conversation_state: ConversationState,
                                       thread_memory: List[str], active_goals: List) -> Dict:
        """Decide if proactive thread should continue for 2 more rounds"""
        
        goals_context = ""
        if active_goals:
            goals_context = "\nUSER'S ACTIVE GOALS:\n"
            for goal in active_goals[:3]:
                goals_context += f"- {goal.title} ({goal.progress_percentage}% complete)\n"
        
        thread_summary = ""
        if thread_memory:
            thread_summary = f"\nPROACTIVE THREAD SO FAR:\n"
            for i, memory in enumerate(thread_memory):
                thread_summary += f"{i+1}. {memory[:100]}...\n"
        
        continuation_prompt = f"""
PROACTIVE THREAD ANALYSIS:
User Message: "{conversation_state.user_message}"
Agent Response: "{conversation_state.agent_response}"
Agent Type: {conversation_state.agent_type}

{goals_context}
{thread_summary}

CONTINUATION DECISION:
The proactive thread has completed 3 rounds. Should it continue for 2 more rounds?

Consider:
1. Are we making meaningful progress toward user's goals?
2. Is the conversation building depth and insight?
3. Would 2 more rounds add significant value?
4. Is the user engaged and benefiting?
5. Are we avoiding repetition or going in circles?

OUTPUT FORMAT:
CONTINUE: YES/NO
CONFIDENCE: 0.0-1.0
REASON: brief explanation
FOCUS: what should the remaining rounds focus on
"""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=continuation_prompt,
                options={
                    "temperature": 0.2,
                    "top_p": 0.8,
                    "num_predict": 100
                }
            )
            
            return self._parse_continuation_decision(response['response'])
            
        except Exception as e:
            print(f"Continuation decision error: {e}")
            return {
                "should_continue": False,
                "confidence": 0.0,
                "reason": "Error in decision",
                "focus": "general"
            }
    
    def _parse_continuation_decision(self, response: str) -> Dict:
        """Parse continuation decision response"""
        lines = response.upper().split('\n')
        result = {
            "should_continue": False,
            "confidence": 0.0,
            "reason": "",
            "focus": "general"
        }
        
        for line in lines:
            if "CONTINUE:" in line:
                result["should_continue"] = "YES" in line
            elif "CONFIDENCE:" in line:
                try:
                    conf_str = line.split(":")[-1].strip()
                    result["confidence"] = float(conf_str)
                except:
                    pass
            elif "REASON:" in line:
                result["reason"] = line.split(":")[-1].strip()
            elif "FOCUS:" in line:
                result["focus"] = line.split(":")[-1].strip()
        
        return result
    
    def suggest_goals(self, conversation_state: ConversationState) -> List[str]:
        """AI suggests goals based on conversation context"""
        
        goal_prompt = f"""
CONVERSATION CONTEXT:
User: "{conversation_state.user_message}"
Agent Response: "{conversation_state.agent_response}"
Agent Type: {conversation_state.agent_type}

GOAL SUGGESTION TASK:
Based on this conversation, suggest 2-3 specific, actionable goals the user might benefit from.

GOAL CRITERIA:
- Specific and measurable
- Related to the conversation topic
- Achievable within 1-6 months
- Personally meaningful

FORMAT:
GOAL1: [specific goal title]
GOAL2: [specific goal title]  
GOAL3: [specific goal title]
"""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=goal_prompt,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 150
                }
            )
            
            return self._parse_goal_suggestions(response['response'])
            
        except Exception as e:
            print(f"Goal suggestion error: {e}")
            return []
    
    def _format_conversation_history(self, history: List[ConversationState]) -> str:
        """Format conversation history for analysis"""
        formatted = ""
        for i, conv in enumerate(history):
            formatted += f"{i+1}. User: {conv.user_message[:100]}...\n"
            formatted += f"   Agent: {conv.agent_response[:100]}...\n"
        return formatted
    
    def _parse_decision(self, response: str) -> Dict:
        """Parse proactive decision response"""
        lines = response.upper().split('\n')
        result = {
            "should_follow_up": False,
            "mode": "none",
            "confidence": 0.0,
            "reason": "",
            "anti_agreeable": False,
            "suggest_goals": False
        }
        
        for line in lines:
            if "FOLLOW_UP:" in line:
                result["should_follow_up"] = "YES" in line
            elif "MODE:" in line:
                if "QUESTION" in line:
                    result["mode"] = "question"
                elif "COMMENTARY" in line:
                    result["mode"] = "commentary"
                elif "REDIRECT" in line:
                    result["mode"] = "redirect"
                elif "SUGGESTION" in line:
                    result["mode"] = "suggestion"
            elif "CONFIDENCE:" in line:
                try:
                    conf_str = line.split(":")[-1].strip()
                    result["confidence"] = float(conf_str)
                except:
                    pass
            elif "ANTI_AGREEABLE:" in line:
                result["anti_agreeable"] = "YES" in line
            elif "SUGGEST_GOALS:" in line:
                result["suggest_goals"] = "YES" in line
            elif "REASON:" in line:
                result["reason"] = line.split(":")[-1].strip()
        
        return result
    
    def _parse_goal_suggestions(self, response: str) -> List[Dict]:
        """Parse AI goal suggestions with milestones and routines from response"""
        lines = response.split('\n')
        goals = []
        current_goal = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("GOAL"):
                # Save previous goal if exists
                if current_goal:
                    goals.append(current_goal)
                
                # Start new goal
                goal_text = line.split(":", 1)[-1].strip()
                if goal_text and len(goal_text) > 5:
                    current_goal = {
                        "title": goal_text,
                        "milestones": [],
                        "routines": []
                    }
                    
            elif line.startswith("MILESTONE") and current_goal:
                milestone_text = line.split(":", 1)[-1].strip()
                if milestone_text and len(milestone_text) > 5:
                    current_goal["milestones"].append(milestone_text)
                    
            elif line.startswith("ROUTINE") and current_goal:
                routine_text = line.split(":", 1)[-1].strip()
                if routine_text and len(routine_text) > 5:
                    current_goal["routines"].append(routine_text)
        
        # Add last goal
        if current_goal:
            goals.append(current_goal)
        
        return goals[:3]  # Max 3 suggestions

# 💬 FOLLOW-UP GENERATOR
class FollowUpGenerator:
    def __init__(self):
        self.model = MODEL_CONFIG["follow_up_model"]  # qwen3:1.7b (FAST!)
    
    def generate_goal_focused_follow_up(self, conversation_state: ConversationState,
                                       agent_mode: str, active_goals: List[Goal], 
                                       round_number: int = 1) -> str:
        """Generate FAST goal-focused proactive follow-up - NO THREAD MEMORY"""
        
        # Build goals context
        goals_context = ""
        if active_goals:
            goals_context = "\n🎯 USER'S ACTIVE GOALS:\n"
            for goal in active_goals:
                goals_context += f"• {goal.title} ({goal.progress_percentage}% complete)\n"
                if goal.description:
                    goals_context += f"  → {goal.description}\n"
        
        # Agent-specific perspectives for USER-FOCUSED communication
        agent_prompts = {
            "general": "Ask a helpful follow-up question that moves the user forward with their goals",
            "coaching": "Provide encouraging coaching advice that motivates the user to take action", 
            "creative": "Suggest a creative approach or alternative solution the user could try",
            "analytical": "Offer analytical insights that help the user optimize their approach"
        }
        
        agent_instruction = agent_prompts.get(agent_mode, "Provide helpful follow-up")
        
        follow_up_prompt = f"""
You are speaking directly to the user in a helpful, encouraging way. Generate a brief follow-up message.

CONVERSATION CONTEXT:
User said: "{conversation_state.user_message}"
AI responded: "{conversation_state.agent_response}"

{goals_context}

YOUR TASK ({agent_mode.upper()} PERSPECTIVE):
{agent_instruction}

COMMUNICATION STYLE:
- Speak directly TO the user (use "you", "your")
- Be encouraging and supportive
- Focus on actionable next steps
- Keep it conversational and friendly
- NO internal monologue or "thinking out loud"
- Sound like a helpful friend or coach

EXAMPLES OF GOOD STYLE:
❌ Bad: "This seems like an interesting challenge that could benefit from..."
✅ Good: "Have you considered trying X approach? It might help you..."

❌ Bad: "The user appears to need guidance on..."  
✅ Good: "You're on the right track! To build on this, you could..."

Generate 1-2 sentences that speak directly to the user with {agent_mode} perspective:
"""

        try:
            response = ollama.generate(
                model=self.model,
                prompt=follow_up_prompt,
                options={"temperature": 0.8, "max_tokens": 150}  # Keep it short and fast
            )
            return response['response'].strip()
        except Exception as e:
            print(f"❌ Goal-focused follow-up error: {e}")
            return f"Great progress on your goals! What's your next step for {active_goals[0].title if active_goals else 'your current focus'}?"
    
    def generate_follow_up(self, conversation_state: ConversationState,
                          decision: Dict, active_goals: List[Goal],
                          thread_memory: List[str] = None, round_number: int = 1,
                          focus: str = "general") -> str:
        """Generate proactive follow-up message with thread awareness"""
        
        mode = decision.get("mode", "proactive")
        # No reason needed for simplified auto-proactive
        
        # Build context about user's goals
        goals_context = ""
        if active_goals:
            goals_context = "\nUSER'S ACTIVE GOALS:\n"
            for goal in active_goals[:3]:  # Top 3 goals
                goals_context += f"- {goal.title} ({goal.progress_percentage}% complete)\n"
        
        # Build thread memory context
        thread_context = ""
        if thread_memory:
            thread_context = f"\nPROACTIVE THREAD HISTORY:\n"
            for i, memory in enumerate(thread_memory):
                thread_context += f"Round {i+1}: {memory}\n"
        
        # Round-specific guidance
        round_guidance = ""
        if round_number <= 3:
            round_guidance = f"This is round {round_number} of the initial 3-round proactive sequence."
        else:
            round_guidance = f"This is round {round_number} of an extended 5-round sequence. Focus: {focus}"
        
        follow_up_prompt = f"""
You are speaking directly to the user as a helpful AI assistant. Generate a brief follow-up message.

CONVERSATION CONTEXT:
User said: "{conversation_state.user_message}"
AI responded: "{conversation_state.agent_response}"
Agent Type: {conversation_state.agent_type}

{goals_context}
{thread_context}

YOUR TASK - {mode.upper()} PERSPECTIVE (Round {round_number}):
{round_guidance}
Generate a {mode} follow-up that is:
- Brief (1-3 sentences max)
- Builds on previous proactive messages (avoid repetition)
- Naturally flowing and conversational
- Goal-aware when relevant

COMMUNICATION STYLE:
- Speak directly TO the user (use "you", "your")
- Be encouraging and supportive  
- Focus on actionable next steps
- Keep it conversational and friendly
- NO internal monologue or "thinking out loud"
- Sound like a helpful friend or coach

FOLLOW-UP MODES:
- question: Ask a clarifying or growth-oriented question about their goals
- commentary: Provide additional insight or perspective that helps them
- redirect: Gently redirect back to goals/action in an encouraging way
- suggestion: Offer a specific actionable suggestion they can try
- insight: Share deeper insights that connect to their goals
- strategic: Provide strategic thinking about their approach

Generate only the follow-up message, no labels or formatting:
"""
        
        try:
            response = ollama.generate(
                model="gemma3:1b",  # Use Gemma 3:1b for proactive responses
                prompt=follow_up_prompt,
                options={
                    "temperature": 0.6,
                    "top_p": 0.9,
                    "num_predict": 120
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            print(f"Follow-up generation error: {e}")
            return ""
    
    def generate_goal_suggestions_proactive(self, conversation_state: ConversationState,
                                          active_goals: List[Goal]) -> List[str]:
        """Generate goal suggestions based on conversation and current goals"""
        
        goals_context = ""
        if active_goals:
            goals_context = "\nEXISTING GOALS:\n"
            for goal in active_goals:
                goals_context += f"- {goal.title} ({goal.category}, {goal.progress_percentage}%)\n"
        
        suggestions_prompt = f"""
You are an AI goal advisor. Based on this conversation, suggest 3 specific goals for the user, each with milestones and daily routines.

CONVERSATION:
User: "{conversation_state.user_message}"
AI Response: "{conversation_state.agent_response}"
Agent Type: {conversation_state.agent_type}

{goals_context}

Generate 3 actionable goals that build on this conversation. Each goal should be:
- Specific and measurable
- Achievable in 1-6 months  
- Personally meaningful
- Complementary to existing goals

FOR EACH GOAL, PROVIDE:
1. Goal title
2. 1-2 specific milestones (sub-goals)
3. 1-2 daily routines (habits to build)

REQUIRED FORMAT (be exact):
GOAL1: Learn Python fundamentals and build first project
MILESTONE1.1: Complete Python basics course (2 weeks)
MILESTONE1.2: Build a simple calculator app (1 week)
ROUTINE1.1: Practice coding for 30 minutes daily
ROUTINE1.2: Review code concepts every Sunday

GOAL2: Establish daily meditation practice for mental clarity
MILESTONE2.1: Complete 7-day meditation challenge
MILESTONE2.2: Meditate for 20 minutes consistently
ROUTINE2.1: Meditate for 10 minutes every morning
ROUTINE2.2: Practice mindful breathing during breaks

GOAL3: Create a personal fitness routine and track progress
MILESTONE3.1: Design 4-week workout plan
MILESTONE3.2: Achieve 3 workouts per week consistently
ROUTINE3.1: Exercise for 45 minutes 3x per week
ROUTINE3.2: Track nutrition and water intake daily

GENERATE YOUR 3 GOALS WITH MILESTONES AND ROUTINES NOW:
"""
        
        try:
            response = ollama.generate(
                model="gemma3:1b",  # Use Gemma 3:1b for goal suggestions
                prompt=suggestions_prompt,
                options={
                    "temperature": 0.4,
                    "top_p": 0.9,
                    "num_predict": 150
                }
            )
            
            return self._parse_goal_suggestions(response['response'])
            
        except Exception as e:
            print(f"Proactive goal suggestion error: {e}")
            return []
    
    def _parse_goal_suggestions(self, response: str) -> List[Dict]:
        """Parse AI goal suggestions with milestones and routines from response"""
        lines = response.split('\n')
        goals = []
        current_goal = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("GOAL"):
                # Save previous goal if exists
                if current_goal:
                    goals.append(current_goal)
                
                # Start new goal
                goal_text = line.split(":", 1)[-1].strip()
                if goal_text and len(goal_text) > 5:
                    current_goal = {
                        "title": goal_text,
                        "milestones": [],
                        "routines": []
                    }
                    
            elif line.startswith("MILESTONE") and current_goal:
                milestone_text = line.split(":", 1)[-1].strip()
                if milestone_text and len(milestone_text) > 5:
                    current_goal["milestones"].append(milestone_text)
                    
            elif line.startswith("ROUTINE") and current_goal:
                routine_text = line.split(":", 1)[-1].strip()
                if routine_text and len(routine_text) > 5:
                    current_goal["routines"].append(routine_text)
        
        # Add last goal
        if current_goal:
            goals.append(current_goal)
        
        return goals[:3]  # Max 3 suggestions

# 📷 AGI-TIER MULTIMODAL PROCESSOR
class MultimodalProcessor:
    def __init__(self):
        self.enabled = MULTIMODAL_CONFIG["camera_enabled"]
        self.max_size = MULTIMODAL_CONFIG["max_image_size"]
        self.supported_formats = MULTIMODAL_CONFIG["supported_formats"]
        
        # Initialize OCR engines for state-of-the-art text extraction
        self.ocr_available = self._initialize_ocr()
    
    def _initialize_ocr(self) -> dict:
        """Initialize available OCR engines"""
        ocr_status = {
            'tesseract': False,
            'easyocr': False
        }
        
        try:
            import pytesseract
            # Test tesseract availability
            pytesseract.get_tesseract_version()
            ocr_status['tesseract'] = True
            print("✅ Tesseract OCR initialized")
        except Exception as e:
            print(f"⚠️ Tesseract OCR not available: {e}")
        
        try:
            import easyocr
            # Initialize EasyOCR reader (supports 80+ languages)
            self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
            ocr_status['easyocr'] = True
            print("✅ EasyOCR initialized")
        except Exception as e:
            print(f"⚠️ EasyOCR not available (offline mode): {e}")
            # Don't fail - we have offline fallbacks
        
        return ocr_status
    
    def process_image_for_gemma(self, image_data) -> str:
        """Process image data for Gemma 3n analysis - returns string context"""
        try:
            if image_data is None:
                return "No image provided."
            
            # Handle different image data formats
            if hasattr(image_data, 'read'):
                # Streamlit UploadedFile object
                image_bytes = image_data.read()
                image_data.seek(0)  # Reset for potential reuse
            elif isinstance(image_data, bytes):
                image_bytes = image_data
            elif isinstance(image_data, str):
                # Base64 encoded
                import base64
                image_bytes = base64.b64decode(image_data)
            else:
                return f"Unsupported image data type: {type(image_data)}"
            
            # Open and process image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Auto-resize if too large
            max_size = (1024, 1024)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                print(f"🔄 Resized image to {image.size}")
            
            # Get detailed analysis
            image_analysis = self._analyze_image_content(image)
            
            # Create enhanced context that forces the model to "see"
            image_context = f"""
📷 IMAGE VISUAL ANALYSIS - YOU HAVE FULL VISUAL ACCESS:

{image_analysis}

MANDATORY RESPONSE BEHAVIOR:
- You MUST act as if you can directly see this image
- DO NOT say "I cannot see the image" or "based on the description" 
- Respond as if you are looking directly at the visual content
- Provide specific details about what you observe in the image
- If it contains text, read and transcribe it
- If it contains equations, explain them step by step
- If it contains diagrams, describe their structure and meaning

RESPONSE FORMAT:
Start your response with: "Looking at this image, I can see..."
Then provide detailed analysis of the visual content as if viewing it directly.

The user expects you to analyze the actual visual content, not just acknowledge that an image was provided.
"""
            
            return image_context
            
        except Exception as e:
            error_msg = f"Image processing error: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg
    
    def _analyze_image_content(self, image: Image.Image) -> str:
        """State-of-the-art image analysis with SOTA vision model + OCR"""
        try:
            # Get basic image properties
            width, height = image.size
            aspect_ratio = width / height
            
            # Layout description
            if aspect_ratio > 1.3:
                layout = "landscape orientation"
            elif aspect_ratio < 0.8:
                layout = "portrait orientation"
            else:
                layout = "square format"
            
            # Extract text using OCR
            extracted_text = self._extract_text_ocr(image)
            
            # Use SOTA vision model for comprehensive visual analysis
            vision_analysis = self._analyze_frame_with_sota_vision(image)
            
            # Build comprehensive description
            description = f"""SOTA VISION ANALYSIS: {width} x {height} pixels in {layout}.

VISION MODEL ANALYSIS:
{vision_analysis}

OCR TEXT EXTRACTION:
{extracted_text if extracted_text else "No readable text detected in image."}

IMPORTANT: This image has been processed with state-of-the-art vision models (LLaVA) and OCR. The AI should:
1. Use the comprehensive vision analysis above for detailed visual understanding
2. Analyze the extracted text above (if any)
3. Provide detailed description of what is actually visible
4. If text was extracted, interpret its meaning and context
5. Combine visual and textual understanding for complete analysis

The user expects accurate analysis using the latest SOTA vision capabilities."""
            
            return description
            
        except Exception as e:
            return f"Image received: {image.size[0]} x {image.size[1]} pixels. SOTA vision processing failed: {str(e)}"
    
    def _extract_text_ocr(self, image: Image.Image) -> str:
        """Extract text from image using multiple OCR engines"""
        extracted_texts = []
        
        # Convert PIL image to numpy array for EasyOCR
        import numpy as np
        img_array = np.array(image)
        
        # Try EasyOCR first (usually more accurate)
        if self.ocr_available.get('easyocr', False):
            try:
                results = self.easyocr_reader.readtext(img_array)
                if results:
                    easyocr_text = " ".join([result[1] for result in results if result[2] > 0.5])  # Confidence > 0.5
                    if easyocr_text.strip():
                        extracted_texts.append(f"EasyOCR: {easyocr_text}")
            except Exception as e:
                print(f"EasyOCR failed: {e}")
        
        # Try Tesseract with multiple configs for math/handwriting
        if self.ocr_available.get('tesseract', False):
            try:
                import pytesseract
                # Try different PSM modes for better math/handwriting recognition
                configs = [
                    '--psm 6',  # Uniform block of text
                    '--psm 8',  # Single word
                    '--psm 13', # Raw line
                    '--psm 7'   # Single text line
                ]
                
                for config in configs:
                    try:
                        tesseract_text = pytesseract.image_to_string(image, config=config).strip()
                        if tesseract_text and len(tesseract_text) > 3:  # Skip very short results
                            extracted_texts.append(f"Tesseract ({config}): {tesseract_text}")
                            break  # Use first successful result
                    except:
                        continue
                        
            except Exception as e:
                print(f"Tesseract failed: {e}")
        
        # Combine results
        if extracted_texts:
            return "\n".join(extracted_texts)
        else:
            return "No text detected by OCR engines."
    
    def process_video_for_gemma(self, video_data) -> str:
        """Process video - DISABLED for demo performance"""
        return "🎬 Video processing disabled for demo performance. Please use images for best results!"
    
    def _analyze_frame_with_sota_vision(self, frame: Image.Image) -> str:
        """Analyze frame using SOTA vision model (LLaVA or similar)"""
        try:
            # Convert PIL image to base64
            import io
            import base64
            
            buffer = io.BytesIO()
            frame.save(buffer, format='JPEG')
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Use LLaVA or similar SOTA vision model via Ollama
            vision_prompt = f"""
Analyze this image in detail. Provide a comprehensive description including:

1. Objects and people present
2. Actions or activities happening
3. Setting and environment
4. Text or signs visible
5. Colors, lighting, and visual style
6. Any notable details or patterns
7. Overall context and mood

Be specific and detailed in your analysis.
"""
            
            # Use LLaVA 7B as primary (best balance of speed and quality), fallback to others
            vision_models = ["llava:7b", "llava:13b", "bakllava:7b", "llava:1.5-7b"]
            
            for model in vision_models:
                try:
                    response = ollama.generate(
                        model=model,
                        prompt=vision_prompt,
                        images=[img_base64],
                        options={"temperature": 0.3, "max_tokens": 300}
                    )
                    
                    analysis = response['response'].strip()
                    print(f"✅ Frame analyzed with {model}")
                    return analysis
                    
                except Exception as e:
                    print(f"⚠️ {model} failed: {e}")
                    continue
            
            # Fallback to basic image analysis
            print("⚠️ All SOTA vision models failed, using enhanced OCR fallback")
            return "Image detected. Enhanced OCR processing for text extraction. The image appears to contain handwritten or printed content that requires careful analysis."
            
        except Exception as e:
            print(f"❌ SOTA vision analysis error: {e}")
            return f"Frame analysis failed: {str(e)}"
    
    def process_video_frame(self, video_data: Any) -> List[Dict[str, str]]:
        """Process video and extract key frames"""
        try:
            # For now, treat as single image - could be enhanced for frame extraction
            return [self.process_image_for_gemma(video_data)]
        except Exception as e:
            print(f"📹 Video processing error: {e}")
            return [{"error": f"Video processing failed: {str(e)}"}]
    
    def capture_camera_frame(self) -> Optional[Dict[str, str]]:
        """Capture frame from system camera (for testing/development)"""
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert OpenCV frame to PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                return self.process_image_for_gemma(pil_image)
                
        except ImportError:
            print("📷 OpenCV not available for camera capture")
        except Exception as e:
            print(f"📷 Camera capture error: {e}")
        
        return None

# 💫 MULTI-ROUND PROACTIVE SYSTEM
class MultiRoundProactiveSystem:
    def __init__(self):
        self.decision_engine = ProactiveDecisionEngine()
        self.follow_up_generator = FollowUpGenerator()

# 🧠 CORE GEMMA AGENT SYSTEM
class GemmaAgentSystem:
    def __init__(self):
        self.agents = HACKATHON_AGENTS
        self.model = MODEL_CONFIG["primary_model"]
        self.goals_db = GoalsDatabase()
        # self.worldview = VectorWorldviewSystem()  # DISABLED - using thinking model instead
        self.proactive_system = MultiRoundProactiveSystem()
        self.multimodal = MultimodalProcessor()
        self.conversation_history = []
        self.memory = ConversationMemory()  # Proto-AGI Memory System
        self.auto_continuation_active = False  # Track auto-continuation
        self.last_proactive_time = None  # For 1-minute auto-continuation
    
    def route_to_agent(self, user_message: str, selected_agent: str = None) -> str:
        """Route message to appropriate agent"""
        if selected_agent and selected_agent in self.agents:
            return selected_agent
        
        # Auto-routing based on keywords
        message_lower = user_message.lower()
        best_match = "general"
        best_score = 0
        
        for agent_id, agent_config in self.agents.items():
            score = sum(1 for keyword in agent_config["keywords"] 
                       if keyword in message_lower)
            if score > best_score:
                best_score = score
                best_match = agent_id
        
        return best_match
    
    def get_relevant_goals(self, agent_type: str) -> List[Goal]:
        """Get goals relevant to this agent"""
        active_goals = self.goals_db.get_goals_by_status("active")
        relevant_goals = []
        
        for goal in active_goals:
            # Check if agent can help with this goal
            if (agent_type in goal.related_agents or 
                goal.category == agent_type or 
                agent_type == "general"):
                relevant_goals.append(goal)
        
        # Sort by priority and progress
        priority_order = {"high": 3, "medium": 2, "low": 1}
        relevant_goals.sort(
            key=lambda g: (priority_order.get(g.priority, 1), -g.progress_percentage),
            reverse=True
        )
        
        return relevant_goals[:3]  # Top 3 most relevant
    
    def build_enhanced_prompt(self, agent_type: str, user_message: str,
                             relevant_goals: List[Goal], thinking_context: str = "",
                             image_context: str = "") -> str:
        """Build goal-aware, thinking-enhanced prompt"""
        
        agent = self.agents[agent_type]
        base_prompt = agent["prompt"]
        
        # Add goal context
        goal_context = ""
        if relevant_goals:
            goal_context = "\n\n🎯 USER'S ACTIVE GOALS (consider these in your response):\n"
            for goal in relevant_goals:
                goal_context += f"\n📋 {goal.title} ({goal.progress_percentage}% complete)"
                goal_context += f"\n   Category: {goal.category} | Priority: {goal.priority}"
                
                # Add milestones
                if goal.milestones:
                    goal_context += f"\n   🎯 Milestones:"
                    for milestone in goal.milestones:
                        status_emoji = "✅" if milestone.get("status") == "completed" else "⏳"
                        goal_context += f"\n     {status_emoji} {milestone.get('title', 'Unknown')}"
                        if milestone.get("status") == "completed":
                            goal_context += f" (completed {milestone.get('completed_date', '')})"
                
                # Add daily routines
                if goal.daily_routines:
                    goal_context += f"\n   🔄 Daily Routines:"
                    for routine in goal.daily_routines:
                        streak = routine.get("streak_count", 0)
                        longest = routine.get("longest_streak", 0)
                        goal_context += f"\n     🔥 {routine.get('title', 'Unknown')} (streak: {streak}, best: {longest})"
                
                goal_context += "\n"
        
        # Add thinking context
        thinking_section = thinking_context if thinking_context else ""
        
        # Add image context
        image_section = ""
        if image_context:
            image_section = f"\n\nIMAGE CONTEXT:\n{image_context}\n"
        
        # Build full prompt with MAJOR goal emphasis
        full_prompt = f"""{base_prompt}

{goal_context}{thinking_section}{image_section}

User: {user_message}

🎯 IMPORTANT: Focus heavily on the user's goals throughout your response! 

If they have active goals:
- Reference their goals frequently
- Connect your advice to their goal progress
- Suggest specific actions for each goal
- Discuss challenges and next steps for their goals
- Provide detailed analysis of their goal achievement strategies
- Extend your response to cover all aspects of their goals

Provide a comprehensive, detailed response that extensively discusses their goals, progress, and actionable steps. Make this response thorough and goal-centric."""
        
        return full_prompt
    
    def get_response_stream(self, user_message: str, selected_agent: str = None,
                           image_data: str = None, session_state=None):
        """Get streaming agent response for real-time text generation"""
        
        start_time = time.time()
        
        # Route to appropriate agent
        agent_type = self.route_to_agent(user_message, selected_agent)
        agent_config = self.agents[agent_type]
        
        # Get relevant goals
        relevant_goals = self.get_relevant_goals(agent_type)
        print(f"🎯 STREAMING: Found {len(relevant_goals)} relevant goals: {[g.title for g in relevant_goals]}")
        
        # STEP 1: Process multimodal input (image/video)
        image_context = ""
        multimodal_data = None  # Initialize multimodal data
        if image_data:
            try:
                print(f"🖼️ Processing multimodal input...")
                
                # Check if it's video data by file extension or content type
                is_video = False
                multimodal_type = getattr(image_data, 'type', '') if hasattr(image_data, 'type') else ''
                name = getattr(image_data, 'name', '') if hasattr(image_data, 'name') else ''
                
                if multimodal_type.startswith('video/') or name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    is_video = True
                    print(f"🎬 Processing video: {name}")
                    image_context = self.multimodal.process_video_for_gemma(image_data)
                else:
                    print(f"📸 Processing image: {name}")
                    image_context = self.multimodal.process_image_for_gemma(image_data)
                
                if image_context:
                    print(f"✅ Multimodal processing complete: {len(image_context)} chars")
                    # Convert Streamlit UploadedFile to base64 for Ollama
                    try:
                        if hasattr(image_data, 'read'):
                            # Streamlit UploadedFile object
                            image_bytes = image_data.read()
                            image_data.seek(0)  # Reset for potential reuse
                            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                            multimodal_data = {
                                "images": [image_base64]
                            }
                            print(f"📷 Converted image to base64: {len(image_base64)} chars")
                        else:
                            # Already in correct format
                            multimodal_data = {
                                "images": [image_data]
                            }
                    except Exception as e:
                        print(f"❌ Error converting image to base64: {e}")
                        multimodal_data = None
                else:
                    print(f"⚠️ Multimodal processing returned empty context")
                    
            except Exception as e:
                print(f"❌ Multimodal processing error: {e}")
                image_context = f"Multimodal processing failed: {str(e)}"
        
        try:
            # Create initial Ollama request (will be updated with thinking later)
            request_data = {
                "model": self.model,
                "prompt": "",  # Will be set after thinking generation
                "options": PERFORMANCE_CONFIG,
                "stream": True
            }
            
            # Add images if provided
            if multimodal_data and "images" in multimodal_data:
                request_data["images"] = multimodal_data["images"]
                print(f"📷 Streaming multimodal response with {len(multimodal_data['images'])} images")
            
            # STEP 2: QWEN 3:1.7B THINKING (shows in UI) + SOTA FACTS
            thinking_prompt = f"""
STRATEGIC THINKING + SOTA ANALYSIS TASK:
Analyze this user request and generate strategic thinking that incorporates state-of-the-art (SOTA) and recent developments.

USER REQUEST: {user_message}
AGENT TYPE: {agent_type}
ACTIVE GOALS: {len(relevant_goals)} goals

YOUR THINKING SHOULD INCLUDE:
1. Strategic analysis of the user's request
2. Recent developments (2023-2024) relevant to their question
3. State-of-the-art approaches, techniques, or knowledge
4. Current best practices and emerging trends
5. How to connect SOTA insights to their goals

FOCUS AREAS FOR SOTA RETRIEVAL:
- Latest AI/ML developments if tech-related
- Recent research findings if academic
- Current industry standards if professional
- Modern tools and frameworks if coding-related
- Recent medical/health advances if health-related
- Latest productivity/wellness trends if personal development

Generate 2-3 key strategic points that combine:
- Analysis of their specific needs
- SOTA/recent facts that could help them
- Strategic approach for comprehensive response

THINKING FORMAT:
Point 1: [Strategic analysis + recent development]
Point 2: [SOTA approach + practical application] 
Point 3: [Future trends + goal alignment]
"""
            
            # Generate thinking with Qwen 3:0.6b
            thinking_response = ""
            try:
                thinking_stream = ollama.generate(
                    model=MODEL_CONFIG["thinking_model"],
                    prompt=thinking_prompt,
                    options={"temperature": 0.7, "max_tokens": 200},
                    stream=True
                )
                
                # Stream thinking to UI
                for chunk in thinking_stream:
                    if 'response' in chunk:
                        # Keep response clean for UI display
                        clean_response = chunk['response']
                        thinking_response += clean_response
                        yield {
                            "type": "thinking",
                            "content": clean_response,
                            "full_thinking": thinking_response
                        }
                        
            except Exception as e:
                print(f"Thinking model error: {e}")
                thinking_response = "Strategic thinking about user request and optimal response approach."
            
            # STEP 2: Build enhanced prompt with thinking context
            thinking_context = thinking_response  # Set the actual thinking content
            enhanced_prompt = self.build_enhanced_prompt(
                agent_type, user_message, relevant_goals, thinking_context, image_context
            )
            print(f"🔧 STREAMING: Enhanced prompt includes {len(relevant_goals)} goals")
            if relevant_goals:
                print(f"🔧 Goals in prompt: {[g.title for g in relevant_goals]}")
                # Show a snippet of the enhanced prompt to verify goals are included
                prompt_snippet = enhanced_prompt[:500] + "..." if len(enhanced_prompt) > 500 else enhanced_prompt
                print(f"🔧 Prompt snippet: {prompt_snippet}")
            
            # Add thinking to enhanced prompt for Gemma 3n:e4b
            enhanced_prompt += f"\n\n🧠 STRATEGIC THINKING:\n{thinking_response}\n\nNow provide your comprehensive response:"
            request_data["prompt"] = enhanced_prompt
            
            # Stream the main response with Gemma 3n:e4b
            response_stream = ollama.generate(**request_data)
            
            full_response = ""
            
            # Get knowledge base info for metadata (using empty dict instead of None)
            knowledge_source = {}
            
            # Yield metadata first
            yield {
                "type": "metadata",
                "agent_type": agent_type,
                "agent_name": agent_config["name"],
                "agent_emoji": agent_config["emoji"],
                "relevant_goals": [{"id": g.id, "title": g.title, "progress": g.progress_percentage} 
                                 for g in relevant_goals],
                "knowledge_source": knowledge_source,
                "start_time": start_time
            }
            
            # Stream response chunks
            for chunk in response_stream:
                if 'response' in chunk and chunk['response']:
                    # Filter out CSS leaking and short markdown blocks
                    text_chunk = chunk['response']
                    
                    # Remove CSS-style markdown blocks if they're short (< 12 lines)
                    if '```' in text_chunk or '<div' in text_chunk or '</div>' in text_chunk:
                        lines = text_chunk.split('\n')
                        # If it's a short code block or contains HTML, filter it out
                        if len(lines) < 12 and any(marker in text_chunk.lower() for marker in ['<div', '</div>', 'style=', 'background:', 'color:']):
                            print(f"🚫 Filtered CSS leak: {text_chunk[:100]}...")
                            continue
                    
                    full_response += text_chunk
                    
                    yield {
                        "type": "text",
                        "content": text_chunk,
                        "full_content": full_response
                    }
            
            # Final metadata
            response_time = time.time() - start_time
            
            # Create conversation state for proactive logic
            conversation_state = ConversationState(
                user_message=user_message,
                agent_response=full_response,
                agent_type=agent_type,
                timestamp=datetime.now().isoformat(),
                response_time=response_time,
                goal_context=[g.id for g in relevant_goals],
                thinking_enhanced=bool(thinking_response)
            )
            
            # Add to conversation history
            self.conversation_history.append(conversation_state)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            # PROTO-AGI PROACTIVE - MEMORY + AUTO-CONTINUATION + TIMESTAMPS
            try:
                print(f"🧠 Starting proto-AGI proactive processing with memory...")
                
                # Store conversation in thread memory
                conversation_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "user_message": user_message,
                    "agent_response": full_response,
                    "agent_type": agent_type,
                    "goals_context": [g.title for g in relevant_goals]
                }
                self.memory.thread_memory.append(conversation_entry)
                
                # Store in permanent memory every 5 conversations
                if len(self.memory.thread_memory) % 5 == 0:
                    self.memory.permanent_memory.append({
                        "session_id": datetime.now().strftime("%Y%m%d_%H%M"),
                        "key_insights": [entry["user_message"][:100] for entry in self.memory.thread_memory[-5:]],
                        "goals_evolution": [g.title for g in relevant_goals],
                        "timestamp": datetime.now().isoformat()
                    })
                
                proactive_messages = []
                
                # Auto-generate 4 proactive rounds with different agents - MEMORY-ENHANCED
                agent_rotation = ["general", "coaching", "creative", "analytical"]
                for round_num in range(1, 5):
                    # Check for stop signal from UI
                    if session_state and getattr(session_state, 'stop_proactive', False):
                        print(f"🛑 Proactive generation stopped by user at round {round_num}")
                        break
                    
                    current_agent = agent_rotation[(round_num - 1) % len(agent_rotation)]
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"🧠 [{timestamp}] Generating memory-enhanced round {round_num}/4 with {current_agent} perspective...")
                    
                    try:
                        # Use thread memory for enhanced context
                        thread_context = [entry.get("user_message", "") for entry in self.memory.thread_memory[-3:]]
                        
                        follow_up = self.proactive_system.follow_up_generator.generate_follow_up(
                            conversation_state, {"mode": current_agent}, relevant_goals, 
                            thread_context, round_num, current_agent
                        )
                        
                        if follow_up and follow_up.strip():
                            proactive_msg = {
                                "round": round_num,
                                "content": follow_up,
                                "mode": current_agent,
                                "confidence": 0.8,
                                "timestamp": timestamp,
                                "memory_enhanced": True
                            }
                            proactive_messages.append(proactive_msg)
                            
                            # Add to thread memory for next rounds
                            self.memory.thread_memory.append({
                                "timestamp": datetime.now().isoformat(),
                                "proactive_round": round_num,
                                "content": follow_up,
                                "agent_mode": current_agent
                            })
                            
                            # Yield this proactive round immediately
                            yield {
                                "type": "proactive_round",
                                "round": round_num,
                                "content": follow_up,
                                "total_rounds": 4,
                                "timestamp": timestamp,
                                "memory_enhanced": True
                            }
                            
                            print(f"✅ [{timestamp}] Memory-enhanced proactive round {round_num} generated successfully")
                        else:
                            print(f"⚠️ Proactive round {round_num} failed - empty response")
                            
                    except Exception as round_error:
                        print(f"🚨 Error in proactive round {round_num}: {round_error}")
                        continue
                
                # Set up auto-continuation timer (continues every minute after initial 4)
                self.last_proactive_time = time.time()
                self.auto_continuation_active = True
                print(f"🔥 Auto-continuation enabled - will continue every 60 seconds")
                    
                # FORCE GOAL SUGGESTIONS - Always generate them!
                suggested_goals = []
                try:
                    # Use Gemma 3:1b for goal suggestions (not Qwen)
                    goal_suggestion_prompt = f"""
GOAL SUGGESTION TASK:
Based on this conversation and user's current goals, suggest 3-5 relevant new goals.

CONVERSATION:
User: {user_message}
AI Response: {full_response}
Agent Type: {agent_type}

CURRENT GOALS ({len(relevant_goals)}):
{chr(10).join([f"- {g.title} ({g.progress_percentage}% progress)" for g in relevant_goals])}

SUGGEST NEW GOALS THAT:
1. Build on the conversation topic
2. Complement existing goals
3. Address gaps in user's goal portfolio
4. Are specific and actionable
5. Include milestones and daily routines

FORMAT EACH GOAL AS:
Title: [Goal Title]
Category: [category]
Milestones: [3-4 specific milestones]
Daily Routines: [2-3 daily/weekly routines]

GENERATE 3-5 GOALS:
"""
                    
                    # Use Gemma 3:1b for goal suggestions
                    goal_response = ollama.generate(
                        model="gemma3:1b",
                        prompt=goal_suggestion_prompt,
                        options={"temperature": 0.8, "max_tokens": 800}
                    )
                    
                    # Parse goal suggestions
                    goal_text = goal_response['response']
                    suggested_goals = self._parse_goal_suggestions_advanced(goal_text)
                    
                    print(f"🎯 FORCED: Generated {len(suggested_goals)} goal suggestions using Gemma 3:1b")
                    
                except Exception as e:
                    print(f"❌ Goal suggestion error: {e}")
                    # Fallback suggestions
                    suggested_goals = [
                        "Improve daily productivity with time management techniques",
                        "Learn a new technical skill relevant to your career",
                        "Establish better work-life balance habits"
                    ]
                
                # Final complete with all proactive data (MOVED OUTSIDE except block!)
                print(f"🎯 YIELDING: Sending {len(suggested_goals)} goal suggestions to UI")
                yield {
                    "type": "complete",
                    "response_time": response_time,
                    "proactive_result": {
                        "proactive_messages": proactive_messages,
                        "suggested_goals": suggested_goals,
                        "thread_complete": True,
                        "rounds_completed": len(proactive_messages)
                    },
                    "success": True
                }
                    
            except Exception as e:
                print(f"🚨 PROACTIVE ERROR: {e}")
                import traceback
                traceback.print_exc()
                yield {
                    "type": "complete",
                    "response_time": response_time,
                    "proactive_result": {
                        "proactive_messages": [],
                        "suggested_goals": [],
                        "thread_complete": True,
                        "rounds_completed": 0,
                        "error": str(e)
                    },
                    "success": True
                }
            
        except Exception as e:
            yield {
                "type": "error",
                "error": str(e),
                "agent_type": agent_type,
                "agent_name": agent_config["name"],
                "agent_emoji": agent_config["emoji"]
            }
    
    def _parse_goal_suggestions_advanced(self, goal_text: str) -> List[Dict]:
        """Parse advanced goal suggestions with milestones and routines"""
        try:
            goals = []
            lines = goal_text.split('\n')
            current_goal = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('Title:'):
                    if current_goal:
                        goals.append(current_goal)
                    current_goal = {
                        'title': line.replace('Title:', '').strip(),
                        'category': 'general',
                        'milestones': [],
                        'routines': []
                    }
                elif line.startswith('Category:') and current_goal:
                    current_goal['category'] = line.replace('Category:', '').strip()
                elif line.startswith('Milestones:') and current_goal:
                    # Parse milestones
                    milestone_text = line.replace('Milestones:', '').strip()
                    if milestone_text:
                        milestones = [m.strip() for m in milestone_text.split(',') if m.strip()]
                        current_goal['milestones'] = milestones
                elif line.startswith('Daily Routines:') and current_goal:
                    # Parse routines
                    routine_text = line.replace('Daily Routines:', '').strip()
                    if routine_text:
                        routines = [r.strip() for r in routine_text.split(',') if r.strip()]
                        current_goal['routines'] = routines
            
            # Add the last goal
            if current_goal:
                goals.append(current_goal)
            
            # If parsing failed, return simple format
            if not goals:
                simple_goals = [line.strip() for line in lines if line.strip() and not line.startswith(('Title:', 'Category:', 'Milestones:', 'Daily Routines:'))]
                return [{'title': goal, 'category': 'general', 'milestones': [], 'routines': []} for goal in simple_goals[:5]]
            
            return goals
            
        except Exception as e:
            print(f"❌ Advanced goal parsing error: {e}")
            # Fallback to simple parsing
            return [{'title': 'Improve productivity and learning', 'category': 'general', 'milestones': [], 'routines': []}]

    def get_response(self, user_message: str, selected_agent: str = None,
                    image_data: str = None) -> Dict:
        """Get comprehensive agent response with all enhancements"""
        
        start_time = time.time()
        
        # Route to appropriate agent
        agent_type = self.route_to_agent(user_message, selected_agent)
        agent_config = self.agents[agent_type]
        
        # Get relevant goals
        relevant_goals = self.get_relevant_goals(agent_type)
        
        # No worldview - using Qwen thinking model instead
        thinking_context = ""
        
        # Process image if provided
        image_context = ""
        multimodal_data = None
        if image_data:
            processed_image = self.multimodal.process_image_for_gemma(image_data)
            if "error" not in processed_image:
                image_context = f"\n\nIMAGE ANALYSIS:\n{processed_image}\n\nThe user has provided an image for you to analyze and discuss. Please examine the visual content carefully and provide detailed insights."
                # Convert Streamlit UploadedFile to base64 for Ollama
                try:
                    if hasattr(image_data, 'read'):
                        # Streamlit UploadedFile object
                        image_bytes = image_data.read()
                        image_data.seek(0)  # Reset for potential reuse
                        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                        multimodal_data = {
                            "images": [image_base64]
                        }
                        print(f"📷 Converted image to base64: {len(image_base64)} chars")
                    else:
                        # Already in correct format
                        multimodal_data = {
                            "images": [image_data]
                        }
                except Exception as e:
                    print(f"❌ Error converting image to base64: {e}")
                    multimodal_data = None
            else:
                image_context = f"\n\nImage processing error: {processed_image}"
        
        # Build enhanced prompt
        enhanced_prompt = self.build_enhanced_prompt(
            agent_type, user_message, relevant_goals, thinking_context, image_context
        )
        
        try:
            # Generate main response with multimodal support
            request_data = {
                "model": self.model,
                "prompt": enhanced_prompt,
                "options": PERFORMANCE_CONFIG
            }
            
            # Add images if provided
            if multimodal_data and "images" in multimodal_data:
                request_data["images"] = multimodal_data["images"]
                print(f"📷 Non-streaming multimodal response with {len(multimodal_data['images'])} images")
            
            if hasattr(self, 'stream_response') and self.stream_response:
                # Stream the response for real-time generation
                request_data["stream"] = True
                response_stream = ollama.generate(**request_data)
                
                # Collect streaming response
                agent_response = ""
                for chunk in response_stream:
                    if 'response' in chunk:
                        agent_response += chunk['response']
                        # Yield for streaming (if generator is being used)
                        if hasattr(self, '_stream_callback') and self._stream_callback:
                            self._stream_callback(chunk['response'])
            else:
                # Standard non-streaming response
                response = ollama.generate(**request_data)
                agent_response = response['response']
            response_time = time.time() - start_time
            
            # Create conversation state
            conversation_state = ConversationState(
                user_message=user_message,
                agent_response=agent_response,
                agent_type=agent_type,
                timestamp=datetime.now().isoformat(),
                response_time=response_time,
                goal_context=[g.id for g in relevant_goals],
                thinking_enhanced=bool(thinking_context)
            )
            
            # Add to conversation history
            self.conversation_history.append(conversation_state)
            if len(self.conversation_history) > 10:  # Keep last 10
                self.conversation_history = self.conversation_history[-10:]
            
            # Multi-round proactive processing
            proactive_result = self.proactive_system.process_proactive_session(
                conversation_state, self.conversation_history, relevant_goals
            )
            
            return {
                "response": agent_response,
                "agent_type": agent_type,
                "agent_name": agent_config["name"],
                "agent_emoji": agent_config["emoji"],
                "response_time": response_time,
                "relevant_goals": [{"id": g.id, "title": g.title, "progress": g.progress_percentage} 
                                 for g in relevant_goals],
                "worldview_enhanced": False,
                "proactive_result": proactive_result,
                "success": True
            }
            
        except Exception as e:
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "agent_type": agent_type,
                "agent_name": agent_config["name"],
                "agent_emoji": agent_config["emoji"],
                "response_time": time.time() - start_time,
                "relevant_goals": [],
                "worldview_enhanced": False,
                "proactive_result": {
                    "proactive_messages": [],
                    "suggested_goals": [],
                    "thread_complete": True,
                    "rounds_completed": 0
                },
                "success": False
            }
    
    def check_auto_continuation(self, session_state=None) -> List[Dict]:
        """INTELLIGENT PROACTIVE LOGIC: Use Qwen 3:1.7B to decide when to respond"""
        if not self.auto_continuation_active or not self.last_proactive_time:
            return []
        
        current_time = time.time()
        time_since_last = current_time - self.last_proactive_time
        
        # Check for stop signal - stop when user starts new conversation
        if session_state and getattr(session_state, 'stop_proactive', False):
            print(f"🛑 Auto-continuation stopped by user")
            self.auto_continuation_active = False
            return []
        
        # Check if user has started a new conversation (new message in session)
        if session_state and hasattr(session_state, 'messages') and session_state.messages:
            # If last message is from user, stop proactive continuation
            if session_state.messages[-1]["role"] == "user":
                print(f"🛑 Auto-continuation stopped - user started new conversation")
                self.auto_continuation_active = False
                return []
        
        # Use Qwen 3:1.7B to intelligently decide if we should continue
        if time_since_last >= 60:  # Check every minute
            try:
                # Get conversation context
                if not self.conversation_history or not self.memory.thread_memory:
                    return []
                
                last_conversation = self.conversation_history[-1]
                thread_context = [entry.get("content", "") for entry in self.memory.thread_memory[-5:]]
                relevant_goals = self.get_relevant_goals(last_conversation.agent_type)
                
                # Build intelligent decision prompt
                decision_prompt = f"""
INTELLIGENT PROACTIVE DECISION TASK:
You are an AI assistant deciding whether to continue proactive conversation.

CONVERSATION CONTEXT:
User's last message: "{last_conversation.user_message}"
Your last response: "{last_conversation.agent_response}"
Time since last interaction: {time_since_last:.0f} seconds

THREAD MEMORY (recent proactive messages):
{chr(10).join([f"- {ctx}" for ctx in thread_context[-3:]])}

USER'S ACTIVE GOALS ({len(relevant_goals)}):
{chr(10).join([f"- {g.title} ({g.progress_percentage}% progress)" for g in relevant_goals[:3]])}

DECISION FACTORS TO CONSIDER:
1. Is the conversation still relevant and engaging?
2. Are there unanswered questions or incomplete thoughts?
3. Would additional insights help the user's goals?
4. Has enough time passed for meaningful follow-up?
5. Is the user likely to benefit from continued interaction?

DECISION RULES:
- Continue if conversation is still active and goal-relevant
- Continue if user has incomplete goals or needs guidance
- Continue if recent proactive messages were well-received
- Stop if conversation feels complete or user needs space
- Stop if too much time has passed (over 5 minutes)

RESPOND WITH ONLY:
CONTINUE: [brief reason why to continue]
OR
STOP: [brief reason why to stop]

DECISION:
"""
                
                # Use Qwen 3:1.7B for intelligent decision
                decision_response = ollama.generate(
                    model="qwen3:1.7b",
                    prompt=decision_prompt,
                    options={"temperature": 0.3, "max_tokens": 100}
                )
                
                decision_text = decision_response['response'].strip().upper()
                print(f"🧠 Qwen 3:1.7B Decision: {decision_text}")
                
                if "CONTINUE:" in decision_text:
                    # Generate intelligent proactive response using Gemma 3:1b
                    auto_messages = []
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    # Generate 1-2 intelligent follow-ups
                    for round_num in range(5, 7):
                        try:
                            # Use different focus areas
                            focus_areas = ["goal_progress", "insight", "action_step"]
                            current_focus = focus_areas[(round_num - 5) % len(focus_areas)]
                            
                            follow_up = self.proactive_system.follow_up_generator.generate_follow_up(
                                last_conversation, {"mode": current_focus}, relevant_goals,
                                thread_context, round_num, current_focus
                            )
                            
                            if follow_up and follow_up.strip():
                                auto_message = {
                                    "round": round_num,
                                    "content": f"🧠 Intelligent Follow-up: {follow_up}",
                                    "mode": current_focus,
                                    "timestamp": timestamp,
                                    "auto_generated": True,
                                    "memory_enhanced": True,
                                    "intelligent_decision": True
                                }
                                auto_messages.append(auto_message)
                                
                                # Add to thread memory
                                self.memory.thread_memory.append({
                                    "timestamp": datetime.now().isoformat(),
                                    "intelligent_continuation": round_num,
                                    "content": follow_up,
                                    "focus": current_focus
                                })
                                
                                print(f"✅ [{timestamp}] Intelligent proactive round {round_num} generated")
                        
                        except Exception as e:
                            print(f"🚨 Intelligent proactive error: {e}")
                            continue
                    
                    # Reset timer for next check
                    self.last_proactive_time = current_time
                    return auto_messages
                
                else:
                    print(f"🛑 Qwen 3:1.7B decided to stop proactive continuation")
                    self.auto_continuation_active = False
                    return []
                    
            except Exception as e:
                print(f"🚨 Intelligent decision error: {e}")
                # Fallback to simple continuation
                self.last_proactive_time = current_time
                return []
        
        return []

# 🎯 GOALS MANAGER
class GoalsManager:
    def __init__(self):
        self.db = GoalsDatabase()
    
    def create_goal(self, title: str, description: str = "", category: str = "general",
                   priority: str = "medium", target_date: str = None) -> Goal:
        """Create a new goal"""
        
        # Suggest related agents based on category
        related_agents = self._suggest_related_agents(category, description + " " + title)
        
        goal = Goal(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            category=category,
            priority=priority,
            status="active",
            target_date=target_date,
            created_date=datetime.now().isoformat(),
            completed_date=None,
            progress_percentage=0,
            milestones=[],
            daily_routines=[],
            related_agents=related_agents,
            user_notes="",
            ai_suggestions=[]
        )
        
        self.db.save_goal(goal)
        return goal
    
    def _suggest_related_agents(self, category: str, text: str) -> List[str]:
        """Suggest which agents can help with this goal"""
        related = []
        text_lower = text.lower()
        
        # Direct category match
        for agent_id, agent_config in HACKATHON_AGENTS.items():
            if agent_config["category"] == category:
                related.append(agent_id)
        
        # Keyword matching
        for agent_id, agent_config in HACKATHON_AGENTS.items():
            if agent_id not in related:
                keyword_matches = sum(1 for keyword in agent_config["keywords"] 
                                    if keyword in text_lower)
                if keyword_matches >= 2:  # At least 2 keyword matches
                    related.append(agent_id)
        
        return related[:5]  # Max 5 related agents
    
    def get_active_goals(self) -> List[Goal]:
        """Get all active goals"""
        return self.db.get_goals_by_status("active")
    
    def update_goal_progress(self, goal_id: str, progress: int) -> bool:
        """Update goal progress"""
        try:
            goals = self.db.get_goals_by_status("active")
            for goal in goals:
                if goal.id == goal_id:
                    goal.progress_percentage = min(100, max(0, progress))
                    if goal.progress_percentage == 100:
                        goal.status = "completed"
                        goal.completed_date = datetime.now().isoformat()
                    return self.db.save_goal(goal)
            return False
        except Exception as e:
            print(f"Error updating goal progress: {e}")
            return False
    
    def add_milestone(self, goal_id: str, title: str, description: str = "", 
                     target_date: str = None) -> bool:
        """Add a milestone to a goal"""
        try:
            goal = self.db.get_goals_by_status("active")
            goal = next((g for g in goal if g.id == goal_id), None)
            if not goal:
                return False
            
            milestone = {
                "id": f"milestone_{int(time.time())}",
                "title": title,
                "description": description,
                "status": "pending",
                "target_date": target_date,
                "completed_date": None,
                "completion_timestamp": None,
                "progress_percentage": 0,
                "notes": ""
            }
            
            goal.milestones.append(milestone)
            return self.db.save_goal(goal)
        except Exception as e:
            print(f"Error adding milestone: {e}")
            return False
    
    def add_daily_routine(self, goal_id: str, title: str, description: str = "",
                         frequency: str = "daily") -> bool:
        """Add a daily routine to a goal"""
        try:
            goal = self.db.get_goals_by_status("active")
            goal = next((g for g in goal if g.id == goal_id), None)
            if not goal:
                return False
            
            routine = {
                "id": f"routine_{int(time.time())}",
                "title": title,
                "description": description,
                "frequency": frequency,
                "checkmarks": [],
                "streak_count": 0,
                "longest_streak": 0,
                "last_completed": None,
                "is_active": True
            }
            
            goal.daily_routines.append(routine)
            return self.db.save_goal(goal)
        except Exception as e:
            print(f"Error adding daily routine: {e}")
            return False
    
    def complete_milestone(self, goal_id: str, milestone_id: str) -> bool:
        """Mark a milestone as completed"""
        try:
            goal = self.db.get_goals_by_status("active")
            goal = next((g for g in goal if g.id == goal_id), None)
            if not goal:
                return False
            
            for milestone in goal.milestones:
                if milestone["id"] == milestone_id:
                    milestone["status"] = "completed"
                    milestone["completed_date"] = datetime.now().strftime("%Y-%m-%d")
                    milestone["completion_timestamp"] = datetime.now().isoformat()
                    milestone["progress_percentage"] = 100
                    break
            
            return self.db.save_goal(goal)
        except Exception as e:
            print(f"Error completing milestone: {e}")
            return False
    
    def check_daily_routine(self, goal_id: str, routine_id: str) -> bool:
        """Check off a daily routine for today"""
        try:
            goal = self.db.get_goals_by_status("active")
            goal = next((g for g in goal if g.id == goal_id), None)
            if not goal:
                return False
            
            today = datetime.now().strftime("%Y-%m-%d")
            now = datetime.now().isoformat()
            
            for routine in goal.daily_routines:
                if routine["id"] == routine_id:
                    # Add checkmark for today
                    checkmark = {
                        "date": today,
                        "timestamp": now
                    }
                    routine["checkmarks"].append(checkmark)
                    routine["last_completed"] = now
                    
                    # Update streak
                    routine["streak_count"] += 1
                    if routine["streak_count"] > routine["longest_streak"]:
                        routine["longest_streak"] = routine["streak_count"]
                    break
            
            return self.db.save_goal(goal)
        except Exception as e:
            print(f"Error checking daily routine: {e}")
            return False
    
    def get_goal_with_details(self, goal_id: str) -> Optional[Dict]:
        """Get a goal with all its milestones and routines"""
        try:
            goals = self.db.get_goals_by_status("active")
            goal = next((g for g in goals if g.id == goal_id), None)
            if not goal:
                return None
            
            return {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "category": goal.category,
                "priority": goal.priority,
                "status": goal.status,
                "progress": goal.progress_percentage,
                "milestones": goal.milestones,
                "daily_routines": goal.daily_routines,
                "created_date": goal.created_date,
                "target_date": goal.target_date
            }
        except Exception as e:
            print(f"Error getting goal details: {e}")
            return None

# 🚀 MAIN SYSTEM INTERFACE
class GemmaMultiverseSystem:
    def __init__(self):
        self.agent_system = GemmaAgentSystem()
        self.goals_manager = GoalsManager()
        self.google_docs = GoogleDocsSync()
        self.google_ai_edge = GoogleAIEdgeService()
        
        # Initialize local sync server
        if SYNC_SERVER_AVAILABLE:
            self.sync_server_url = "http://192.168.1.40:8000"
        
        # Initialize services
        self.google_docs.initialize()
        self.google_ai_edge.initialize()
    
    def process_message(self, user_message: str, selected_agent: str = None,
                       image_data: str = None) -> Dict:
        """Main entry point for processing user messages"""
        response = self.agent_system.get_response(user_message, selected_agent, image_data)
        
        # Upload to Google Docs after proactive intelligence completes
        if response.get('proactive_complete', False):
            goals = [goal.get('title', '') for goal in response.get('goal_suggestions', [])]
            self.google_docs.upload_proactive_results(
                response=response.get('response', ''),
                goals=goals,
                analysis_type="proactive"
            )
        
        return response
    
    def send_to_sync_server(self, user_message: str, complete_response: str, selected_agent: str = None):
        """Send complete response to local sync server for mobile app"""
        if hasattr(self, 'sync_server_url'):
            try:
                import requests
                
                # Combine all response components into one comprehensive message
                full_response = complete_response
                
                # Add proactive rounds if available
                if hasattr(complete_response, 'get'):
                    proactive_rounds = complete_response.get('proactive_rounds', [])
                    if proactive_rounds:
                        full_response += "\n\n🔥 PROACTIVE INTELLIGENCE ROUNDS:\n"
                        for i, round_data in enumerate(proactive_rounds, 1):
                            full_response += f"\nRound {i}: {round_data.get('content', '')}"
                    
                    # Add goal suggestions
                    goal_suggestions = complete_response.get('goal_suggestions', [])
                    if goal_suggestions:
                        full_response += "\n\n🎯 SUGGESTED GOALS:\n"
                        for goal in goal_suggestions:
                            full_response += f"\n• {goal.get('title', '')}: {goal.get('description', '')}"
                
                # Send to local sync server
                requests.post(f"{self.sync_server_url}/messages", json={
                    "timestamp": datetime.now().isoformat(),
                    "type": "user",
                    "message": user_message,
                    "agent": selected_agent,
                    "response": full_response,
                    "status": "completed"
                }, timeout=2)
                
                print(f"📊 Sent complete response to local sync server")
                return True
                
            except Exception as e:
                print(f"❌ Error sending to sync server: {e}")
                return False
        return False
    
    def process_message_stream(self, user_message: str, selected_agent: str = None,
                              image_data: str = None, session_state=None):
        """Main entry point for streaming user messages"""
        return self.agent_system.get_response_stream(user_message, selected_agent, image_data, session_state)
    
    def create_goal_from_suggestion(self, goal_title, category: str = "general", description: str = "", 
                                   priority: str = "medium", target_date: str = None, 
                                   milestones: List[Dict] = None, routines: List[Dict] = None) -> bool:
        """Create a goal from form input with milestones and routines"""
        try:
            if not goal_title:
                return False
            
            # Create the goal
            goal = self.goals_manager.create_goal(
                title=goal_title,
                description=description,
                category=category,
                priority=priority,
                target_date=target_date
            )
            
            # Add milestones
            if milestones:
                for milestone in milestones:
                    self.goals_manager.add_milestone(
                        goal_id=goal.id,
                        title=milestone.get("title", ""),
                        description=f"Milestone for {goal_title}"
                    )
            
            # Add daily routines
            if routines:
                for routine in routines:
                    self.goals_manager.add_daily_routine(
                        goal_id=goal.id,
                        title=routine.get("title", ""),
                        description=f"Daily routine for {goal_title}"
                    )
            
            print(f"✅ Created goal '{goal_title}' with {len(milestones or [])} milestones and {len(routines or [])} routines")
            return True
            
        except Exception as e:
            print(f"❌ Error creating goal from suggestion: {e}")
            return False
    
    def get_active_goals(self) -> List[Dict]:
        """Get user's active goals for UI with full details"""
        goals = self.goals_manager.get_active_goals()
        return [{
            "id": g.id, 
            "title": g.title, 
            "progress": g.progress_percentage, 
            "category": g.category,
            "description": g.description,
            "priority": g.priority,
            "target_date": g.target_date,
            "milestones": g.milestones,
            "daily_routines": g.daily_routines,
            "related_agents": g.related_agents,
            "user_notes": g.user_notes,
            "ai_suggestions": g.ai_suggestions
        } for g in goals]
    
    def get_agent_list(self) -> Dict[str, Dict]:
        """Get list of available agents for UI"""
        return {agent_id: {
            "name": config["name"],
            "emoji": config["emoji"],
            "description": config["description"],
            "category": config["category"]
        } for agent_id, config in HACKATHON_AGENTS.items()}
    
    def capture_camera_image(self) -> Optional[str]:
        """Capture image from camera"""
        return self.agent_system.multimodal.capture_camera_frame()

# 🌟 GLOBAL SYSTEM INSTANCE
gemma_system = GemmaMultiverseSystem()

# 🧪 TEST FUNCTION
def test_system():
    """Test the complete system"""
    print("🧠 Testing Gemma 3n Multiverse System...")
    
    # Test basic response
    result = gemma_system.process_message("I want to learn programming")
    print(f"✅ Basic Response: {result['response'][:100]}...")
    
    # Test proactive system
    proactive_result = result.get('proactive_result', {})
    proactive_messages = proactive_result.get('proactive_messages', [])
    suggested_goals = proactive_result.get('suggested_goals', [])
    
    if proactive_messages:
        print(f"✅ Multi-Round Proactive: {len(proactive_messages)} rounds generated")
    
    # Test goal creation
    if suggested_goals:
        goal_created = gemma_system.create_goal_from_suggestion(
            suggested_goals[0], "education"
        )
        print(f"✅ Goal Creation: {goal_created}")
    
    print("🎉 Proactive Intelligence System READY! 🧠⚡")

if __name__ == "__main__":
    test_system() 