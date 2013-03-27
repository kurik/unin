# google_sheet python module

import gspread
import datetime
import w1_term
import my_config

print('Updating Google spreadsheet')

# make sure we can access all the worksheets we need
gc = gspread.login(my_config.google_login, my_config.google_password)
spreadsheet = gc.open(my_config.google_sheet_name)
w_summary = spreadsheet.worksheet('SUMMARY')
w_daily = spreadsheet.worksheet('DAILY')
w_weekly = spreadsheet.worksheet('WEEKLY')
w_monthly = spreadsheet.worksheet('MONTHLY')
print('... Initialization is done')

# Get the data
now = datetime.datetime.now()
out_temp = float(w1_term.Therm(my_config.out_sensor).getDegrees()) / 1000
in_temp = float(w1_term.Therm(my_config.in_sensor).getDegrees()) / 1000

# Update the SUMMARY sheet
w_summary.update_acell('B2', out_temp)
w_summary.update_acell('C2', in_temp)
w_summary.update_acell('A1', now.strftime("%Y-%m-%d\n%H:%M"))
print('... Summary sheet updated')

class Tracking:
	start_row = 2 # The number of row, where the first data can be entered
	sheet = None # Worksheet object (gspread)
	latest_update = None # The cell object (gspread) where ID of the latest update is located
	timestamp = None # The datetime object containing timestamp data
	out_temp = None # The outdoor temperature (in degrees)
	in_temp = None # The indoor temperature (in degrees)

	def __init__(self, sheet, latest_update, timestamp, out_temp, in_temp):
		self.sheet = sheet
		self.latest_update = latest_update
		self.timestamp = timestamp
		self.out_temp = out_temp
		self.in_temp = in_temp


def update_monthly(w_summary, w_monthly, out_temp, in_temp, now):
	# Calculate coordinates
	first_row = 2
	last_update = now.day
	row_number = last_update + first_row
	max_row = 31 + first_row
	last_row = int(w_summary.acell('D5').value) + first_row
	# Update the time
	w_monthly.update_acell('A' + str(row_number), now.day)
	### Fill all the lines between latest update and now, with temperature
	if last_row < row_number:
		while last_row < row_number:
			last_row += 1
			w_monthly.update_acell('B' + str(last_row), out_temp)
			w_monthly.update_acell('C' + str(last_row), in_temp)
	else:
		while last_row < max_row:
			last_row += 1
			w_monthly.update_acell('B' + str(last_row), out_temp)
			w_monthly.update_acell('C' + str(last_row), in_temp)
		last_row = first_row
		while last_row < row_number:
			last_row += 1
			w_monthly.update_acell('B' + str(last_row), out_temp)
			w_monthly.update_acell('C' + str(last_row), in_temp)
	# Save timestamp
	w_summary.update_acell('D5', last_update)

def update_weekly(w_summary, w_weekly, out_temp, in_temp, now):
	# Calculate coordinates
	first_row = 2
	last_update = int(now.strftime("%w"))
	row_number = last_update + first_row
	max_row = 7 + first_row
	last_row = int(w_summary.acell('D4').value) + first_row
	# Update the time
	w_weekly.update_acell('A' + str(row_number), now.strftime("%A"))
	### Fill all the lines between latest update and now, with temperature
	if last_row < row_number:
		w_summary.update_acell('D4', last_update)
		while last_row < row_number:
			last_row += 1
			w_weekly.update_acell('B' + str(last_row), out_temp)
			w_weekly.update_acell('C' + str(last_row), in_temp)
	else:
		if last_row == row_number:
			w_summary.update_acell('D4', last_update - 1)
		else:
			w_summary.update_acell('D4', last_update)
		while last_row < max_row:
			last_row += 1
			w_weekly.update_acell('B' + str(last_row), out_temp)
			w_weekly.update_acell('C' + str(last_row), in_temp)
		last_row = first_row
		while last_row < row_number:
			last_row += 1
			w_weekly.update_acell('B' + str(last_row), out_temp)
			w_weekly.update_acell('C' + str(last_row), in_temp)


def update_daily(w_summary, w_daily, out_temp, in_temp, now):
	# Calculate coordinates
	first_row = 2
	last_update = (now.hour * 60) + now.minute
	row_number = last_update + first_row
	max_row = 1439 + first_row
	last_row = int(w_summary.acell('D3').value) + first_row
	# Update the time
	w_daily.update_acell('A' + str(row_number), now.strftime("%H:%M"))
	### Fill all the lines between latest update and now, with temperature
	if last_row < row_number:
		while last_row < row_number:
			last_row += 1
			w_daily.update_acell('B' + str(last_row), out_temp)
			w_daily.update_acell('C' + str(last_row), in_temp)
	else:
		while last_row < max_row:
			last_row += 1
			w_daily.update_acell('B' + str(last_row), out_temp)
			w_daily.update_acell('C' + str(last_row), in_temp)
		last_row = first_row
		while last_row < row_number:
			last_row += 1
			w_daily.update_acell('B' + str(last_row), out_temp)
			w_daily.update_acell('C' + str(last_row), in_temp)
	# Save timestamp
	w_summary.update_acell('D3', last_update)

update_daily(w_summary, w_daily, out_temp, in_temp, now)
print('... Daily sheet updated')

###out_temp = w_summary.acell('B3').value
###in_temp = w_summary.acell('C3').value
###update_weekly(w_summary, w_weekly, out_temp, in_temp, now)
###print('... Weekly sheet updated')

###out_temp = w_summary.acell('B4').value
###in_temp = w_summary.acell('C4').value
###update_monthly(w_summary, w_monthly, out_temp, in_temp, now)
###print('... Monthly sheet updated')

print('Whole update is done')
