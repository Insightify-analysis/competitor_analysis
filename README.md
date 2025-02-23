# competitor_analysis

## Overview
A competitor analysis tool that aggregates data and provides market insights.

## Project Setup

### Create a Virtual Environment
Run the following command to set up a virtual environment:
```
python -m venv venv
```

### Install Dependencies
Activate your virtual environment and install packages:
```
venv\Scripts\activate   # on Windows
source venv/bin/activate  # on macOS/Linux
pip install -r requirements.txt
```

### Set Up Environment Variables
Create (or update) the .env file in the project root with:
```
PINECONE_API_KEY="your_api_key"
PINECONE_ENV="your_environment"
PINECONE_INDEX_NAME="your_index"
GEMINI_API_KEY="your_gemini_api_key"
```
Adjust values as needed.

### Prepare Data Files
Ensure the `categories.json` file is present in the root or in the default data directory. Add any context files under the `context_data` folder if needed.

## Usage

### Command Line Interface (CLI)
Run the CLI for interactive categorization:
```
python cli.py
```
Or perform file-based categorization by passing a file path (supports Excel, CSV, JSON).

### Flask Server API
To launch the Flask API, run:
```
python flask_server.py
```
The server supports endpoints:
- `/categorize` – Analyze a company name via GET.
- `/categorize_file` – Categorize data from a file.
- `/stream_categorize` – Stream JSON categorization output.

## Contributing
Fork the repository and create a feature branch.
- Write tests for new functionality.
- Ensure code style consistency.
Submit pull requests with clear commit messages.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
