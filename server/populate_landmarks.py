import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from services.models import Base, Landmark
import sys

# Database configuration
DATABASE_URL = "sqlite:///file_storage.db"  # Change if using another DB
engine = create_engine(DATABASE_URL)

# Create tables in the database
Base.metadata.create_all(engine)

# Function to populate the database from a JSON file
def populate_landmarks(json_file_path):
    with open(json_file_path, "r") as file:
        landmark_json = json.load(file)

    session = Session(bind=engine)

    for landmark in landmark_json:
        existing_landmark = session.query(Landmark).filter_by(landmark_name=landmark["landmark_name"]).first()
        if not existing_landmark:
            new_landmark = Landmark(
                id=landmark["_id"]["$oid"],
                landmark_name=landmark["landmark_name"],
                latitude=landmark["coordinates"][0],
                longitude=landmark["coordinates"][1],
            )
            session.add(new_landmark)

    session.commit()
    session.close()
    print("Landmarks successfully populated!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python populate_landmarks.py <path_to_json_file>")
    else:
        json_file_path = sys.argv[1]
        populate_landmarks(json_file_path)
