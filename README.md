# Sprint Spark AI Planner

A comprehensive sprint planning and management tool that leverages AI to optimize task assignments and sprint planning.

## Features

- **AI-Powered Sprint Planning**: Automatically assigns tasks to developers based on skills, capacity, and preferences
- **Task Management**: Track and manage tasks with detailed information including story points, dependencies, and required skills
- **Team Capacity Planning**: Visualize and manage team capacity across sprints
- **Data Visualization**: Interactive charts and graphs for better insights
- **Natural Language Processing**: AI-powered sprint summaries and task descriptions

## Project Structure

```
sprintpredict/
├── backend/                 # FastAPI backend
│   ├── data_ingestion/     # Data loading and generation
│   ├── nlp/               # Natural Language Processing
│   ├── optimization/      # Sprint optimization algorithms
│   ├── visualization/     # Data visualization
│   ├── main.py           # FastAPI application
│   └── requirements.txt  # Python dependencies
│
├── frontend/              # React frontend
│   ├── src/              # Source code
│   ├── public/           # Static assets
│   └── package.json      # Node.js dependencies
│
└── run.sh                # Script to start both frontend and backend
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/harshitinfiniteinsight/sprintpredict.git
cd sprintpredict
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install streamlit #streamlit run app.py #in case need to run streamlit 
pip install transformers
pip3 install torch torchvision torchaudio
#streamlit run app.py #in case need to run streamlit 
```

3. Set up the frontend:
```bash
cd ../frontend
npm install
```

4. Create environment files:
```bash
# Backend
cp backend/.env.example backend/.env
# Frontend
cp frontend/.env.example frontend/.env
```

5. Start the application:
```bash
# From the project root
./run.sh
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Configuration

### Environment Variables

#### Backend (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
BACKEND_PORT=8000
BACKEND_HOST=localhost
FRONTEND_URL=http://localhost:5173
DATA_DIR=./data
DUMMY_DATA_DIR=./data/dummy
```

#### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
