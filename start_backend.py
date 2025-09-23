import uvicorn
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'policy_extractor'))

if __name__ == "__main__":
    # Change to the policy extractor directory
    os.chdir(os.path.join(os.path.dirname(__file__), 'backend', 'policy_extractor'))
    
    # Import the app
    from main import app
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8002)