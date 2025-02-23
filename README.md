# Competitor Analysis Tool

## Overview
The Competitor Analysis Tool aggregates data from various sources to analyze competitor information and deliver actionable market insights. The project is organized as a modular, pip-installable Python package for easy development and deployment.

## File Structure
```
competitor_analysis/
├── README.md                # Project overview and documentation
├── app.py                   # Core application logic and company categorization
├── cli.py                   # Command-line interface entry point
├── requirements.txt         # Project dependencies
├── .env                     # Environment configuration
├── .gitignore              # Git ignore rules
└── src/                    # Source code directory
    ├── file_manager.py     # File handling utilities
    ├── config.py           # Configuration management
    ├── excel_utils.py      # Excel file processing
    └── company_domain_categorizer.py  # Domain categorization logic
```

## Core Components

### Main Application (app.py)
The `CompanyCategorizerApp` class provides:
- Interactive company categorization
- Batch processing from files
- JSON result handling and posting
- Integration with domain categorization

### CLI Interface (cli.py)
Provides command-line interaction:
```bash
# Interactive mode
python cli.py

# File processing mode
python cli.py path/to/companies.xlsx

# Clean output mode
python cli.py --clean
```

### Supported File Formats
- Excel (.xlsx, .xls)
- CSV files (.csv)
- JSON files (.json)

## Dependencies
Key packages required (from requirements.txt):
```
requests==2.28.1        # HTTP requests
beautifulsoup4==4.11.1  # Web scraping
pandas==1.5.3          # Data manipulation
numpy==1.23.5         # Numerical operations
flask                 # API server
google-generativeai   # AI integration
yfinance             # Financial data
```

## Project Setup

### 1. Create a Virtual Environment
Run the command below to set up a virtual environment:
```
python -m venv venv
```

### 2. Install Dependencies
Activate your virtual environment and install required packages:
```
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Environment Configuration
Required environment variables in `.env`:
```env
# AI Model Configuration
GEMINI_API_KEY="your_key"      # Google's Gemini AI
OPENAI_API_KEY="your_key"      # Optional: OpenAI backup

# Vector Database
PINECONE_API_KEY="your_key"    # Vector similarity search
PINECONE_ENV="environment"     # Pinecone environment
PINECONE_INDEX_NAME="index"    # Vector index name

# Application Settings
CACHE_ENABLED=true            # Enable response caching
REQUESTS_PER_MINUTE=60       # Rate limiting
LOG_LEVEL=INFO              # Logging verbosity
```

## Usage

### Command Line Interface (CLI)
Run the tool interactively using:
```
python main.py --config competitor_config.json
```
Adjust command line arguments as necessary for custom configurations.

## Advanced Usage

### Data Collection
```python
# Collect competitor data
python main.py --collect --competitors "competitor_list.json"

# Update existing data
python main.py --update --age 7  # Update data older than 7 days
```

### Analysis Features
- Market Position Analysis
  ```python
  python main.py --analyze position --competitor "CompanyName"
  ```
- Feature Comparison
  ```python
  python main.py --analyze features --output "comparison.xlsx"
  ```
- Sentiment Analysis
  ```python
  python main.py --analyze sentiment --timeframe "2024-01"
  ```

### API Integration
The tool can be integrated into other applications using the provided API:

```python
from competitor_analysis import CompetitorAnalyzer

analyzer = CompetitorAnalyzer()
results = analyzer.analyze_competitor("CompanyName")
```

### Extensibility
You can extend the project by adding more modules, creating tests, or integrating new data sources.

## Testing
For testing, add your unit tests under a tests directory and run:
```
pytest
```

## Troubleshooting

### Common Issues
1. **API Rate Limiting**
   - Symptom: "Too Many Requests" error
   - Solution: Adjust `REQUESTS_PER_MINUTE` in .env file

2. **Data Collection Failures**
   - Symptom: "Connection timeout" errors
   - Solution: Check network settings, adjust `REQUEST_TIMEOUT`

3. **Vector Database Issues**
   - Symptom: Pinecone connection errors
   - Solution: Verify API keys and environment settings

### Debug Mode
Enable detailed logging:
```python
python main.py --debug
```

## Performance Optimization

### Caching
Configure caching behavior in .env:
```env
CACHE_ENABLED=true
CACHE_EXPIRY=3600  # seconds
```

### Parallel Processing
For bulk analysis:
```python
python main.py --analyze bulk --parallel 4
```

## Security Considerations
- Keep .env file secure and never commit to version control
- Regularly rotate API keys
- Use environment-specific configurations
- Implement rate limiting for API endpoints

## Contributing
Contributions are welcome:
- Fork the repository and create a feature branch.
- Add your enhancements along with tests.
- Submit a pull request with clear commit messages.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
