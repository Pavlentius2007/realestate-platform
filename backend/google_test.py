from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 👇 путь к твоему JSON-файлу
GOOGLE_CREDENTIALS = "fastapi-users-462815-d6c34495b9cd.json"
GOOGLE_SHEET_NAME = "UserRegistrations"

def test_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1

    # Тестовые данные
    sheet.append_row([
        "test@example.com",
        "Иван Тестович",
        "+79001234567",
        "Тестовая регистрация",
        datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    ])
    print("✅ Данные успешно отправлены в Google Sheets!")

if __name__ == "__main__":
    test_google_sheets()
