from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import pipeline
import os
import re
from typing import List, Dict, Optional

app = FastAPI(title="Intelligent Workflow Assistant")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models (using lighter models for faster performance)
try:
    # Using text-generation pipeline as FLAN-T5 task is not available in this transformers version
    generator = pipeline("text-generation", model="gpt2")
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    generator = pipeline("text-generation", model="gpt2")

# Data models
class WorkflowRequest(BaseModel):
    goal: str
    context: Optional[str] = None

class WorkflowStep(BaseModel):
    step_number: int
    task: str
    description: str
    tools: List[str]
    estimated_effort: str
    dependencies: Optional[List[int]] = None

class WorkflowResponse(BaseModel):
    goal: str
    total_steps: int
    steps: List[WorkflowStep]
    overall_tools: List[str]

# Tool recommendation system
TOOL_MAPPING = {
    "data": ["Python", "Pandas", "SQL", "Kaggle", "Google Sheets"],
    "model": ["PyTorch", "TensorFlow", "Scikit-learn", "XGBoost"],
    "training": ["Jupyter Notebook", "Google Colab", "Paperspace"],
    "deployment": ["Docker", "AWS", "Google Cloud", "Hugging Face", "GitHub"],
    "visualization": ["Matplotlib", "Plotly", "Tableau", "PowerBI"],
    "frontend": ["React", "Vue.js", "Next.js", "Streamlit"],
    "api": ["FastAPI", "Flask", "Django", "Node.js"],
    "database": ["PostgreSQL", "MongoDB", "Firebase", "MySQL"],
    "testing": ["Pytest", "Jest", "Selenium"],
    "monitoring": ["Prometheus", "Grafana", "DataDog"],
    "documentation": ["Markdown", "Sphinx", "Swagger"],
    "version control": ["Git", "GitHub", "GitLab"],
    "ml": ["TensorFlow", "PyTorch", "Scikit-learn"],
    "nlp": ["NLTK", "SpaCy", "Transformers", "BERT"],
    "cv": ["OpenCV", "Pillow", "YOLO"],
}

def extract_tools_from_task(task: str) -> List[str]:
    """Extract relevant tools based on task keywords"""
    task_lower = task.lower()
    tools = []

    keyword_priority = [
        ("collect", ["Python", "Pandas", "Kaggle"]),
        ("data", ["Python", "Pandas", "SQL"]),
        ("dataset", ["Python", "Pandas", "Kaggle"]),
        ("model", ["PyTorch", "TensorFlow", "Scikit-learn"]),
        ("train", ["PyTorch", "TensorFlow", "Jupyter Notebook"]),
        ("deploy", ["Docker", "AWS", "GitHub"]),
        ("api", ["FastAPI", "Flask", "Django"]),
        ("frontend", ["React", "Vue.js", "Next.js"]),
        ("web", ["React", "Vue.js", "Next.js"]),
        ("test", ["Pytest", "Selenium", "Jest"]),
        ("validate", ["Pytest", "Postman", "Selenium"]),
        ("monitor", ["Prometheus", "Grafana"]),
        ("document", ["Markdown", "Swagger"]),
        ("design", ["Figma", "Miro"]),
        ("visual", ["Matplotlib", "Plotly", "Tableau"]),
        ("nlp", ["SpaCy", "Transformers", "NLTK"]),
        ("image", ["OpenCV", "Pillow", "YOLO"]),
        ("database", ["PostgreSQL", "MongoDB", "Firebase"]),
        ("version control", ["Git", "GitHub"]),
        ("git", ["Git", "GitHub"]),
    ]

    for keyword, tool_list in keyword_priority:
        if keyword in task_lower:
            for tool in tool_list:
                if tool not in tools:
                    tools.append(tool)

    if not tools:
        tools = ["Python", "Git"]

    return tools[:4]

def estimate_effort(task: str) -> str:
    """Estimate effort level based on task complexity"""
    task_lower = task.lower()
    
    complex_keywords = ["train", "deploy", "optimize", "design", "architecture", "build"]
    medium_keywords = ["process", "analyze", "implement", "test", "document", "collect", "prepare", "validate"]
    
    if any(keyword in task_lower for keyword in complex_keywords):
        return "High (1-2 weeks)"
    elif any(keyword in task_lower for keyword in medium_keywords):
        return "Medium (2-5 days)"
    else:
        return "Low (1-2 days)"


def parse_step_line(line: str):
    """Extract step title and description from a single numbered line."""
    match = re.match(r'^\s*(\d+)[\.\)]\s*(.+)$', line)
    if not match:
        return None

    step_text = match.group(2).strip()
    lower_text = step_text.lower()

    # Reject prompt echoes and placeholders
    reject_phrases = [
        'break this goal into',
        'provide steps in this format',
        'step title',
        'brief description',
        'only output',
        'goal:',
        'return only',
        'numbers steps',
    ]
    if any(phrase in lower_text for phrase in reject_phrases):
        return None

    if ':' in step_text:
        title, description = [part.strip() for part in step_text.split(':', 1)]
    else:
        parts = re.split(r'\s+[-–—]\s+', step_text, 1)
        title = parts[0].strip()
        description = parts[1].strip() if len(parts) > 1 else None

    if not title or len(title) <= 3:
        return None
    if title.lower() in ['step', 'step title']:
        return None

    if description and len(description) <= 3:
        description = None

    return title, description


