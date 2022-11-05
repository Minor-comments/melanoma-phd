from datetime import datetime


class TimestampSaver:
    """
    Save and load a timestamp to/from disk
    """

    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    DEFAULT_DATE = datetime(year=1970, month=1, day=1)

    @staticmethod
    def save_date(filename, date):
        with open(filename, "w+") as file:
            file.write(TimestampSaver.date_to_string(date))

    @staticmethod
    def load_date(filename):
        date = None
        with open(filename, "r") as file:
            date = TimestampSaver.string_to_date(file.read())
        return date

    @staticmethod
    def date_to_string(date, format=TIMESTAMP_FORMAT):
        if date:
            return date.strftime(format)
        return ""

    @staticmethod
    def string_to_date(string, format=TIMESTAMP_FORMAT):
        if string:
            return datetime.strptime(string, format)
        return TimestampSaver.DEFAULT_DATE
