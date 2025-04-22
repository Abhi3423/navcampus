🚀 Pathfinding Server
=====================

This project provides a multi-floor pathfinding server using Flask and Dijkstra's algorithm. This README will guide you through initializing the server, configuring the database, and running the API server.

🛠️ Requirements
----------------

*   **Python 3.8+**
*   **PIP** - Ensure Python's package manager is installed

📦 Setup
--------

1.  **Clone the repository**
    
        git clone https://github.com/yourusername/pathfinding-server.git
        cd pathfinding-server
    
2.  **Create and Activate a Virtual Environment** (optional, but recommended)
    
    _On macOS and Linux:_
    
        python3 -m venv env
        source env/bin/activate
    
    _On Windows:_
    
        python -m venv env
        .\env\Scripts\activate
    
3.  **Install Dependencies**
    
        pip install -r requirements.txt
    

🔧 Database Initialization
--------------------------

This project uses SQLite to store floor and path data. Follow these steps to initialize the database:

1.  **Create the Database Schema**
    
        python -c 'from models import Base, engine; Base.metadata.create_all(engine)'
    
    🎉 **Tip:** This command only needs to be run once or when database schemas are modified.
    
2.  **Add Floor and Map Data**
    *   Use the provided Tkinter app to upload or update floor maps and model files.
    *   Files can also be manually added via API to ensure they follow the naming conventions (`model-<floor>.txt` and `mapbase-<floor>.png`).

🌐 Running the Server
---------------------

Once the setup is complete, you can run the Flask server.

1.  **Start the Flask Server**
    
        python app.py
    
2.  **Access the API**
    *   Server runs on `http://127.0.0.1:5000` by default.
    *   **Available Routes:**
        *   `/api/nodes` - Retrieves all nodes grouped by floor.
        *   `/api/path` - Generates paths based on start and end nodes across floors.

🧪 Testing the API
------------------

1.  **Get Floor Nodes**
    
    Test with your browser or any API client like Postman to retrieve nodes:
    
        GET http://127.0.0.1:5000/api/nodes
    
2.  **Generate a Path**
    
    Use the `POST /api/path` route with JSON data specifying `start`, `end`, `start_floor`, and `end_floor` to create paths.
    
    Example:
    
        POST http://127.0.0.1:5000/api/path
        Content-Type: application/json
        
        {
          "start": "TP 111",
          "end": "TP 221",
          "start_floor": "1",
          "end_floor": "2"
        }
    

🏃 Tips
-------

*   **Virtual Environment** - Remember to activate your virtual environment each time you start working on this project.
*   **Database Setup** - Re-run the database initialization command (`python -c ...`) if you modify the `models.py` file.
*   **Testing Changes** - Use a tool like [Postman](https://www.postman.com/) for easy API testing.

Happy pathfinding! 😊
