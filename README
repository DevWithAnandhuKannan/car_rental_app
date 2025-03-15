# 🚗 Online Car Rental Project

This project is an online car rental system built with Django for the main application and Flask for a car damage segmentation and detection model. The system allows users to rent vehicles, manage bookings, review vehicles or spare parts, and includes an admin interface. Additionally, it integrates a machine learning model for detecting and segmenting car damage.

## 📂 Folder Structure Overview
```
/Users/anandhu/Desktop/carrental/
├── .gitignore
├── env/ (ignored)
├── onlinecarrental/
│   ├── app/ (Django app logic)
│   ├── media/ (Uploaded files: vehicles, spare parts, etc.)
│   ├── model/ (Flask app for car damage detection)
│   ├── onlinecarrental/ (Django settings and main project files)
│   ├── static/ (CSS, JS, images)
│   ├── template/ (HTML templates)
│   ├── manage.py (Django management script)
├── requirements.txt (Dependencies)
```

## 🚀 How to Run the Project

### 1️⃣ Setting up the Django Application
#### Create and Activate Virtual Environment
```bash
cd /Users/anandhu/Desktop/carrental/
python3 -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate    # On Windows
```
#### Install Dependencies
```bash
pip install -r requirements.txt
```
#### Run Django Server
```bash
cd onlinecarrental
python manage.py migrate
python manage.py runserver
```
By default, the Django app will be available at **http://127.0.0.1:8000/**.

### 2️⃣ Setting up the Flask Model (Car Damage Segmentation and Detection)
#### Open a New Terminal and Navigate to the Model Folder
```bash
cd /Users/anandhu/Desktop/carrental/onlinecarrental/model
```
#### Create and Activate Virtual Environment for Flask
```bash
python3 -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate    # On Windows
```
#### Install Dependencies
```bash
pip install -r requirements.txt
```
Ensure `requirements.txt` includes **Flask** and necessary ML dependencies (e.g., TensorFlow, PyTorch, Detectron2).

#### Run the Flask Server
```bash
python app.py  # Or, if rundev.py is the entry point:
python rundev.py
```
By default, the Flask app will be available at **http://127.0.0.1:5000/**.

## 🛠 Features
- **Django App**: Vehicle rentals, bookings, reviews, spare parts management.
- **Flask Model**: Upload images of damaged cars for segmentation and detection.
- **Admin Interface**: Manage users, vehicles, and bookings.

## 🔧 Troubleshooting
- **Django Errors**: Check `settings.py` for database configurations.
- **Flask Errors**: Ensure ML model files (e.g., `model_final.pth`) are present.
- **Port Conflicts**: Change ports in `app.py` or `manage.py` if needed.

## 🤝 Contributing
- Add new features via pull requests.
- Update `requirements.txt` when adding dependencies.

Happy coding! 🎉