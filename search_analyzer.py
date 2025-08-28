"""
Advanced search and keyword analysis for Alnylam filings
"""
import re
import pandas as pd
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
import config
from data_manager import DataManager

class SearchAnalyzer:
    def __init__(self):
        self.data_manager = DataManager()
        
    def search_filings_content(self, 
                             query: str, 
                             form_types: List[str] = None,
                             case_sensitive: bool = False,
                             whole_words: bool = False) -> List[Dict]:
        """
        Search for content within stored filings
        
        Args:
            query: Search query
            form_types: List of form types to search
            case_sensitive: Whether search should be case sensitive
            whole_words: Whether to match whole words only
        """
        form_types = form_types or config.SUPPORTED_FILING_TYPES
        filings = self.data_manager.parser.get_all_parsed_filings()
        
        # Filter by form types
        filtered_filings = [f for f in filings if f.get('form_type') in form_types]
        
        results = []
        search_text = query if case_sensitive else query.lower()
        
        for filing in filtered_filings:
            content = filing.get('content', '')
            if not content:
                continue
                
            search_content = content if case_sensitive else content.lower()
            
            # Build regex pattern
            if whole_words:
                pattern = r'\b' + re.escape(search_text) + r'\b'
            else:
                pattern = re.escape(search_text)
            
            matches = list(re.finditer(pattern, search_content, re.IGNORECASE if not case_sensitive else 0))
            
            if matches:
                # Extract context around matches
                contexts = []
                for match in matches[:5]:  # Limit to 5 matches per filing
                    start = max(0, match.start() - 200)
                    end = min(len(content), match.end() + 200)
                    context = content[start:end]
                    contexts.append({
                        'position': match.start(),
                        'context': context,
                        'highlight': match.group()
                    })
                
                results.append({
                    'filing_id': filing.get('filing_id', ''),
                    'form_type': filing.get('form_type', ''),
                    'filing_date': filing.get('filing_date', ''),
                    'period_of_report': filing.get('period_of_report', ''),
                    'company_name': filing.get('company_name', ''),
                    'match_count': len(matches),
                    'contexts': contexts
                })
        
        # Sort by match count and filing date
        results.sort(key=lambda x: (x['match_count'], x['filing_date']), reverse=True)
        
        return results
    
    def analyze_biotech_keywords(self) -> Dict:
        """Analyze biotech-specific keywords across all filings"""
        keyword_analysis = self.data_manager.get_biotech_keyword_analysis()
        
        # Enhanced analysis
        enhanced_analysis = {}
        
        for keyword, data in keyword_analysis.items():
            if data['mentions'] > 0:
                # Analyze trends over time
                filing_dates = []
                for filing in data['filings']:
                    if filing.get('filing_date'):
                        filing_dates.append(filing['filing_date'])
                
                # Count mentions by year
                yearly_mentions = defaultdict(int)
                for date in filing_dates:
                    if date:
                        year = date.split('-')[0]
                        yearly_mentions[year] += 1
                
                enhanced_analysis[keyword] = {
                    'total_mentions': data['mentions'],
                    'filings_count': len(data['filings']),
                    'yearly_mentions': dict(yearly_mentions),
                    'average_mentions_per_filing': data['mentions'] / len(data['filings']) if data['filings'] else 0,
                    'contexts': data['contexts'][:5]  # Top 5 contexts
                }
        
        return enhanced_analysis
    
    def search_pipeline_mentions(self) -> List[Dict]:
        """Search for drug pipeline and development mentions"""
        pipeline_keywords = [
            'pipeline', 'clinical trial', 'phase', 'FDA', 'approval', 
            'drug development', 'therapeutic', 'oncology', 'rare disease',
            'RNAi', 'siRNA', 'gene therapy', 'patent', 'intellectual property'
        ]
        
        pipeline_results = []
        
        for keyword in pipeline_keywords:
            results = self.search_filings_content(keyword, whole_words=True)
            pipeline_results.extend(results)
        
        # Remove duplicates and aggregate
        unique_results = {}
        for result in pipeline_results:
            filing_id = result['filing_id']
            if filing_id not in unique_results:
                unique_results[filing_id] = result
            else:
                unique_results[filing_id]['match_count'] += result['match_count']
                unique_results[filing_id]['contexts'].extend(result['contexts'])
        
        return list(unique_results.values())
    
    def search_financial_metrics(self, metric_name: str) -> List[Dict]:
        """Search for specific financial metrics mentions"""
        metric_patterns = {
            'revenue': [r'revenue[s]?', r'net\s+revenue[s]?', r'total\s+revenue[s]?'],
            'net_income': [r'net\s+income', r'net\s+earnings', r'profit'],
            'rd_spending': [r'research\s+and\s+development', r'r\s*&\s*d', r'rd'],
            'cash': [r'cash\s+and\s+cash\s+equivalents', r'cash\s+position', r'liquidity'],
            'debt': [r'debt', r'borrowings', r'liabilities'],
            'assets': [r'total\s+assets', r'assets']
        }
        
        if metric_name not in metric_patterns:
            return []
        
        results = []
        for pattern in metric_patterns[metric_name]:
            search_results = self.search_filings_content(pattern, whole_words=False)
            results.extend(search_results)
        
        return results
    
    def search_risk_factors(self) -> List[Dict]:
        """Search for risk factors and challenges"""
        risk_keywords = [
            'risk', 'challenge', 'uncertainty', 'volatility', 'competition',
            'regulatory', 'clinical', 'safety', 'efficacy', 'market',
            'reimbursement', 'pricing', 'intellectual property', 'litigation'
        ]
        
        risk_results = []
        
        for keyword in risk_keywords:
            results = self.search_filings_content(keyword, whole_words=True)
            risk_results.extend(results)
        
        # Aggregate and rank by risk mentions
        risk_aggregated = defaultdict(list)
        for result in risk_results:
            filing_id = result['filing_id']
            risk_aggregated[filing_id].append(result)
        
        # Create risk score for each filing
        risk_analysis = []
        for filing_id, results in risk_aggregated.items():
            total_risk_mentions = sum(r['match_count'] for r in results)
            risk_analysis.append({
                'filing_id': filing_id,
                'form_type': results[0]['form_type'],
                'filing_date': results[0]['filing_date'],
                'risk_mentions': total_risk_mentions,
                'risk_keywords_found': len(results),
                'risk_score': total_risk_mentions * len(results)  # Simple risk score
            })
        
        # Sort by risk score
        risk_analysis.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return risk_analysis
    
    def search_partnerships(self) -> List[Dict]:
        """Search for partnership and collaboration mentions"""
        partnership_keywords = [
            'collaboration', 'partnership', 'alliance', 'agreement', 'licensing',
            'milestone', 'royalty', 'joint venture', 'strategic', 'commercial'
        ]
        
        partnership_results = []
        
        for keyword in partnership_keywords:
            results = self.search_filings_content(keyword, whole_words=True)
            partnership_results.extend(results)
        
        # Aggregate partnership mentions
        partnership_aggregated = defaultdict(list)
        for result in partnership_results:
            filing_id = result['filing_id']
            partnership_aggregated[filing_id].append(result)
        
        partnership_analysis = []
        for filing_id, results in partnership_aggregated.items():
            total_mentions = sum(r['match_count'] for r in results)
            partnership_analysis.append({
                'filing_id': filing_id,
                'form_type': results[0]['form_type'],
                'filing_date': results[0]['filing_date'],
                'partnership_mentions': total_mentions,
                'partnership_keywords_found': len(results),
                'partnership_score': total_mentions * len(results)
            })
        
        # Sort by partnership score
        partnership_analysis.sort(key=lambda x: x['partnership_score'], reverse=True)
        
        return partnership_analysis
    
    def generate_search_report(self, query: str = None) -> Dict:
        """Generate a comprehensive search analysis report"""
        report = {
            'search_query': query,
            'analysis_date': pd.Timestamp.now().isoformat(),
            'biotech_keywords': self.analyze_biotech_keywords(),
            'pipeline_mentions': self.search_pipeline_mentions(),
            'risk_analysis': self.search_risk_factors(),
            'partnership_analysis': self.search_partnerships()
        }
        
        if query:
            report['search_results'] = self.search_filings_content(query)
        
        return report
    
    def get_keyword_trends(self) -> pd.DataFrame:
        """Get keyword mention trends over time"""
        keyword_analysis = self.analyze_biotech_keywords()
        
        trend_data = []
        for keyword, data in keyword_analysis.items():
            for year, mentions in data['yearly_mentions'].items():
                trend_data.append({
                    'keyword': keyword,
                    'year': int(year),
                    'mentions': mentions
                })
        
        if not trend_data:
            return pd.DataFrame()
        
        trend_df = pd.DataFrame(trend_data)
        return trend_df.sort_values(['keyword', 'year'])
    
    def export_search_results(self, results: List[Dict], filename: str = None) -> str:
        """Export search results to Excel"""
        if not filename:
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            filename = f"search_results_{timestamp}.xlsx"
        
        filepath = os.path.join(config.REPORTS_DIR, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main results
            if results:
                results_df = pd.DataFrame(results)
                results_df.to_excel(writer, sheet_name='Search_Results', index=False)
            
            # Keyword trends
            trends_df = self.get_keyword_trends()
            if not trends_df.empty:
                trends_df.to_excel(writer, sheet_name='Keyword_Trends', index=False)
            
            # Risk analysis
            risk_results = self.search_risk_factors()
            if risk_results:
                risk_df = pd.DataFrame(risk_results)
                risk_df.to_excel(writer, sheet_name='Risk_Analysis', index=False)
        
        return filepath
