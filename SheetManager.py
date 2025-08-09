import gspread
from google.oauth2.service_account import Credentials
from typing import List, Optional, Union
from gspread.exceptions import APIError, SpreadsheetNotFound

# When using GoogleSheetManager:
#	- creds_path: must contain the path to your service account credentials JSON file ("Credentials.json"),
#	- spreadsheet_id: must contain the ID of the Google Sheet you want to manage.

class GoogleSheetsManager:
	# ==================== INITIALIZATION ==================== #
    def __init__(self, creds_path: str, spreadsheet_id: str):
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds_path = creds_path
        self.spreadsheet_id = spreadsheet_id

        try:
            self.creds = Credentials.from_service_account_file(creds_path, scopes=self.scopes)
            self.client = gspread.authorize(self.creds)
            self.spreadsheet = self.client.open_by_key(spreadsheet_id)
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found at {creds_path}")
        except APIError as e:
            if "disabled" in str(e).lower():
                raise PermissionError("Google Sheets API is disabled. Please enable it in Google Cloud Console.")
            raise
        except SpreadsheetNotFound:
            raise ValueError(f"Spreadsheet with ID {spreadsheet_id} not found")

    # ==================== SHEET OPERATIONS ==================== #
    def get_available_sheets(self) -> List[str]:
        """Get list of all worksheet names in the spreadsheet"""
        return [sheet.title for sheet in self.spreadsheet.worksheets()]

    def sheet_exists(self, sheet_name: str) -> bool:
        """Check if a worksheet exists"""
        return sheet_name in self.get_available_sheets()

    def get_sheet(self, sheet_name: Optional[str] = None) -> Optional[gspread.Worksheet]:
        """
        Get a worksheet by name
        Returns None if sheet doesn't exist
        """
        if sheet_name is None:
            return self.spreadsheet.sheet1
            
        if not self.sheet_exists(sheet_name):
            print(f"Worksheet '{sheet_name}' not found. Available sheets: {self.get_available_sheets()}")
            return None
            
        return self.spreadsheet.worksheet(sheet_name)

    def create_sheet(self, sheet_name: str) -> gspread.Worksheet:
        """Create a new worksheet"""
        if self.sheet_exists(sheet_name):
            raise ValueError(f"Sheet '{sheet_name}' already exists")
        return self.spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

    def delete_sheet(self, sheet_name: str) -> None:
        """Delete a worksheet"""
        if not self.sheet_exists(sheet_name):
            raise ValueError(f"Sheet '{sheet_name}' does not exist")
        sheet = self.get_sheet(sheet_name)
        self.spreadsheet.del_worksheet(sheet)

    # ==================== DATA RETRIEVAL ==================== #
    def get_all_values(self, sheet_name: Optional[str] = None) -> List[List[Union[str, int, float]]]:
        """Get all values from a worksheet as list of lists"""
        sheet = self.get_sheet(sheet_name)
        return sheet.get_all_values() if sheet else []

    def get_available_columns(self, sheet_name: str) -> List[str]:
        """Get column headers from a worksheet"""
        values = self.get_all_values(sheet_name)
        return values[0] if values else []

    def get_value_from(self, sheet_name: str, cell: str) -> Union[str, int, float, None]:
        """Get value from a specific cell"""
        sheet = self.get_sheet(sheet_name)
        if not sheet:
            raise ValueError(f"Sheet '{sheet_name}' not found")
        return sheet.acell(cell).value

    def get_values_from_column(self, sheet_name: str, column_name: str) -> List[Union[str, int, float]]:
        """
        Get all values from a column by header name
        Returns empty list if column not found
        """
        sheet = self.get_sheet(sheet_name)
        if not sheet:
            raise ValueError(f"Sheet '{sheet_name}' not found")
            
        values = sheet.get_all_values()
        if not values:
            return []
            
        try:
            col_index = values[0].index(column_name)
            return [row[col_index] for row in values[1:] if len(row) > col_index]
        except ValueError:
            return []

    # ==================== DATA SEARCH ==================== #
    def get_values_with_id(self, sheet_name: str, id_value: Union[str, int]) -> List[List[Union[str, int, float]]]:
        """
        Get all rows matching a specific ID value
        Returns empty list if no matches found
        """
        values = self.get_all_values(sheet_name)
        if not values:
            return []
            
        try:
            id_index = values[0].index("ID")
            return [row for row in values[1:] if len(row) > id_index and row[id_index] == str(id_value)]
        except ValueError:
            return []

    def get_values_where(self, sheet_name: str, column: str, value: Union[str, int]) -> List[List[Union[str, int, float]]]:
        """
        Get all rows where specified column matches value
        Returns empty list if no matches found
        """
        values = self.get_all_values(sheet_name)
        if not values:
            return []
            
        try:
            col_index = values[0].index(column)
            return [row for row in values[1:] if len(row) > col_index and row[col_index] == str(value)]
        except ValueError:
            return []

    # ==================== DATA MODIFICATION ==================== #
    def set_value_on(self, sheet_name: str, cell: str, value: Union[str, int, float]) -> None:
        """Set value in a specific cell"""
        sheet = self.get_sheet(sheet_name)
        if not sheet:
            raise ValueError(f"Sheet '{sheet_name}' not found")
        sheet.update_acell(cell, value)

    def append_row(self, sheet_name: str, row_name: List[Union[str, int, float]]) -> None:
        """
        Append a new row to the specified worksheet
        """
        sheet = self.get_sheet(sheet_name)
        if not sheet:
            raise ValueError(f"Sheet '{sheet_name}' not found")
        sheet.append_row(row_name)