def extract_tools_from_task(task: str) -> List[str]:
    """Extract relevant tools based on task keywords"""
    task_lower = task.lower()
    tools = []

    keyword_tool_pairs = [
        ("collect", ["Python", "Pandas", "Kaggle"]),
        ("dataset", ["Python", "Pandas", "Kaggle"]),
        ("data", ["Python", "Pandas", "SQL"]),
        ("label", ["Python", "LabelImg", "Pandas"]),
        ("model", ["PyTorch", "TensorFlow", "Scikit-learn"]),
        ("train", ["PyTorch", "TensorFlow", "Jupyter Notebook"]),
        ("deploy", ["Docker", "AWS", "GitHub"]),
        ("api", ["FastAPI", "Flask", "Django"]),
        ("frontend", ["React", "Vue.js", "Next.js"]),
        ("web", ["React", "Next.js", "HTML/CSS"]),
        ("test", ["Pytest", "Selenium", "Postman"]),
        ("validate", ["Pytest", "Postman", "Selenium"]),
        ("monitor", ["Prometheus", "Grafana"]),
        ("document", ["Markdown", "Swagger"]),
        ("design", ["Figma", "Miro"]),
        ("visual", ["Matplotlib", "Plotly", "Tableau"]),
        ("nlp", ["SpaCy", "Transformers", "NLTK"]),
        ("image", ["OpenCV", "Pillow", "YOLO"]),
        ("database", ["PostgreSQL", "MongoDB", "Firebase"]),
        ("git", ["Git", "GitHub"]),
    ]

    for keyword, tool_list in keyword_tool_pairs:
        if keyword in task_lower:
            for tool in tool_list:
                if tool not in tools:
                    tools.append(tool)

    if not tools:
        tools = ["Python", "Git"]

    return tools[:4]


def structure_workflow_response(raw_response: str, goal: str) -> WorkflowResponse:
    """
    Convert raw AI output into structured workflow format
    """
    # Clean up the response
    lines = raw_response.split('\n')
    lines = [line.strip() for line in lines if line.strip() and not line.startswith('Goal:')]
    
    steps = []
    step_number = 1
    
    for line in lines:
        parsed = parse_step_line(line)
        if not parsed:
            continue

        task, description = parsed

        if not description:
            description = f"Execute {task.lower()} and complete this step."

        tools = extract_tools_from_tools(task)
        
        step = WorkflowStep(
            step_number=step_number,
            task=task,
            description=description,
            tools=tools,
            estimated_effort=estimate_effort(task),
            dependencies=[step_number - 1] if step_number > 1 else None
        )
        steps.append(step)
        step_number += 1
    
    if not steps or all(step.task.lower() in ['step title', 'step name', ''] for step in steps):
        return _get_default_workflow_response(goal)

    all_tools = set()
    for step in steps:
        all_tools.update(step.tools)
    
    return WorkflowResponse(
        goal=goal,
        total_steps=len(steps),
        steps=steps,
        overall_tools=list(all_tools)
    )

def extract_tools_from_tools(text: str) -> List[str]:
    """Extract tools mentioned in text"""
    return extract_tools_from_task(text)

def _get_default_workflow(goal: str) -> List[WorkflowStep]:
    """Provide a default workflow structure"""
    return [
        WorkflowStep(
            step_number=1,
            task="Define Requirements",
            description="Gather and document project requirements and constraints",
            tools=["Google Sheets", "Markdown", "Notion"],
            estimated_effort="Low (1-2 days)",
            dependencies=None
        ),
        WorkflowStep(
            step_number=2,
            task="Data Collection",
            description="Gather and prepare the necessary data",
            tools=["Python", "Pandas", "Kaggle"],
            estimated_effort="Medium (2-5 days)",
            dependencies=[1]
        ),
        WorkflowStep(
            step_number=3,
            task="Model Development",
            description="Build and train the AI model",
            tools=["Python", "PyTorch", "Jupyter Notebook"],
            estimated_effort="High (1-2 weeks)",
            dependencies=[2]
        ),
        WorkflowStep(
            step_number=4,
            task="Testing & Validation",
            description="Test and validate model performance",
            tools=["Pytest", "Python", "TensorBoard"],
            estimated_effort="Medium (2-5 days)",
            dependencies=[3]
        ),
        WorkflowStep(
            step_number=5,
            task="Deployment",
            description="Deploy the solution to production",
            tools=["Docker", "AWS", "GitHub"],
            estimated_effort="High (1-2 weeks)",
            dependencies=[4]
        ),
    ]


