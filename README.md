# 🛡️ PhishShield AI

PhishShield AI is an advanced, machine-learning-powered phishing detection system designed to analyze URLs and determine if they are legitimate or malicious. It extracts various features from a given URL (such as entropy, suspicious keywords, domain properties, etc.) and uses a trained **Random Forest** model to predict the risk level in real-time.

## ✨ Features

- **Real-Time URL Scanning**: Instantly analyze any URL for phishing threats.
- **Machine Learning Powered**: Uses a Random Forest Classifier trained on thousands of data points for high accuracy.
- **Detailed Feature Analysis**: Breaks down the specific characteristics of a URL that flagged it as dangerous or safe (e.g., URL length, suspicious TLDs, entropy).
- **Beautiful Interactive UI**: A stunning, modern frontend with particle animations, smooth scrolling, and dynamic statistics rendering.
- **Model Comparison**: See how Random Forest compares against Decision Tree, Naive Bayes, and Logistic Regression algorithms on the dataset.

---

## 🛠️ Tech Stack

- **Backend**: Python, Django, Django REST Framework
- **Machine Learning**: Scikit-Learn, Pandas, NumPy, Joblib
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+), Lucide Icons
- **Database**: SQLite (default for Django)

---

## 🚀 How to Setup on a New Laptop

Follow these steps carefully to get the project running on a new machine.

### Prerequisites
1. **Python 3.8+**: Ensure Python is installed. You can download it from [python.org](https://www.python.org/downloads/).
2. **Git**: Ensure Git is installed for version control. Download from [git-scm.com](https://git-scm.com/).

### 1. Clone the Repository
Open your terminal (or Command Prompt / PowerShell) and run:
```bash
git clone https://github.com/nitishChangti/phising.git
cd phising
```

### 2. Setup the Backend (Django + Machine Learning)

We recommend using a virtual environment to keep dependencies organized.

**Windows:**
```powershell
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate

# Install all required Python packages
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install all required Python packages
pip install -r requirements.txt
```

### 3. Initialize the Database
Navigate to the `backend` folder and run the Django database migrations:
```bash
cd backend
python manage.py migrate
```

### 4. Train the Machine Learning Model
Before the API can predict URLs, you **must train the model**. We have provided a script that generates a realistic dataset, trains multiple models, and saves the best one (Random Forest).

Ensure you are still in the `backend` folder, then run:
```bash
python ml/train_model.py
```
*Wait for the script to finish. It will print the accuracy and save `model.pkl`, `scaler.pkl`, and `metrics.json` inside the `backend/ml/` directory.*

### 5. Start the Backend Server
Start the Django API server:
```bash
python manage.py runserver
```
The backend API is now running at `http://127.0.0.1:8000/`. Keep this terminal window open.

### 6. Start the Frontend
The frontend is pure HTML/CSS/JS and does not require a build step (like Node.js or React). 

Simply open the `frontend/index.html` file in your favorite web browser (Chrome, Edge, Firefox, etc.).
- **Option 1**: Double-click `index.html` in your file explorer.
- **Option 2**: Use a VS Code extension like "Live Server" for auto-reloading.

You can now use the UI to paste URLs and scan them for phishing threats!

---

## 📁 Project Structure

```text
phising/
│
├── backend/                  # Django API & Machine Learning
│   ├── api/                  # API Views, URLs, and Feature Extraction logic
│   ├── ml/                   # Model training scripts and saved models (.pkl)
│   ├── phishshield/          # Django core settings
│   ├── manage.py             # Django entry point
│   └── data/                 # Contains the dataset.csv used for training
│
├── frontend/                 # User Interface
│   ├── css/                  # Styling (style.css)
│   ├── js/                   # Frontend logic, animations, and API calls (app.js)
│   └── index.html            # Main website file
│
├── requirements.txt          # Python dependencies
├── .gitignore                # Ignored files for Git
└── README.md                 # Project Documentation
```

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/nitishChangti/phising/issues).
