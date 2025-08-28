# 🧬 Alnylam Financial Analyzer

A specialized financial analysis tool designed exclusively for analyzing Alnylam Pharmaceuticals' SEC filings and financial performance.

## 🎯 Overview

This tool provides comprehensive analysis of Alnylam Pharmaceuticals (NASDAQ: ALNY), a leading biotech company specializing in RNAi therapeutics. The analyzer fetches, processes, and analyzes SEC filings including 10-K, 10-Q, 8-K, and other regulatory documents to provide deep insights into the company's financial health, R&D investments, and business operations.

## ✨ Features

### 📊 Financial Analysis
- **Financial Health Scoring**: Comprehensive scoring system evaluating revenue growth, R&D investment, cash position, profitability, and asset efficiency
- **Trend Analysis**: Track key financial metrics over time with growth rate calculations
- **Ratio Analysis**: Calculate important financial ratios including profit margins, asset turnover, and R&D intensity
- **Cash Management**: Analyze cash position, liquidity trends, and cash flow patterns

### 🔬 Biotech-Specific Analysis
- **R&D Investment Tracking**: Monitor research and development spending patterns
- **Pipeline Analysis**: Search and analyze drug development pipeline mentions
- **Partnership Tracking**: Identify collaboration and licensing agreements
- **Patent Analysis**: Track intellectual property and patent mentions

### 🔍 Advanced Search & Analysis
- **Content Search**: Search across all filings for specific keywords and phrases
- **Risk Factor Analysis**: Identify and analyze risk factors mentioned in filings
- **Keyword Trend Analysis**: Track biotech-specific keyword mentions over time
- **Context Extraction**: Get relevant context around search results

### 📈 Interactive Dashboard
- **Web-based Interface**: Modern Streamlit dashboard with interactive charts
- **Real-time Data**: Live updates and data refresh capabilities
- **Export Functionality**: Export analysis results to Excel format
- **Visual Analytics**: Interactive plots and charts for data visualization

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- SEC-API account and API key (get from [sec-api.io](https://sec-api.io/))

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**:
   - Copy `env_example.txt` to `.env`
   - Add your SEC-API key to the `.env` file:
     ```
     SEC_API_KEY=your_actual_api_key_here
     ```

4. **Run the application**:
   ```bash
   python main.py
   ```

### Using the Web Dashboard

Launch the interactive web dashboard:
```bash
streamlit run dashboard.py
```

## 📁 Project Structure

```
Alnylam Financial Analyzer/
├── main.py                 # Main application entry point
├── dashboard.py            # Streamlit web dashboard
├── config.py              # Configuration settings
├── sec_api_client.py      # SEC-API integration
├── filing_parser.py       # SEC filing parser
├── data_manager.py        # Data management system
├── financial_analyzer.py  # Financial analysis engine
├── search_analyzer.py     # Search and keyword analysis
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
├── README.md             # This file
└── data/                 # Data storage directory
    ├── filings/          # Parsed SEC filings
    ├── analysis/         # Analysis results
    └── reports/          # Exported reports
```

## 🔧 Usage

### Command Line Interface

The main application provides a menu-driven interface:

1. **Fetch SEC Filings**: Download and store Alnylam's SEC filings
2. **Generate Reports**: Create comprehensive financial analysis reports
3. **Search Content**: Search for specific information across filings
4. **View Trends**: Analyze financial trends over time
5. **Health Score**: Check overall financial health assessment
6. **R&D Analysis**: Analyze research and development investments
7. **Cash Management**: Review cash position and liquidity
8. **Data Summary**: View overview of stored data
9. **Export Data**: Export analysis to Excel format
10. **Launch Dashboard**: Open the web-based dashboard

### Web Dashboard

The Streamlit dashboard provides:
- **Overview**: Company summary and financial health score
- **Financial Trends**: Interactive charts of key metrics
- **R&D Analysis**: Research and development investment tracking
- **Cash Management**: Cash position and liquidity analysis
- **Filing Search**: Advanced search capabilities
- **Data Management**: Data refresh and export options

## 📊 Key Metrics Analyzed

### Financial Metrics
- Revenue and revenue growth
- Net income and profitability
- Total assets and asset turnover
- Cash and cash equivalents
- Research and development spending
- Operating expenses

### Biotech-Specific Metrics
- R&D intensity (R&D as % of revenue)
- Pipeline development mentions
- Clinical trial references
- Patent and IP mentions
- Partnership and collaboration tracking
- Regulatory milestone mentions

### Risk Analysis
- Risk factor identification
- Competitive landscape mentions
- Regulatory challenges
- Market volatility factors
- Clinical trial risks

## 🎯 Alnylam-Specific Features

This tool is specifically designed for Alnylam Pharmaceuticals and includes:

- **Company-Specific Configuration**: Pre-configured with Alnylam's CIK and ticker
- **RNAi Focus**: Specialized keyword analysis for RNA interference technology
- **Rare Disease Analysis**: Focus on rare disease therapeutic development
- **Partnership Tracking**: Monitor collaborations with major pharma companies
- **Regulatory Milestones**: Track FDA approvals and regulatory progress

## 📈 Sample Analysis Outputs

### Financial Health Score
- Overall percentage score (0-100%)
- Letter grade (A-F)
- Component breakdown (revenue growth, R&D investment, cash position, etc.)

### Trend Analysis
- Quarterly and annual growth rates
- Volatility measurements
- Trend direction indicators

### Keyword Analysis
- Biotech keyword mention frequency
- Year-over-year trend analysis
- Context extraction for key mentions

## 🔒 Data Security

- All data is stored locally
- No data is transmitted to external servers (except SEC-API for fetching)
- API keys are stored in local environment files
- Parsed filings are stored in local JSON format

## 🤝 Contributing

This tool is specifically designed for Alnylam Pharmaceuticals analysis. For modifications or enhancements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational and research purposes. Please ensure compliance with SEC-API terms of service and SEC data usage policies.

## 🆘 Support

For issues or questions:
1. Check the configuration (API key, dependencies)
2. Review the error messages in the console
3. Ensure you have an active SEC-API subscription
4. Check that Alnylam's filings are available in the SEC database

## 🔄 Updates

The tool automatically fetches the latest filings when you run the data fetch function. For the most up-to-date analysis, regularly refresh your data using the "Fetch Recent Filings" option.

---

**Note**: This tool is designed specifically for Alnylam Pharmaceuticals analysis. The financial health scoring and analysis methods are tailored to biotech companies and may not be suitable for other industries.
