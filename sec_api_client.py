"""
SEC-API Client for fetching Alnylam Pharmaceuticals filings
"""
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import config

class SECAPIClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.SEC_API_KEY
        self.base_url = config.SEC_API_BASE_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a request to the SEC-API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return {}
    
    def get_company_filings(self, 
                          cik: str = None, 
                          ticker: str = None,
                          form_types: List[str] = None,
                          start_date: str = None,
                          end_date: str = None,
                          limit: int = 100) -> List[Dict]:
        """
        Get company filings from SEC-API
        
        Args:
            cik: Central Index Key (defaults to Alnylam's CIK)
            ticker: Stock ticker symbol
            form_types: List of form types to filter (e.g., ['10-K', '10-Q'])
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            limit: Maximum number of results
        """
        cik = cik or config.ALNYLAM_CIK
        form_types = form_types or config.SUPPORTED_FILING_TYPES
        
        params = {
            'cik': cik,
            'formTypes': ','.join(form_types),
            'limit': limit
        }
        
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if ticker:
            params['ticker'] = ticker
            
        return self._make_request('filings', params)
    
    def get_filing_content(self, filing_url: str) -> str:
        """Get the full content of a specific filing"""
        try:
            response = requests.get(filing_url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching filing content from {filing_url}: {e}")
            return ""
    
    def search_filings(self, 
                      query: str, 
                      cik: str = None,
                      form_types: List[str] = None,
                      start_date: str = None,
                      end_date: str = None) -> List[Dict]:
        """
        Search for specific content within filings
        
        Args:
            query: Search query string
            cik: Central Index Key (defaults to Alnylam's CIK)
            form_types: List of form types to search
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        """
        cik = cik or config.ALNYLAM_CIK
        form_types = form_types or config.SUPPORTED_FILING_TYPES
        
        params = {
            'query': query,
            'cik': cik,
            'formTypes': ','.join(form_types)
        }
        
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
            
        return self._make_request('search', params)
    
    def get_company_info(self, cik: str = None) -> Dict:
        """Get company information"""
        cik = cik or config.ALNYLAM_CIK
        return self._make_request(f'company/{cik}')
    
    def get_recent_filings(self, days: int = 30) -> List[Dict]:
        """Get recent filings from the last N days"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        return self.get_company_filings(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_annual_reports(self, years: int = 5) -> List[Dict]:
        """Get annual reports (10-K) for the last N years"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=years*365)).strftime('%Y-%m-%d')
        
        return self.get_company_filings(
            form_types=['10-K'],
            start_date=start_date,
            end_date=end_date
        )
    
    def get_quarterly_reports(self, quarters: int = 8) -> List[Dict]:
        """Get quarterly reports (10-Q) for the last N quarters"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=quarters*90)).strftime('%Y-%m-%d')
        
        return self.get_company_filings(
            form_types=['10-Q'],
            start_date=start_date,
            end_date=end_date
        )
