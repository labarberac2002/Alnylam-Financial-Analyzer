"""
Configuration settings for Alnylam Financial Analyzer
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SEC-API Configuration
SEC_API_KEY = os.getenv('SEC_API_KEY')
SEC_API_BASE_URL = 'https://api.sec-api.io'

# Alnylam Pharmaceuticals specific settings
ALNYLAM_CIK = '1178670'  # Alnylam's Central Index Key
ALNYLAM_TICKER = 'ALNY'
ALNYLAM_COMPANY_NAME = 'Alnylam Pharmaceuticals, Inc.'

# Data storage settings
DATA_DIR = 'data'
FILINGS_DIR = os.path.join(DATA_DIR, 'filings')
ANALYSIS_DIR = os.path.join(DATA_DIR, 'analysis')
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')

# Analysis settings
SUPPORTED_FILING_TYPES = ['10-K', '10-Q', '8-K', 'DEF 14A', 'S-1', 'S-3', '424B']
KEY_METRICS = [
    'revenue', 'net_income', 'total_assets', 'total_liabilities', 
    'cash_and_equivalents', 'research_development', 'operating_expenses',
    'gross_profit', 'ebitda', 'debt', 'equity'
]

# Search keywords for biotech analysis
BIOTECH_KEYWORDS = [
    'pipeline', 'clinical trial', 'FDA approval', 'drug development',
    'therapeutic', 'oncology', 'rare disease', 'gene therapy',
    'RNAi', 'siRNA', 'patent', 'intellectual property',
    'collaboration', 'partnership', 'licensing', 'milestone'
]

# Create directories if they don't exist
for directory in [DATA_DIR, FILINGS_DIR, ANALYSIS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)
