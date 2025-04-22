from flask import Blueprint, jsonify, request, Response
from config import SessionLocal
from services.models import FileStorage, Landmark
from datetime import datetime as dt
import mimetypes
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

admin_bp = Blueprint('admin_routes', __name__)

@admin_bp.route('/update_file', methods=['POST'])
def update_file():
    """API to upload a new file version for a landmark."""
    db = SessionLocal()
    file = request.files.get('file')
    landmark = request.form.get('landmark')
    if not file or not landmark:
        return jsonify({"error": "No file or landmark provided"}), 400
    filename = file.filename
    content = file.read()
    file_type = 'image' if filename.endswith('.png') else 'text'
    try:
        new_file = FileStorage(
            filename=filename,
            file_type=file_type,
            content=content,
            timestamp=dt.utcnow(),
            landmark=landmark
        )
        db.add(new_file)
        db.commit()
        return jsonify({"status": "File updated successfully"}), 200
    except Exception as e:
        db.rollback()
        print("Error saving file to database:", e)
        return jsonify({"error": "Failed to save file"}), 500
    finally:
        db.close()

@admin_bp.route('/get_landmarks', methods=['GET'])
def get_landmarks():
    """API to get all landmark names."""
    db = SessionLocal()
    try:
        landmarks = db.query(Landmark).all()
        names = [lm.landmark_name for lm in landmarks]
        return jsonify({"landmarks": names}), 200
    except Exception as e:
        db.rollback()
        print("Error retrieving landmarks:", e)
        return jsonify({"error": "Failed to retrieve landmarks"}), 500
    finally:
        db.close()

# RESTful endpoints for landmarks
@admin_bp.route('/landmarks', methods=['GET', 'POST'])
def handle_landmarks():
    db = SessionLocal()
    if request.method == 'GET':
        try:
            q = request.args.get('q')
            if q:
                records = db.query(Landmark).filter(
                    (Landmark.id.ilike(f"%{q}%")) | (Landmark.landmark_name.ilike(f"%{q}%"))
                ).all()
            else:
                records = db.query(Landmark).all()
            result = [
                {"id": lm.id, "landmark_name": lm.landmark_name,
                 "latitude": lm.latitude, "longitude": lm.longitude}
                for lm in records
            ]
            return jsonify(result), 200
        except Exception as e:
            db.rollback()
            print("Error retrieving landmarks:", e)
            return jsonify({"error": "Failed to retrieve landmarks"}), 500
        finally:
            db.close()
    elif request.method == 'POST':
        data = request.get_json() or request.form.to_dict()
        if not data or not all(k in data for k in ["id", "landmark_name", "latitude", "longitude"]):
            return jsonify({"error": "Missing required fields"}), 400
        try:
            lat_val = float(data["latitude"])
            lon_val = float(data["longitude"])
        except ValueError:
            return jsonify({"error": "Latitude and Longitude must be numbers"}), 400
        new_landmark = Landmark(
            id=data["id"], 
            landmark_name=data["landmark_name"],
            latitude=lat_val, longitude=lon_val
        )
        try:
            db.add(new_landmark)
            db.commit()
            return jsonify({"message": "Landmark created successfully"}), 201
        except IntegrityError:
            db.rollback()
            return jsonify({"error": "Landmark with given ID or name already exists"}), 400
        except Exception as e:
            db.rollback()
            print("Error adding landmark:", e)
            return jsonify({"error": "Failed to add landmark"}), 500
        finally:
            db.close()

@admin_bp.route('/landmarks/<string:landmark_id>', methods=['PUT', 'DELETE'])
def handle_landmark_by_id(landmark_id):
    db = SessionLocal()
    landmark = db.query(Landmark).get(landmark_id)
    if not landmark:
        db.close()
        return jsonify({"error": "Landmark not found"}), 404
    if request.method == 'PUT':
        data = request.get_json() or request.form.to_dict()
        if "landmark_name" in data:
            landmark.landmark_name = data["landmark_name"]
        if "latitude" in data:
            try:
                landmark.latitude = float(data["latitude"])
            except ValueError:
                db.rollback()
                db.close()
                return jsonify({"error": "Latitude must be a number"}), 400
        if "longitude" in data:
            try:
                landmark.longitude = float(data["longitude"])
            except ValueError:
                db.rollback()
                db.close()
                return jsonify({"error": "Longitude must be a number"}), 400
        try:
            db.commit()
            return jsonify({"message": "Landmark updated successfully"}), 200
        except IntegrityError:
            db.rollback()
            db.close()
            return jsonify({"error": "Landmark name already exists"}), 400
        except Exception as e:
            db.rollback()
            print("Error updating landmark:", e)
            db.close()
            return jsonify({"error": "Failed to update landmark"}), 500
    elif request.method == 'DELETE':
        try:
            db.delete(landmark)
            db.commit()
            return jsonify({"message": "Landmark deleted successfully"}), 200
        except Exception as e:
            db.rollback()
            print("Error deleting landmark:", e)
            return jsonify({"error": "Failed to delete landmark"}), 500
        finally:
            db.close()

