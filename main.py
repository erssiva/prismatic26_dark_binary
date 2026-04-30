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
    # Using text-generation pipeline as FLAN-T5 task is available in this transformers version
    generator = pipeline("text-generation", model="google/flan-t5-base")
except Exception as e:
    print(f"Warning: Could not load model: {e}")
    generator = pipeline("text-generation", model="google/flan-t5-base")

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

# ✅ FIXED: Single definition of extract_tools_from_task
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

        # ✅ FIXED: Correct function name (was extract_tools_from_tools)
        tools = extract_tools_from_task(task)
        
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
    
    all_tools = set()
    for step in steps:
        all_tools.update(step.tools)
    
    return WorkflowResponse(
        goal=goal,
        total_steps=len(steps),
        steps=steps,
        overall_tools=list(all_tools)
    )


# ✅ IMPROVED: Generate goal-specific default workflows based on detected category
def detect_goal_category(goal: str) -> str:
    """Detect the category of the goal to provide better defaults"""
    goal_lower = goal.lower()
    
    if any(word in goal_lower for word in ["disease", "detect", "image", "vision", "cv", "object"]):
        return "cv"
    elif any(word in goal_lower for word in ["nlp", "text", "language", "sentiment", "chat", "translation"]):
        return "nlp"
    elif any(word in goal_lower for word in ["api", "backend", "server", "rest", "service"]):
        return "api"
    elif any(word in goal_lower for word in ["frontend", "react", "vue", "ui", "web app"]):
        return "frontend"
    elif any(word in goal_lower for word in ["deploy", "docker", "cloud", "production"]):
        return "deployment"
    elif any(word in goal_lower for word in ["data", "pipeline", "etl", "analytics"]):
        return "data"
    else:
        return "ml"


