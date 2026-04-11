# Intelligent Workflow Assistant - Prototype Implementation Guide

## 🎯 Project Overview

A sophisticated Python-based assistant that transforms user goals into structured, step-by-step workflows with recommended tools and technologies. Built with FastAPI backend and modern HTML5 frontend.

---

## 📁 Project Structure

```
prototype/
├── main.py                              # FastAPI backend server
├── run_server.py                        # Server launcher script
├── intelligent_workflow_assistant.html  # Frontend UI
├── test_api_simple.py                   # API testing script
└── README.md                            # This file
```

---

## 🚀 Quick Start Guide

### Phase 1: Prerequisites
- **Python 3.10+** - Installed (currently using 3.14.2)
- **VS Code** - For development
- **Required Python packages:**
  - `fastapi` - Web framework
  - `uvicorn` - ASGI server
  - `transformers` - AI models
  - `torch` - Deep learning framework
  - `python-multipart` - Form data parsing

### Phase 2: Setup & Installation

All dependencies are pre-installed. To verify:
```bash
pip list | grep -E "fastapi|uvicorn|transformers|torch"
```

### Phase 3: Running the Backend Server

**Option 1: Using the launcher script**
```bash
python run_server.py
```

**Option 2: Direct uvicorn command**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on **http://localhost:8000**

### Phase 4: Accessing the Frontend

1. Start the backend server:
```bash
python run_server.py
```
2. Open the web app in your browser:
```text
http://localhost:8000/app
```
3. Enter a goal (e.g., "Build a plant disease detection app")
4. Click "Generate" to create a workflow
5. View structured steps with tools and effort estimates

> Do not open `intelligent_workflow_assistant.html` directly with `file://`, because browser security may block requests to the API server.

---

## 🔌 API Endpoints

### 1. Health Check
```http
GET /
```
**Response:**
```json
{
  "message": "Intelligent Workflow Assistant Running",
  "version": "1.0",
  "status": "online"
}
```

### 2. Generate Workflow (Main Endpoint)
```http
POST /generate-workflow/
Content-Type: application/json

{
  "goal": "Build a plant disease detection app",
  "context": "Optional context about the project"
}
```

**Response:**
```json
{
  "goal": "Build a plant disease detection app",
  "total_steps": 5,
  "steps": [
    {
      "step_number": 1,
      "task": "Define Requirements",
      "description": "Gather and document project requirements",
      "tools": ["Google Sheets", "Markdown", "Notion"],
      "estimated_effort": "Low (1-2 days)",
      "dependencies": null
    },
    ...
  ],
  "overall_tools": ["Git", "Python", "Docker", ...]
}
```

### 3. Refine Step (Detailed Guidance)
```http
POST /refine-step/
{
  "step_task": "Train the ML model",
  "suggestions": true
}
```

### 4. Get Available Tools
```http
GET /tools/
```

**Response:**
```json
{
  "available_tools": ["Python", "PyTorch", "TensorFlow", ...],
  "tool_categories": {
    "data": ["Python", "Pandas", "SQL", ...],
    "model": ["PyTorch", "TensorFlow", ...],
    ...
  }
}
```

### 5. Get Example Workflows
```http
GET /examples/
```

---

## 🧠 Core Features Implemented

### Phase 1: Basic Input/Output ✅
- **Input:** User enters a goal
- **Output:** Step-by-step workflow generated
- **Bonus:** Tool suggestions for each step

### Phase 2: Improved Prompt Engineering ✅
```python
prompt = """Break this goal into clear steps:
Goal: {user_input}

Output format:
1. [Step name]: [Description]
2. [Step name]: [Description]
...
Tools required for each step."""
```

### Phase 3: Workflow Structuring ✅
Converts raw AI output into structured JSON:
```python
WorkflowStep:
  - step_number: int
  - task: str
  - description: str
  - tools: List[str]
  - estimated_effort: str
  - dependencies: List[int]
```

### Phase 4: Smart Tool Suggestion Engine ✅
Automatically recommends tools based on task keywords:

```python
TOOL_MAPPING = {
    "data": ["Python", "Pandas", "SQL", "Kaggle"],
    "model": ["PyTorch", "TensorFlow", "Scikit-learn"],
    "training": ["Jupyter", "Colab", "Paperspace"],
    "deployment": ["Docker", "AWS", "Google Cloud"],
    "nlp": ["NLTK", "SpaCy", "Transformers"],
    "cv": ["OpenCV", "YOLO", "Pillow"],
    ...
}
```

### Phase 5: Effort Estimation ✅
Automatically estimates effort based on complexity keywords:
- **Low:** 1-2 days (preparation, planning)
- **Medium:** 2-5 days (processing, implementation)
- **High:** 1-2 weeks (training, deployment)

### Phase 6: Frontend Integration ✅
Modern UI with:
- Real-time status updates
- Animated step cards
- Tool tags and effort indicators
- Error handling and validation

---

## 📊 Model Used

**FLAN-T5 (Fallback: GPT-2)**
- Lightweight and efficient
- Better structured output formatting
- Suitable for local deployment
- Can be upgraded to LLaMA or other models

