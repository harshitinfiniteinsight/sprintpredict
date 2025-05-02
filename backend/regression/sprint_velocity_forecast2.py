import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split # Still imported, but we'll do manual time series split
from sklearn.metrics import mean_absolute_error # Used for evaluation
import matplotlib.pyplot as plt
from datetime import timedelta, date

# --- 1. Simulate Historical Sprint Data (Changed to ~2 Years) ---
# Replace this section with loading your actual historical sprint data.
# Ensure your data includes columns for:
# - sprint_number (or a unique sprint identifier)
# - start_date (datetime)
# - end_date (datetime)
# - team_size (number of developers)
# - committed_story_points (story points committed at the start of the sprint)
# - completed_story_points (actual completed story points - this is your target velocity)
# - planned_leave_days_team (total planned leave days for the team during the sprint)
# - unplanned_leave_days_team (total unplanned leave days for the team during the sprint)
# - major_impediment (a binary flag or severity score for major blockers during the sprint)
# - backlog_well_refined_percentage (a measure of how well-defined the work was)

num_historical_sprints = 52 # Simulate approximately 2 years of bi-weekly sprints (52 sprints * 2 weeks = 104 weeks ≈ 2 years)
start_date_hist = pd.to_datetime('2023-01-01') # Start date adjusted to end around early 2025

historical_data_list = []
current_start = start_date_hist
current_team_size = 7 # Starting team size

for i in range(num_historical_sprints):
    sprint_number = i + 1
    start_date = current_start
    end_date = start_date + timedelta(weeks=2) - timedelta(days=1) # Assume 2-week sprints

    # Simulate more dynamic data - Adjusted team size change logic for 52 sprints
    if sprint_number > 26 and current_team_size == 7: # Change team size after ~1 year
        current_team_size = 8
    if sprint_number > 45 and current_team_size == 8: # Another small change later
         current_team_size = 7


    committed_sp = np.random.randint(20, 50) # Wider range
    # Completed SP will be related to committed, team size, leaves, impediments, refinement
    # Add some noise and dependency
    base_velocity = committed_sp * (current_team_size / 8.0) # Base on committed and team size (adjusting reference size)
    leave_impact = (np.random.randint(0, 5) + np.random.randint(0, 3)) * 0.5 # Some planned + unplanned impact
    impediment_impact = np.random.choice([0, 0, 0, 0, 10, 20], p=[0.6, 0.2, 0.1, 0.05, 0.04, 0.01]) # Occasional major impediments
    refinement_impact = (np.random.randint(60, 100) - 80) * 0.2 # Impact based on refinement avg 80

    completed_sp = base_velocity - leave_impact - impediment_impact + refinement_impact + np.random.normal(0, 4) # Add some random noise (slightly less noise)
    completed_sp = max(5, round(completed_sp)) # Ensure velocity is not negative and is an integer

    planned_leave = np.random.randint(0, 5)
    unplanned_leave = np.random.randint(0, 3)
    major_impediment = 1 if np.random.random() < 0.15 else 0 # 15% chance of major impediment
    backlog_refined = np.random.randint(60, 100) # Wider range for refinement

    historical_data_list.append({
        'sprint_number': sprint_number,
        'start_date': start_date,
        'end_date': end_date,
        'team_size': current_team_size,
        'committed_story_points': committed_sp,
        'completed_story_points': completed_sp,
        'planned_leave_days_team': planned_leave,
        'unplanned_leave_days_team': unplanned_leave,
        'major_impediment': major_impediment,
        'backlog_well_refined_percentage': backlog_refined,
    })

    current_start = end_date + timedelta(days=1)

historical_sprints_df = pd.DataFrame(historical_data_list)

# Calculate sprint duration in working days (excluding weekends)
historical_sprints_df['sprint_duration_days'] = historical_sprints_df.apply(
    lambda row: np.busday_count(row['start_date'].date(), row['end_date'].date() + timedelta(days=1)), axis=1
)

