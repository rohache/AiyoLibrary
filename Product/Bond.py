from StaticData.Calendar.Calendar import *

import datetime as dt


class Bond:
    def __init__(self, **kwargs):
        self.maturity = kwargs.get('maturity', None)
        self.main_schedule_info = kwargs.get('main_schedule_info', None)
        self.fixing_schedule_info = kwargs.get('fixing_schedule_info', None)
        self.payment_schedule_info = kwargs.get('payment_schedule_info', None)
        self.spread = kwargs.get('spread', 0)
        self.day_count = kwargs.get('day_count', None)
        self.coupon = kwargs.get('coupon', None)

    def get_price(self, current_date, one_rate):
        schedule = Schedule(
            start_date=current_date,
            end_date=self.maturity,
            main_schedule_info=self.main_schedule_info,
            fixing_schedule_info=self.fixing_schedule_info,
            payment_schedule_info=self.payment_schedule_info,
            day_count=self.day_count)
        schedule.df_fill_rates(rate=one_rate)
        df = schedule.df_schedule
        sr_coupon = pd.Series(index=df.index, data=[self.coupon] * (df.shape[0] - 1) + [1 + self.coupon])
        res = (df['discountFactor'] * sr_coupon).sum()
        return res


if __name__ == '__main__':
    roll_convention = RollConvention.Following
    frequency = Frequency(1, Period.M)
    calendar = Calendar('')
    schedule_info = ScheduleInfo(roll_convention, Frequency(1, Period.M), calendar)
    fixing_schedule_info = ScheduleInfo(roll_convention, Frequency(2, Period.D), calendar)
    payment_schedule_info = ScheduleInfo(roll_convention, Frequency(0, Period.D), calendar, payment_period=PaymentPeriod.EndPeriod)

    bond = Bond(
        maturity=dt.datetime(2021, 12, 31),
        main_schedule_info=schedule_info,
        fixing_schedule_info=fixing_schedule_info,
        payment_schedule_info=payment_schedule_info,
        day_count=DayCount.DC_ACT_360,
        coupon=0.01,
    )
    test = bond.get_price(dt.datetime.now(), 0.01)