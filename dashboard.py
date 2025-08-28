"""
Interactive dashboard for Alnylam Financial Analysis
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import config
from data_manager import DataManager
from financial_analyzer import FinancialAnalyzer

# Page configuration
st.set_page_config(
    page_title="Alnylam Financial Analyzer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .health-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
    }
    .grade-A { color: #28a745; }
    .grade-B { color: #17a2b8; }
    .grade-C { color: #ffc107; }
    .grade-D { color: #fd7e14; }
    .grade-F { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache data"""
    data_manager = DataManager()
    analyzer = FinancialAnalyzer()
    
    return {
        'data_manager': data_manager,
        'analyzer': analyzer,
        'financial_df': data_manager.get_financial_timeline(),
        'summary': data_manager.get_data_summary(),
        'report': analyzer.generate_financial_report()
    }

def main():
    # Header
    st.markdown('<h1 class="main-header">🧬 Alnylam Financial Analyzer</h1>', unsafe_allow_html=True)
    st.markdown(f"**Company:** {config.ALNYLAM_COMPANY_NAME} | **Ticker:** {config.ALNYLAM_TICKER}")
    
    # Load data
    with st.spinner("Loading data..."):
        data = load_data()
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select Analysis",
        ["Overview", "Financial Trends", "R&D Analysis", "Cash Management", "Filing Search", "Data Management"]
    )
    
    # Data refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Display selected page
    if page == "Overview":
        show_overview(data)
    elif page == "Financial Trends":
        show_financial_trends(data)
    elif page == "R&D Analysis":
        show_rd_analysis(data)
    elif page == "Cash Management":
        show_cash_management(data)
    elif page == "Filing Search":
        show_filing_search(data)
    elif page == "Data Management":
        show_data_management(data)

