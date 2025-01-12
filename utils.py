# utils.py
import base64
from PIL import Image
import io
from datetime import datetime
import os
import json

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string"""
    try:
        if image_file is not None:
            image_bytes = image_file.getvalue()
            encoded = base64.b64encode(image_bytes).decode('utf-8')
            return encoded
    except Exception as e:
        raise Exception(f"Error encoding image: {str(e)}")
    return None

def validate_image(image_file, max_size):
    """Validate uploaded image file"""
    if image_file is None:
        return False, "No file uploaded"
    
    if image_file.size > max_size:
        return False, f"File size exceeds {max_size/1024/1024}MB limit"
    
    try:
        img = Image.open(image_file)
        img.verify()
        return True, "Image is valid"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def save_analysis_history(image_name, image_base64, analysis):
    """Save analysis and image to history"""
    history_file = "analysis_history.json"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create history entry
    entry = {
        "timestamp": timestamp,
        "image_name": image_name,
        "image_data": image_base64,
        "analysis": analysis
    }
    
    # Load existing history
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []
    
    # Add new entry
    history.append(entry)
    
    # Save updated history
    with open(history_file, 'w') as f:
        json.dump(history, f)

def load_analysis_history():
    """Load analysis history"""
    history_file = "analysis_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def get_analysis_by_image_name(image_name):
    """Get analysis for a specific image"""
    history = load_analysis_history()
    for entry in history:
        if entry["image_name"] == image_name:
            return entry
    return None

def delete_analysis_history(image_name):
    """Delete a specific analysis from history"""
    history_file = "analysis_history.json"
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
            
            # Filter out the entry to delete
            new_history = [entry for entry in history if entry["image_name"] != image_name]
            
            # Save updated history
            with open(history_file, 'w') as f:
                json.dump(new_history, f)
            
            return True, "Analysis deleted successfully"
        except Exception as e:
            return False, f"Error deleting analysis: {str(e)}"
    return False, "History file not found"

def clear_analysis_history():
    """Clear all analysis history"""
    history_file = "analysis_history.json"
    try:
        # Create empty history file
        with open(history_file, 'w') as f:
            json.dump([], f)
        return True, "History cleared successfully"
    except Exception as e:
        return False, f"Error clearing history: {str(e)}"