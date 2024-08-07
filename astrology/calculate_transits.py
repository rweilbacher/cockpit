import swisseph as swe
from datetime import datetime, date, timedelta, time
from dataclasses import dataclass, field
from icalendar import Calendar, Event

# TODO add calculations for a single day also involving moon etc.
# TODO improve applying calculation (or not. seems like kind of a pain in the ass)
# TODO choose better orb limits (or not. seems mostly fine)

# TODO add imaginary elements like mid heaven and ascendant
# TODO make signs optional
# TODO sorting (planet, sign, type, orb)

ORB_RANGE = 6

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

PLANET_SYMBOLS = {
    'Sun': '☉',
    'Moon': '☽',
    'Mercury': '☿',
    'Venus': '♀',
    'Mars': '♂',
    'Jupiter': '♃',
    'Saturn': '♄',
    'Uranus': '♅',
    'Neptune': '♆',
    'Pluto': '♇'
}

ASPECT_SYMBOLS = {
    'conjunct': '☌',
    'sextile': '⚹',
    'square': '□',
    'trine': '△',
    'opposite': '☍'
}


@dataclass
class TransitAspect:
    natal_planet: str
    natal_sign: str
    aspect_type: str
    trans_planet: str
    trans_sign: str
    orb: float
    applying: bool

    def __str__(self):
        return f"({self.natal_sign}) {self.natal_planet} {self.aspect_type} {self.trans_planet} ({self.trans_sign}) | {'+' if self.orb > 0 else ''}{self.orb:.2f}°'{'A' if self.applying else 'S'}"


@dataclass
class Transit:
    natal_planet: str
    natal_sign: str
    aspect_type: str
    trans_planet: str
    trans_sign: str
    start_date: date
    end_date: date = None
    daily_orbs: dict = field(default_factory=dict)


class SwissEphWrapper:
    def __init__(self, ephe_path='./ephemeris'):
        swe.set_ephe_path(ephe_path)

    def _to_jd(self, date_or_datetime):
        if isinstance(date_or_datetime, date) and not isinstance(date_or_datetime, datetime):
            date_or_datetime = datetime.combine(date_or_datetime, time())
        return swe.julday(date_or_datetime.year, date_or_datetime.month, date_or_datetime.day,
                          date_or_datetime.hour + date_or_datetime.minute / 60)

    def get_planet_position(self, date_or_datetime, planet):
        jd = self._to_jd(date_or_datetime)
        return self.get_planet(jd, planet)

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
            return PlanetInfo(planet, sign, degree, lon)
        except Exception as e:
            print(f"Error calculating position for {planet} at JD {jd}: {str(e)}")
            raise

    def aspect(self, planet1, planet2, orb=ORB_RANGE):
        angle = abs((planet2.longitude - planet1.longitude + 180) % 360 - 180)
        for asp_angle, asp_type in ASPECTS.items():
            if abs(angle - asp_angle) <= orb:
                return AspectInfo(asp_type, angle - asp_angle, angle < asp_angle)
        return None

    def close(self):
        swe.close()


class PlanetInfo:
    def __init__(self, name, sign, degree, longitude):
        self.name = name
        self.sign = sign
        self.degree = degree
        self.longitude = longitude

    @property
    def lon(self):
        return self.longitude

    def __str__(self):
        return f"{self.name} in {self.sign} at {self.degree}"


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
        for natal_planet in PLANETS:
            if natal_planet == "Moon":
                # Skip the moon as natal planet because it moves too fast to be considered on a full day basis
                continue
            for trans_planet in PLANETS:
                if trans_planet == "Moon":
                    continue
                natal_obj = birth_chart.get(natal_planet)
                trans_obj = transit_chart.get(trans_planet)
                aspect = wrapper.aspect(natal_obj, trans_obj)
                if aspect:
                    aspects.append(TransitAspect(
                        natal_planet, natal_obj.sign, aspect.type,
                        trans_planet, trans_obj.sign, aspect.orb, aspect.applying
                    ))

        daily_aspects.append((current_date, aspects))
        current_date += timedelta(days=1)
    wrapper.close()
    return daily_aspects


