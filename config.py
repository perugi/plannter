# Hour in the day notifications are sent out
MAIL_NOTIFICATIONS_HOUR = 20

# Month third names in the format of 1_1, 1_2, 1_3, 2_1, ... , 12_3
VALID_MONTH_NAMES = []
for i in range(1, 13):
    for j in range(1, 4):
        VALID_MONTH_NAMES.append(f"todo_{i}_{j}")

WEEK_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

TASK_NAMES = {
    "S": "Sow for seedlings",
    "Pi": "Prepare seedlings",
    "Pr": "Transplant/Sow to garden",
    "R": "Plant growth",
    "P": "Harvest",
}
