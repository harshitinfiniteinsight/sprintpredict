import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from datetime import timedelta, date # Import date

# --- 1. Simulate Historical Sprint Data ---
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

data = {
    'sprint_number': range(1, 21),
    'start_date': pd.to_datetime(['2024-01-08', '2024-01-22', '2024-02-05', '2024-02-19', '2024-03-04',
                                  '2024-03-18', '2024-04-01', '2024-04-15', '2024-04-29', '2024-05-13',
                                  '2024-05-27', '2024-06-10', '2024-06-24', '2024-07-08', '2024-07-22',
                                  '2024-08-05', '2024-08-19', '2024-09-02', '2024-09-16', '2024-09-30']),
    'end_date': pd.to_datetime(['2024-01-19', '2024-02-02', '2024-02-16', '2024-03-01', '2024-03-15',
                                '2024-03-29', '2024-04-12', '2024-04-26', '2024-05-10', '2024-05-24',
                                '2024-06-07', '2024-06-21', '2024-07-05', '2024-07-19', '2024-08-02',
                                '2024-08-16', '2024-08-30', '2024-09-13', '2024-09-27', '2024-10-11']),
    'team_size': [7] * 10 + [8] * 10, # Example: Team size changed after sprint 10
    'committed_story_points': np.random.randint(25, 45, 20), # Simulated committed points
    'completed_story_points': np.random.randint(20, 40, 20), # Simulated actual velocity
    'planned_leave_days_team': [0, 1, 0, 0, 2, 0, 0, 1, 0, 3, 0, 0, 1, 0, 0, 2, 0, 0, 1, 0], # Simulated leaves
    'unplanned_leave_days_team': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0], # Simulated unplanned leaves
    'major_impediment': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], # Simulated blockers (0 or 1)
    'backlog_well_refined_percentage': np.random.randint(70, 100, 20), # Simulated refinement
}

historical_sprints_df = pd.DataFrame(data)

# Calculate sprint duration in working days (excluding weekends)
# Ensure dates are in the correct format for np.busday_count
historical_sprints_df['sprint_duration_days'] = historical_sprints_df.apply(
    lambda row: np.busday_count(row['start_date'].date(), row['end_date'].date() + timedelta(days=1)), axis=1
)

# Calculate effective team capacity in person-days for historical sprints
# Assuming 5 working days a week and accounting for leaves
historical_sprints_df['available_person_days'] = (
    historical_sprints_df['team_size'] * historical_sprints_df['sprint_duration_days'] -
    historical_sprints_df['planned_leave_days_team'] - historical_sprints_df['unplanned_leave_days_team']
)

# Feature Engineering: Lagged velocity (velocity of previous sprint)
# This is a crucial feature for time series forecasting
historical_sprints_df['lagged_velocity'] = historical_sprints_df['completed_story_points'].shift(1)
historical_sprints_df = historical_sprints_df.dropna() # Remove the first row which will have NaN for lagged velocity

print("--- Historical Sprint Data (first 5 rows) ---")
print(historical_sprints_df[['sprint_number', 'start_date', 'end_date', 'team_size', 'committed_story_points',
                             'completed_story_points', 'sprint_duration_days', 'available_person_days',
                             'lagged_velocity']].head().to_markdown(index=False)) # Using to_markdown for better display

# --- 2. Define Future Sprints and Calendar Data ---
# Define the period you want to forecast for (e.g., the next year)
last_hist_end_date = historical_sprints_df['end_date'].max()
future_sprints_start_date = last_hist_end_date + timedelta(days=1)

# Define public holidays for the forecasting period (replace with actual holidays)
# Example for Singapore in 2025 (adjust as needed)
public_holidays_future_datetimeindex = pd.to_datetime([
    '2025-01-01', '2025-01-29', '2025-01-30', '2025-04-18', '2025-05-01',
    '2025-05-12', '2025-06-02',
    # Adding a simulated holiday in September for a more pronounced dip
    '2025-09-08',
    '2025-08-09', '2025-10-23', '2025-12-25'
])

# Convert public holidays to a list of date objects for np.busday_count
public_holidays_future = public_holidays_future_datetimeindex.date.tolist()


# Define future sprints (e.g., 2-week sprints starting after the last historical sprint)
sprint_duration_weeks = 2 # Assuming consistent sprint duration
team_size_future = 8 # Assuming team size remains constant for the forecast period

