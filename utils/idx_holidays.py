"""
Indonesian National Holidays and Market Closures
For IDX (Indonesia Stock Exchange) trading calendar
"""
from datetime import datetime, date

# IDX National Holidays 2026
# Source: Based on typical Indonesian national holidays
# Note: Some dates (especially religious holidays) may change based on official announcement
HOLIDAYS_2026 = [
    # Fixed Holidays
    date(2026, 1, 1),   # Tahun Baru Masehi (New Year)
    date(2026, 5, 1),   # Hari Buruh Internasional (Labor Day)
    date(2026, 6, 1),   # Hari Lahir Pancasila (Pancasila Day)
    date(2026, 8, 17),  # Hari Kemerdekaan RI (Independence Day)
    date(2026, 12, 25), # Hari Raya Natal (Christmas)

    # Religious Holidays (estimates - verify with official calendar!)
    # Tahun Baru Imlek (Chinese New Year)
    date(2026, 2, 17),

    # Hari Raya Nyepi (Balinese New Year)
    date(2026, 3, 21),

    # Wafat Isa Al-Masih (Good Friday)
    date(2026, 4, 3),

    # Kenaikan Isa Al-Masih (Ascension Day)
    date(2026, 5, 14),

    # Hari Raya Waisak (Vesak Day)
    date(2026, 5, 31),

    # Isra Mikraj Nabi Muhammad SAW
    date(2026, 2, 6),

    # Hari Raya Idul Fitri (Eid al-Fitr) - 2 days + cuti bersama
    date(2026, 3, 30),  # 1 Syawal
    date(2026, 3, 31),  # 2 Syawal
    date(2026, 3, 29),  # Cuti bersama (estimate)
    date(2026, 4, 1),   # Cuti bersama (estimate)
    date(2026, 4, 2),   # Cuti bersama (estimate)

    # Hari Raya Idul Adha (Eid al-Adha)
    date(2026, 6, 7),

    # Tahun Baru Islam 1 Muharram
    date(2026, 6, 27),

    # Maulid Nabi Muhammad SAW
    date(2026, 9, 5),
]

# IDX National Holidays 2025 (for reference if still in 2025)
HOLIDAYS_2025 = [
    # Fixed Holidays
    date(2025, 1, 1),   # Tahun Baru Masehi
    date(2025, 5, 1),   # Hari Buruh Internasional
    date(2025, 6, 1),   # Hari Lahir Pancasila
    date(2025, 8, 17),  # Hari Kemerdekaan RI
    date(2025, 12, 25), # Hari Raya Natal

    # Religious Holidays (2025)
    date(2025, 1, 29),  # Tahun Baru Imlek
    date(2025, 2, 12),  # Isra Mikraj
    date(2025, 3, 22),  # Hari Raya Nyepi
    date(2025, 3, 29),  # Wafat Isa Al-Masih
    date(2025, 3, 31),  # Idul Fitri (1 Syawal)
    date(2025, 4, 1),   # Idul Fitri (2 Syawal)
    date(2025, 3, 28),  # Cuti bersama
    date(2025, 4, 2),   # Cuti bersama
    date(2025, 4, 3),   # Cuti bersama
    date(2025, 4, 4),   # Cuti bersama
    date(2025, 5, 8),   # Kenaikan Isa Al-Masih
    date(2025, 5, 12),  # Hari Raya Waisak
    date(2025, 6, 6),   # Idul Adha
    date(2025, 6, 26),  # Tahun Baru Islam
    date(2025, 9, 4),   # Maulid Nabi Muhammad SAW
]

# Combined holidays dictionary
ALL_HOLIDAYS = {
    2025: HOLIDAYS_2025,
    2026: HOLIDAYS_2026,
}

def is_idx_holiday(check_date=None):
    """
    Check if a given date is an IDX national holiday

    Args:
        check_date: date object or None (uses today if None)

    Returns:
        tuple: (is_holiday: bool, holiday_name: str or None)
    """
    if check_date is None:
        check_date = datetime.now().date()

    if isinstance(check_date, datetime):
        check_date = check_date.date()

    year = check_date.year

    # Get holidays for the year
    holidays = ALL_HOLIDAYS.get(year, [])

    if check_date in holidays:
        # Try to identify the holiday name
        holiday_name = get_holiday_name(check_date)
        return True, holiday_name

    return False, None

