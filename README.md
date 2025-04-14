# Sprint Spark AI Planner

An AI-driven sprint planning application that combines a powerful backend with a modern frontend interface.

## Project Structure

```
merged-project/
├── backend/           # Python backend
│   ├── src/          # Source code
│   ├── data/         # Data files
│   ├── requirements.txt
│   └── .env
├── frontend/         # React frontend
│   ├── src/          # Source code
│   ├── public/       # Static files
│   └── package.json
└── package.json      # Root package.json
```

## Setup

1. Install dependencies:
   ```bash
   npm run install:all
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env` in the backend directory
   - Update the variables as needed

## Running the Application

Start both frontend and backend:
```bash
npm start
```

Or run them separately:
```bash
# Backend
npm run backend

# Frontend
npm run frontend
```

## Features

- AI-powered sprint planning
- Task management
- Team capacity planning
- Data visualization
- Real-time updates

## Technologies Used

- Backend:
  - Python
  - FastAPI
  - Pandas
  - Scikit-learn
  - OpenAI

- Frontend:
  - React
  - TypeScript
  - Tailwind CSS
  - Vite
  - Plotly 