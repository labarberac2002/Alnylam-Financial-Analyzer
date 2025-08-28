"""
Main application entry point for Alnylam Financial Analyzer
"""
import os
import sys
from datetime import datetime
import config
from data_manager import DataManager
from financial_analyzer import FinancialAnalyzer
from search_analyzer import SearchAnalyzer

def check_api_key():
    """Check if SEC-API key is configured"""
    if not config.SEC_API_KEY or config.SEC_API_KEY == 'your_sec_api_key_here':
        print("❌ SEC-API key not configured!")
        print("Please:")
        print("1. Copy 'env_example.txt' to '.env'")
        print("2. Add your SEC-API key to the .env file")
        print("3. Get your API key from https://sec-api.io/")
        return False
    return True

def main_menu():
    """Display main menu and handle user choices"""
    while True:
        print("\n" + "="*60)
        print("🧬 ALNYLAM PHARMACEUTICALS FINANCIAL ANALYZER")
        print("="*60)
        print("1. 📥 Fetch and Store SEC Filings")
        print("2. 📊 Generate Financial Analysis Report")
        print("3. 🔍 Search Filings Content")
        print("4. 📈 View Financial Trends")
        print("5. 🏥 Check Financial Health Score")
        print("6. 🔬 Analyze R&D Investment")
        print("7. 💰 Analyze Cash Management")
        print("8. 📋 View Data Summary")
        print("9. 📤 Export Data to Excel")
        print("10. 🌐 Launch Web Dashboard")
        print("0. Exit")
        print("="*60)
        
        choice = input("Enter your choice (0-10): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            fetch_filings()
        elif choice == '2':
            generate_report()
        elif choice == '3':
            search_filings()
        elif choice == '4':
            view_trends()
        elif choice == '5':
            check_health_score()
        elif choice == '6':
            analyze_rd()
        elif choice == '7':
            analyze_cash()
        elif choice == '8':
            view_data_summary()
        elif choice == '9':
            export_data()
        elif choice == '10':
            launch_dashboard()
        else:
            print("❌ Invalid choice. Please try again.")

def fetch_filings():
    """Fetch and store SEC filings"""
    print("\n📥 FETCHING SEC FILINGS")
    print("-" * 30)
    
    if not check_api_key():
        return
    
    data_manager = DataManager()
    
    # Get user preferences
    print("Select filing types to fetch:")
    for i, form_type in enumerate(config.SUPPORTED_FILING_TYPES, 1):
        print(f"{i}. {form_type}")
    
    try:
        choice = input("Enter numbers (comma-separated) or 'all' for all types: ").strip()
        
        if choice.lower() == 'all':
            form_types = config.SUPPORTED_FILING_TYPES
        else:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            form_types = [config.SUPPORTED_FILING_TYPES[i] for i in indices if 0 <= i < len(config.SUPPORTED_FILING_TYPES)]
        
        years = int(input("How many years back to fetch? (default: 5): ") or "5")
        
        print(f"\nFetching {form_types} filings for the last {years} years...")
        
        filings = data_manager.fetch_and_store_filings(
            form_types=form_types,
            years_back=years,
            force_refresh=False
        )
        
        print(f"✅ Successfully processed {len(filings)} filings")
        
    except Exception as e:
        print(f"❌ Error fetching filings: {e}")

def generate_report():
    """Generate comprehensive financial analysis report"""
    print("\n📊 GENERATING FINANCIAL ANALYSIS REPORT")
    print("-" * 40)
    
    analyzer = FinancialAnalyzer()
    
    try:
        report = analyzer.generate_financial_report()
        
        print(f"Company: {report['company']}")
        print(f"Ticker: {report['ticker']}")
        print(f"Analysis Date: {report['analysis_date']}")
        
        # Financial Health Score
        health_score = report['financial_health_score']
        print(f"\n🏥 Financial Health Score: {health_score['percentage']:.1f}% (Grade: {health_score['grade']})")
        
        # Key trends
        trends = report['financial_trends']
        if trends:
            print("\n📈 Key Financial Trends:")
            for metric, data in trends.items():
                print(f"  {metric.replace('_', ' ').title()}: {data['latest_growth_rate']:.1f}% growth")
        
        # R&D Analysis
        rd_analysis = report['rd_analysis']
        if rd_analysis:
            print(f"\n🔬 R&D Analysis:")
            print(f"  Total R&D Investment: ${rd_analysis.get('total_rd_investment', 0):,.0f}M")
            print(f"  R&D as % of Revenue: {rd_analysis.get('rd_as_percentage_of_revenue', 0):.1f}%")
        
        # Cash Analysis
        cash_analysis = report['cash_analysis']
        if cash_analysis:
            print(f"\n💰 Cash Analysis:")
            print(f"  Current Cash Position: ${cash_analysis.get('current_cash', 0):,.0f}M")
            print(f"  Cash Trend: {cash_analysis.get('cash_trend', 'Unknown')}")
        
        print("\n✅ Report generated successfully!")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")

def search_filings():
    """Search filings content"""
    print("\n🔍 SEARCH FILINGS CONTENT")
    print("-" * 30)
    
    search_analyzer = SearchAnalyzer()
    
    query = input("Enter search query: ").strip()
    if not query:
        print("❌ Please enter a search query")
        return
    
    try:
        results = search_analyzer.search_filings_content(query)
        
        if results:
            print(f"\n✅ Found {len(results)} results:")
            for i, result in enumerate(results[:10], 1):  # Show first 10
                print(f"\n{i}. {result['form_type']} - {result['filing_date']}")
                print(f"   Matches: {result['match_count']}")
                print(f"   Company: {result['company_name']}")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Error searching filings: {e}")

def view_trends():
    """View financial trends"""
    print("\n📈 FINANCIAL TRENDS")
    print("-" * 20)
    
    analyzer = FinancialAnalyzer()
    
    try:
        trends = analyzer.get_financial_metrics_trends()
        
        if trends:
            print("Key Financial Trends:")
            for metric, data in trends.items():
                print(f"\n{metric.replace('_', ' ').title()}:")
                print(f"  Latest Value: ${data['latest_value']:,.0f}M")
                print(f"  Latest Growth Rate: {data['latest_growth_rate']:.1f}%")
                print(f"  Average Growth Rate: {data['average_growth_rate']:.1f}%")
                print(f"  Trend Direction: {data['trend_direction']}")
        else:
            print("❌ No financial trends data available")
            
    except Exception as e:
        print(f"❌ Error viewing trends: {e}")

def check_health_score():
    """Check financial health score"""
    print("\n🏥 FINANCIAL HEALTH SCORE")
    print("-" * 30)
    
    analyzer = FinancialAnalyzer()
    
    try:
        health_score = analyzer.get_financial_health_score()
        
        print(f"Overall Score: {health_score['total_score']}/{health_score['max_possible_score']}")
        print(f"Percentage: {health_score['percentage']:.1f}%")
        print(f"Grade: {health_score['grade']}")
        
        print("\nScore Breakdown:")
        for component, score in health_score['components'].items():
            print(f"  {component.replace('_', ' ').title()}: {score}")
            
    except Exception as e:
        print(f"❌ Error checking health score: {e}")

def analyze_rd():
    """Analyze R&D investment"""
    print("\n🔬 R&D INVESTMENT ANALYSIS")
    print("-" * 30)
    
    analyzer = FinancialAnalyzer()
    
    try:
        rd_analysis = analyzer.analyze_rd_investment()
        
        if rd_analysis:
            print(f"Total R&D Investment: ${rd_analysis.get('total_rd_investment', 0):,.0f}M")
            print(f"Average Quarterly R&D: ${rd_analysis.get('average_quarterly_rd', 0):,.0f}M")
            print(f"R&D Growth Rate: {rd_analysis.get('rd_growth_rate', 0):.1f}%")
            print(f"R&D as % of Revenue: {rd_analysis.get('rd_as_percentage_of_revenue', 0):.1f}%")
            print(f"R&D Trend: {rd_analysis.get('rd_trend', 'Unknown')}")
        else:
            print("❌ No R&D data available")
            
    except Exception as e:
        print(f"❌ Error analyzing R&D: {e}")

def analyze_cash():
    """Analyze cash management"""
    print("\n💰 CASH MANAGEMENT ANALYSIS")
    print("-" * 30)
    
    analyzer = FinancialAnalyzer()
    
    try:
        cash_analysis = analyzer.analyze_cash_management()
        
        if cash_analysis:
            print(f"Current Cash Position: ${cash_analysis.get('current_cash', 0):,.0f}M")
            print(f"Average Cash: ${cash_analysis.get('average_cash', 0):,.0f}M")
            print(f"Cash Growth Rate: {cash_analysis.get('cash_growth_rate', 0):.1f}%")
            print(f"Cash Trend: {cash_analysis.get('cash_trend', 'Unknown')}")
            print(f"Cash Volatility: ${cash_analysis.get('cash_volatility', 0):,.0f}M")
        else:
            print("❌ No cash data available")
            
    except Exception as e:
        print(f"❌ Error analyzing cash: {e}")

def view_data_summary():
    """View data summary"""
    print("\n📋 DATA SUMMARY")
    print("-" * 15)
    
    data_manager = DataManager()
    
    try:
        summary = data_manager.get_data_summary()
        
        print(f"Total Filings: {summary['total_filings']}")
        print(f"Financial Metrics Available: {summary['financial_metrics_available']}")
        print(f"Last Updated: {summary['last_updated']}")
        
        if summary['filing_types']:
            print("\nFiling Types:")
            for form_type, count in summary['filing_types'].items():
                print(f"  {form_type}: {count}")
        
        if summary['date_range']:
            print(f"\nDate Range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")
            
    except Exception as e:
        print(f"❌ Error viewing data summary: {e}")

def export_data():
    """Export data to Excel"""
    print("\n📤 EXPORTING DATA TO EXCEL")
    print("-" * 30)
    
    data_manager = DataManager()
    
    try:
        filepath = data_manager.export_to_excel()
        print(f"✅ Data exported successfully to: {filepath}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def launch_dashboard():
    """Launch web dashboard"""
    print("\n🌐 LAUNCHING WEB DASHBOARD")
    print("-" * 30)
    
    print("Starting Streamlit dashboard...")
    print("The dashboard will open in your default web browser.")
    print("Press Ctrl+C to stop the dashboard.")
    
    try:
        os.system("streamlit run dashboard.py")
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    print("🧬 Welcome to Alnylam Financial Analyzer!")
    print("This tool specializes in analyzing Alnylam Pharmaceuticals' SEC filings.")
    
    # Check if API key is configured
    if not check_api_key():
        print("\nPlease configure your SEC-API key before using the application.")
        sys.exit(1)
    
    # Start main menu
    main_menu()
