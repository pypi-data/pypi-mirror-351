
    Zenbite dataset
    ----------------

    This is a real world dataset from Zenbite. Zenbite is a fast casual restaurant providing good service
    and food at short waiting times. The dataset contains the demand for the main ingredients at Zenbite.
    Moreover, it stores a number of demand features. These features include information about the day, month, year,
    lag demand, weather conditions and more. A full description of targets and features is given below.


    **Dataset Characteristics:**

        :Number of Instances: 714

        :Number of Targets: 7

        :Number of Features: 12

        :Target Information:
            - 'salmon' the demand for salmon
            - 'beef' the demand for beef
            - 'chicken' the demand for chicken
            - 'prawns' the demand for prawns
            - 'pork' the demand for pork
            - 'crabs' the demand for crabs
            - 'duck' the demand for duck
 

    :Feature Information:
        - 'date' the date,
        - 'weekday' the day of the week,
        - 'month' the month of the year,
        - 'year' the year,
        - 'is_holiday' whether or not it is a national holiday,
        - 'is_closed' whether or not the restaurant is closed,
        - 'weekend' whether or not it is weekend,
        - 'wind' the wind force,
        - 'clouds' the cloudiness degree,
        - 'rain' the amount of rain,
        - 'sunshine' the sunshine hours,
        - 'temperature' the outdoor temperature

    Note: By default the date feature is not included when loading the data. You can include it
    by setting the parameter `include_date` to `True`.

