import re
from datetime import datetime


class Vin:
    def __init__(self, vin):
        self.vin = vin

    def check(self):
        if not re.fullmatch(r"^[A-HJ-NPR-Z0-9]{17}$", self.vin):
            return False
        else:
            return True

    def year(self):
        year_code = self.vin[9]
        current_year = datetime.now().year

        year_map = {
            "A": 1980,
            "B": 1981,
            "C": 1982,
            "D": 1983,
            "E": 1984,
            "F": 1985,
            "G": 1986,
            "H": 1987,
            "J": 1988,
            "K": 1989,
            "L": 1990,
            "M": 1991,
            "N": 1992,
            "P": 1993,
            "R": 1994,
            "S": 1995,
            "T": 1996,
            "V": 1997,
            "W": 1998,
            "X": 1999,
            "Y": 2000,
            "1": 2001,
            "2": 2002,
            "3": 2003,
            "4": 2004,
            "5": 2005,
            "6": 2006,
            "7": 2007,
            "8": 2008,
            "9": 2009,
        }

        if year_code not in year_map:
            return None

        base_year = year_map[year_code]

        while base_year + 30 <= current_year:
            base_year += 30

        return base_year

    def serial_number(self):
        return self.vin[11:]

    def summary(self):
        return {
            "vin": self.vin,
            "valid": self.check(),
            "country": self.country(),
            "year": self.year(),
            "serial_number": self.serial_number(),
        }

    def __getattr__(self, item):
        raise AttributeError(f"'Vin' object has no attribute '{item}'")