# RESTful endpoints for file storage
@admin_bp.route('/file_storage', methods=['GET', 'POST'])
def handle_files():
    db = SessionLocal()
    if request.method == 'GET':
        try:
            q = request.args.get('q')
            if q:
                records = db.query(FileStorage).filter(
                    (FileStorage.filename.ilike(f"%{q}%")) | (FileStorage.landmark.ilike(f"%{q}%"))
                ).all()
            else:
                records = db.query(FileStorage).all()
            result = [
                {"id": f.id, "filename": f.filename, "file_type": f.file_type,
                 "timestamp": f.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "landmark": f.landmark}
                for f in records
            ]
            return jsonify(result), 200
        except Exception as e:
            db.rollback()
            print("Error retrieving files:", e)
            return jsonify({"error": "Failed to retrieve files"}), 500
        finally:
            db.close()
    elif request.method == 'POST':
        file = request.files.get('file')
        landmark_name = request.form.get('landmark')
        if not file or not landmark_name:
            return jsonify({"error": "File and landmark are required"}), 400
        filename = file.filename
        content = file.read()
        file_type = 'image' if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'text'
        new_file = FileStorage(filename=filename, file_type=file_type,
                               content=content, timestamp=dt.utcnow(), landmark=landmark_name)
        try:
            db.add(new_file)
            db.commit()
            return jsonify({"message": "File record created successfully", "id": new_file.id}), 201
        except Exception as e:
            db.rollback()
            print("Error saving file:", e)
            return jsonify({"error": "Failed to save file"}), 500
        finally:
            db.close()

@admin_bp.route('/file_storage/<int:file_id>', methods=['PUT', 'DELETE'])
def handle_file_by_id(file_id):
    db = SessionLocal()
    file_rec = db.query(FileStorage).get(file_id)
    if not file_rec:
        db.close()
        return jsonify({"error": "File record not found"}), 404
    if request.method == 'PUT':
        file = request.files.get('file')
        data = request.form.to_dict()
        if file:
            file_content = file.read()
            new_filename = file.filename
            new_type = 'image' if new_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'text'
            file_rec.content = file_content
            file_rec.filename = new_filename
            file_rec.file_type = new_type
            file_rec.timestamp = dt.utcnow()
        else:
            # Handle updates sent via form data (e.g., from the model file viewer)
            if "content" in data and data["content"]:
                file_rec.content = data["content"].encode('utf-8')
                file_rec.timestamp = dt.utcnow()
        if "filename" in data and data["filename"]:
            file_rec.filename = data["filename"]
            ext = data["filename"].lower().rsplit('.', 1)[-1] if '.' in data["filename"] else ""
            if ext in ("png", "jpg", "jpeg", "gif"):
                file_rec.file_type = 'image'
            elif ext:
                file_rec.file_type = 'text'
        if "landmark" in data and data["landmark"]:
            file_rec.landmark = data["landmark"]
        try:
            db.commit()
            return jsonify({"message": "File record updated successfully"}), 200
        except Exception as e:
            db.rollback()
            print("Error updating file record:", e)
            return jsonify({"error": "Failed to update file record"}), 500
        finally:
            db.close()
    elif request.method == 'DELETE':
        try:
            db.delete(file_rec)
            db.commit()
            return jsonify({"message": "File record deleted successfully"}), 200
        except Exception as e:
            db.rollback()
            print("Error deleting file record:", e)
            return jsonify({"error": "Failed to delete file record"}), 500
        finally:
            db.close()

@admin_bp.route('/file/<int:file_id>', methods=['GET'])
def download_file(file_id):
    """Download the content of a file for viewing/downloading."""
    db = SessionLocal()
    file_rec = db.query(FileStorage).get(file_id)
    if not file_rec:
        db.close()
        return jsonify({"error": "File not found"}), 404
    mime_type, _ = mimetypes.guess_type(file_rec.filename)
    if not mime_type:
        mime_type = 'application/octet-stream' if file_rec.file_type == 'image' else 'text/plain'
    data = file_rec.content
    db.close()
    response = Response(data, mimetype=mime_type)
    response.headers['Content-Disposition'] = f'inline; filename="{file_rec.filename}"'
    return response

# New endpoint for executing arbitrary SQL commands (used by the SQL tab)
@admin_bp.route('/execute_sql', methods=['POST'])
def execute_sql():
    """
    Executes an SQL command sent in the request and returns the result.
    For SELECT queries, returns the fetched rows.
    For non-SELECT queries, commits the transaction and returns a success message.
    """
    db = SessionLocal()
    # Get SQL command from JSON or form data.
    if request.is_json:
        command = request.json.get("command")
    else:
        command = request.form.get("command")
    if not command:
        db.close()
        return jsonify({"error": "No SQL command provided"}), 400
    try:
        # Wrap the command with text() for a textual SQL expression.
        result = db.execute(text(command))
        # If the command is a SELECT query, fetch the results.
        if command.strip().lower().startswith("select"):
            rows = result.fetchall()
            # Convert row objects to lists so they can be JSON-serializable.
            results = [list(row) for row in rows]
            db.close()
            return jsonify({"result": results}), 200
        else:
            db.commit()
            db.close()
            return jsonify({"message": "SQL command executed successfully"}), 200
    except Exception as e:
        db.rollback()
        db.close()
        return jsonify({"error": str(e)}), 500