def get_holiday_name(check_date):
    """
    Get the name of a holiday

    Args:
        check_date: date object

    Returns:
        str: Holiday name or "Hari Libur Nasional"
    """
    # Holiday names mapping
    holiday_names = {
        (1, 1): "Tahun Baru Masehi",
        (5, 1): "Hari Buruh Internasional",
        (6, 1): "Hari Lahir Pancasila",
        (8, 17): "Hari Kemerdekaan RI",
        (12, 25): "Hari Raya Natal",
    }

    month_day = (check_date.month, check_date.day)

    if month_day in holiday_names:
        return holiday_names[month_day]

    # Check for Idul Fitri period (late March to early April)
    if check_date.month == 3 and check_date.day >= 28:
        return "Libur Idul Fitri"
    if check_date.month == 4 and check_date.day <= 5:
        return "Libur Idul Fitri"

    # Check for common religious holidays by month
    if check_date.month == 2:
        if 10 <= check_date.day <= 20:
            return "Tahun Baru Imlek / Isra Mikraj"
    if check_date.month == 3 and 20 <= check_date.day <= 23:
        return "Hari Raya Nyepi"
    if check_date.month == 5:
        if 7 <= check_date.day <= 15:
            return "Kenaikan Isa Al-Masih / Waisak"
    if check_date.month == 6:
        if 1 <= check_date.day <= 10:
            return "Idul Adha"
        if 25 <= check_date.day <= 30:
            return "Tahun Baru Islam"
    if check_date.month == 9 and 1 <= check_date.day <= 7:
        return "Maulid Nabi Muhammad SAW"

    return "Hari Libur Nasional"

def get_next_trading_day(from_date=None):
    """
    Get the next trading day (skip weekends and holidays)

    Args:
        from_date: date object or None (uses today if None)

    Returns:
        date: Next trading day
    """
    from datetime import timedelta

    if from_date is None:
        current = datetime.now().date()
    elif isinstance(from_date, datetime):
        current = from_date.date()
    else:
        current = from_date

    # Start from tomorrow
    current = current + timedelta(days=1)

    max_iterations = 30  # Safety limit
    iterations = 0

    while iterations < max_iterations:
        # Check if weekend (Saturday=5, Sunday=6)
        weekday = current.weekday()
        if weekday >= 5:  # Weekend
            current = current + timedelta(days=1)
            iterations += 1
            continue

        # Check if holiday
        is_holiday, _ = is_idx_holiday(current)
        if is_holiday:
            current = current + timedelta(days=1)
            iterations += 1
            continue

        # Found a trading day!
        return current

    # Fallback (shouldn't happen)
    return current

def get_holidays_in_month(year, month):
    """
    Get all holidays in a specific month

    Args:
        year: int
        month: int (1-12)

    Returns:
        list: List of date objects for holidays in that month
    """
    holidays = ALL_HOLIDAYS.get(year, [])

    month_holidays = [
        d for d in holidays
        if d.month == month
    ]

    return sorted(month_holidays)

def is_trading_day(check_date=None):
    """
    Check if a date is a trading day (not weekend, not holiday)

    Args:
        check_date: date object or None (uses today if None)

    Returns:
        bool: True if trading day, False otherwise
    """
    if check_date is None:
        check_date = datetime.now().date()

    if isinstance(check_date, datetime):
        check_date = check_date.date()

    # Check weekend
    if check_date.weekday() >= 5:
        return False

    # Check holiday
    is_holiday, _ = is_idx_holiday(check_date)
    if is_holiday:
        return False

    return True

# Add holidays for future years (template)
def add_holiday(year, month, day, description=""):
    """
    Add a new holiday to the calendar

    Args:
        year: int
        month: int
        day: int
        description: str (optional)
    """
    new_date = date(year, month, day)

    if year not in ALL_HOLIDAYS:
        ALL_HOLIDAYS[year] = []

    if new_date not in ALL_HOLIDAYS[year]:
        ALL_HOLIDAYS[year].append(new_date)
        ALL_HOLIDAYS[year].sort()
        print(f"✅ Added holiday: {new_date} - {description}")
    else:
        print(f"⚠️ Holiday already exists: {new_date}")

if __name__ == "__main__":
    # Test the holiday checker
    print("="*60)
    print("IDX HOLIDAY CHECKER")
    print("="*60)

    # Check today
    today = datetime.now().date()
    is_holiday, name = is_idx_holiday(today)

    print(f"\nToday: {today.strftime('%A, %d %B %Y')}")
    print(f"Is Holiday: {is_holiday}")
    if is_holiday:
        print(f"Holiday Name: {name}")

    # Check if trading day
    is_trading = is_trading_day(today)
    print(f"Is Trading Day: {is_trading}")

    # Get next trading day
    next_trading = get_next_trading_day(today)
    print(f"Next Trading Day: {next_trading.strftime('%A, %d %B %Y')}")

    # Show all holidays this year
    year = today.year
    print(f"\n{'='*60}")
    print(f"ALL HOLIDAYS {year}")
    print(f"{'='*60}")

    holidays = ALL_HOLIDAYS.get(year, [])
    for holiday in sorted(holidays):
        is_h, name = is_idx_holiday(holiday)
        print(f"{holiday.strftime('%A, %d %B %Y'):40} - {name}")

    print(f"\nTotal holidays: {len(holidays)}")
