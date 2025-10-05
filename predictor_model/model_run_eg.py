import os
import django
import sys

# Step 1: Add your Django project base path
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

# Step 2: Set the DJANGO_SETTINGS_MODULE to your project settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudapp.settings')  

# Step 3: Setup Django - THIS MUST BE BEFORE ANY DJANGO IMPORTS
django.setup()

# Step 4: NOW import Django models and your utilities
from django.contrib.auth.models import User
from medicines.models import Medication
from medicines.utils.feature_extractor import extract_features
from medicines.utils.model_loader import get_adherence_model
import pandas as pd

def predict_user_medication(user, medication):
    """Predict whether user will take or miss a medication"""
    try:
        features = extract_features(user, medication)
        model = get_adherence_model()
        
        if model is None:
            print("Model not loaded")
            return None, 0
            
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        prob = model.predict_proba(df)[0][prediction]
        return prediction, prob
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, 0

# Test the prediction
try:
    user = User.objects.filter(username="acads").first()
    if user:
        med = Medication.objects.filter(user=user).first()
        if med:
            pred, prob = predict_user_medication(user, med)
            if pred is not None:
                if pred == 1:
                    print("Will likely MISS dose (probability:", f"{prob:.2f})")
                else:
                    print("Will likely TAKE dose (probability:", f"{prob:.2f})")
            else:
                print("Could not make prediction")
        else:
            print("No medications found for user")
    else:
        print("User not found")
        
except Exception as e:
    print(f"Error: {e}")