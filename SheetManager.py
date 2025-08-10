import gspread
from google.oauth2.service_account import Credentials
from typing import List, Optional, Union
from gspread.exceptions import APIError, SpreadsheetNotFound

# When using GoogleSheetManager:
#	- creds_path: must contain the path to your service account credentials JSON file ("Credentials.json"),
#	- spreadsheet_id: must contain the ID of the Google Sheet you want to manage.
#   - sheet: optional, if not provided, the first sheet will be used by default.

class GoogleSheetsManager:
	# ==================== INITIALIZATION ==================== #
    def __init__(self, creds_path: str, spreadsheet_id: str, sheet: Optional[str] = None):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds_path = creds_path
        self.spreadsheet_id = spreadsheet_id
        self._worksheet = None
        self.sheet_name = None

        try:
            self.creds = Credentials.from_service_account_file(creds_path, scopes=self.scopes)
            self.client = gspread.authorize(self.creds)
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
            if sheet:
                self.set_sheet(sheet)
            else:
                self._worksheet = self.spreadsheet.sheet1
                self.sheet_name = self.spreadsheet.sheet1.title

        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found at {creds_path}")
        except APIError as e:
            if "disabled" in str(e).lower():
                raise PermissionError("Google Sheets API is disabled. Please enable it in Google Cloud Console.")
            raise
        except SpreadsheetNotFound:
            raise ValueError(f"Spreadsheet with ID {spreadsheet_id} not found")

    # ==================== SHEET MANAGEMENT ==================== #
    # == setters
    def set_sheet(self, sheet_name: str):
        try:
            self.sheet_name = self.spreadsheet.worksheet(sheet_name).title
            self._worksheet = self.spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            raise ValueError(f"Sheet with name '{sheet_name}' not found in spreadsheet.")
    # == getters
    def get_sheet(self) -> gspread.Worksheet:
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        return self._worksheet
    def get_sheet_name(self) -> str:
        if self.sheet_name is None:
            raise ValueError("No sheet name set. Use set_sheet() to select a worksheet.")
        return self.sheet_name
    def get_all_sheets(self) -> List[str]:
        return [sheet.title for sheet in self.spreadsheet.worksheets()]

    # ==================== DATA MANAGEMENT ==================== #
    # == Single cell
    def get_cell(self, cell: str) -> Union[str, int, float]:
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        return self._worksheet.acell(cell).value
    def update_cell(self, cell: str, value: Union[str, int, float]):
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        self._worksheet.update_acell(cell, value)
    def del_cell(self, cell: str):
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        self._worksheet.update_acell(cell, "")

    # == Range of cells
    def get_range(self, cell_range: str) -> List[List[Union[str, int, float]]]:
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        return self._worksheet.get(cell_range)
    def update_range(self, cell_range: str, values: List[List[Union[str, int, float]]]):
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        self._worksheet.update(cell_range, values)
    def del_range(self, cell_range: str):
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        self._worksheet.batch_clear([cell_range])

    # == All values
    def get_all_values(self) -> List[List[Union[str, int, float]]]:
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        return self._worksheet.get_all_values()
    def clear(self):
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        self._worksheet.clear()

    # ==================== CELL MANAGEMENT ==================== #
    def move_to(self, cell: str, target_cell: str):
        value = self.get_cell(cell)
        self.update_cell(target_cell, value)
        self.del_cell(cell)
    def copy_to(self, cell: str, target_cell: str):
        value = self.get_cell(cell)
        self.update_cell(target_cell, value)

    # ========================================================== #
    # DATA BASE MANAGEMENT
    # ========================================================== #
    def db_get_headers(self) -> List[str]:
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        
        # Assuming headers are in the first row
        headers = self._worksheet.row_values(1)
        return headers
    def db_add_header(self, header: str):
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        headers = self.db_get_headers()
        if header in headers:
            raise ValueError(f"Header '{header}' already exists.")
        else:
            headers.append(header)
            self._worksheet.update('A1', [headers])
    def db_add_headers(self, headers: List[str]):
        """Add multiple headers to the database"""
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        
        for header in headers:
            self.db_add_header(header)
    def db_create(self, headers: Optional[List[str]] = None):
        """Create a new database with the specified headers, clearing the actual sheet and adding ID by default"""
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")

        self.clear()
        self.db_add_header("ID")  # Always add an ID header
        if headers:
            for header in headers:
                self.db_add_header(header)  
    def db_add_value(self, values: List[Union[str, int, float]]):
        """Add a new row of values to the database"""
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        
        headers = self.db_get_headers()
        if len(values) != len(headers) - 1:  # Exclude ID header
            raise ValueError(f"Expected {len(headers) - 1} values, got {len(values)}")
        else:
            next_row = len(self._worksheet.get_all_values()) + 1
            values.insert(0, next_row - 1)
            self._worksheet.append_row(values)
    def db_get_all_values(self) -> List[List[Union[str, int, float]]]:
        """Get all values from the database, including the ID column but excluding headers"""
        if self._worksheet is None:
            raise ValueError("No worksheet set. Use set_sheet() to select a worksheet.")
        
        all_values = self._worksheet.get_all_values()
        return all_values[1:]