---

## 🔧 Architecture Overview

```
User Input
    ↓
Frontend (HTML/CSS/JavaScript)
    ↓
FastAPI Backend (port 8000)
    ↓
AI Model (FLAN-T5)
    ↓
Tool Recommendation Engine
    ↓
Workflow Structuring Logic
    ↓
JSON Response
    ↓
Render on Frontend
```

---

## 💡 Example Workflows Generated

### Example 1: Plant Disease Detection App
1. **Define Requirements** - Gather requirements (1-2 days)
2. **Data Collection** - Collect plant images (2-5 days)
3. **Model Development** - Train ML model (1-2 weeks)
4. **Testing & Validation** - Test performance (2-5 days)
5. **Deployment** - Deploy to production (1-2 weeks)

### Example 2: REST API Development
1. **Design API Schema** - Define endpoints (1-2 days)
2. **Setup Environment** - Create project structure (1-2 days)
3. **Implement Backend** - Code API endpoints (2-5 days)
4. **Database Setup** - Configure database (2-5 days)
5. **Testing** - Write and run tests (2-5 days)
6. **Deployment** - Deploy API (1-2 days)

---

## 🤖 Frontend Features

**Dashboard Components:**
- Real-time status bar with animated spinner
- Stats cards showing:
  - Number of steps
  - Estimated time
  - Difficulty level
- Workflow overview summary
- Step cards with:
  - Sequential numbering
  - Task title and description
  - Recommended tools
  - Effort estimation
  - Smooth animations

---

## 📝 Configuration & Customization

### Modify Tool Mappings
Edit `main.py` TOOL_MAPPING dictionary:
```python
TOOL_MAPPING = {
    "your_category": ["tool1", "tool2", "tool3"],
    ...
}
```

### Change AI Model
In `main.py`, update the pipeline initialization:
```python
generator = pipeline(
    "text2text-generation",
    model="your-model-name"  # e.g., "meta-llama/Llama-2-7b"
)
```

### Adjust effort estimation
Modify `estimate_effort()` function to customize complexity keywords.

---

## 🧪 Testing the API

**Run tests with:**
```bash
python test_api_simple.py
```

**Manual curl test:**
```bash
# Health check
curl http://localhost:8000/

# Generate workflow
curl -X POST http://localhost:8000/generate-workflow/ \
  -H "Content-Type: application/json" \
  -d '{"goal": "Build an ML app"}'
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution:** Reinstall dependencies
```bash
pip install fastapi uvicorn transformers torch python-multipart
```

### Issue: Port 8000 already in use
**Solution:** Change port in `run_server.py` or `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

### Issue: CORS errors in frontend
**Solution:** CORS is already enabled in `main.py`. Check browser console for errors.

### Issue: Frontend can't connect to backend
**Solution:** Ensure backend is running and accessible at `http://localhost:8000`

---

## 🚀 Future Enhancements

### Phase 7: Advanced Features
- [ ] User authentication & workflow saving
- [ ] Workflow sharing and collaboration
- [ ] Integration with GitHub/GitLab
- [ ] Real-time progress tracking
- [ ] Workflow templates library
- [ ] Step-by-step videoguides
- [ ] AI-powered subtask generation
- [ ] Automated code generation

### Phase 8: Upgrades
- [ ] Switch to larger LLMs (GPT-4, Claude)
- [ ] Fine-tuned models for specific domains
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Desktop application (Electron)
- [ ] Plugin system for custom tools

---

## 📄 API Response Structure

### WorkflowResponse Schema
```json
{
  "goal": "string - user's goal",
  "total_steps": "int - number of steps",
  "steps": [
    {
      "step_number": "int",
      "task": "string - step name",
      "description": "string - detailed description",
      "tools": ["array", "of", "tools"],
      "estimated_effort": "string - effort level",
      "dependencies": [null, 1, 2] - step dependencies
    }
  ],
  "overall_tools": ["all", "tools", "used"]
}
```

---

## 🎓 Learning Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Transformers Library:** https://huggingface.co/transformers/
- **FLAN-T5 Model:** https://huggingface.co/google/flan-t5-base
- **Uvicorn Server:** https://www.uvicorn.org/

---

## 📌 Summary

This prototype demonstrates a fully functional AI-powered workflow generation system with:
- ✅ Backend API with 5+ endpoints
- ✅ Smart tool recommendation engine
- ✅ Automatic effort estimation
- ✅ Modern responsive frontend
- ✅ CORS-enabled for cross-origin requests
- ✅ Error handling and validation
- ✅ Scalable architecture

**Status:** Production-ready for local deployment. Ready for cloud deployment with minimal configuration changes.

---

## 📞 Support & Feedback

For issues or feature requests, please check:
1. FastAPI logs in terminal
2. Browser console (F12)
3. Run test_api_simple.py for backend verification

---

**Last Updated:** April 8, 2026  
**Version:** 1.0  
**Team:** Dark Binary  
**Institution:** Thangavelu Engineering College, Chennai
