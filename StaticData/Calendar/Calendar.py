from StaticData.Calendar.CalendarHandlerBase import *
import math
import pandas as pd


class Calendar:
    def __init__(self, name):
        self.name = name
        self.list_days_off = list()
        self.list_days_weekend = [5, 6]  # saturday, sunday

    def is_business_day(self, date):
        return (date not in self.list_days_off) and (date.weekday() not in self.list_days_weekend)

    def dt_get_business_date(self, date, bool_next=True):
        current_date = date
        while not self.is_business_day(current_date):
            nb = 1 if bool_next else -1
            current_date = current_date + dt.timedelta(days=nb)
        return current_date

    def dt_get_business_date_according_to_roll_convention(self, date, roll_convention):
        if roll_convention in [RollConvention.Following, RollConvention.ModFollowing]:
            target_date = self.dt_get_business_date(date, bool_next=True)
        else:
            target_date = self.dt_get_business_date(date, bool_next=False)
        return target_date

    def dts_get_business_date_from_frequency(self, date, frequency, roll_convention, bool_next):
        date = Period.dt_get_date(frequency, date, bool_next)
        if date is None:
            return None
        target_date = self.dt_get_business_date_according_to_roll_convention(date, roll_convention)
        return date, target_date

    def list_get_dates_from_end_date_backward(self, start_date, end_date, frequency, roll_convention):
        list_res = [end_date]
        date = end_date
        while date > start_date:
            date, target_date = self.dts_get_business_date_from_frequency(date, frequency, roll_convention, bool_next=False)
            if target_date is None:
                list_res.append(start_date)
                break
            list_res.append(target_date)
        return list_res

    def list_get_dates_from_end_date_forward(self, start_date, end_date, frequency, roll_convention):
        list_res = [start_date]
        date = start_date
        while date < end_date:
            date, target_date = self.dts_get_business_date_from_frequency(date, frequency, roll_convention, bool_next=True)
            if target_date is None:
                list_res.append(end_date)
                break
            list_res.append(target_date)
        return list_res


class InterestPeriod:
    def __init__(self, start_date, end_date, rate, payment_period, day_count):
        self.start_date = start_date
        self.end_date = end_date
        self.rate = rate
        self.payment_period = payment_period
        self.day_count = day_count

    def compute_discount_factor(self):
        delta_t = DayCount.get_nb_days_between_two_dates(self.start_date, self.end_date, self.day_count)
        res = 1 / math.pow(1 + self.rate, delta_t)

        if self.payment_period == PaymentPeriod.BeginPeriod:
            res = res / (1 + delta_t * self.rate)
        if self.payment_period == PaymentPeriod.EndPeriod:
            res = res
        return res

    # def dict_compute_flow(self, nominal):
    #     flow = nominal * self.compute_discount_factor()
    #     str_start_date = self.start_date.strftime("%Y-%m-%d")
    #     str_end_date = self.end_date.strftime("%Y-%m-%d")
    #     dict_res = {"{} - {}".format(str_start_date, str_end_date): flow}
    #     return dict_res


class ScheduleInfo:
    def __init__(self, roll_convention, frequency, calendar, **kwargs):
        self.roll_convention = roll_convention
        self.frequency = frequency
        self.calendar = calendar
        self.payment_period = kwargs.get('payment_period', PaymentPeriod.EndPeriod)

    def dt_get_business_date_according_to_roll_convention(self, date):
        if self.roll_convention in [RollConvention.Following, RollConvention.ModFollowing]:
            target_date = self.calendar.dt_get_business_date(date, bool_next=True)
        else:
            target_date = self.calendar.dt_get_business_date(date, bool_next=False)
        return target_date

    def dt_get_business_date_from_frequency(self, date, bool_next):
        date, target_date = self.calendar.dts_get_business_date_from_frequency(date, self.frequency, self.roll_convention, bool_next)
        return target_date

    def list_get_dates_from_end_date_backward(self, start_date, end_date):
        list_res = self.calendar.list_get_dates_from_end_date_backward(
            start_date, end_date, self.frequency, self.roll_convention)
        return list_res

    def list_get_dates_from_end_date_forward(self, start_date, end_date):
        list_res = self.calendar.list_get_dates_from_end_date_forward(
            start_date, end_date, self.frequency, self.roll_convention)
        return list_res


