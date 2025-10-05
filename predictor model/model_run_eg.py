import os
import django
import sys

# Step 1: Add your Django project base path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Step 2: Set the DJANGO_SETTINGS_MODULE to your project settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudapp.settings')  

# Step 3: Setup Django
django.setup()

# Now you can import models and utils
from medicines.utils.model_loader import get_adherence_model




# from medicines.utils.model_loader import get_adherence_model
# import pandas as pd

# def predict_adherence(features_dict):
#     model = get_adherence_model()
#     df = pd.DataFrame([features_dict])  # model expects a DataFrame
#     prediction = model.predict(df)[0]
#     probability = model.predict_proba(df)[0][prediction]
#     return prediction, probability


# features = {
#     'dose_complexity': 1,
#     'past_adherence_rate': 0.9,
#     'lifestyle_routine': 1,
#     'time_of_day_Afternoon': 0,
#     'time_of_day_Evening': 0,
#     'time_of_day_Morning': 1,
#     'time_of_day_Night': 0,
# }

# prediction, prob = predict_adherence(features)
# print("Will miss:", bool(prediction), "Probability:", prob)

from medicines.utils.feature_extractor import extract_features
from medicines.utils.model_loader import get_adherence_model
import pandas as pd

def predict_user_medication(user, medication):
    features = extract_features(user, medication)
    model = get_adherence_model()
    df = pd.DataFrame([features])
    prediction = model.predict(df)[0]
    prob = model.predict_proba(df)[0][prediction]
    return prediction, prob

pred, prob = predict_user_medication(request.user, med)
if pred == 1:
    print("Will likely MISS dose (probability:", prob, ")")
else:
    print("Will likely TAKE dose (probability:", prob, ")")
