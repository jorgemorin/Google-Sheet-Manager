# Google-Sheet-Manager (v1.0)
A python library for easy interaction with Google Sheets API, providing a clean and intuitive interface for common spreadsheet operations,

## Features
- **Sheet Management**: Easily switch between worksheets and get sheetes information
- **Cell Operations**: Read, write, and delete individual cells or ranges
- **Database-like Functions**: Manage data in a structured way with headers and rows

## Installation
1. Install the required packages:
  ```
  pip install gspread google-auth
  ```
2. Enable Google Sheets API in your Google Cloud Console
3. Create a service account and download the credentials JSON file

## Usage
### Basic Setup
```
from SheetManager import GoogleSheetsManager

manager = GoogleSheetsManager(
    creds_path="path/to/credentials.json",
    spreadsheet_id="your-spreadsheet-id",
    sheet="Sheet1"  # optional
)
```
### Basic Operations
```
# Update a single cell
manager.update_cell("A1", "Hello World!")

# Get cell value
value = manager.get_cell("A1")

# Update a range
manager.update_range("A1:B2", [["Name", "Age"], ["John", 30]])

# Get all values
all_data = manager.get_all_values()
```
### Basic Database Operations
```
# Create a new database structure
manager.db_create(["Name", "Age", "Email"])

# Add data
manager.db_add_value(["John Doe", 30, "john@example.com"])
manager.db_add_value(["Jane Smith", 25, "jane@example.com"])

# Get all data
data = manager.db_get_all_values()
```
## API Reference
### Sheet Management
* set_sheet(sheet_name: str): Switch to a different worksheet
* get_sheet() -> gspread.Worksheet: Get current worksheet object
* get_sheet_name() -> str: Get current sheet name
* get_all_sheets() -> List[str]: Get all sheet names
### Cell Operations
* get_cell(cell: str): Get cell value
* update_cell(cell: str, value): Update single cell
* del_cell(cell: str): Clear cell content
* get_range(cell_range: str): Get range of cells
* update_range(cell_range: str, values): Update range of cells
* del_range(cell_range: str): Clear range of cells
* get_all_values() -> List[List]: Get all worksheet values
* clear(): Clear entire worksheet
### Database Operations
* db_get_headers() -> List[str]: Get column headers
* db_add_header(header: str): Add new column header
* db_add_headers(headers: List[str]): Add multiple headers
* db_create(headers: Optional[List[str]]): Initialize database structure
* db_add_value(values: List): Add new row of data
* db_get_all_values() -> List[List]: Get all data rows

## Requirements
- Python 3.7+
- gspread
- google-auth

## License
MIT License