def show_overview(data):
    """Show overview dashboard"""
    st.header("📊 Company Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Filings",
            value=data['summary']['total_filings'],
            help="Number of SEC filings analyzed"
        )
    
    with col2:
        st.metric(
            label="Date Range",
            value=f"{data['summary']['date_range'].get('earliest', 'N/A')} to {data['summary']['date_range'].get('latest', 'N/A')}",
            help="Range of filing dates"
        )
    
    with col3:
        st.metric(
            label="Financial Metrics Available",
            value=data['summary']['financial_metrics_available'],
            help="Number of filings with financial data"
        )
    
    with col4:
        health_score = data['report']['financial_health_score']
        st.metric(
            label="Financial Health Score",
            value=f"{health_score['percentage']:.1f}%",
            delta=f"Grade: {health_score['grade']}",
            help="Overall financial health assessment"
        )
    
    # Financial Health Score
    st.subheader("🏥 Financial Health Assessment")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = health_score['percentage'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Financial Health Score"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Score Breakdown")
        for component, score in health_score['components'].items():
            st.write(f"**{component.replace('_', ' ').title()}:** {score}")
    
    # Filing Types Distribution
    st.subheader("📋 Filing Types Distribution")
    
    if data['summary']['filing_types']:
        filing_types_df = pd.DataFrame(
            list(data['summary']['filing_types'].items()),
            columns=['Filing Type', 'Count']
        )
        
        fig = px.pie(
            filing_types_df, 
            values='Count', 
            names='Filing Type',
            title="Distribution of Filing Types"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_financial_trends(data):
    """Show financial trends analysis"""
    st.header("📈 Financial Trends Analysis")
    
    financial_df = data['financial_df']
    
    if financial_df.empty:
        st.warning("No financial data available. Please fetch filings first.")
        return
    
    # Convert date columns
    financial_df['filing_date'] = pd.to_datetime(financial_df['filing_date'])
    
    # Metric selection
    metrics = ['revenue', 'net_income', 'total_assets', 'cash_and_equivalents', 'research_development']
    available_metrics = [m for m in metrics if m in financial_df.columns and financial_df[m].notna().any()]
    
    if not available_metrics:
        st.warning("No financial metrics available in the data.")
        return
    
    selected_metrics = st.multiselect(
        "Select metrics to display:",
        available_metrics,
        default=available_metrics[:3] if len(available_metrics) >= 3 else available_metrics
    )
    
    if selected_metrics:
        # Create subplot
        fig = make_subplots(
            rows=len(selected_metrics), 
            cols=1,
            subplot_titles=[m.replace('_', ' ').title() for m in selected_metrics],
            vertical_spacing=0.1
        )
        
        for i, metric in enumerate(selected_metrics, 1):
            metric_data = financial_df[['filing_date', metric]].dropna()
            
            fig.add_trace(
                go.Scatter(
                    x=metric_data['filing_date'],
                    y=metric_data[metric],
                    mode='lines+markers',
                    name=metric.replace('_', ' ').title(),
                    line=dict(width=3)
                ),
                row=i, col=1
            )
        
        fig.update_layout(
            height=300 * len(selected_metrics),
            showlegend=False,
            title="Financial Metrics Over Time"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth rates
        st.subheader("📊 Growth Rates")
        
        growth_data = []
        for metric in selected_metrics:
            metric_data = financial_df[['filing_date', metric]].dropna().sort_values('filing_date')
            if len(metric_data) > 1:
                latest_growth = metric_data[metric].pct_change().iloc[-1] * 100
                growth_data.append({
                    'Metric': metric.replace('_', ' ').title(),
                    'Latest Growth Rate (%)': f"{latest_growth:.2f}%",
                    'Trend': '📈' if latest_growth > 0 else '📉'
                })
        
        if growth_data:
            growth_df = pd.DataFrame(growth_data)
            st.dataframe(growth_df, use_container_width=True)

def show_rd_analysis(data):
    """Show R&D analysis"""
    st.header("🔬 R&D Investment Analysis")
    
    rd_analysis = data['report']['rd_analysis']
    
    if not rd_analysis:
        st.warning("No R&D data available.")
        return
    
    # R&D metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total R&D Investment",
            value=f"${rd_analysis.get('total_rd_investment', 0):,.0f}M",
            help="Total R&D spending across all periods"
        )
    
    with col2:
        st.metric(
            label="Average Quarterly R&D",
            value=f"${rd_analysis.get('average_quarterly_rd', 0):,.0f}M",
            help="Average R&D spending per quarter"
        )
    
    with col3:
        st.metric(
            label="R&D Growth Rate",
            value=f"{rd_analysis.get('rd_growth_rate', 0):.1f}%",
            help="Average quarterly R&D growth rate"
        )
    
    with col4:
        st.metric(
            label="R&D as % of Revenue",
            value=f"{rd_analysis.get('rd_as_percentage_of_revenue', 0):.1f}%",
            help="R&D intensity relative to revenue"
        )
    
    # R&D trend
    financial_df = data['financial_df']
    if 'research_development' in financial_df.columns:
        rd_data = financial_df[['filing_date', 'research_development']].dropna()
        
        if not rd_data.empty:
            rd_data['filing_date'] = pd.to_datetime(rd_data['filing_date'])
            
            fig = px.line(
                rd_data, 
                x='filing_date', 
                y='research_development',
                title="R&D Investment Over Time",
                labels={'research_development': 'R&D Investment ($M)', 'filing_date': 'Filing Date'}
            )
            
            fig.update_traces(line=dict(width=3, color='#1f77b4'))
            st.plotly_chart(fig, use_container_width=True)

def show_cash_management(data):
    """Show cash management analysis"""
    st.header("💰 Cash Management Analysis")
    
    cash_analysis = data['report']['cash_analysis']
    
    if not cash_analysis:
        st.warning("No cash data available.")
        return
    
    # Cash metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Current Cash Position",
            value=f"${cash_analysis.get('current_cash', 0):,.0f}M",
            help="Latest cash and cash equivalents"
        )
    
    with col2:
        st.metric(
            label="Average Cash",
            value=f"${cash_analysis.get('average_cash', 0):,.0f}M",
            help="Average cash position over time"
        )
    
    with col3:
        st.metric(
            label="Cash Growth Rate",
            value=f"{cash_analysis.get('cash_growth_rate', 0):.1f}%",
            help="Average quarterly cash growth rate"
        )
    
    with col4:
        trend_emoji = "📈" if cash_analysis.get('cash_trend') == 'increasing' else "📉"
        st.metric(
            label="Cash Trend",
            value=trend_emoji,
            help="Overall cash position trend"
        )
    
    # Cash position chart
    financial_df = data['financial_df']
    if 'cash_and_equivalents' in financial_df.columns:
        cash_data = financial_df[['filing_date', 'cash_and_equivalents']].dropna()
        
        if not cash_data.empty:
            cash_data['filing_date'] = pd.to_datetime(cash_data['filing_date'])
            
            fig = px.area(
                cash_data, 
                x='filing_date', 
                y='cash_and_equivalents',
                title="Cash and Cash Equivalents Over Time",
                labels={'cash_and_equivalents': 'Cash Position ($M)', 'filing_date': 'Filing Date'}
            )
            
            fig.update_traces(fill='tonexty', line=dict(width=3, color='#28a745'))
            st.plotly_chart(fig, use_container_width=True)

