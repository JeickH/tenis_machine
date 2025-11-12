from datetime import datetime, timedelta

def parse_date(date_str):
    if isinstance(date_str, datetime):
        return date_str.date()

    formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")

def get_date_range(period):
    today = datetime.now().date()

    if period == "last_day":
        return today - timedelta(days=1), today
    elif period == "last_week":
        return today - timedelta(days=7), today
    elif period == "last_15_days":
        return today - timedelta(days=15), today
    elif period == "last_month":
        return today - timedelta(days=30), today
    else:
        raise ValueError(f"Unknown period: {period}")

def is_today(date):
    if isinstance(date, str):
        date = parse_date(date)
    return date == datetime.now().date()

def is_yesterday(date):
    if isinstance(date, str):
        date = parse_date(date)
    return date == (datetime.now().date() - timedelta(days=1))

def get_yesterday():
    return datetime.now().date() - timedelta(days=1)

def get_today():
    return datetime.now().date()