# Calculate effective team capacity in person-days for historical sprints
historical_sprints_df['available_person_days'] = (
    historical_sprints_df['team_size'] * historical_sprints_df['sprint_duration_days'] -
    historical_sprints_df['planned_leave_days_team'] - historical_sprints_df['unplanned_leave_days_team']
)

# Feature Engineering: Lagged velocity (velocity of previous sprint)
historical_sprints_df['lagged_velocity'] = historical_sprints_df['completed_story_points'].shift(1)
historical_sprints_df = historical_sprints_df.dropna().reset_index(drop=True) # Remove the first row and reset index

print("--- Historical Sprint Data (first 5 rows) ---")
print(historical_sprints_df[['sprint_number', 'start_date', 'end_date', 'team_size', 'committed_story_points',
                             'completed_story_points', 'sprint_duration_days', 'available_person_days',
                             'lagged_velocity']].head().to_markdown(index=False))

print("\n--- Historical Sprint Data (last 5 rows) ---")
print(historical_sprints_df[['sprint_number', 'start_date', 'end_date', 'team_size', 'committed_story_points',
                             'completed_story_points', 'sprint_duration_days', 'available_person_days',
                             'lagged_velocity']].tail().to_markdown(index=False))


# --- 2. Prepare Data for Modeling (Time Series Split) ---

# Define the features (input variables) and the target (output variable)
features = ['team_size', 'sprint_duration_days', 'available_person_days',
            'committed_story_points', 'lagged_velocity', 'major_impediment',
            'backlog_well_refined_percentage']
target = 'completed_story_points'

X = historical_sprints_df[features]
y = historical_sprints_df[target]

# Perform a time series split: train on earlier data, test on later data
# Hold out the last 20% of the data for testing
test_data_percentage = 0.2
split_index = int(len(historical_sprints_df) * (1 - test_data_percentage))

X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

print(f"\n--- Data Split ---")
print(f"Total historical sprints: {len(historical_sprints_df)}")

# CORRECTED LINES: Access sprint_number from the original historical_sprints_df using the split index
print(f"Training sprints: {len(X_train)} (from {historical_sprints_df['sprint_number'][:split_index].min()} to {historical_sprints_df['sprint_number'][:split_index].max()})")
print(f"Testing sprints: {len(X_test)} (from {historical_sprints_df['sprint_number'][split_index:].min()} to {historical_sprints_df['sprint_number'][split_index:].max()})")


# --- 3. Train the Model (on Training Data) ---
# We use a Random Forest Regressor, which is suitable for this type of data.

model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10, min_samples_split=5) # Added some hyperparameters
model.fit(X_train, y_train) # Train using ONLY the training data

print("\n--- Model Training Complete on Training Data ---")

# --- 4. Evaluate the Model (on Test Data) ---

# Predict on the test set
y_pred_test = model.predict(X_test)

# Evaluate the model using Mean Absolute Error
mae = mean_absolute_error(y_test, y_pred_test)

print(f"\n--- Model Evaluation on Test Set ---")
print(f"Mean Absolute Error (MAE): {mae:.2f} story points")
# You could add other metrics here if needed, e.g., MSE, R-squared

# --- 5. Forecast Future Velocity ---

# Define Future Sprints and Calendar Data
# Define the period you want to forecast for (e.g., the next year or two)
last_hist_end_date = historical_sprints_df['end_date'].max() # Get end date from the *full* historical data (last test sprint)
future_sprints_start_date = last_hist_end_date + timedelta(days=1)

# Define public holidays for the forecasting period (replace with actual holidays)
# Using 2025 and 2026 holidays as before
public_holidays_future_datetimeindex = pd.to_datetime([
    '2025-01-01', '2025-01-29', '2025-01-30', # Jan 2025
    '2025-02-17', # Feb 2025 (Simulated)
    '2025-04-18', # April 2025
    '2025-05-01', '2025-05-12', # May 2025
    '2025-06-02', # June 2025
    '2025-08-09', # August 2025
    '2025-09-08', # September 2025 (Simulated)
    '2025-10-23', # October 2025
    '2025-12-25', '2025-12-26', # Dec 2025 (Christmas + Simulated Boxing Day)
    # Add holidays for 2026 as well
    '2026-01-01', '2026-01-20', '2026-01-21', # Jan 2026
    '2026-04-03', # April 2026
    '2026-05-01', '2026-05-30', # May 2026
    '2026-08-09', '2026-08-10', # August 2026
    '2026-10-09', # October 2026
    '2026-12-25' # Dec 2026
])