def show_filing_search(data):
    """Show filing search interface"""
    st.header("🔍 Filing Search")
    
    # Search options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("Search query:", placeholder="Enter keywords to search in filings...")
    
    with col2:
        form_types = st.multiselect(
            "Form types:",
            config.SUPPORTED_FILING_TYPES,
            default=['10-K', '10-Q']
        )
    
    if st.button("Search") and search_query:
        with st.spinner("Searching filings..."):
            results = data['data_manager'].search_filings(search_query, form_types)
            
            if results:
                st.success(f"Found {len(results)} results")
                
                for result in results[:10]:  # Show first 10 results
                    with st.expander(f"{result.get('formType', 'Unknown')} - {result.get('filingDate', 'Unknown date')}"):
                        st.write(f"**Company:** {result.get('companyName', 'N/A')}")
                        st.write(f"**Filing Date:** {result.get('filingDate', 'N/A')}")
                        st.write(f"**Period of Report:** {result.get('periodOfReport', 'N/A')}")
                        
                        if result.get('filingUrl'):
                            st.write(f"**Filing URL:** [View Filing]({result['filingUrl']})")
            else:
                st.warning("No results found.")

def show_data_management(data):
    """Show data management interface"""
    st.header("🗄️ Data Management")
    
    # Data summary
    st.subheader("Current Data Status")
    
    summary = data['summary']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Total Filings:** {summary['total_filings']}")
        st.write(f"**Financial Metrics Available:** {summary['financial_metrics_available']}")
        st.write(f"**Last Updated:** {summary['last_updated']}")
    
    with col2:
        st.write("**Filing Types:**")
        for form_type, count in summary['filing_types'].items():
            st.write(f"- {form_type}: {count}")
    
    # Data operations
    st.subheader("Data Operations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Fetch Recent Filings"):
            with st.spinner("Fetching recent filings..."):
                try:
                    new_filings = data['data_manager'].fetch_and_store_filings(
                        years_back=2,
                        force_refresh=False
                    )
                    st.success(f"Fetched {len(new_filings)} new filings")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error fetching filings: {e}")
    
    with col2:
        if st.button("📊 Export to Excel"):
            with st.spinner("Exporting data..."):
                try:
                    filepath = data['data_manager'].export_to_excel()
                    st.success(f"Data exported to: {filepath}")
                except Exception as e:
                    st.error(f"Error exporting data: {e}")
    
    with col3:
        if st.button("🔄 Refresh All Data"):
            with st.spinner("Refreshing all data..."):
                try:
                    new_filings = data['data_manager'].fetch_and_store_filings(
                        years_back=5,
                        force_refresh=True
                    )
                    st.success(f"Refreshed {len(new_filings)} filings")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error refreshing data: {e}")

if __name__ == "__main__":
    main()