class Schedule:
    def __init__(self, start_date, end_date, main_schedule_info, fixing_schedule_info, payment_schedule_info, day_count):
        self.start_date = start_date
        self.end_date = end_date
        self.main_schedule_info = main_schedule_info
        self.payment_schedule_info = payment_schedule_info
        self.fixing_schedule_info = fixing_schedule_info

        self.day_count = day_count

        self.df_schedule = pd.DataFrame()
        self.set_df_dates()

    def set_df_dates(self):
        list_dates = self.main_schedule_info.list_get_dates_from_end_date_backward(self.start_date, self.end_date)
        list_res = list()
        for i in range(len(list_dates) - 1, 0, -1):
            start_date = list_dates[i]
            end_date = list_dates[i-1]
            fixing_date = self.fixing_schedule_info.dt_get_business_date_from_frequency(start_date, bool_next=True)
            if self.payment_schedule_info.payment_period == PaymentPeriod.EndPeriod:
                payment_date = self.payment_schedule_info.dt_get_business_date_from_frequency(end_date, bool_next=False)
            else:
                payment_date = self.payment_schedule_info.dt_get_business_date_from_frequency(start_date, bool_next=True)
            list_res.append({
                'startDate': start_date,
                'endDate': end_date,
                'fixingDate': fixing_date,
                'paymentDate': payment_date,
            })
        df = pd.DataFrame(list_res)
        self.df_schedule = df

    def df_fill_discount_factor(self, rate):

        self.df_schedule['discountFactor'] = self.df_schedule.apply(
            lambda row: InterestPeriod(
                start_date=row['startDate'],
                end_date=row['endDate'],
                rate=rate,
                payment_period=self.payment_schedule_info.payment_period,
                day_count=self.day_count).compute_discount_factor(),
            axis=1, result_type='reduce'
        )

    def df_fill_delta_time(self):
        self.df_schedule['deltaTime'] = self.df_schedule.apply(
            lambda row: DayCount.get_nb_days_between_two_dates(
                start_date=row['startDate'],
                end_date=row['endDate'],
                day_count=self.day_count
            ),
            axis=1, result_type='reduce'
        )

    def df_fill_forward_rate(self):
        sr_prev = self.df_schedule['discountFactor'].shift(periods=1, fill_value=1)
        sr_next = self.df_schedule['discountFactor']
        self.df_schedule['forwardRate'] = (sr_prev / sr_next - 1) / self.df_schedule['deltaTime']

    def df_fill_rates(self, rate):
        self.df_fill_discount_factor(rate)
        self.df_fill_delta_time()
        self.df_fill_forward_rate()


if __name__ == '__main__':
    roll_convention = RollConvention.Following
    frequency = Frequency(1, Period.M)
    calendar = Calendar('')
    schedule_info = ScheduleInfo(roll_convention, Frequency(1, Period.M), calendar)
    fixing_schedule_info = ScheduleInfo(roll_convention, Frequency(2, Period.D), calendar)
    payment_schedule_info = ScheduleInfo(roll_convention, Frequency(0, Period.D), calendar, payment_period=PaymentPeriod.EndPeriod)

    schedule = Schedule(
        start_date=dt.datetime.now(),
        end_date=dt.datetime(2021, 12, 31),
        main_schedule_info=schedule_info,
        fixing_schedule_info=fixing_schedule_info,
        payment_schedule_info=payment_schedule_info,
        day_count=DayCount.DC_ACT_360)
    schedule.df_fill_rates(0.001)
    print()