# Convert public holidays to a list of date objects for np.busday_count
public_holidays_future = public_holidays_future_datetimeindex.date.tolist()


# Define future sprints (e.g., 2-week sprints starting after the last historical sprint)
sprint_duration_weeks = 2 # Assuming consistent sprint duration
team_size_future = historical_sprints_df['team_size'].iloc[-1] # Start with the last known team size from historical data

# Simulate planned leaves for the future period (replace with your actual planned leave calendar)
# Map sprint start dates to total planned leave days for that sprint
# Using the same planned leave data as before, covering 2024-2026
planned_leaves_future_events = {
    pd.to_datetime('2024-10-14'): 1, pd.to_datetime('2024-10-28'): 0,
    pd.to_datetime('2024-11-11'): 2, pd.to_datetime('2024-11-25'): 0,
    pd.to_datetime('2024-12-09'): 1, pd.to_datetime('2024-12-23'): 4, # Christmas period leave
    pd.to_datetime('2025-01-06'): 3, pd.to_datetime('2025-01-20'): 5, # CNY period leave
    pd.to_datetime('2025-02-03'): 1, pd.to_datetime('2025-02-17'): 0,
    pd.to_datetime('2025-03-03'): 2, pd.to_datetime('2025-03-17'): 0, pd.to_datetime('2025-03-31'): 1,
    pd.to_datetime('2025-04-14'): 10, # Significant planned leave
    pd.to_datetime('2025-04-28'): 2,
    pd.to_datetime('2025-05-12'): 3, pd.to_datetime('2025-05-26'): 2,
    pd.to_datetime('2025-06-09'): 1, pd.to_datetime('2025-06-23'): 0,
    pd.to_datetime('2025-07-07'): 1, pd.to_datetime('2025-07-21'): 0,
    pd.to_datetime('2025-08-04'): 4, # National Day period leave
    pd.to_datetime('2025-08-18'): 1,
    pd.to_datetime('2025-09-01'): 2, pd.to_datetime('2025-09-15'): 20, # Another significant planned leave
    pd.to_datetime('2025-09-29'): 0,
    pd.to_datetime('2025-10-13'): 0, pd.to_datetime('2025-10-27'): 0, # Minimal leaves in Oct to show recovery
    pd.to_datetime('2025-11-10'): 2, pd.to_datetime('2025-11-24'): 0,
    pd.to_datetime('2025-12-08'): 3, pd.to_datetime('2025-12-22'): 5, # Christmas/New Year period leave
    # Add planned leaves for 2026
    pd.to_datetime('2026-01-05'): 4, pd.to_datetime('2026-01-19'): 6, # CNY 2026
    pd.to_datetime('2026-02-02'): 1, pd.to_datetime('2026-02-16'): 0,
    pd.to_datetime('2026-03-02'): 2, pd.to_datetime('2026-03-16'): 0,
     pd.to_datetime('2026-03-30'): 1,
    pd.to_datetime('2026-04-13'): 8, # Planned leave
    pd.to_datetime('2026-04-27'): 2,
    pd.to_datetime('2026-05-11'): 3, pd.to_datetime('2026-05-25'): 2,
    pd.to_datetime('2026-06-08'): 1, pd.to_datetime('2026-06-22'): 0,
    pd.to_datetime('2026-07-06'): 1, pd.to_datetime('2026-07-20'): 0,
    pd.to_datetime('2026-08-03'): 4, # National Day period leave
    pd.to_datetime('2026-08-17'): 1,
    pd.to_datetime('2026-09-14'): 15, # Planned leave
    pd.to_datetime('2026-09-28'): 0,
     pd.to_datetime('2026-10-12'): 0, pd.to_datetime('2026-10-26'): 0,
    pd.to_datetime('2026-11-09'): 2, pd.to_datetime('2026-11-23'): 0,
    pd.to_datetime('2026-12-07'): 3, pd.to_datetime('2026-12-21'): 5, # Christmas/New Year period leave
}


