# AI-Driven Sprint Planning and Prioritization System

A Streamlit application that automates sprint planning by analyzing historical sprint data, product backlogs, and team data. The system optimizes task assignments based on priorities, team capacity, dependencies, and skills.

## Features

- File upload for product backlog, historical sprint data, and team data
- Data visualization and preprocessing
- MILP-based optimization for sprint planning
- AI-powered sprint summaries using Llama 3.2
- Interactive dashboards and reports
- CSV export functionality

## Project Structure

```
sprintpredict/
├── app.py                 # Main Streamlit application
├── data/                  # Data directory
│   ├── dummy/            # Dummy data generation
│   └── templates/        # CSV templates
├── src/                  # Source code
│   ├── data_ingestion/   # Data loading and preprocessing
│   ├── optimization/     # MILP solver implementation
│   ├── nlp/             # NLP components for summaries
│   └── visualization/    # Visualization utilities
└── requirements.txt      # Project dependencies
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Usage

1. Upload your CSV files or use the provided dummy data
2. Review the data visualization and preprocessing steps
3. Run the optimization to generate the sprint plan
4. View the AI-generated sprint summary
5. Download the final sprint plan as CSV

## Data Format

### Product Backlog CSV
- Issue Key
- Summary
- Description
- Priority
- Story Points
- Dependencies
- Pre-mapped Skills

### Historical Sprint Data CSV
- Sprint ID
- Task IDs
- Story Points Committed
- Story Points Completed
- Slippage metrics

### Team Data CSV
- Developer Name
- Role
- Capacity (story points per sprint)
- Skill Sets
- Preferences

## License

MIT License 