def calculate_transits(start_date, end_date, birth_data):
    birth_datetime, lat, lon = birth_data
    birth_chart = Chart(birth_datetime, lat, lon)
    wrapper = SwissEphWrapper()

    active_transits = {}
    completed_transits = []

    current_date = start_date
    while current_date <= end_date:
        transit_chart = Chart(datetime.combine(current_date, datetime.min.time()), lat, lon)

        # Check all active transits first
        for transit_key in list(active_transits.keys()):
            natal_planet, trans_planet = transit_key
            natal_obj = birth_chart.get(natal_planet)
            trans_obj = transit_chart.get(trans_planet)
            aspect = wrapper.aspect(natal_obj, trans_obj)

            if aspect:
                transit = active_transits[transit_key]
                transit.daily_orbs[current_date] = (aspect.orb, aspect.applying)
            else:
                transit = active_transits.pop(transit_key)
                transit.end_date = current_date - timedelta(days=1)
                completed_transits.append(transit)

        # Now check for new transits
        for natal_planet in PLANETS:
            if natal_planet == "Moon":
                continue
            for trans_planet in PLANETS:
                if trans_planet == "Moon":
                    continue
                if (natal_planet, trans_planet) not in active_transits:
                    natal_obj = birth_chart.get(natal_planet)
                    trans_obj = transit_chart.get(trans_planet)
                    aspect = wrapper.aspect(natal_obj, trans_obj)

                    if aspect:
                        transit = Transit(
                            natal_planet, natal_obj.sign, aspect.type,
                            trans_planet, trans_obj.sign, current_date
                        )
                        transit.daily_orbs[current_date] = (aspect.orb, aspect.applying)
                        active_transits[(natal_planet, trans_planet)] = transit

        current_date += timedelta(days=1)

    # Handle any remaining active transits
    for transit in active_transits.values():
        transit.end_date = end_date
        completed_transits.append(transit)

    wrapper.close()
    return completed_transits


def create_ics_file(transits, output_file):
    cal = Calendar()
    cal.add('prodid', '-//Astrological Transits//EN')
    cal.add('version', '2.0')

    for transit in transits:
        total_days = len(transit.daily_orbs)
        for i, (day, (orb, applying)) in enumerate(sorted(transit.daily_orbs.items()), 1):
            event = Event()
            # Create a unique UID for each day
            event.add('uid', f"{transit.natal_planet}_{transit.trans_planet}_{transit.aspect_type}_{day}")
            # Use the provided summary format with a sequence number prefix
            event.add('summary', f"{PLANET_SYMBOLS[transit.natal_planet]} {ASPECT_SYMBOLS[transit.aspect_type]} {PLANET_SYMBOLS[transit.trans_planet]} {'+' if orb > 0 else ''}{orb:.2f}°{'A' if applying else 'S'} ({i}/{total_days})")
            event.add('dtstart', day)
            event.add('dtend', day + timedelta(days=1))
            event.add('description', f"Natal {transit.natal_planet} in {transit.natal_sign} {transit.aspect_type} {transit.trans_planet} in {transit.trans_sign}")
            cal.add_component(event)

    with open(output_file, 'wb') as f:
        f.write(cal.to_ical())


def print_aligned_transits(day, aspects):
    if not aspects:
        print(f"### {day}")
        print("No aspects found.")
        print()
        return

    # Find the maximum length of the aspect descriptions
    max_length = max(len(f"({aspect.natal_sign}) {aspect.natal_planet} {aspect.aspect_type} {aspect.trans_planet} ({aspect.trans_sign})") for aspect in aspects)

    print(f"### {day}")
    for aspect in aspects:
        aspect_desc = f"({aspect.natal_sign}) {aspect.natal_planet} {aspect.aspect_type} {aspect.trans_planet} ({aspect.trans_sign})"
        padding = " " * (max_length - len(aspect_desc))
        print(f"{aspect_desc}{padding} | {'+' if aspect.orb > 0 else ''}{aspect.orb:.2f}°'{'A' if aspect.applying else 'S'}")
    print()


# Example usage
with open("birthdata.txt", "r") as file:
    raw_data = file.read().split("\n")
    birth_datetime = datetime.fromisoformat(raw_data[0])
    lat = float(raw_data[1])
    lon = float(raw_data[2])
    birth_data = (birth_datetime, lat, lon)
    start_date = date(2024, 8, 6)
    end_date = date(2024, 9, 30)
    daily_aspects = calculate_daily_aspects_and_signs(start_date, end_date, birth_data)
    for day, aspects in daily_aspects:
        print_aligned_transits(day, aspects)
    transits = calculate_transits(start_date, end_date, birth_data)
    create_ics_file(transits, "./astro_calendar_test.ics")

