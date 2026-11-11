import os
from dotenv import load_dotenv

# Load environment variables from .env before initializing the application
load_dotenv()

from mission_control import create_app

app = create_app(os.getenv("FLASK_CONFIG", "development"))

if __name__ == "__main__":
    app.run()
