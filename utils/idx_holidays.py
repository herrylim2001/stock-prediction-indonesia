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

# IDX National Holidays 2027 (estimates - verify with official calendar)
HOLIDAYS_2027 = [
    # Fixed Holidays
    date(2027, 1, 1),   # Tahun Baru Masehi
    date(2027, 5, 1),   # Hari Buruh Internasional
    date(2027, 6, 1),   # Hari Lahir Pancasila
    date(2027, 8, 17),  # Hari Kemerdekaan RI
    date(2027, 12, 25), # Hari Raya Natal

    # Religious Holidays (estimates based on lunar calendar)
    date(2027, 2, 6),   # Tahun Baru Imlek (Chinese New Year)
    date(2027, 1, 16),  # Isra Mikraj Nabi Muhammad SAW
    date(2027, 3, 11),  # Hari Raya Nyepi (Balinese New Year)
    date(2027, 4, 18),  # Wafat Isa Al-Masih (Good Friday)
    date(2027, 5, 27),  # Kenaikan Isa Al-Masih (Ascension Day)
    date(2027, 5, 20),  # Hari Raya Waisak (Vesak Day)

    # Hari Raya Idul Fitri (Eid al-Fitr) + Cuti Bersama
    date(2027, 3, 9),   # Cuti bersama (estimate)
    date(2027, 3, 10),  # Cuti bersama (estimate)
    date(2027, 3, 11),  # Idul Fitri 1 Syawal
    date(2027, 3, 12),  # Idul Fitri 2 Syawal
    date(2027, 3, 15),  # Cuti bersama (estimate)
    date(2027, 3, 16),  # Cuti bersama (estimate)

    # Hari Raya Idul Adha
    date(2027, 5, 18),  # Idul Adha (10 Dzulhijjah)

    # Tahun Baru Islam
    date(2027, 6, 7),   # Tahun Baru Islam 1 Muharram

    # Maulid Nabi Muhammad SAW
    date(2027, 8, 16),  # Maulid Nabi Muhammad SAW (12 Rabiul Awal)
]

# IDX National Holidays 2028 (estimates - verify with official calendar)
HOLIDAYS_2028 = [
    # Fixed Holidays
    date(2028, 1, 1),   # Tahun Baru Masehi
    date(2028, 5, 1),   # Hari Buruh Internasional
    date(2028, 6, 1),   # Hari Lahir Pancasila
    date(2028, 8, 17),  # Hari Kemerdekaan RI
    date(2028, 12, 25), # Hari Raya Natal

    # Religious Holidays (estimates)
    date(2028, 1, 26),  # Tahun Baru Imlek
    date(2028, 1, 5),   # Isra Mikraj Nabi Muhammad SAW
    date(2028, 3, 30),  # Hari Raya Nyepi
    date(2028, 4, 14),  # Wafat Isa Al-Masih (Good Friday)
    date(2028, 5, 25),  # Kenaikan Isa Al-Masih
    date(2028, 5, 9),   # Hari Raya Waisak

    # Hari Raya Idul Fitri + Cuti Bersama
    date(2028, 2, 24),  # Cuti bersama (estimate)
    date(2028, 2, 25),  # Cuti bersama (estimate)
    date(2028, 2, 28),  # Idul Fitri 1 Syawal
    date(2028, 2, 29),  # Idul Fitri 2 Syawal
    date(2028, 3, 1),   # Cuti bersama (estimate)
    date(2028, 3, 2),   # Cuti bersama (estimate)

    # Hari Raya Idul Adha
    date(2028, 5, 6),   # Idul Adha

    # Tahun Baru Islam
    date(2028, 5, 26),  # Tahun Baru Islam 1 Muharram

    # Maulid Nabi Muhammad SAW
    date(2028, 8, 4),   # Maulid Nabi Muhammad SAW
]