forecasted_velocities = []
num_sprints_to_forecast = 52 # Forecast for approximately 2 years (can adjust this independently)

# Start the forecasting with the LAST ACTUAL velocity from the TEST set
last_known_velocity = y_test.iloc[-1]
last_sprint_number = historical_sprints_df['sprint_number'].max()

# For features that are unknown in future sprints (like committed points, impediments, refinement),
# we'll use a placeholder value. Using the historical average is a common simple approach.
# Use averages from the TRAINING data to avoid data leakage from the test set
avg_committed = X_train['committed_story_points'].mean()
avg_impediment = X_train['major_impediment'].mean()
avg_refinement = X_train['backlog_well_refined_percentage'].mean()

# Simulate potential team size changes in the future (optional)
future_team_size_changes = {
     pd.to_datetime('2025-03-17'): 9, # Example: Team grows in March 2025
     pd.to_datetime('2026-04-13'): 8, # Example: Team shrinks in April 2026
}

future_sprints = [] # Initialize future_sprints list here

current_start_date = future_sprints_start_date # Start forecasting from the day after last historical sprint

for i in range(1, num_sprints_to_forecast + 1):
    sprint_start = current_start_date
    sprint_end = sprint_start + timedelta(weeks=sprint_duration_weeks) - timedelta(days=1)
    sprint_number = last_sprint_number + i

    # Check for future team size changes based on sprint start date
    if sprint_start in future_team_size_changes:
        team_size_future = future_team_size_changes[sprint_start]
        print(f"--- Team size changed to {team_size_future} starting sprint on {sprint_start.date()} ---")


    # Calculate working days, considering weekends and public holidays
    num_working_days = np.busday_count(sprint_start.date(), sprint_end.date() + timedelta(days=1),
                                       holidays=public_holidays_future)

    # Get planned leave days for this sprint from your calendar data
    # Use the simplified lookup based on sprint start date
    planned_leave_days_in_sprint = planned_leaves_future_events.get(sprint_start, 0)


    # Calculate effective available person-days for the future sprint
    available_person_days_future = (team_size_future * num_working_days) - planned_leave_days_in_sprint

    # Prepare features for the current future sprint
    future_sprint_features = pd.DataFrame({
        'team_size': [team_size_future],
        'sprint_duration_days': [num_working_days],
        'available_person_days': [available_person_days_future],
        'committed_story_points': [avg_committed], # Using average from training data
        'lagged_velocity': [last_known_velocity], # Using the last known/predicted velocity
        'major_impediment': [avg_impediment],     # Using average from training data
        'backlog_well_refined_percentage': [avg_refinement] # Using average from training data
    })

    # Ensure the order of columns matches the features used during training
    future_sprint_features = future_sprint_features[features]

    # Predict velocity for the current sprint
    predicted_velocity = model.predict(future_sprint_features)[0]
    predicted_velocity = max(0, predicted_velocity) # Ensure prediction is not negative

    # Append the prediction and update the last_known_velocity for the next iteration
    # forecasted_velocities.append(predicted_velocity) # Not needed if adding directly to list below
    last_known_velocity = predicted_velocity


    future_sprints.append({
        'sprint_number': sprint_number,
        'start_date': sprint_start,
        'end_date': sprint_end,
        'team_size': team_size_future,
        'sprint_duration_days': num_working_days,
        'available_person_days': available_person_days_future,
        'forecasted_velocity': predicted_velocity # Add prediction here
    })
    current_start_date = sprint_end + timedelta(days=1)

future_sprints_df = pd.DataFrame(future_sprints)


print("\n--- Future Sprints with Forecasted Velocity (first 5 rows) ---")
print(future_sprints_df[['sprint_number', 'start_date', 'end_date', 'team_size',
                          'sprint_duration_days', 'available_person_days', 'forecasted_velocity']].head().to_markdown(index=False))

