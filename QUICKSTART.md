# QUICK START - Intelligent Workflow Assistant

## 1. Start the Backend Server

```bash
cd c:\Users\SIVA R\OneDrive\Desktop\prototype
python run_server.py
```

Wait for message: `INFO: Uvicorn running on http://0.0.0.0:8000`

## 2. Open Frontend

Open the web app in your browser:
```text
http://localhost:8000/app
```

> Do not open `intelligent_workflow_assistant.html` directly from the file system.

## 3. Use the Assistant

### Enter a Goal
Type your goal in the text area:
```
Examples:
- Build a plant disease detection app
- Create a REST API for a todo app
- Learn machine learning from scratch
- Develop a mobile app
- Setup a data pipeline
```

### Generate Workflow
Click the "Generate" button or press Ctrl+Enter

### View Results
The system will generate:
- Number of steps (5-8)
- Estimated time to complete
- Difficulty level (Beginner/Intermediate/Advanced)
- Step-by-step breakdown with:
  - Task name
  - Description
  - Recommended tools
  - Effort estimate

## 4. Testing the API (Optional)

Run the test script to verify backend:
```bash
python test_api_simple.py
```

## API Endpoints Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | Health check |
| POST | `/generate-workflow/` | Generate workflow (main) |
| POST | `/refine-step/` | Get detailed step guidance |
| GET | `/tools/` | Get available tools list |
| GET | `/examples/` | Get example workflows |

## Troubleshooting

**Q: "Cannot reach server" error?**
A: Make sure `python run_server.py` is running in another terminal

**Q: Port 8000 already in use?**
A: Kill the process or edit port number in `run_server.py`

**Q: Workflow generation takes long?**
A: First generation loads the AI model (~2-3 minutes). Subsequent requests are faster.

## File Descriptions

- `main.py` - FastAPI backend with all API endpoints
- `run_server.py` - Server launcher script
- `intelligent_workflow_assistant.html` - Frontend UI (open in browser)
- `test_api_simple.py` - Simple API test script
- `README.md` - Detailed documentation

## Features

✅ AI-powered workflow generation
✅ Smart tool recommendation
✅ Automatic effort estimation
✅ Step dependency tracking
✅ Beautiful modern UI
✅ Real-time status updates
✅ CORS-enabled for integration

---

**Ready to go!** Start the server and begin generating workflows.