def _get_goal_specific_workflow(goal: str) -> List[WorkflowStep]:
    """Provide goal-specific workflow structure based on detected category"""
    category = detect_goal_category(goal)
    
    if category == "cv":
        return [
            WorkflowStep(
                step_number=1,
                task="Define Vision Project Scope",
                description="Identify target objects, use cases, and required accuracy metrics",
                tools=["Figma", "Markdown", "Notion"],
                estimated_effort="Low (1-2 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Collect and Annotate Image Data",
                description="Gather images and label with bounding boxes or segmentation masks",
                tools=["LabelImg", "Python", "Pandas"],
                estimated_effort="High (1-2 weeks)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Train Computer Vision Model",
                description="Train YOLO, Faster R-CNN, or transformer-based model",
                tools=["PyTorch", "OpenCV", "Jupyter Notebook"],
                estimated_effort="High (1-2 weeks)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Validate and Optimize Model",
                description="Test accuracy, handle edge cases, optimize inference speed",
                tools=["Pytest", "TensorBoard", "Python"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Deploy as API or Application",
                description="Deploy model as REST API or integrate into applications",
                tools=["Docker", "FastAPI", "AWS"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]
    
    elif category == "nlp":
        return [
            WorkflowStep(
                step_number=1,
                task="Define NLP Task and Dataset",
                description="Specify task type, target language, and evaluation metrics",
                tools=["Python", "Markdown", "Notion"],
                estimated_effort="Low (1-2 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Prepare and Preprocess Text Data",
                description="Clean, tokenize, and prepare dataset with proper train/test splits",
                tools=["Python", "NLTK", "Pandas"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Train Language Model",
                description="Fine-tune transformer models like BERT or GPT for your task",
                tools=["Transformers", "PyTorch", "Jupyter Notebook"],
                estimated_effort="High (1-2 weeks)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Evaluate and Improve Performance",
                description="Calculate metrics (BLEU, F1), handle class imbalance, hyperparameter tuning",
                tools=["Pytest", "Python", "TensorBoard"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Deploy NLP Service",
                description="Create API endpoint and deploy to production",
                tools=["FastAPI", "Docker", "AWS"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]
    
    elif category == "api":
        return [
            WorkflowStep(
                step_number=1,
                task="Design API Architecture",
                description="Define endpoints, request/response models, authentication mechanism",
                tools=["Swagger", "Postman", "Markdown"],
                estimated_effort="Low (1-2 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Set Up Backend Project",
                description="Initialize FastAPI/Flask project with environment and dependencies",
                tools=["FastAPI", "Python", "Git"],
                estimated_effort="Low (1-2 days)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Implement Core Endpoints",
                description="Build CRUD operations and business logic",
                tools=["FastAPI", "PostgreSQL", "SQLAlchemy"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Add Testing and Documentation",
                description="Write unit tests, integration tests, and API documentation",
                tools=["Pytest", "Swagger", "Python"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Deploy to Production",
                description="Containerize and deploy using Docker, set up CI/CD pipeline",
                tools=["Docker", "GitHub", "AWS"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]
    
    elif category == "frontend":
        return [
            WorkflowStep(
                step_number=1,
                task="Design UI/UX Mockups",
                description="Create wireframes and design mockups for all pages",
                tools=["Figma", "Adobe XD", "Sketch"],
                estimated_effort="Medium (2-5 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Set Up Frontend Project",
                description="Initialize React/Vue project with build tools and CSS framework",
                tools=["React", "Next.js", "Tailwind CSS"],
                estimated_effort="Low (1-2 days)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Build Components and Pages",
                description="Develop reusable components and implement page layouts",
                tools=["React", "HTML/CSS", "JavaScript"],
                estimated_effort="High (1-2 weeks)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Implement State Management and API Integration",
                description="Set up state management and connect to backend APIs",
                tools=["Redux", "Axios", "Jest"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Test and Deploy Frontend",
                description="Run tests, optimize performance, deploy to hosting",
                tools=["Jest", "Selenium", "Vercel"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]
    
    elif category == "deployment":
        return [
            WorkflowStep(
                step_number=1,
                task="Prepare Application for Deployment",
                description="Finalize code, remove debug code, set up environment variables",
                tools=["Git", "Python", "Markdown"],
                estimated_effort="Low (1-2 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Create Docker Container",
                description="Write Dockerfile, build and test container locally",
                tools=["Docker", "Docker Compose", "Git"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Set Up Cloud Infrastructure",
                description="Configure cloud provider, set up databases, networking, security groups",
                tools=["AWS", "Google Cloud", "Terraform"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Deploy and Monitor",
                description="Deploy container, set up monitoring, logging, and alerting",
                tools=["Docker", "Prometheus", "Grafana"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Set Up CI/CD Pipeline",
                description="Automate testing and deployment with GitHub Actions or Jenkins",
                tools=["GitHub", "Jenkins", "GitLab"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]
    
    elif category == "data":
        return [
            WorkflowStep(
                step_number=1,
                task="Define Data Requirements",
                description="Identify data sources, formats, quality standards, and storage needs",
                tools=["SQL", "Google Sheets", "Markdown"],
                estimated_effort="Low (1-2 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Extract and Collect Data",
                description="Connect to data sources, extract raw data, implement data ingestion",
                tools=["Python", "SQL", "Pandas"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Transform and Clean Data",
                description="Handle missing values, normalize formats, validate data quality",
                tools=["Pandas", "Python", "SQL"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Load to Data Warehouse",
                description="Structure data and load into data warehouse or lake",
                tools=["PostgreSQL", "BigQuery", "Spark"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Create Analytics and Dashboards",
                description="Build dashboards and reports for insights",
                tools=["Tableau", "PowerBI", "Matplotlib"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]
    
    else:  # Generic ML
        return [
            WorkflowStep(
                step_number=1,
                task="Define Problem and Requirements",
                description="Identify problem type, success metrics, and constraints",
                tools=["Markdown", "Jupyter Notebook", "Notion"],
                estimated_effort="Low (1-2 days)",
                dependencies=None
            ),
            WorkflowStep(
                step_number=2,
                task="Collect and Prepare Dataset",
                description="Gather data, perform exploratory analysis, handle missing values",
                tools=["Python", "Pandas", "Kaggle"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[1]
            ),
            WorkflowStep(
                step_number=3,
                task="Feature Engineering",
                description="Create and select relevant features for your model",
                tools=["Python", "Scikit-learn", "Pandas"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[2]
            ),
            WorkflowStep(
                step_number=4,
                task="Train and Tune Model",
                description="Train multiple models and optimize hyperparameters",
                tools=["PyTorch", "TensorFlow", "Scikit-learn"],
                estimated_effort="High (1-2 weeks)",
                dependencies=[3]
            ),
            WorkflowStep(
                step_number=5,
                task="Evaluate and Deploy",
                description="Validate performance and deploy to production",
                tools=["Pytest", "Docker", "AWS"],
                estimated_effort="Medium (2-5 days)",
                dependencies=[4]
            ),
        ]


def _get_goal_specific_workflow_response(goal: str) -> WorkflowResponse:
    """Generate goal-specific workflow response"""
    steps = _get_goal_specific_workflow(goal)
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

        # ✅ FIXED: Consistent parameter usage
        try:
            result = generator(
                prompt,
                max_length=220,
                temperature=0.4,
                top_p=0.9,
                do_sample=True,
                return_full_text=False,
            )
            raw_response = result[0]['generated_text'] if result else ""
        except Exception as e:
            print(f"Model generation failed: {e}. Using goal-specific defaults.")
            raw_response = ""

        # Remove any prompt echo if present
        if raw_response:
            first_step_match = re.search(r'^\s*1[\.\)]', raw_response, re.MULTILINE)
            if first_step_match:
                raw_response = raw_response[first_step_match.start():]

        # Structure the response
        workflow = structure_workflow_response(raw_response, request.goal)
        
        # ✅ IMPROVED: Use goal-specific defaults instead of generic fallback
        if workflow.total_steps < 3:
            print(f"Model output insufficient ({workflow.total_steps} steps). Using goal-specific workflow.")
            workflow = _get_goal_specific_workflow_response(request.goal)
        
        return workflow
        
    except Exception as e:
        print(f"Error generating workflow: {str(e)}")
        # ✅ IMPROVED: Fallback to goal-specific workflow on error
        try:
            return _get_goal_specific_workflow_response(request.goal)
        except Exception as fallback_error:
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

        # ✅ FIXED: Use consistent parameters
        result = generator(prompt, max_length=200, do_sample=True)
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