# IDX National Holidays 2029 (estimates - verify with official calendar)
HOLIDAYS_2029 = [
    # Fixed Holidays
    date(2029, 1, 1),   # Tahun Baru Masehi
    date(2029, 5, 1),   # Hari Buruh Internasional
    date(2029, 6, 1),   # Hari Lahir Pancasila
    date(2029, 8, 17),  # Hari Kemerdekaan RI
    date(2029, 12, 25), # Hari Raya Natal

    # Religious Holidays (estimates)
    date(2029, 2, 13),  # Tahun Baru Imlek
    date(2029, 12, 24), # Isra Mikraj (2028 calendar, carries to 2029)
    date(2029, 3, 19),  # Hari Raya Nyepi
    date(2029, 3, 30),  # Wafat Isa Al-Masih
    date(2029, 5, 10),  # Kenaikan Isa Al-Masih
    date(2029, 5, 28),  # Hari Raya Waisak

    # Hari Raya Idul Fitri + Cuti Bersama
    date(2029, 2, 13),  # Cuti bersama (estimate)
    date(2029, 2, 14),  # Cuti bersama (estimate)
    date(2029, 2, 15),  # Idul Fitri 1 Syawal
    date(2029, 2, 16),  # Idul Fitri 2 Syawal
    date(2029, 2, 19),  # Cuti bersama (estimate)
    date(2029, 2, 20),  # Cuti bersama (estimate)

    # Hari Raya Idul Adha
    date(2029, 4, 24),  # Idul Adha

    # Tahun Baru Islam
    date(2029, 5, 15),  # Tahun Baru Islam 1 Muharram

    # Maulid Nabi Muhammad SAW
    date(2029, 7, 25),  # Maulid Nabi Muhammad SAW
]