def _get_default_workflow_response(goal: str) -> WorkflowResponse:
    steps = _get_default_workflow(goal)
    overall_tools = set()
    for step in steps:
        overall_tools.update(step.tools)
    return WorkflowResponse(
        goal=goal,
        total_steps=len(steps),
        steps=steps,
        overall_tools=list(overall_tools)
    )

# API Endpoints

@app.get("/app")
def frontend_app():
    """Serve the frontend HTML application"""
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "intelligent_workflow_assistant.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Frontend file not found")
    return FileResponse(html_path, media_type="text/html")

@app.get("/")
def home():
    """Health check endpoint"""
    return {
        "message": "Intelligent Workflow Assistant Running",
        "version": "1.0",
        "status": "online"
    }

@app.post("/generate-workflow/", response_model=WorkflowResponse)
def generate_workflow(request: WorkflowRequest):
    """
    Generate a structured workflow from a user goal
    
    Request body:
    {
        "goal": "Build a plant disease detection app",
        "context": "Optional additional context"
    }
    """
    try:
        if not request.goal or len(request.goal.strip()) == 0:
            raise HTTPException(status_code=400, detail="Goal cannot be empty")
        
        # Create structured prompt for concrete step generation
        prompt = f"""Generate a concrete, actionable workflow for this goal.

Example 1:
Goal: Build a plant disease detection app
1. Define the project scope: Identify the target crops, diseases, and deployment settings.
2. Collect plant images: Gather healthy and diseased leaf photos from public datasets and field samples.
3. Label and clean the data: Annotate images with disease categories and remove duplicates.
4. Train the model: Build and train a classifier using a suitable deep learning architecture.
5. Validate and deploy: Test the model and deploy the app with an API or mobile interface.

Example 2:
Goal: Create a REST API for a todo application
1. Define API requirements: Specify endpoints, data models, and authentication rules.
2. Set up the backend project: Create a FastAPI project, environment, and basic routing.
3. Implement CRUD endpoints: Build create, read, update, and delete operations.
4. Add validation and tests: Validate input data and write automated tests.
5. Deploy the API: Containerize and deploy the service to a cloud provider.

Goal: {request.goal}

Return only 5 to 7 numbered steps.
Each line must include a real step title followed by a short description.
Do NOT repeat the prompt, instructions, or placeholder text.
Use this exact output format only:
1. Step title: Brief description of what to do
2. Step title: Brief description of what to do
3. Step title: Brief description of what to do
4. Step title: Brief description of what to do
5. Step title: Brief description of what to do

Do not output any other text.
"""

        # Generate response from AI
        result = generator(
            prompt,
            max_length=220,
            temperature=0.4,
            top_p=0.9,
            do_sample=True,
            return_full_text=False,
        )
        raw_response = result[0]['generated_text'] if result else ""

        # Remove any prompt echo if present
        first_step_match = re.search(r'^\s*1[\.\)]', raw_response, re.MULTILINE)
        if first_step_match:
            raw_response = raw_response[first_step_match.start():]

        # Structure the response
        workflow = structure_workflow_response(raw_response, request.goal)
        if workflow.total_steps < 3:
            # Fallback to a generic structured workflow if model output is not valid
            workflow = _get_default_workflow_response(request.goal)
        
        return workflow
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating workflow: {str(e)}")

@app.post("/refine-step/", response_model=Dict)
def refine_step(step_task: str, suggestions: bool = True):
    """
    Refine a specific workflow step with more detailed guidance
    """
    try:
        prompt = f"""Provide a detailed breakdown for this step: {step_task}
        
Include:
1. Sub-tasks required
2. Tools and resources
3. Estimated timeline
4. Potential challenges
5. Success metrics"""

        result = generator(prompt, max_length=250)
        refined_content = result[0]['generated_text'] if result else ""
        
        tools = extract_tools_from_task(step_task)
        
        return {
            "step": step_task,
            "refined_breakdown": refined_content,
            "recommended_tools": tools,
            "estimated_effort": estimate_effort(step_task)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining step: {str(e)}")

@app.get("/tools/")
def get_available_tools():
    """Get list of all available tools in the system"""
    all_tools = set()
    for tools_list in TOOL_MAPPING.values():
        all_tools.update(tools_list)
    
    return {
        "available_tools": sorted(list(all_tools)),
        "tool_categories": TOOL_MAPPING
    }

@app.get("/examples/")
def get_example_workflows():
    """Get example workflows for reference"""
    examples = [
        {"goal": "Build a plant disease detection app", "category": "ML/AI"},
        {"goal": "Create a real-time chat application", "category": "Web Development"},
        {"goal": "Develop a data pipeline for financial analytics", "category": "Data Engineering"},
        {"goal": "Build a mobile game with multiplayer features", "category": "Game Development"},
    ]
    return {"examples": examples}

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
