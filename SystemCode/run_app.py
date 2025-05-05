import os
import subprocess

def main():
    # Set the working directory to the project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run the Streamlit app
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main() 