# Combined holidays dictionary
ALL_HOLIDAYS = {
    2025: HOLIDAYS_2025,
    2026: HOLIDAYS_2026,
    2027: HOLIDAYS_2027,
    2028: HOLIDAYS_2028,
    2029: HOLIDAYS_2029,
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
    Get the name of a holiday with detailed mapping

    Args:
        check_date: date object

    Returns:
        str: Holiday name or "Hari Libur Nasional"
    """
    # Fixed holidays mapping (same date every year)
    fixed_holidays = {
        (1, 1): "Tahun Baru Masehi",
        (5, 1): "Hari Buruh Internasional",
        (6, 1): "Hari Lahir Pancasila",
        (8, 17): "Hari Kemerdekaan Republik Indonesia",
        (12, 25): "Hari Raya Natal",
    }

    month_day = (check_date.month, check_date.day)

    if month_day in fixed_holidays:
        return fixed_holidays[month_day]

    # Get all holidays for the year
    year_holidays = ALL_HOLIDAYS.get(check_date.year, [])

    # Detailed mapping for religious holidays
    # These dates change yearly based on lunar calendar

    # Idul Fitri detection (usually late Feb to early April)
    if check_date.month in [2, 3, 4]:
        for h in year_holidays:
            if h.month == check_date.month:
                # Check if within Idul Fitri period (±5 days from any Idul Fitri date)
                if abs((check_date - h).days) <= 5 and h.month in [2, 3, 4]:
                    if h.day == check_date.day:
                        return "Hari Raya Idul Fitri"
                    elif check_date < h:
                        return "Cuti Bersama Idul Fitri"
                    else:
                        return "Libur Idul Fitri"

    # Tahun Baru Imlek (Chinese New Year) - usually late Jan to mid Feb
    if check_date.month in [1, 2] and 15 <= check_date.day <= 20 and check_date in year_holidays:
        return "Tahun Baru Imlek"

    # Isra Mikraj - varies by year
    if check_date in year_holidays:
        if check_date.month in [1, 2, 12] and 1 <= check_date.day <= 31:
            # Check if it's likely Isra Mikraj
            other_matches = [fixed_holidays.get(month_day),
                           "Tahun Baru Imlek" if check_date.month in [1,2] else None]
            if not any(other_matches):
                return "Isra Mikraj Nabi Muhammad SAW"

    # Nyepi (Balinese New Year) - usually March
    if check_date.month == 3 and 10 <= check_date.day <= 31 and check_date in year_holidays:
        return "Hari Raya Nyepi (Tahun Baru Saka)"

    # Wafat Isa Al-Masih (Good Friday) - usually March/April
    if check_date.month in [3, 4] and check_date in year_holidays:
        # Check if it's a Friday and likely Good Friday
        if check_date.weekday() == 4:  # Friday
            return "Wafat Isa Al-Masih (Jumat Agung)"

    # Kenaikan Isa Al-Masih (Ascension Day) - usually May
    if check_date.month == 5 and 1 <= check_date.day <= 31 and check_date in year_holidays:
        if check_date.weekday() == 3:  # Thursday
            return "Kenaikan Isa Al-Masih"

    # Waisak - usually May
    if check_date.month == 5 and 1 <= check_date.day <= 31 and check_date in year_holidays:
        return "Hari Raya Waisak"

    # Idul Adha - varies by year
    if check_date.month in [5, 6, 7] and check_date in year_holidays:
        return "Hari Raya Idul Adha"

    # Tahun Baru Islam (1 Muharram) - varies by year
    if check_date.month in [6, 7, 8] and check_date in year_holidays:
        return "Tahun Baru Islam 1 Muharram"

    # Maulid Nabi Muhammad SAW - varies by year
    if check_date.month in [8, 9, 10] and check_date in year_holidays:
        return "Maulid Nabi Muhammad SAW"

    # Generic cuti bersama
    if check_date in year_holidays:
        return "Cuti Bersama"

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

def get_trading_days_count(year, month):
    """
    Get the number of trading days in a specific month

    Args:
        year: int
        month: int (1-12)

    Returns:
        int: Number of trading days
    """
    from calendar import monthrange

    # Get number of days in month
    _, num_days = monthrange(year, month)

    trading_days = 0

    for day in range(1, num_days + 1):
        check_date = date(year, month, day)
        if is_trading_day(check_date):
            trading_days += 1

    return trading_days

def get_trading_days_in_range(start_date, end_date):
    """
    Get list of all trading days between two dates

    Args:
        start_date: date object
        end_date: date object

    Returns:
        list: List of trading days (date objects)
    """
    from datetime import timedelta

    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()

    trading_days = []
    current = start_date

    while current <= end_date:
        if is_trading_day(current):
            trading_days.append(current)
        current = current + timedelta(days=1)

    return trading_days

def get_upcoming_holidays(days_ahead=30):
    """
    Get upcoming holidays in the next N days

    Args:
        days_ahead: int (number of days to look ahead)

    Returns:
        list: List of tuples (date, holiday_name)
    """
    from datetime import timedelta

    today = datetime.now().date()
    end_date = today + timedelta(days=days_ahead)

    upcoming = []

    current = today
    while current <= end_date:
        is_holiday, name = is_idx_holiday(current)
        if is_holiday:
            upcoming.append((current, name))
        current = current + timedelta(days=1)

    return upcoming

def is_long_weekend(check_date=None):
    """
    Check if a date is part of a long weekend (3+ consecutive non-trading days)

    Args:
        check_date: date object or None

    Returns:
        tuple: (is_long_weekend: bool, duration: int)
    """
    from datetime import timedelta

    if check_date is None:
        check_date = datetime.now().date()

    if isinstance(check_date, datetime):
        check_date = check_date.date()

    # Count consecutive non-trading days around this date
    consecutive_days = 0

    # Go backwards
    current = check_date
    while not is_trading_day(current):
        consecutive_days += 1
        current = current - timedelta(days=1)
        if consecutive_days > 7:  # Safety limit
            break

    # Go forwards
    current = check_date + timedelta(days=1)
    while not is_trading_day(current):
        consecutive_days += 1
        current = current + timedelta(days=1)
        if consecutive_days > 7:  # Safety limit
            break

    is_long = consecutive_days >= 3

    return is_long, consecutive_days

def get_holiday_stats(year):
    """
    Get statistics about holidays and trading days for a year

    Args:
        year: int

    Returns:
        dict: Holiday statistics
    """
    from calendar import monthrange

    holidays = ALL_HOLIDAYS.get(year, [])

    # Total days in year
    total_days = 366 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 365

    # Count weekends
    weekends = 0
    for month in range(1, 13):
        _, num_days = monthrange(year, month)
        for day in range(1, num_days + 1):
            check_date = date(year, month, day)
            if check_date.weekday() >= 5:
                weekends += 1

    # Count holidays (excluding weekends)
    weekday_holidays = 0
    for holiday in holidays:
        if holiday.weekday() < 5:  # Not weekend
            weekday_holidays += 1

    # Trading days
    trading_days = total_days - weekends - weekday_holidays

    return {
        'year': year,
        'total_days': total_days,
        'weekends': weekends,
        'total_holidays': len(holidays),
        'weekday_holidays': weekday_holidays,
        'trading_days': trading_days,
        'trading_days_pct': (trading_days / total_days) * 100
    }

if __name__ == "__main__":
    # Test the holiday checker
    print("="*70)
    print("IDX HOLIDAY CHECKER & TRADING CALENDAR")
    print("="*70)

    # Check today
    today = datetime.now().date()
    is_holiday, name = is_idx_holiday(today)

    print(f"\n📅 TODAY: {today.strftime('%A, %d %B %Y')}")
    print(f"   Is Holiday: {'YES ❌' if is_holiday else 'NO ✅'}")
    if is_holiday:
        print(f"   Holiday Name: {name}")

    # Check if trading day
    is_trading = is_trading_day(today)
    print(f"   Is Trading Day: {'YES 📈' if is_trading else 'NO 🚫'}")

    # Long weekend check
    is_long, duration = is_long_weekend(today)
    if is_long:
        print(f"   🏖️  Part of LONG WEEKEND ({duration} days)")

    # Get next trading day
    next_trading = get_next_trading_day(today)
    print(f"\n📈 Next Trading Day: {next_trading.strftime('%A, %d %B %Y')}")

    # Upcoming holidays
    print(f"\n{'='*70}")
    print("🎊 UPCOMING HOLIDAYS (Next 60 days)")
    print(f"{'='*70}")

    upcoming = get_upcoming_holidays(60)
    if upcoming:
        for hol_date, hol_name in upcoming:
            days_until = (hol_date - today).days
            print(f"{hol_date.strftime('%A, %d %B %Y'):35} - {hol_name:30} ({days_until} days)")
    else:
        print("No upcoming holidays in the next 60 days")

    # Show all holidays this year
    year = today.year
    print(f"\n{'='*70}")
    print(f"📋 ALL HOLIDAYS {year}")
    print(f"{'='*70}")

    holidays = ALL_HOLIDAYS.get(year, [])
    for holiday in sorted(holidays):
        is_h, name = is_idx_holiday(holiday)
        day_name = holiday.strftime('%A')
        emoji = "🔴" if holiday.weekday() < 5 else "⚪"  # Red for weekday holidays
        print(f"{emoji} {holiday.strftime('%d %b %Y'):15} ({day_name:10}) - {name}")

    print(f"\n   Total holidays: {len(holidays)}")

    # Year statistics
    print(f"\n{'='*70}")
    print(f"📊 TRADING CALENDAR STATISTICS {year}")
    print(f"{'='*70}")

    stats = get_holiday_stats(year)
    print(f"   Total days in year: {stats['total_days']}")
    print(f"   Weekends (Sat-Sun): {stats['weekends']}")
    print(f"   National holidays: {stats['total_holidays']}")
    print(f"   Weekday holidays: {stats['weekday_holidays']}")
    print(f"   📈 TRADING DAYS: {stats['trading_days']} ({stats['trading_days_pct']:.1f}%)")

    # Monthly trading days
    print(f"\n{'='*70}")
    print(f"📅 TRADING DAYS PER MONTH {year}")
    print(f"{'='*70}")

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for month in range(1, 13):
        trading_days = get_trading_days_count(year, month)
        month_holidays = get_holidays_in_month(year, month)
        print(f"   {month_names[month-1]} {year}: {trading_days:2} trading days ({len(month_holidays)} holidays)")

    print(f"\n{'='*70}")
    print("✅ Holiday checker test completed!")
    print(f"{'='*70}")
