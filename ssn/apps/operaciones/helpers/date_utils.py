import datetime
from typing import List, Tuple


def get_last_week_id(week_choices: List[Tuple[str, str]]) -> str:
    """
    Determina el identificador de la semana anterior a la actual.

    Args:
        week_choices: Lista de tuplas, donde cada tupla contiene:
                      [0]: Week identifier (e.g. "2025-15")
                      [1]: Date range (e.g. "14/04/2025 - 20/04/2025")

    Returns:
        El identificador de la semana anterior a la actual en formato "YYYY-NN".
        Si estamos en la primera semana o no se encuentra la semana actual,
        devuelve la primera semana disponible.
    """
    # Obtener la fecha actual
    today = datetime.date.today()

    # Buscar el índice de la semana actual
    current_week_index = -1
    for i, (week_id, date_range) in enumerate(week_choices):
        # Parsear el rango de fechas
        start_str, end_str = date_range.split(" - ")
        start_date = datetime.datetime.strptime(start_str, "%d/%m/%Y").date()
        end_date = datetime.datetime.strptime(end_str, "%d/%m/%Y").date()

        # Verificar si la fecha actual está dentro de este rango
        if start_date <= today <= end_date:
            current_week_index = i
            break

    # Si encontramos la semana actual y no es la primera, devolver la semana anterior
    if current_week_index > 0:
        return week_choices[current_week_index - 1][0]

    # Si estamos en la primera semana o no se encontró ninguna semana,
    # devolver la primera semana del calendario
    return week_choices[0][0] if week_choices else ""


def get_iso_week_range(
    year: int, week_number: int
) -> Tuple[datetime.date, datetime.date]:
    """
    Gets the start and end dates of a specific ISO week.

    ISO week starts on Monday and ends on Sunday according to ISO 8601 standard.

    Args:
        year: The ISO year to which the week belongs.
        week_number: The ISO week number (1-53).

    Returns:
        A tuple with start date (Monday) and end date (Sunday) of the week.

    Example:
        >>> start, end = get_iso_week_range(2025, 1)
        >>> print(start, end)
        2024-12-30 2025-01-05
    """
    # Create a date in the desired week (day 1 = Monday of that week)
    start_date = datetime.datetime.strptime(
        f"{year}-{week_number}-1", "%G-%V-%u"
    ).date()
    # The end of the week is 6 days later (Sunday)
    end_date = start_date + datetime.timedelta(days=6)

    return start_date, end_date


def format_week_option(
    year: int, week_counter: int, start_date: datetime.date, end_date: datetime.date
) -> List[str]:
    """
    Formats a week entry for the calendar.

    Args:
        year: The year to display in the week identifier.
        week_counter: The sequential week number.
        start_date: The start date of the week.
        end_date: The end date of the week.

    Returns:
        A list with two elements:
        - Week identifier in format "YYYY-NN"
        - Date range in format "dd/mm/yyyy - dd/mm/yyyy"
    """
    # Create the week identifier and date range
    week_id = f"{year}-{week_counter:02d}"
    date_range = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"

    return [week_id, date_range]


def generate_week_options(year: int) -> Tuple[List[str], ...]:
    """
    Generates a complete custom calendar for a specific year.

    The calendar consists of a tuple of lists, where each list contains:
    - Week identifier in format "YYYY-NN" where NN is the sequential number
    - Date range in format "dd/mm/yyyy - dd/mm/yyyy"

    The calendar starts with the first full week of the year (which may start in
    December of the previous year) and ends with the last week that includes
    days of the specified year (which may end in January of the following year).

    Args:
        year: The year for which to generate the calendar.

    Returns:
        A tuple of lists, each with two elements:
        - [0]: Week identifier in format "YYYY-NN"
        - [1]: Date range in format "dd/mm/yyyy - dd/mm/yyyy"

    Example:
        >>> calendar = generate_week_options(2025)
        >>> print(calendar[0])
        ['2025-01', '30/12/2024 - 05/01/2025']
    """
    # Initialize the calendar weeks list
    calendar_weeks = []
    week_counter = 1

    # Get the start date of the first ISO week of the year
    first_week_start, _ = get_iso_week_range(year, 1)

    # Determine which ISO week to start with based on whether the first week
    # begins in December of the previous year (in that case, start with week 2)
    starting_week = 2 if first_week_start.year < year else 1

    # Get the total number of ISO weeks in the year using December 28 date
    # This date always falls in the last ISO week of the year
    last_week = datetime.date(year, 12, 28).isocalendar()[1]

    # Generate the calendar weeks
    for iso_week in range(starting_week, last_week + 1):
        # Get the start and end dates
        start_date, end_date = get_iso_week_range(year, iso_week)
        # Add the week to the calendar
        calendar_weeks.append(
            format_week_option(year, week_counter, start_date, end_date)
        )
        week_counter += 1

    # Add the first week of the next year to complete the calendar
    next_year = year + 1
    start_date, end_date = get_iso_week_range(next_year, 1)
    calendar_weeks.append(format_week_option(year, week_counter, start_date, end_date))

    # Convert the list to a tuple to make it immutable
    return tuple(calendar_weeks)

def generate_monthly_options(year: int) -> Tuple[List[str], ...]:
    """
    Generates monthly options for a given year.
    
    The function returns a tuple of lists, where each list contains:
    - Month identifier in format "YYYY-MM"
    - Month name and year (e.g. "Enero 2025")
    
    Args:
        year: The year for which to generate the monthly options.
        
    Returns:
        A tuple of lists, each with two elements:
        - [0]: Month identifier in format "YYYY-MM"
        - [1]: Month name and year
        
    Example:
        >>> options = generate_monthly_options(2025)
        >>> print(options[0])
        ['2025-01', 'Enero 2025']
    """
    # Dictionary with Spanish month names
    month_names = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    
    options = []
    for month in range(1, 13):
        month_id = f"{year}-{month:02d}"
        month_label = f"{month_names[month]} {year}"
        options.append([month_id, month_label])
    
    return tuple(options)


def get_default_cronograma(tipo):
    """
    Devuelve el valor por defecto para el cronograma basado en el tipo.
    Para 'Semanal' toma la semana anterior y para 'Mensual' el mes anterior.

    Args:
        tipo (str): Tipo de cronograma ('Semanal' o 'Mensual').

    Returns:
        str: Valor por defecto para el cronograma en formato 'YYYY-WW' (semanal)
             o 'YYYY-MM' (mensual).
    """
    # Restamos 7 días para obtener la semana anterior
    current_date = datetime.date.today() - datetime.timedelta(days=7)
    if tipo == "Semanal":
        return f"{current_date.year}-{(current_date.isocalendar()[1] - 1):02d}"
    elif tipo == "Mensual":
        if current_date.month == 1:
            prev_month = 12
            prev_year = current_date.year - 1
        else:
            prev_month = current_date.month - 1
            prev_year = current_date.year
        return f"{prev_year}-{prev_month:02d}"
    return None
