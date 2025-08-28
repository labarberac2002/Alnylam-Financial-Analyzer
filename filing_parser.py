"""
Filing parser for extracting and processing SEC filing data
"""
import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import pandas as pd
import config

class FilingParser:
    def __init__(self):
        self.financial_patterns = {
            'revenue': [
                r'total\s+revenue[s]?\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?',
                r'net\s+revenue[s]?\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?',
                r'revenue[s]?\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?'
            ],
            'net_income': [
                r'net\s+income\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?',
                r'net\s+earnings\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?'
            ],
            'total_assets': [
                r'total\s+assets\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?'
            ],
            'cash_and_equivalents': [
                r'cash\s+and\s+cash\s+equivalents\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?',
                r'cash\s+and\s+equivalents\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?'
            ],
            'research_development': [
                r'research\s+and\s+development\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?',
                r'r\s*&\s*d\s*\$?([0-9,]+(?:\.[0-9]+)?)\s*(?:million|thousand|billion)?'
            ]
        }
        
    def parse_filing(self, filing_data: Dict) -> Dict:
        """Parse a single filing and extract relevant information"""
        parsed_data = {
            'filing_id': filing_data.get('id', ''),
            'form_type': filing_data.get('formType', ''),
            'filing_date': filing_data.get('filingDate', ''),
            'period_of_report': filing_data.get('periodOfReport', ''),
            'company_name': filing_data.get('companyName', ''),
            'ticker': filing_data.get('ticker', ''),
            'filing_url': filing_data.get('filingUrl', ''),
            'content': '',
            'financial_metrics': {},
            'key_highlights': [],
            'risk_factors': [],
            'business_overview': '',
            'pipeline_info': [],
            'partnerships': [],
            'patents': []
        }
        
        # Extract content if available
        if 'content' in filing_data:
            parsed_data['content'] = filing_data['content']
            parsed_data.update(self._extract_financial_metrics(filing_data['content']))
            parsed_data.update(self._extract_business_info(filing_data['content']))
        
        return parsed_data
    
    def _extract_financial_metrics(self, content: str) -> Dict:
        """Extract financial metrics from filing content"""
        metrics = {}
        
        for metric_name, patterns in self.financial_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    # Take the first match and convert to number
                    try:
                        value_str = matches[0].replace(',', '')
                        metrics[metric_name] = float(value_str)
                        break
                    except ValueError:
                        continue
        
        return {'financial_metrics': metrics}
    
    def _extract_business_info(self, content: str) -> Dict:
        """Extract business-specific information relevant to biotech"""
        business_info = {
            'key_highlights': [],
            'risk_factors': [],
            'business_overview': '',
            'pipeline_info': [],
            'partnerships': [],
            'patents': []
        }
        
        # Extract pipeline information
        pipeline_patterns = [
            r'clinical\s+trial[s]?\s*[:\-]?\s*([^.]{50,200})',
            r'pipeline\s*[:\-]?\s*([^.]{50,200})',
            r'drug\s+development\s*[:\-]?\s*([^.]{50,200})'
        ]
        
        for pattern in pipeline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            business_info['pipeline_info'].extend(matches[:3])  # Limit to 3 matches
        
        # Extract partnership information
        partnership_patterns = [
            r'collaboration[s]?\s*[:\-]?\s*([^.]{50,200})',
            r'partnership[s]?\s*[:\-]?\s*([^.]{50,200})',
            r'licensing\s*[:\-]?\s*([^.]{50,200})'
        ]
        
        for pattern in partnership_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            business_info['partnerships'].extend(matches[:3])
        
        # Extract patent information
        patent_patterns = [
            r'patent[s]?\s*[:\-]?\s*([^.]{50,200})',
            r'intellectual\s+property\s*[:\-]?\s*([^.]{50,200})'
        ]
        
        for pattern in patent_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            business_info['patents'].extend(matches[:3])
        
        return business_info
    
    def save_parsed_filing(self, parsed_data: Dict, filename: str = None) -> str:
        """Save parsed filing data to JSON file"""
        if not filename:
            filing_id = parsed_data.get('filing_id', 'unknown')
            form_type = parsed_data.get('form_type', 'unknown')
            filing_date = parsed_data.get('filing_date', 'unknown')
            filename = f"{form_type}_{filing_date}_{filing_id}.json"
        
        filepath = os.path.join(config.FILINGS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_parsed_filing(self, filepath: str) -> Dict:
        """Load parsed filing data from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_all_parsed_filings(self) -> List[Dict]:
        """Get all parsed filings from the filings directory"""
        filings = []
        
        for filename in os.listdir(config.FILINGS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(config.FILINGS_DIR, filename)
                try:
                    filing_data = self.load_parsed_filing(filepath)
                    filings.append(filing_data)
                except Exception as e:
                    print(f"Error loading filing {filename}: {e}")
        
        return filings
    
    def create_filings_summary(self) -> pd.DataFrame:
        """Create a summary DataFrame of all parsed filings"""
        filings = self.get_all_parsed_filings()
        
        if not filings:
            return pd.DataFrame()
        
        summary_data = []
        for filing in filings:
            summary_data.append({
                'filing_id': filing.get('filing_id', ''),
                'form_type': filing.get('form_type', ''),
                'filing_date': filing.get('filing_date', ''),
                'period_of_report': filing.get('period_of_report', ''),
                'company_name': filing.get('company_name', ''),
                'ticker': filing.get('ticker', ''),
                'revenue': filing.get('financial_metrics', {}).get('revenue'),
                'net_income': filing.get('financial_metrics', {}).get('net_income'),
                'total_assets': filing.get('financial_metrics', {}).get('total_assets'),
                'cash_and_equivalents': filing.get('financial_metrics', {}).get('cash_and_equivalents'),
                'research_development': filing.get('financial_metrics', {}).get('research_development')
            })
        
        return pd.DataFrame(summary_data)
