#  features of model :  "time_of_day", "dose_complexity", "past_adherence_rate", "lifestyle_routine"
# mapping :-
# lifestyle routine : {"regular": 1 , irregualr:0}
# will_miss_dose : {miss : 1 , take : 0}

import pandas as pd

dummy_data = pd.DataFrame([
    [1, 65, "Morning", 1, 0.90, 1, 0],
    [2, 45, "Evening", 2, 0.70, 0, 1],
    [3, 30, "Afternoon", 1, 0.85, 1, 0],
    [4, 50, "Night", 3, 0.40, 0, 1],
    [5, 72, "Morning", 1, 0.60, 1, 0],
    [6, 60, "Evening", 2, 0.55, 0, 1],
    [7, 25, "Afternoon", 1, 0.95, 1, 0],
    [8, 35, "Night", 3, 0.50, 0, 1],
    [9, 48, "Morning", 2, 0.65, 0, 1],
    [10, 55, "Evening", 1, 0.80, 1, 0],
    [11, 40, "Morning", 2, 0.75, 1, 0],
    [12, 28, "Afternoon", 1, 0.90, 1, 0],
    [13, 62, "Night", 3, 0.35 ,0, 1],
    [14, 38, "Evening", 2, 0.60, 0, 1],
    [15, 50, "Morning", 1, 0.70, 1, 0],
    [16, 47, "Afternoon", 2, 0.55, 0, 1],
    [17, 33, "Evening", 1, 0.85, 1, 0],
    [18, 58, "Night", 3, 0.45, 0, 1],
    [19, 29, "Morning", 1, 0.95, 1, 0],
    [20, 52, "Evening", 2, 0.60, 0, 1]
], columns=[
    "user_id", "age", "time_of_day", "dose_complexity",
    "past_adherence_rate", "lifestyle_routine", "will_miss_dose"
])


data = dummy_data.drop(columns=["user_id" , "age"])
X=data.drop(columns="will_miss_dose")
Y=data["will_miss_dose"]

# one hot encoding for "time_of_day" & "lifestyle_routine"
dummies=pd.get_dummies(X.time_of_day)

X=X.drop(columns="time_of_day")
X=pd.concat([X,dummies], axis='columns')

from sklearn.model_selection import train_test_split
x_train, x_test, y_train , y_test = train_test_split(X, Y, test_size=0.2)

from sklearn.linear_model import LogisticRegression
model=LogisticRegression()

model.fit(x_train, y_train)

# test
print(model.predict(x_test))
print(model.score(x_test, y_test))
print(model.predict_proba(x_test))



# integartion in db (saving the model in file)

import joblib
joblib.dump(model, 'adherence_model.pkl')
print("done")