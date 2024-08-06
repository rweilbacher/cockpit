import swisseph as swe
from datetime import datetime, date, timedelta
from dataclasses import dataclass

# TODO sorting (planet, sign, type, orb)
# TODO make signs optional
# TODO add imaginary elements like mid heaven and ascendant
# TODO add calculation of date ranges for transits
# TODO create .ics file out of those date ranges

ORB_RANGE = 5

SIGNS = [
    'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
    'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
]

PLANETS = {
    'Sun': 0, 'Moon': 1, 'Mercury': 2, 'Venus': 3, 'Mars': 4,
    'Jupiter': 5, 'Saturn': 6, 'Uranus': 7, 'Neptune': 8, 'Pluto': 9
}

ASPECTS = {
    0: 'conjunct', 60: 'sextile', 90: 'square', 120: 'trine', 180: 'opposite'
}


@dataclass
class TransitAspect:
    trans_planet: str
    trans_sign: str
    aspect_type: str
    natal_planet: str
    natal_sign: str
    orb: float
    applying: bool

    def __str__(self):
        return f"({self.trans_sign}) {self.trans_planet} {self.aspect_type} {self.natal_planet} ({self.natal_sign}) | {'+' if self.orb > 0 else ''}{self.orb:.2f}°’{'A' if self.applying else 'S'}"


class SwissEphWrapper:
    def __init__(self, ephe_path='./ephemeris'):
        swe.set_ephe_path(ephe_path)

    def _to_jd(self, date):
        return swe.julday(date.year, date.month, date.day, date.hour + date.minute / 60)

    def get_planet(self, jd, planet):
        try:
            planet_id = PLANETS[planet]
            result, flag = swe.calc_ut(jd, planet_id)

            if not isinstance(result, tuple) or len(result) < 6:
                raise ValueError(
                    f"Unexpected result from swe.calc_ut for planet {planet}. Expected tuple of 6 elements, got: {result}")

            lon = result[0]
            sign = SIGNS[int(lon / 30)]
            degree = lon % 30
            return PlanetInfo(planet, sign, degree)
        except Exception as e:
            print(f"Error calculating position for {planet} at JD {jd}: {str(e)}")
            raise

    def aspect(self, planet1, planet2, orb=ORB_RANGE):
        angle = (planet2.longitude - planet1.longitude + 180) % 360 - 180
        for asp_angle, asp_type in ASPECTS.items():
            if abs(angle - asp_angle) <= orb:
                return AspectInfo(asp_type, angle - asp_angle, angle < asp_angle)
        return None

    def close(self):
        swe.close()


class PlanetInfo:
    def __init__(self, name, sign, degree):
        self.name = name
        self.sign = sign
        self.degree = degree
        self.longitude = (SIGNS.index(sign) * 30) + degree

    @property
    def lon(self):
        return self.longitude


class AspectInfo:
    def __init__(self, type, orb, applying):
        self.type = type
        self.orb = orb
        self.applying = applying


class Chart:
    def __init__(self, date, lat, lon):
        self.date = date
        self.lat = lat
        self.lon = lon
        self.jd = SwissEphWrapper()._to_jd(date)
        self.wrapper = SwissEphWrapper()

    def get(self, planet):
        return self.wrapper.get_planet(self.jd, planet)


def calculate_daily_aspects_and_signs(start_date, end_date, birth_data):
    birth_datetime, lat, lon = birth_data
    birth_chart = Chart(birth_datetime, lat, lon)
    wrapper = SwissEphWrapper()

    daily_aspects = []
    current_date = start_date
    while current_date <= end_date:
        transit_chart = Chart(datetime.combine(current_date, datetime.min.time()), lat, lon)

        # Calculate aspects
        aspects = []
        for trans_planet in PLANETS:
            for natal_planet in PLANETS:
                trans_obj = transit_chart.get(trans_planet)
                natal_obj = birth_chart.get(natal_planet)
                aspect = wrapper.aspect(trans_obj, natal_obj)
                if aspect:
                    aspects.append(TransitAspect(
                        trans_planet, trans_obj.sign, aspect.type,
                        natal_planet, natal_obj.sign, aspect.orb, aspect.applying
                    ))

        daily_aspects.append((current_date, aspects))
        current_date += timedelta(days=1)
    wrapper.close()
    return daily_aspects


def print_aligned_transits(day, aspects):
    if not aspects:
        print(f"### {day}")
        print("No aspects found.")
        print()
        return

    # Find the maximum length of the aspect descriptions
    max_length = max(len(f"({aspect.trans_sign}) {aspect.trans_planet} {aspect.aspect_type} {aspect.natal_planet} ({aspect.natal_sign})") for aspect in aspects)

    print(f"### {day}")
    for aspect in aspects:
        aspect_desc = f"({aspect.trans_sign}) {aspect.trans_planet} {aspect.aspect_type} {aspect.natal_planet} ({aspect.natal_sign})"
        padding = " " * (max_length - len(aspect_desc))
        print(f"{aspect_desc}{padding} | {'+' if aspect.orb > 0 else ''}{aspect.orb:.2f}°’{'A' if aspect.applying else 'S'}")
    print()


# Example usage
with open("birthdata.txt", "r") as file:
    raw_data = file.read().split("\n")
    birth_datetime = datetime.fromisoformat(raw_data[0])
    lat = float(raw_data[1])
    lon = float(raw_data[2])
    birth_data = (birth_datetime, lat, lon)
    start_date = date(2024, 8, 6)
    end_date = date(2024, 8, 31)
    daily_aspects = calculate_daily_aspects_and_signs(start_date, end_date, birth_data)
    for day, aspects in daily_aspects:
        print_aligned_transits(day, aspects)