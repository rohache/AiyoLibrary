import datetime as dt
from enum import Enum
from calendar import monthrange
from dateutil.relativedelta import relativedelta


class DayCount(Enum):
    DC_30_360 = 0
    DC_30E_360 = 1
    DC_30E_360_ISDA = 2
    DC_ACT_365 = 3
    DC_ACT_360 = 4

    @staticmethod
    def get_nb_days_between_two_dates(start_date, end_date, day_count):
        if day_count in [DayCount.DC_30_360, DayCount.DC_30E_360, DayCount.DC_30E_360_ISDA]:
            if day_count == DayCount.DC_30_360:
                d1 = min([start_date.day, 30])
                d2 = min([end_date.day, 30]) if d1 == 30 or d1 == 31 else end_date.day
            elif day_count == DayCount.DC_30E_360:
                d1 = 30 if start_date.day == 31 else end_date.day
                d2 = 30 if end_date.day == 31 else end_date.day
            else:  # elif day_count == DayCount.DC_30E_360_ISDA:
                d1 = 30 if start_date.day == monthrange(start_date.year, start_date.month)[1] else start_date.day
                d2 = 30 if end_date.day == monthrange(end_date.year, start_date.month)[1] else end_date.day
            year_diff = (
                    (360 * (end_date.year - start_date.year)
                     + 30 * (end_date.month - start_date.month)
                     + (d2 - d1)
                     ) / 360)
        elif day_count == DayCount.DC_ACT_365:
            year_diff = (end_date - start_date).days / 365
        elif day_count == DayCount.DC_ACT_360:
            year_diff = (end_date - start_date).days / 360
        else:
            raise Exception("Daycount unknoww")

        return year_diff


class Period(Enum):
    D = 0
    W = 1
    M = 2
    Y = 3
    Z = 4

    @staticmethod
    def dt_get_date(frequency, date, bool_next):
        factor = 1 if bool_next else -1
        n = frequency.n
        if frequency.period == Period.D:
            date = date + factor * dt.timedelta(days=n)
        elif frequency.period == Period.W:
            date = date + factor * dt.timedelta(days=7 * n)
        elif frequency.period == Period.M:
            date = date + factor * relativedelta(months=n)
        elif frequency.period == Period.Y:
            date = date + factor * relativedelta(years=n)
        else:
            date = None
        return date


class RollConvention(Enum):
    Following = 0
    Preceding = 1
    ModFollowing = 2
    ModPreceding = 3


class PaymentPeriod(Enum):
    BeginPeriod = 0
    EndPeriod = 1


class Frequency:
    def __init__(self, n, period=Period.Z):
        self.n = n
        self.period = period
