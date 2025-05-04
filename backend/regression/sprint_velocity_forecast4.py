import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import timedelta, date
import json

class VelocityForecaster:
    """
    A class to simulate historical sprint data, train a velocity forecasting
    model, forecast future velocity, and output the results as JSON.
    """

    def __init__(self, num_historical_sprints=52, start_date_hist='2023-01-01', num_sprints_to_forecast=52):
        """
        Initializes the VelocityForecaster with simulation parameters.

        Args:
            num_historical_sprints (int): The number of historical sprints to simulate.
            start_date_hist (str): The start date for historical data simulation (YYYY-MM-DD).
            num_sprints_to_forecast (int): The number of future sprints to forecast.
        """
        self.num_historical_sprints = num_historical_sprints
        self.start_date_hist = pd.to_datetime(start_date_hist)
        self.num_sprints_to_forecast = num_sprints_to_forecast
        self.historical_sprints_df = None
        self.future_sprints_df = None
        self.model = None
        self.plotting_df = None
        self.mae = None # Store MAE for potential output

        # Define features and target
        self.features = ['team_size', 'sprint_duration_days', 'available_person_days',
                         'committed_story_points', 'lagged_velocity', 'major_impediment',
                         'backlog_well_refined_percentage']
        self.target = 'completed_story_points'

        # Define future calendar data (can be moved to a config or passed in)
        self.public_holidays_future_datetimeindex = pd.to_datetime([
            '2025-01-01', '2025-01-29', '2025-01-30',
            '2025-02-17',
            '2025-04-18',
            '2025-05-01', '2025-05-12',
            '2025-06-02',
            '2025-08-09',
            '2025-09-08',
            '2025-10-23',
            '2025-12-25', '2025-12-26',
            '2026-01-01', '2026-01-20', '2026-01-21',
            '2026-04-03',
            '2026-05-01', '2026-05-30',
            '2026-08-09', '2026-08-10',
            '2026-10-09',
            '2026-12-25'
        ])
        self.public_holidays_future = self.public_holidays_future_datetimeindex.date.tolist()

        self.planned_leaves_future_events = {
            pd.to_datetime('2024-10-14'): 1, pd.to_datetime('2024-10-28'): 0,
            pd.to_datetime('2024-11-11'): 2, pd.to_datetime('2024-11-25'): 0,
            pd.to_datetime('2024-12-09'): 1, pd.to_datetime('2024-12-23'): 4,
            pd.to_datetime('2025-01-06'): 3, pd.to_datetime('2025-01-20'): 5,
            pd.to_datetime('2025-02-03'): 1, pd.to_datetime('2025-02-17'): 0,
            pd.to_datetime('2025-03-03'): 2, pd.to_datetime('2025-03-17'): 0, pd.to_datetime('2025-03-31'): 1,
            pd.to_datetime('2025-04-14'): 10,
            pd.to_datetime('2025-04-28'): 2,
            pd.to_datetime('2025-05-12'): 3, pd.to_datetime('2025-05-26'): 2,
            pd.to_datetime('2025-06-09'): 1, pd.to_datetime('2025-06-23'): 0,
            pd.to_datetime('2025-07-07'): 1, pd.to_datetime('2025-07-21'): 0,
            pd.to_datetime('2025-08-04'): 4,
            pd.to_datetime('2025-08-18'): 1,
            pd.to_datetime('2025-09-01'): 2, pd.to_datetime('2025-09-15'): 20,
            pd.to_datetime('2025-09-29'): 0,
            pd.to_datetime('2025-10-13'): 0, pd.to_datetime('2025-10-27'): 0,
            pd.to_datetime('2025-11-10'): 2, pd.to_datetime('2025-11-24'): 0,
            pd.to_datetime('2025-12-08'): 3, pd.to_datetime('2025-12-22'): 5,
            pd.to_datetime('2026-01-05'): 4, pd.to_datetime('2026-01-19'): 6,
            pd.to_datetime('2026-02-02'): 1, pd.to_datetime('2026-02-16'): 0,
            pd.to_datetime('2026-03-02'): 2, pd.to_datetime('2026-03-16'): 0,
             pd.to_datetime('2026-03-30'): 1,
            pd.to_datetime('2026-04-13'): 8,
            pd.to_datetime('2026-04-27'): 2,
            pd.to_datetime('2026-05-11'): 3, pd.to_datetime('2026-05-25'): 2,
            pd.to_datetime('2026-06-08'): 1, pd.to_datetime('2026-06-22'): 0,
            pd.to_datetime('2026-07-06'): 1, pd.to_datetime('2026-07-20'): 0,
            pd.to_datetime('2026-08-03'): 4,
            pd.to_datetime('2026-08-17'): 1,
            pd.to_datetime('2026-09-14'): 15,
            pd.to_datetime('2026-09-28'): 0,
             pd.to_datetime('2026-10-12'): 0, pd.to_datetime('2026-10-26'): 0,
            pd.to_datetime('2026-11-09'): 2, pd.to_datetime('2026-11-23'): 0,
            pd.to_datetime('2026-12-07'): 3, pd.to_datetime('2026-12-21'): 5,
        }

        self.future_team_size_changes = {
             pd.to_datetime('2025-03-17'): 9,
             pd.to_datetime('2026-04-13'): 8,
        }


    def simulate_historical_data(self):
        """Simulates historical sprint data."""
        historical_data_list = []
        current_start = self.start_date_hist
        current_team_size = 7 # Starting team size

        for i in range(self.num_historical_sprints):
            sprint_number = i + 1
            start_date = current_start
            end_date = start_date + timedelta(weeks=2) - timedelta(days=1) # Assume 2-week sprints

            # Simulate more dynamic data - Adjusted team size change logic
            if sprint_number > self.num_historical_sprints // 2 and current_team_size == 7:
                current_team_size = 8
            if sprint_number > self.num_historical_sprints * 0.85 and current_team_size == 8:
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

        self.historical_sprints_df = pd.DataFrame(historical_data_list)

        # Calculate sprint duration in working days (excluding weekends)
        self.historical_sprints_df['sprint_duration_days'] = self.historical_sprints_df.apply(
            lambda row: np.busday_count(row['start_date'].date(), row['end_date'].date() + timedelta(days=1)), axis=1
        )

        # Calculate effective team capacity in person-days for historical sprints
        self.historical_sprints_df['available_person_days'] = (
            self.historical_sprints_df['team_size'] * self.historical_sprints_df['sprint_duration_days'] -
            self.historical_sprints_df['planned_leave_days_team'] - self.historical_sprints_df['unplanned_leave_days_team']
        )

        # Feature Engineering: Lagged velocity (velocity of previous sprint)
        self.historical_sprints_df['lagged_velocity'] = self.historical_sprints_df['completed_story_points'].shift(1)
        self.historical_sprints_df = self.historical_sprints_df.dropna().reset_index(drop=True) # Remove the first row and reset index


    def prepare_data(self, test_data_percentage=0.2):
        """Prepares data for modeling using a time series split."""
        if self.historical_sprints_df is None:
            raise ValueError("Historical data not simulated. Call simulate_historical_data() first.")

        X = self.historical_sprints_df[self.features]
        y = self.historical_sprints_df[self.target]

        # Perform a time series split
        split_index = int(len(self.historical_sprints_df) * (1 - test_data_percentage))

        self.X_train, self.X_test = X[:split_index], X[split_index:]
        self.y_train, self.y_test = y[:split_index], y[split_index:]

        # Store split index for later use in combining data
        self.split_index = split_index


    def train_model(self):
        """Trains the RandomForestRegressor model."""
        if self.X_train is None or self.y_train is None:
            raise ValueError("Data not prepared. Call prepare_data() first.")

        self.model = RandomForestRegressor(n_estimators=200, random_state=42, max_depth=10, min_samples_split=5)
        self.model.fit(self.X_train, self.y_train)

    def evaluate_model(self):
        """Evaluates the trained model on the test set."""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        if self.X_test is None or self.y_test is None:
             raise ValueError("Data not prepared. Call prepare_data() first.")

        y_pred_test = self.model.predict(self.X_test)
        self.mae = mean_absolute_error(self.y_test, y_pred_test)
        return self.mae, y_pred_test # Return predictions for plotting


    def forecast_velocity(self):
        """Forecasts future sprint velocity."""
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        if self.historical_sprints_df is None:
             raise ValueError("Historical data not simulated. Call simulate_historical_data() first.")
        if self.y_test is None:
             raise ValueError("Data not prepared. Call prepare_data() first.")


        last_hist_end_date = self.historical_sprints_df['end_date'].max()
        future_sprints_start_date = last_hist_end_date + timedelta(days=1)

        sprint_duration_weeks = 2
        team_size_future = self.historical_sprints_df['team_size'].iloc[-1] # Start with last known team size
        last_known_velocity = self.y_test.iloc[-1] # Start forecasting with the last actual test velocity
        last_sprint_number = self.historical_sprints_df['sprint_number'].max()

        # Use averages from the TRAINING data for other features whose future is unknown/static
        avg_impediment = self.X_train['major_impediment'].mean()
        avg_refinement = self.X_train['backlog_well_refined_percentage'].mean()

        # *** NEW: Initialize committed points for the first forecast sprint ***
        # Based on the last historical velocity from the test set + 5%
        committed_points_for_this_sprint = round(last_known_velocity * 1.05)
        # Ensure committed points are non-negative
        committed_points_for_this_sprint = max(0, committed_points_for_this_sprint)


        future_sprints_list = []
        current_start_date = future_sprints_start_date

        for i in range(1, self.num_sprints_to_forecast + 1):
            sprint_start = current_start_date
            sprint_end = sprint_start + timedelta(weeks=sprint_duration_weeks) - timedelta(days=1)
            sprint_number = last_sprint_number + i

            # Check for future team size changes
            if sprint_start in self.future_team_size_changes:
                team_size_future = self.future_team_size_changes[sprint_start]

            # Calculate working days, considering weekends and public holidays
            # np.busday_count correctly handles list of date objects for holidays
            num_working_days = np.busday_count(sprint_start.date(), sprint_end.date() + timedelta(days=1),
                                               holidays=self.public_holidays_future)

            # Get planned leave days for this sprint
            # Use .get() with a default of 0 if the date is not in planned_leaves_future_events
            planned_leave_days_in_sprint = self.planned_leaves_future_events.get(sprint_start, 0)

            # Calculate effective available person-days
            available_person_days_future = (team_size_future * num_working_days) - planned_leave_days_in_sprint
            # Ensure available person days is non-negative
            available_person_days_future = max(0, available_person_days_future)


            # Prepare features for the current future sprint
            future_sprint_features = pd.DataFrame({
                'team_size': [team_size_future],
                'sprint_duration_days': [num_working_days],
                'available_person_days': [available_person_days_future],
                # *** Use the dynamically calculated committed points for THIS sprint ***
                'committed_story_points': [committed_points_for_this_sprint],
                # *** Use the last known velocity (predicted from previous sprint) as lagged velocity ***
                'lagged_velocity': [last_known_velocity],
                # Use averages for other features if their future is unknown/static
                'major_impediment': [avg_impediment],
                'backlog_well_refined_percentage': [avg_refinement]
            })

            # Ensure column order matches training data features
            future_sprint_features = future_sprint_features[self.features]

            # Predict velocity for the current sprint using the prepared features
            predicted_velocity = self.model.predict(future_sprint_features)[0]
            # Ensure prediction is not negative
            predicted_velocity = max(0, predicted_velocity)


            # *** Update variables for the NEXT iteration (NEXT sprint's features) ***
            # The velocity just predicted becomes the 'last_known_velocity' for the next sprint
            last_known_velocity = predicted_velocity

            # Calculate the committed points for the NEXT sprint based on the velocity just predicted + 5%
            committed_points_for_next_sprint = round(predicted_velocity * 1.05)
            # Ensure committed points are non-negative for the next sprint
            committed_points_for_next_sprint = max(0, committed_points_for_next_sprint)
            # Set the calculated points as the committed points for the 'this_sprint' variable for the next loop iteration
            committed_points_for_this_sprint = committed_points_for_next_sprint


            # Append the results for the CURRENT sprint to the list
            future_sprints_list.append({
                'sprint_number': sprint_number,
                'start_date': sprint_start,
                'end_date': sprint_end,
                'team_size': team_size_future,
                'sprint_duration_days': num_working_days,
                'available_person_days': available_person_days_future,
                'forecasted_velocity': predicted_velocity # Store the prediction for this sprint
            })

            # Move to the next sprint start date
            current_start_date = sprint_end + timedelta(days=1)

        self.future_sprints_df = pd.DataFrame(future_sprints_list)


    def prepare_plotting_data(self):
        """Combines historical and forecasted data for plotting."""
        if self.historical_sprints_df is None or self.future_sprints_df is None or self.X_test is None or self.y_test is None or self.model is None:
             raise ValueError("Data or model not ready. Ensure simulation, preparation, training, and forecasting are complete.")

        # Get predictions for the historical test set
        y_pred_test = self.model.predict(self.X_test)


        historical_train_plotting_df = pd.DataFrame({
            'start_date': self.historical_sprints_df['start_date'][:self.split_index].reset_index(drop=True),
            'velocity': self.historical_sprints_df['completed_story_points'][:self.split_index].reset_index(drop=True),
            'type': 'Historical Train Velocity'
        })

        historical_test_actual_plotting_df = pd.DataFrame({
            'start_date': self.historical_sprints_df['start_date'][self.split_index:].reset_index(drop=True),
            'velocity': self.historical_sprints_df['completed_story_points'][self.split_index:].reset_index(drop=True),
            'type': 'Historical Test Actual Velocity'
        })

        historical_test_predicted_plotting_df = pd.DataFrame({
            'start_date': self.historical_sprints_df['start_date'][self.split_index:].reset_index(drop=True),
            'velocity': y_pred_test,
            'type': 'Historical Test Predicted Velocity'
        })

        future_plotting_df = self.future_sprints_df[['start_date', 'forecasted_velocity']].copy()
        future_plotting_df = future_plotting_df.rename(columns={'forecasted_velocity': 'velocity'})
        future_plotting_df['type'] = 'Forecasted Velocity'

        self.plotting_df = pd.concat([historical_train_plotting_df,
                                      historical_test_actual_plotting_df,
                                      historical_test_predicted_plotting_df,
                                      future_plotting_df])

        self.plotting_df = self.plotting_df.sort_values(by='start_date').reset_index(drop=True)

        # Convert start_date to string format for JSON compatibility
        self.plotting_df['start_date'] = self.plotting_df['start_date'].dt.strftime('%Y-%m-%d')


    def to_json(self):
        """Converts the prepared plotting data to a JSON string."""
        if self.plotting_df is None:
             raise ValueError("Plotting data not prepared. Call prepare_plotting_data() first.")

        return self.plotting_df.to_json(orient='records')

# --- Example Usage ---
if __name__ == "__main__":
    forecaster = VelocityForecaster(num_historical_sprints=52, num_sprints_to_forecast=52)

    forecaster.simulate_historical_data()
    forecaster.prepare_data(test_data_percentage=0.2)
    forecaster.train_model()
    mae, y_pred_test = forecaster.evaluate_model() # You can use MAE here if needed
    forecaster.forecast_velocity()
    forecaster.prepare_plotting_data()

    # Get and print the JSON output
    json_output = forecaster.to_json()
    print(json_output)
