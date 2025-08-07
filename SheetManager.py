import gspread
from google.oauth2.service_account import Credentials
from typing import List, Optional, Union
from gspread.exceptions import APIError, SpreadsheetNotFound

# When using GoogleSheetManager:
#	- creds_path: must contain the path to your service account credentials JSON file ("Credentials.json"),
#	- spreadsheet_id: must contain the ID of the Google Sheet you want to manage.

class GoogleSheetsManager:
	#====================================================================#
	#	Google Sheet Manager initialization
	#====================================================================#
	def __init__(self, creds_path: str, spreadsheet_id: str):
		self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
		self.creds_path = creds_path
		self.spreadsheet_id = spreadsheet_id

		try:
			self.creds = Credentials.from_service_account_file(creds_path, scopes=self.scopes)
			self.client = gspread.authorize(self.creds)
			self.spreadsheet = self.client.open_by_key(spreadsheet_id)
		except FileNotFoundError:
			raise FileNotFoundError(f"Credentials file not found at {creds_path}. Please provide a valid path.")
		except APIError as e:
			if "disabled" in str(e).lower():
				raise PermissionError("Google Sheets API is disabled. Please enable it in your Google Cloud Console.") from e
			raise
		except SpreadsheetNotFound:
			raise ValueError(f"Spreadsheet with ID {spreadsheet_id} not found. Please check the ID and ensure you have access to the spreadsheet.")
		
	#====================================================================#
	#	Get the specified sheet from the spreadsheet
	#====================================================================#
	def get_sheet(self, sheet_name: Optional[str] = None):
		if sheet_name:
			return self.spreadsheet.worksheet(sheet_name)
		return self.spreadsheet.sheet1
		
	#====================================================================#
	#	Read a range of cells from the specified sheet
	#====================================================================#
	def read_range(self, range_name: str, sheet_name: Optional[str] = None) -> List[List[Union[str, int, float]]]:
		sheet = self.get_sheet(sheet_name)
		return sheet.get(range_name)

	#====================================================================#
	#	Write a range of cells to the specified sheet
	#====================================================================#
	def write_range(self, range_name: str, data: List[List[Union[str, int, float]]], sheet_name: Optional[str] = None):
		sheet = self.get_sheet(sheet_name)
		sheet.update(range_name, data)

	#====================================================================#
	#	Append a row to the specified sheet
	#====================================================================#
	def append_row(self, data: List[Union[str, int, float]], sheet_name: Optional[str] = None):
		sheet = self.get_sheet(sheet_name)
		sheet.append_row(data)

	#====================================================================#
	#	Get all records from the specified sheet (heads as keys)
	#====================================================================#
	def get_all_records(self, sheet_name: Optional[str] = None) -> List[dict]:
		sheet = self.get_sheet(sheet_name)
		return sheet.get_all_records()

	#====================================================================#
	#	Add a new column to the specified sheet
	#====================================================================#
	def add_col(self, col_name: str, sheet_name: Optional[str] = None):
		sheet = self.get_sheet(sheet_name)
		last_col_index = len(sheet.row_values(1)) + 1
		# Check if the column already exists
		if col_name in sheet.row_values(1):
			raise ValueError(f"Column '{col_name}' already exists in the sheet.")
		sheet.update_cell(1, last_col_index, col_name)
		return last_col_index

	#====================================================================#
	#	Delete a column from the specified sheet
	#====================================================================#
	def delete_col(self, col_name: str, sheet_name: Optional[str] = None):
		sheet = self.get_sheet(sheet_name)
		headers = sheet.row_values(1)
		try:
			col_index = headers.index(col_name) + 1
		except ValueError:
			raise ValueError(f"Column '{col_name}' not found in sheet")
		sheet.delete_columns(col_index)