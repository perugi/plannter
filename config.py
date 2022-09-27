import os

# Hour in the day notifications are sent out
MAIL_NOTIFICATIONS_HOUR = 22

# Month third names in the format of 1_1, 1_2, 1_3, 2_1, ... , 12_3
VALID_MONTH_NAMES = []
for i in range(1, 13):
    for j in range(1, 4):
        VALID_MONTH_NAMES.append(f"todo_{i}_{j}")

WEEK_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

TASK_NAMES = {
    "S": {"en": "Sow for seedlings", "si": "Setev za vzgojo sadik"},
    "Pi": {"en": "Prepare seedlings", "si": "Pikiranje sadik"},
    "Pr": {"en": "Transplant/Sow to garden", "si": "Presajanje ali setev na gredo"},
    "R": {"en": "Plant growth", "si": "Rast"},
    "P": {"en": "Harvest", "si": "Pridelek"},
}

# Configure the app to use the Heroku Postgres database.
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")


class Config:
    # Ensure templates are auto-reloaded
    TEMPLATES_AUTO_RELOAD = True

    # Configure session to use filesystem (instead of signed cookies)
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    # Configure the app for sending mail using gmail.
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # Configure the app to use the APscheduler
    SCHEDULER_API_ENABLED = True
