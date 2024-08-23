def format_date(date_obj):
    # Get the day of the month
    day = date_obj.day
    
    # Determine the ordinal suffix
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    
    # Format the date string with the day and suffix
    formatted_date = date_obj.strftime(f"%A {day}{suffix} %B %Y")
    
    return formatted_date