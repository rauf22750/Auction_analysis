# Auction Analysis Dashboard Project

This repository contains a Django-based project for creating a auction analysis dashboard. This dashboard is basically used for analysis the data of auction on your selecting auction.

## Features
- Over all summary of auction.
- Top product vs low product.
- Day by day auction and product  wise.
- Top bidders.
- Auto vs manual bids product.
- Auto vs manual bids user.

---

## Requirements
Auction data file are avaiable in your pc other wise on cloud 

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)

### Installation
Ensure you have the required Python version installed on your system. To install the project dependencies, follow the steps below.

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv env
source env/bin/activate  # For Linux/macOS
env\Scripts\activate   # For Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Migrate the Database
```bash
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to set up an admin user.

### 7. Run the Server
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:2222/`


### 8. Acknowledgements
- Django Framework
