# MISMO XML Anonymizer API

A FastAPI-based REST API that anonymizes personally identifiable information (PII) in MISMO XML documents. The API features built-in Swagger UI for easy testing and integration.

## Features

- **File Upload**: Upload individual MISMO XML files via multipart/form-data
- **Text Input**: Submit XML as text via POST request
- **Folder Processing**: Process all XML files in a folder and save anonymized versions to an `anon` subfolder
- **Comprehensive Anonymization**:
  - Names (_FirstName, _LastName, _UnparsedName, etc.)
  - Social Security Numbers (_SSN)
  - Date of Birth (_BirthDate, _AgeYears)
  - Addresses (_StreetAddress, _City, _State, _PostalCode)
  - Contact Information (Phone, Fax, Email)
  - Creditor/Mortgage Company Names (_Name in _CREDITOR tags)
  - Financial Data (Account IDs, Loan IDs, Internal Identifiers)
- **XML Recovery Mode**: Automatically handles malformed XML (unescaped special characters)
- **Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative API documentation at `/redoc`

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone the repository:

```bash
git clone https://github.com/raghul-ravi/report-anonymizer.git
cd report-anonymizer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Access Swagger UI

Open your browser and navigate to:

```
http://localhost:8000/docs
```

The Swagger UI provides an interactive interface to test the API endpoints.

### API Endpoints

#### 1. Upload XML File

**Endpoint**: `POST /anonymize`

Upload a MISMO XML file for anonymization.

```bash
curl -X POST "http://localhost:8000/anonymize" \
  -H "accept: application/xml" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_mismo.xml" \
  -o anonymized_output.xml
```

#### 2. Submit XML as Text

**Endpoint**: `POST /anonymize/text`

Submit XML content as text.

```bash
curl -X POST "http://localhost:8000/anonymize/text" \
  -H "Content-Type: application/json" \
  -d '{"xml_text": "<CREDIT_RESPONSE>...</CREDIT_RESPONSE>"}' \
  -o anonymized_output.xml
```

#### 3. Process Entire Folder

**Endpoint**: `POST /anonymize/folder`

Process all XML files in a folder and save anonymized versions to an `anon` subfolder.

```bash
curl -X POST "http://localhost:8000/anonymize/folder" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/absolute/path/to/xml/folder"}'
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Processed 10 files successfully",
  "folder": "/absolute/path/to/xml/folder",
  "output_folder": "/absolute/path/to/xml/folder/anon",
  "processed": 10,
  "failed": 0,
  "files": [
    {"original": "report1.xml", "anonymized": "anon/report1.xml"},
    {"original": "report2.xml", "anonymized": "anon/report2.xml"}
  ]
}
```

**Note:** The folder path must be an absolute path (e.g., `/Users/username/documents/xml-files`)

#### 4. Health Check

**Endpoint**: `GET /health`

Check API health status.

```bash
curl http://localhost:8000/health
```

## Anonymization Rules

The anonymizer applies the following transformations to XML attributes:

| Data Type | XML Attribute | Transformation |
|-----------|---------------|----------------|
| First Name | `_FirstName` | Random first name (John, Jane, etc.) |
| Middle Name | `_MiddleName` | Random letter (A, B, C, etc.) |
| Last Name | `_LastName` | Random last name (Smith, Jones, etc.) |
| Full Name | `_UnparsedName` | Combined random full name |
| SSN | `_SSN` | Random 9-digit number |
| Date of Birth | `_BirthDate` | Random date (30-50 years ago) |
| Age | `_AgeYears` | Random age (30-50) |
| Street Address | `_StreetAddress` | Random number + "Main Street" |
| City | `_City` | "Anytown" |
| State | `_State` | "CA" |
| Postal Code | `_PostalCode` | "90001" |
| Phone/Fax | `_Value` (Phone) | 555-xxx-xxxx format |
| Creditor Name | `_Name` (_CREDITOR) | Random creditor from preset list |
| Company Name | `_Name` (REQUESTING_PARTY) | Random company from preset list |
| Account ID | `_AccountIdentifier` | ACC + random digits |
| Internal ID | `InternalAccountIdentifier` | INT + random digits |
| Lender Case ID | `LenderCaseIdentifier` | Random 7-digit number |
| Requested By | `_RequestedByName` | user + random number |

## Project Structure

```
report-anonymizer/
├── main.py              # FastAPI application
├── anonymizer.py        # XML anonymization logic
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── sample_mismo.xml    # Sample XML for testing (optional)
```

## Example Usage with Python

```python
import requests

# 1. Upload single file
with open('sample_mismo.xml', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/anonymize', files=files)

    with open('anonymized.xml', 'wb') as output:
        output.write(response.content)

# 2. Submit XML as text
xml_content = "<CREDIT_RESPONSE>...</CREDIT_RESPONSE>"
response = requests.post(
    'http://localhost:8000/anonymize/text',
    json={'xml_text': xml_content}
)
print(response.text)

# 3. Process entire folder
response = requests.post(
    'http://localhost:8000/anonymize/folder',
    json={'folder_path': '/absolute/path/to/xml/folder'}
)
result = response.json()
print(f"Processed {result['processed']} files")
print(f"Output folder: {result['output_folder']}")
```

## Testing with Swagger UI

### Single File Upload
1. Navigate to `http://localhost:8000/docs`
2. Click on the `/anonymize` endpoint
3. Click "Try it out"
4. Upload your MISMO XML file
5. Click "Execute"
6. Download the anonymized XML from the response

### Folder Processing
1. Navigate to `http://localhost:8000/docs`
2. Click on the `/anonymize/folder` endpoint
3. Click "Try it out"
4. Enter the absolute path to your folder containing XML files
5. Click "Execute"
6. View the response showing which files were processed
7. Find anonymized files in the `anon` subfolder within your specified folder

## Security Notes

- This tool is designed for anonymizing test data and should not be used as the sole method for data protection
- Always verify that your specific use case requirements are met
- The anonymization is randomized - different fake values are generated for each request
- No data is stored by the application
- When using folder processing, the original files are NOT modified - only copies are created in the `anon` subfolder
- The API accepts absolute file paths for folder processing - ensure proper access controls are in place
- XML parsing uses recovery mode to handle malformed XML with unescaped special characters

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **lxml**: XML parsing and manipulation
- **python-multipart**: File upload support

## Use Cases

- Anonymize production credit reports for testing environments
- Create sample datasets without exposing PII
- Bulk process MISMO XML files for compliance testing
- Generate anonymized data for development and QA

## License

This project is provided as-is for educational and testing purposes.

## Contributing

Feel free to submit issues or pull requests for improvements.

## Support

For issues or questions, please open an issue on the [GitHub repository](https://github.com/raghul-ravi/report-anonymizer).
