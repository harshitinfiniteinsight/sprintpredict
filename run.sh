#!/bin/bash

# Start the backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip3 install tabulate 
pip3 install --no-cache-dir --upgrade --force-reinstall pandas numpy scikit-learn matplotlib
pip3 install flask
pip3 install openai
pip install --upgrade openai httpx
python main.py &

BACKEND_PID=$!

# Start the frontend
cd ../frontend
npm install
npm run dev &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 