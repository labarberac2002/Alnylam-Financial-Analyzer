"""
Financial analysis engine for Alnylam Pharmaceuticals
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import config
from data_manager import DataManager

class FinancialAnalyzer:
    def __init__(self):
        self.data_manager = DataManager()
        
    def get_financial_metrics_trends(self) -> Dict:
        """Analyze trends in key financial metrics over time"""
        financial_df = self.data_manager.get_financial_timeline()
        
        if financial_df.empty:
            return {}
        
        trends = {}
        
        # Calculate trends for each metric
        metrics = ['revenue', 'net_income', 'total_assets', 'cash_and_equivalents', 'research_development']
        
        for metric in metrics:
            if metric in financial_df.columns:
                # Remove null values and sort by date
                metric_data = financial_df[['filing_date', metric]].dropna()
                metric_data = metric_data.sort_values('filing_date')
                
                if len(metric_data) > 1:
                    # Calculate growth rates
                    metric_data['growth_rate'] = metric_data[metric].pct_change() * 100
                    metric_data['quarterly_growth'] = metric_data[metric].diff()
                    
                    trends[metric] = {
                        'latest_value': metric_data[metric].iloc[-1],
                        'latest_date': metric_data['filing_date'].iloc[-1].strftime('%Y-%m-%d'),
                        'average_growth_rate': metric_data['growth_rate'].mean(),
                        'latest_growth_rate': metric_data['growth_rate'].iloc[-1],
                        'volatility': metric_data['growth_rate'].std(),
                        'trend_direction': 'increasing' if metric_data['growth_rate'].iloc[-1] > 0 else 'decreasing',
                        'data_points': len(metric_data)
                    }
        
        return trends
    
    def calculate_financial_ratios(self) -> Dict:
        """Calculate key financial ratios"""
        financial_df = self.data_manager.get_financial_timeline()
        
        if financial_df.empty:
            return {}
        
        ratios = {}
        
        # Get latest data point
        latest_data = financial_df.iloc[-1]
        
        # Calculate ratios if data is available
        if pd.notna(latest_data.get('revenue')) and pd.notna(latest_data.get('total_assets')):
            ratios['asset_turnover'] = latest_data['revenue'] / latest_data['total_assets']
        
        if pd.notna(latest_data.get('net_income')) and pd.notna(latest_data.get('revenue')):
            ratios['net_profit_margin'] = latest_data['net_income'] / latest_data['revenue']
        
        if pd.notna(latest_data.get('research_development')) and pd.notna(latest_data.get('revenue')):
            ratios['rd_intensity'] = latest_data['research_development'] / latest_data['revenue']
        
        if pd.notna(latest_data.get('cash_and_equivalents')) and pd.notna(latest_data.get('total_assets')):
            ratios['cash_ratio'] = latest_data['cash_and_equivalents'] / latest_data['total_assets']
        
        return ratios
    
    def analyze_rd_investment(self) -> Dict:
        """Analyze R&D investment patterns"""
        financial_df = self.data_manager.get_financial_timeline()
        
        if financial_df.empty or 'research_development' not in financial_df.columns:
            return {}
        
        rd_data = financial_df[['filing_date', 'research_development', 'revenue']].dropna()
        
        if rd_data.empty:
            return {}
        
        rd_analysis = {
            'total_rd_investment': rd_data['research_development'].sum(),
            'average_quarterly_rd': rd_data['research_development'].mean(),
            'rd_growth_rate': rd_data['research_development'].pct_change().mean() * 100,
            'rd_as_percentage_of_revenue': (rd_data['research_development'] / rd_data['revenue']).mean() * 100,
            'rd_trend': 'increasing' if rd_data['research_development'].iloc[-1] > rd_data['research_development'].iloc[0] else 'decreasing'
        }
        
        return rd_analysis
    
    def analyze_cash_management(self) -> Dict:
        """Analyze cash and liquidity position"""
        financial_df = self.data_manager.get_financial_timeline()
        
        if financial_df.empty or 'cash_and_equivalents' not in financial_df.columns:
            return {}
        
        cash_data = financial_df[['filing_date', 'cash_and_equivalents']].dropna()
        
        if cash_data.empty:
            return {}
        
        cash_analysis = {
            'current_cash': cash_data['cash_and_equivalents'].iloc[-1],
            'cash_trend': 'increasing' if cash_data['cash_and_equivalents'].iloc[-1] > cash_data['cash_and_equivalents'].iloc[0] else 'decreasing',
            'cash_volatility': cash_data['cash_and_equivalents'].std(),
            'average_cash': cash_data['cash_and_equivalents'].mean(),
            'cash_growth_rate': cash_data['cash_and_equivalents'].pct_change().mean() * 100
        }
        
        return cash_analysis
    
    def get_quarterly_performance(self) -> pd.DataFrame:
        """Get quarterly performance metrics"""
        financial_df = self.data_manager.get_financial_timeline()
        
        if financial_df.empty:
            return pd.DataFrame()
        
        # Filter for quarterly reports (10-Q)
        quarterly_df = financial_df[financial_df['form_type'] == '10-Q'].copy()
        
        if quarterly_df.empty:
            return pd.DataFrame()
        
        # Calculate quarterly changes
        quarterly_df = quarterly_df.sort_values('filing_date')
        
        metrics = ['revenue', 'net_income', 'total_assets', 'cash_and_equivalents', 'research_development']
        
        for metric in metrics:
            if metric in quarterly_df.columns:
                quarterly_df[f'{metric}_qoq_change'] = quarterly_df[metric].pct_change() * 100
                quarterly_df[f'{metric}_qoq_absolute'] = quarterly_df[metric].diff()
        
        return quarterly_df
    
    def analyze_annual_performance(self) -> pd.DataFrame:
        """Analyze annual performance from 10-K reports"""
        financial_df = self.data_manager.get_financial_timeline()
        
        if financial_df.empty:
            return pd.DataFrame()
        
        # Filter for annual reports (10-K)
        annual_df = financial_df[financial_df['form_type'] == '10-K'].copy()
        
        if annual_df.empty:
            return pd.DataFrame()
        
        # Calculate year-over-year changes
        annual_df = annual_df.sort_values('filing_date')
        
        metrics = ['revenue', 'net_income', 'total_assets', 'cash_and_equivalents', 'research_development']
        
        for metric in metrics:
            if metric in annual_df.columns:
                annual_df[f'{metric}_yoy_change'] = annual_df[metric].pct_change() * 100
                annual_df[f'{metric}_yoy_absolute'] = annual_df[metric].diff()
        
        return annual_df
    
    def get_financial_health_score(self) -> Dict:
        """Calculate a financial health score for Alnylam"""
        trends = self.get_financial_metrics_trends()
        ratios = self.calculate_financial_ratios()
        rd_analysis = self.analyze_rd_investment()
        cash_analysis = self.analyze_cash_management()
        
        score_components = {}
        total_score = 0
        max_score = 0
        
        # Revenue growth (25 points)
        if 'revenue' in trends:
            revenue_growth = trends['revenue']['latest_growth_rate']
            if revenue_growth > 20:
                score_components['revenue_growth'] = 25
            elif revenue_growth > 10:
                score_components['revenue_growth'] = 20
            elif revenue_growth > 0:
                score_components['revenue_growth'] = 15
            else:
                score_components['revenue_growth'] = 5
        else:
            score_components['revenue_growth'] = 0
        total_score += score_components['revenue_growth']
        max_score += 25
        
        # R&D Investment (20 points)
        if rd_analysis and rd_analysis.get('rd_trend') == 'increasing':
            score_components['rd_investment'] = 20
        elif rd_analysis:
            score_components['rd_investment'] = 15
        else:
            score_components['rd_investment'] = 0
        total_score += score_components['rd_investment']
        max_score += 20
        
        # Cash Position (20 points)
        if cash_analysis:
            if cash_analysis['current_cash'] > 1000:  # Assuming millions
                score_components['cash_position'] = 20
            elif cash_analysis['current_cash'] > 500:
                score_components['cash_position'] = 15
            else:
                score_components['cash_position'] = 10
        else:
            score_components['cash_position'] = 0
        total_score += score_components['cash_position']
        max_score += 20
        
        # Profitability (15 points)
        if 'net_profit_margin' in ratios:
            margin = ratios['net_profit_margin']
            if margin > 0.1:
                score_components['profitability'] = 15
            elif margin > 0:
                score_components['profitability'] = 10
            else:
                score_components['profitability'] = 5
        else:
            score_components['profitability'] = 0
        total_score += score_components['profitability']
        max_score += 15
        
        # Asset Efficiency (10 points)
        if 'asset_turnover' in ratios:
            turnover = ratios['asset_turnover']
            if turnover > 0.5:
                score_components['asset_efficiency'] = 10
            elif turnover > 0.3:
                score_components['asset_efficiency'] = 7
            else:
                score_components['asset_efficiency'] = 5
        else:
            score_components['asset_efficiency'] = 0
        total_score += score_components['asset_efficiency']
        max_score += 10
        
        # R&D Intensity (10 points)
        if rd_analysis and rd_analysis.get('rd_as_percentage_of_revenue', 0) > 20:
            score_components['rd_intensity'] = 10
        elif rd_analysis and rd_analysis.get('rd_as_percentage_of_revenue', 0) > 10:
            score_components['rd_intensity'] = 7
        else:
            score_components['rd_intensity'] = 5
        total_score += score_components['rd_intensity']
        max_score += 10
        
        health_score = {
            'total_score': total_score,
            'max_possible_score': max_score,
            'percentage': (total_score / max_score * 100) if max_score > 0 else 0,
            'grade': self._get_grade(total_score / max_score * 100) if max_score > 0 else 'F',
            'components': score_components,
            'analysis_date': datetime.now().isoformat()
        }
        
        return health_score
    
    def _get_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
    
    def generate_financial_report(self) -> Dict:
        """Generate a comprehensive financial analysis report"""
        report = {
            'company': config.ALNYLAM_COMPANY_NAME,
            'ticker': config.ALNYLAM_TICKER,
            'analysis_date': datetime.now().isoformat(),
            'data_summary': self.data_manager.get_data_summary(),
            'financial_trends': self.get_financial_metrics_trends(),
            'financial_ratios': self.calculate_financial_ratios(),
            'rd_analysis': self.analyze_rd_investment(),
            'cash_analysis': self.analyze_cash_management(),
            'financial_health_score': self.get_financial_health_score(),
            'quarterly_performance': self.get_quarterly_performance().to_dict('records') if not self.get_quarterly_performance().empty else [],
            'annual_performance': self.analyze_annual_performance().to_dict('records') if not self.analyze_annual_performance().empty else []
        }
        
        return report
