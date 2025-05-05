from src.data_ingestion.dummy_data_generator import DummyDataGenerator
import os

def main():
    # Create data directory if it doesn't exist
    os.makedirs("data/dummy", exist_ok=True)
    
    # Generate dummy data
    generator = DummyDataGenerator()
    dummy_data = generator.save_dummy_data()
    
    print("Dummy data generated successfully!")
    print(f"Backlog: {len(dummy_data['backlog'])} tasks")
    print(f"Sprint Data: {len(dummy_data['sprint_data'])} sprints")
    print(f"Team Data: {len(dummy_data['team_data'])} developers")

if __name__ == "__main__":
    main() 