"""
Data management system for storing and organizing Alnylam filings
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import config
from sec_api_client import SECAPIClient
from filing_parser import FilingParser

class DataManager:
    def __init__(self):
        self.sec_client = SECAPIClient()
        self.parser = FilingParser()
        self.filings_cache = {}
        
    def fetch_and_store_filings(self, 
                               form_types: List[str] = None,
                               years_back: int = 5,
                               force_refresh: bool = False) -> List[Dict]:
        """
        Fetch filings from SEC-API and store them locally
        
        Args:
            form_types: List of form types to fetch
            years_back: Number of years to look back
            force_refresh: Whether to re-fetch existing filings
        """
        form_types = form_types or config.SUPPORTED_FILING_TYPES
        
        print(f"Fetching {form_types} filings for the last {years_back} years...")
        
        # Calculate date range
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - pd.DateOffset(years=years_back)).strftime('%Y-%m-%d')
        
        # Fetch filings from SEC-API
        filings = self.sec_client.get_company_filings(
            form_types=form_types,
            start_date=start_date,
            end_date=end_date,
            limit=200  # Increased limit for comprehensive data
        )
        
        if not filings:
            print("No filings found or error occurred")
            return []
        
        print(f"Found {len(filings)} filings")
        
        # Process and store each filing
        stored_filings = []
        for i, filing in enumerate(filings):
            filing_id = filing.get('id', f'filing_{i}')
            
            # Check if already stored (unless force refresh)
            if not force_refresh and self._is_filing_stored(filing_id):
                print(f"Filing {filing_id} already stored, skipping...")
                continue
            
            try:
                # Get full content if not already present
                if 'content' not in filing and filing.get('filingUrl'):
                    print(f"Fetching content for {filing_id}...")
                    filing['content'] = self.sec_client.get_filing_content(filing['filingUrl'])
                
                # Parse the filing
                parsed_filing = self.parser.parse_filing(filing)
                
                # Store the parsed filing
                filepath = self.parser.save_parsed_filing(parsed_filing)
                stored_filings.append(parsed_filing)
                
                print(f"Stored filing: {parsed_filing.get('form_type', 'Unknown')} - {parsed_filing.get('filing_date', 'Unknown date')}")
                
            except Exception as e:
                print(f"Error processing filing {filing_id}: {e}")
                continue
        
        print(f"Successfully stored {len(stored_filings)} filings")
        return stored_filings
    
    def _is_filing_stored(self, filing_id: str) -> bool:
        """Check if a filing is already stored locally"""
        for filename in os.listdir(config.FILINGS_DIR):
            if filing_id in filename:
                return True
        return False
    
    def get_filings_by_type(self, form_type: str) -> List[Dict]:
        """Get all filings of a specific type"""
        filings = self.parser.get_all_parsed_filings()
        return [f for f in filings if f.get('form_type') == form_type]
    
    def get_filings_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get filings within a specific date range"""
        filings = self.parser.get_all_parsed_filings()
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered_filings = []
        for filing in filings:
            filing_date = filing.get('filing_date', '')
            if filing_date:
                try:
                    filing_dt = datetime.strptime(filing_date, '%Y-%m-%d')
                    if start_dt <= filing_dt <= end_dt:
                        filtered_filings.append(filing)
                except ValueError:
                    continue
        
        return filtered_filings
    
    def get_financial_timeline(self) -> pd.DataFrame:
        """Get financial metrics over time"""
        summary_df = self.parser.create_filings_summary()
        
        if summary_df.empty:
            return pd.DataFrame()
        
        # Convert date columns
        summary_df['filing_date'] = pd.to_datetime(summary_df['filing_date'], errors='coerce')
        summary_df['period_of_report'] = pd.to_datetime(summary_df['period_of_report'], errors='coerce')
        
        # Sort by filing date
        summary_df = summary_df.sort_values('filing_date')
        
        return summary_df
    
    def search_filings(self, query: str, form_types: List[str] = None) -> List[Dict]:
        """Search for specific content in filings"""
        form_types = form_types or config.SUPPORTED_FILING_TYPES
        
        # Use SEC-API search
        search_results = self.sec_client.search_filings(
            query=query,
            form_types=form_types
        )
        
        return search_results
    
    def get_biotech_keyword_analysis(self) -> Dict:
        """Analyze filings for biotech-specific keywords"""
        filings = self.parser.get_all_parsed_filings()
        keyword_analysis = {}
        
        for keyword in config.BIOTECH_KEYWORDS:
            keyword_analysis[keyword] = {
                'mentions': 0,
                'filings': [],
                'contexts': []
            }
        
        for filing in filings:
            content = filing.get('content', '').lower()
            filing_info = {
                'filing_id': filing.get('filing_id', ''),
                'form_type': filing.get('form_type', ''),
                'filing_date': filing.get('filing_date', '')
            }
            
            for keyword in config.BIOTECH_KEYWORDS:
                if keyword.lower() in content:
                    keyword_analysis[keyword]['mentions'] += 1
                    keyword_analysis[keyword]['filings'].append(filing_info)
                    
                    # Extract context around keyword
                    keyword_pos = content.find(keyword.lower())
                    if keyword_pos != -1:
                        start = max(0, keyword_pos - 100)
                        end = min(len(content), keyword_pos + 100)
                        context = content[start:end]
                        keyword_analysis[keyword]['contexts'].append(context)
        
        return keyword_analysis
    
    def export_to_excel(self, filename: str = None) -> str:
        """Export all data to Excel file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alnylam_analysis_{timestamp}.xlsx"
        
        filepath = os.path.join(config.REPORTS_DIR, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Financial timeline
            financial_df = self.get_financial_timeline()
            if not financial_df.empty:
                financial_df.to_excel(writer, sheet_name='Financial_Timeline', index=False)
            
            # Filings summary
            summary_df = self.parser.create_filings_summary()
            if not summary_df.empty:
                summary_df.to_excel(writer, sheet_name='Filings_Summary', index=False)
            
            # Keyword analysis
            keyword_analysis = self.get_biotech_keyword_analysis()
            keyword_data = []
            for keyword, data in keyword_analysis.items():
                keyword_data.append({
                    'keyword': keyword,
                    'mentions': data['mentions'],
                    'filings_count': len(data['filings'])
                })
            
            if keyword_data:
                keyword_df = pd.DataFrame(keyword_data)
                keyword_df.to_excel(writer, sheet_name='Keyword_Analysis', index=False)
        
        return filepath
    
    def get_data_summary(self) -> Dict:
        """Get a summary of all stored data"""
        filings = self.parser.get_all_parsed_filings()
        
        summary = {
            'total_filings': len(filings),
            'filing_types': {},
            'date_range': {},
            'financial_metrics_available': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        if filings:
            # Filing types breakdown
            for filing in filings:
                form_type = filing.get('form_type', 'Unknown')
                summary['filing_types'][form_type] = summary['filing_types'].get(form_type, 0) + 1
            
            # Date range
            filing_dates = [f.get('filing_date') for f in filings if f.get('filing_date')]
            if filing_dates:
                summary['date_range'] = {
                    'earliest': min(filing_dates),
                    'latest': max(filing_dates)
                }
            
            # Financial metrics availability
            for filing in filings:
                if filing.get('financial_metrics'):
                    summary['financial_metrics_available'] += 1
        
        return summary