print("\n--- Future Sprints with Forecasted Velocity (last 5 rows) ---")
print(future_sprints_df[['sprint_number', 'start_date', 'end_date', 'team_size',
                          'sprint_duration_days', 'available_person_days', 'forecasted_velocity']].tail().to_markdown(index=False))


# --- 6. Prepare Data for Plotting ---

# Combine historical and forecasted data for plotting
# Create dataframes/series for each plot line
historical_train_plotting_df = pd.DataFrame({
    'start_date': historical_sprints_df['start_date'][:split_index].reset_index(drop=True), # Reset index
    'velocity': historical_sprints_df['completed_story_points'][:split_index].reset_index(drop=True), # Reset index
    'type': 'Historical Train Velocity'
})

historical_test_actual_plotting_df = pd.DataFrame({
    'start_date': historical_sprints_df['start_date'][split_index:].reset_index(drop=True),
    'velocity': historical_sprints_df['completed_story_points'][split_index:].reset_index(drop=True),
    'type': 'Historical Test Actual Velocity'
})

historical_test_predicted_plotting_df = pd.DataFrame({
    'start_date': historical_sprints_df['start_date'][split_index:].reset_index(drop=True),
    'velocity': y_pred_test, # Use the predictions on the test set
    'type': 'Historical Test Predicted Velocity'
})


future_plotting_df = future_sprints_df[['start_date', 'forecasted_velocity']].copy()
future_plotting_df = future_plotting_df.rename(columns={'forecasted_velocity': 'velocity'})
future_plotting_df['type'] = 'Forecasted Velocity'

# Concatenate all dataframes for plotting
plotting_df = pd.concat([historical_train_plotting_df,
                         historical_test_actual_plotting_df,
                         historical_test_predicted_plotting_df,
                         future_plotting_df])

# Sort by date for correct plotting order
plotting_df = plotting_df.sort_values(by='start_date').reset_index(drop=True)


print("\n--- Data Prepared for Plotting (first 5 rows) ---")
print(plotting_df.head().to_markdown(index=False))
print("\n--- Data Prepared for Plotting (last 5 rows) ---")
print(plotting_df.tail().to_markdown(index=False))


# --- 7. Plotting the Forecast ---

plt.figure(figsize=(18, 9)) # Increase figure size
plt.plot(plotting_df[plotting_df['type'] == 'Historical Train Velocity']['start_date'],
         plotting_df[plotting_df['type'] == 'Historical Train Velocity']['velocity'],
         marker='o', linestyle='-', label='Historical Train Velocity (Actual)', color='blue', markersize=4)
plt.plot(plotting_df[plotting_df['type'] == 'Historical Test Actual Velocity']['start_date'],
         plotting_df[plotting_df['type'] == 'Historical Test Actual Velocity']['velocity'],
         marker='o', linestyle='-', label='Historical Test Velocity (Actual)', color='green', markersize=4)
plt.plot(plotting_df[plotting_df['type'] == 'Historical Test Predicted Velocity']['start_date'],
         plotting_df[plotting_df['type'] == 'Historical Test Predicted Velocity']['velocity'],
         marker='x', linestyle='--', label='Historical Test Velocity (Predicted)', color='red', markersize=5)
plt.plot(plotting_df[plotting_df['type'] == 'Forecasted Velocity']['start_date'],
         plotting_df[plotting_df['type'] == 'Forecasted Velocity']['velocity'],
         marker='o', linestyle='--', label='Forecasted Velocity', color='orange', markersize=4)

plt.title('Team Sprint Velocity Forecast Over Time', fontsize=16)
plt.xlabel('Sprint Start Date', fontsize=12)
plt.ylabel('Velocity (Story Points)', fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, which='both', linestyle='-', linewidth=0.5)
plt.xticks(rotation=45, ha='right')
plt.yticks(np.arange(0, plotting_df['velocity'].max() + 10, 10)) # Improve y-axis ticks
plt.tight_layout()
plt.show()

print("\n--- Plot Generated ---")