# Simulate planned leaves for the future period (replace with your actual planned leave calendar)
# This should be a list of dates where team members are on planned leave.
# For simplicity here, we'll associate total planned leave days with sprint start dates.
# A more accurate approach would be to have a list of individual leave dates and aggregate per sprint.
planned_leaves_future_events = {
    # sprint_start_date: total_planned_leave_days_team_in_sprint
    pd.to_datetime('2024-10-14'): 1,
    pd.to_datetime('2024-11-11'): 2,
    pd.to_datetime('2024-12-09'): 1,
    pd.to_datetime('2025-01-06'): 3, # Example: related to New Year holidays
    pd.to_datetime('2025-02-03'): 1,
    pd.to_datetime('2025-03-03'): 2,
    pd.to_datetime('2025-04-14'): 10,
    pd.to_datetime('2025-05-26'): 2,
    pd.to_datetime('2025-07-07'): 1,
    pd.to_datetime('2025-08-04'): 3, # Example: related to National Day holiday
    pd.to_datetime('2025-09-15'): 25, # Significant planned leave in September
    pd.to_datetime('2025-11-10'): 2,
    pd.to_datetime('2025-12-08'): 2, # Example: related to Christmas holidays
    # Minimal leaves in October to show a spike after the September drop
    pd.to_datetime('2025-10-13'): 0,
    pd.to_datetime('2025-10-27'): 0,
}


future_sprints = []
current_start_date = future_sprints_start_date
# Forecast for approximately a year (26 bi-weekly sprints)
num_sprints_to_forecast = 26

# --- 3. Prepare Data for Modeling ---

# Define the features (input variables) and the target (output variable)
# These must match the columns you prepared in your historical data.
features = ['team_size', 'sprint_duration_days', 'available_person_days',
            'committed_story_points', 'lagged_velocity', 'major_impediment',
            'backlog_well_refined_percentage']
target = 'completed_story_points'

X = historical_sprints_df[features]
y = historical_sprints_df[target]

# --- 4. Train the Model ---
# We use a Random Forest Regressor, which is suitable for this type of data.
# It learns the complex relationships between the features and the completed velocity.

model = RandomForestRegressor(n_estimators=100, random_state=42) # n_estimators is the number of trees in the forest
model.fit(X, y) # This is where the model is trained on your historical data

print("\n--- Model Training Complete ---")

# --- 5. Forecast Future Velocity ---

# To forecast future sprints sequentially, we need the predicted velocity of the
# previous sprint to use as the 'lagged_velocity' feature for the current sprint.

forecasted_velocities = []
# Start with the actual completed velocity of the last historical sprint
last_known_velocity = historical_sprints_df['completed_story_points'].iloc[-1]

# For features that are unknown in future sprints (like committed points, impediments, refinement),
# we'll use a placeholder value. Using the historical average is a common simple approach.
avg_committed = historical_sprints_df['committed_story_points'].mean()
avg_impediment = historical_sprints_df['major_impediment'].mean() # Treat binary as a probability/average
avg_refinement = historical_sprints_df['backlog_well_refined_percentage'].mean()


for i in range(1, num_sprints_to_forecast + 1):
    sprint_start = current_start_date
    sprint_end = sprint_start + timedelta(weeks=sprint_duration_weeks) - timedelta(days=1)

    # Calculate working days, considering weekends and public holidays
    # Pass the list of date objects to holidays
    num_working_days = np.busday_count(sprint_start.date(), sprint_end.date() + timedelta(days=1),
                                       holidays=public_holidays_future)

    # Get planned leave days for this sprint from your calendar data
    # This is a simplified lookup. A real system would iterate through
    # individual planned leaves within the sprint dates and sum them up.
    # Need to find the planned leave entry that falls within this sprint dates
    planned_leave_days_in_sprint = 0
    # Check if the sprint_start date is in the planned_leaves_future_events keys
    if sprint_start in planned_leaves_future_events:
         planned_leave_days_in_sprint = planned_leaves_future_events[sprint_start]
    # Note: The previous loop logic was simplified and might not capture leaves correctly
    # if the leave date wasn't exactly the sprint start date.
    # The dictionary lookup above assumes the key is the sprint start date.
    # For a more robust solution, you'd need a more detailed leave calendar structure.


    # Calculate effective available person-days for the future sprint
    # We cannot know unplanned leave or major impediments in advance for forecasting.
    # The model will use the historical relationship between 'available_person_days'
    # (which included unplanned leaves historically) and velocity to make a prediction.
    # For the future, we calculate 'available_person_days' based on known factors (team size, duration, planned leave).
    available_person_days_future = (team_size_future * num_working_days) - planned_leave_days_in_sprint

    # --- Restore Prediction Logic ---
    # Prepare features for the current future sprint based on known future data
    # and estimated/average values for unknown future features.
    future_sprint_features = pd.DataFrame({
        'team_size': [team_size_future], # Use future team size
        'sprint_duration_days': [num_working_days], # Use calculated working days
        'available_person_days': [available_person_days_future], # Use calculated available person-days
        'committed_story_points': [avg_committed], # Use average from historical data
        'lagged_velocity': [last_known_velocity], # Use the last predicted/actual velocity
        'major_impediment': [avg_impediment], # Use average from historical data
        'backlog_well_refined_percentage': [avg_refinement] # Use average from historical data
    })

    # Ensure the order of columns matches the features used during training
    future_sprint_features = future_sprint_features[features]

    # Predict velocity for the current sprint using the trained model
    predicted_velocity = model.predict(future_sprint_features)[0]

    # Append the prediction and update the last_known_velocity for the next iteration's prediction
    forecasted_velocities.append(predicted_velocity)
    last_known_velocity = predicted_velocity # The prediction becomes the lagged velocity for the next sprint
    # --- End Restore Prediction Logic ---


    future_sprints.append({
        'sprint_number': historical_sprints_df['sprint_number'].max() + i,
        'start_date': sprint_start,
        'end_date': sprint_end,
        'team_size': team_size_future,
        'sprint_duration_days': num_working_days,
        'available_person_days': available_person_days_future,
        # lagged_velocity will be added during the forecasting loop
        # committed_story_points, major_impediment, backlog_well_refined_percentage
        # will be estimated or set to historical averages for forecasting
    })
    current_start_date = sprint_end + timedelta(days=1)

