# google_sheet python module

import gspread
import datetime
import w1_term
import my_config

gc = gspread.login(google_login, google_password)
wks = gc.open(google_sheet_name).sheet1

now = datetime.datetime.now()

wks.update_acell('B2', float(w1_term.Therm(out_sensor).getDegrees()) / 1000)
wks.update_acell('C2', float(w1_term.Therm(in_sensor).getDegrees()) / 1000)
wks.update_acell('D2', now.strftime("%Y-%m-%d\n%H:%M"))
