## 🏥 Project Overview

Many patients, especially those with chronic conditions, struggle with medication adherence. Forgetting doses or confusing schedules can lead to serious health risks. Existing solutions often lack personalization, proactive reminders, and intuitive user interfaces.

**MediMimes** fills this gap by combining:

- A user‑friendly medication scheduler  
- AI‑powered adherence prediction  
- An interactive health chatbot assistant  

It not only reminds users to take medicines, but also predicts at‑risk schedules and offers personalized nudges and conversational support.

---

## ✅ Features

1. Register / log in (user authentication)  
2. Create medicine schedules (pill name, dosage, time, frequency)  
3. Receive reminders , notifications
4. Log taken vs. missed doses  
5. View dashboard:
   - Upcoming doses  
   - Past logs  
   - Adherence summary  
   - Trends & graphs  
6. Edit or delete schedules  
7. AI‑based **Adherence Prediction** (detect patterns of high risk of missing dose)  
8. AI **Chatbot Health Assistant** (queries related to user )  
9. Integration with **Google Calendar** (automatic sync & updates)

---

## 🧩 Architecture & Process Flow

1. **User Authentication**  
   - User signs up / logs in  
2. **Medication Schedule Setup**  
   - Input pill name, dosage, time, frequency  
   - Stored in backend, synced with Google Calendar  
3. **Dashboard View**  
   - Shows upcoming doses, adherence history, medication schedule
4. **Reminder Notifications**  
   - At scheduled times, sends notification 
   - Buttons: “Taken” / “Missed”  
5. **Logging Dose Status**  
   - **Taken**:
     - Record status in DB  
     - Update calendar event  
     - Refresh dashboard graphs  
   - **Missed**:
     - Record status  
     - Update calendar event  
     - AI model analyzes for pattern  
     - Trigger proactive reminders if risk detected  
6. **AI Modules**  
   - **Adherence Predictor**: spot high‑risk times & trigger extra reminders  
   - **Chatbot Assistant**: natural language queries (health / medication related)  
7. **Visualization Dashboard**  
   - Graphs: adherence rates, missed doses, long‑term trends  
   - Insights into user behavior  
8. **Google Calendar Integration**  
   - Create events for doses  
   - Auto‑update if doses missed/rescheduled  


---

## 🛠️ Tech Stack & External Libraries / APIs

- **Backend / Web Framework**: Django  
- **Authentication**: django-allauth, Google-auth 
- **Database**: SQLite3 (via Django ORM)  
- **Scheduling / Reminders**: APScheduler , Django backgroud tasks 
- **Browser Push Notifications**: pywebpush  
- **Google Calendar / OAuth**: google-api-python-client, google-auth, google-auth-oauthlib  
- **Data Processing / ML**: pandas, numpy, scikit-learn  
- **Chatbot**: langchain  
- **Visualization**: Plotly  
- **Frontend / UI**: Bootstrap  

---

