from datetime import date , timedelta

today  = date.today()
days_later = today + timedelta(days=10)

print(days_later)
