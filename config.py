import os

# Root of project: d:\project scratch data\code scratch data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
CHARTS_DIR = os.path.join(REPORTS_DIR, 'charts')
SLIDE_CHARTS_DIR = os.path.join(os.path.dirname(BASE_DIR), 'slide_charts')

# Ensure directories exist
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(SLIDE_CHARTS_DIR, exist_ok=True)
