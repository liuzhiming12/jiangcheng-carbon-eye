import subprocess
import sys
import os

if __name__ == "__main__":
    print("========================================")
    print("   Starting Jiangcheng Carbon Eye Pro...")
    print("========================================")
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Start Streamlit
    python_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".venv", "Scripts", "python.exe")
    result = subprocess.run([python_path, "-m", "streamlit", "run", "ui/app.py"])
    sys.exit(result.returncode)
