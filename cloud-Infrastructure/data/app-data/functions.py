def determine_velocity(age, gender):
    velocity = 1.36
    age = int(age)
    if gender == 'male':
        if age >= 20 and age <= 29:
            velocity = 1.36
        elif age >= 30 and age <= 39:
            velocity = 1.43
        elif age >= 40 and age <= 49:
            velocity = 1.43
        elif age >= 50 and age <= 59:
            velocity = 1.43
        elif age >= 60 and age <= 69:
            velocity = 1.34
        elif age >= 70 and age <= 79:
            velocity = 1.26
        elif age >= 30 and age <= 39:
            velocity = 0.97
    else:
        if age >= 20 and age <= 29:
            velocity = 1.34
        elif age >= 30 and age <= 39:
            velocity = 1.34
        elif age >= 40 and age <= 49:
            velocity = 1.39
        elif age >= 50 and age <= 59:
            velocity = 1.31
        elif age >= 60 and age <= 69:
            velocity = 1.24
        elif age >= 70 and age <= 79:
            velocity = 1.13
        elif age >= 30 and age <= 39:
            velocity = 0.94
    return velocity
