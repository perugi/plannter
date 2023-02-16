# Hour in the day notifications are sent out
MAIL_NOTIFICATIONS_HOUR = 20
MAIL_NOTIFICATIONS_MINUTE = 0

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

LANGUAGES = [
    ("en", "English"),
    ("si", "Slovenian"),
]
