def calculate_angle(hour, minute):
    """Calculate the angle between the hour and minute hands of a clock."""
    
    if hour > 12:
        hour -= 12

    # Formula: (30 * hour) - (11/2) * minute
    angle = (30 * hour) - ((11 / 2) * minute)

    if angle < 0:
        print(angle * -1)
    else:
        print(angle)