future_sprints_df = pd.DataFrame(future_sprints)

# Add the forecasted velocities to the future sprints DataFrame AFTER the loop
future_sprints_df['forecasted_velocity'] = forecasted_velocities


print("\n--- Future Sprints with Forecasted Velocity (first 5 rows) ---")
print(future_sprints_df[['sprint_number', 'start_date', 'end_date', 'team_size',
                          'sprint_duration_days', 'available_person_days', 'forecasted_velocity']].head().to_markdown(index=False))

print("\n--- Columns of future_sprints_df after adding forecasted_velocity ---")
print(future_sprints_df.columns.tolist()) # Check columns here


print("\n--- Future Sprints with Forecasted Velocity (showing sprints around Sep/Oct 2025) ---")
# Find the sprints around Sep/Oct 2025 to print their details
sep_oct_sprints = future_sprints_df[
    (future_sprints_df['start_date'] >= pd.to_datetime('2025-09-01')) &
    (future_sprints_df['start_date'] <= pd.to_datetime('2025-10-31'))
].copy() # Added .copy()


print("\n--- Columns of sep_oct_sprints before printing ---")
print(sep_oct_sprints.columns.tolist()) # Check columns here


print(sep_oct_sprints[['sprint_number', 'start_date', 'end_date', 'team_size',
                         'sprint_duration_days', 'available_person_days', 'forecasted_velocity']].to_markdown(index=False))


# --- 6. Prepare Data for Plotting ---

# Combine historical and forecasted data for plotting
# Create a column to distinguish between historical and forecasted data
historical_plotting_df = historical_sprints_df[['start_date', 'completed_story_points']].copy()
historical_plotting_df = historical_plotting_df.rename(columns={'completed_story_points': 'velocity'})
historical_plotting_df['type'] = 'Historical Velocity'

future_plotting_df = future_sprints_df[['start_date', 'forecasted_velocity']].copy()
future_plotting_df = future_plotting_df.rename(columns={'forecasted_velocity': 'velocity'})
future_plotting_df['type'] = 'Forecasted Velocity'


plotting_df = pd.concat([historical_plotting_df, future_plotting_df])

# Sort by date for correct plotting order
plotting_df = plotting_df.sort_values(by='start_date')

print("\n--- Data Prepared for Plotting (first 5 rows) ---")
print(plotting_df.head().to_markdown(index=False))

# --- 7. Plotting the Forecast ---

# You can use this data (plotting_df) to create your graph over the year.
# Here's the matplotlib code to generate the plot:

plt.figure(figsize=(14, 7)) # Increase figure size for better readability
plt.plot(plotting_df[plotting_df['type'] == 'Historical Velocity']['start_date'],
         plotting_df[plotting_df['type'] == 'Historical Velocity']['velocity'],
         marker='o', linestyle='-', label='Historical Velocity', color='blue')
plt.plot(plotting_df[plotting_df['type'] == 'Forecasted Velocity']['start_date'],
         plotting_df[plotting_df['type'] == 'Forecasted Velocity']['velocity'],
         marker='o', linestyle='--', label='Forecasted Velocity', color='orange')

plt.title('Team Sprint Velocity Forecast Over Time')
plt.xlabel('Sprint Start Date')
plt.ylabel('Velocity (Story Points)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45, ha='right') # Rotate labels for better readability
plt.tight_layout() # Adjust layout to prevent labels overlapping
plt.show()

print("\n--- Plot Generated ---")
