from StaticData.Calendar.Calendar import *
from StaticData.Calendar.CalendarHandlerBase import *


class CrossCurrencySwap:
    def __init__(self, **kwargs):
        self.maturity = kwargs.get('maturity', None)
        self.main_schedule_info = kwargs.get('main_schedule_info', None)
        self.fixing_schedule_info = kwargs.get('fixing_schedule_info', None)
        self.payment_schedule_info = kwargs.get('payment_schedule_info', None)
        self.spread = kwargs.get('spread', 0)
        self.day_count = kwargs.get('day_count', None)
        self.coupon_DC = kwargs.get('coupon_DC', None)
        self.coupon_FC = kwargs.get('coupon_FC', None)
        self.nominal_FC = kwargs.get('nominal_FC', None)
        self.nominal_DC = kwargs.get('nominal_DC', None)

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
        sr_coupon_DC = pd.Series(index=df.index, data=[self.coupon_DC] * (df.shape[0] - 1) + [1 + self.coupon_DC])
        sr_coupon_FC = pd.Series(index=df.index, data=[self.coupon_FC] * (df.shape[0] - 1) + [1 + self.coupon_FC])
        pv_DC = (self.nominal_DC * sr_coupon_DC * df['discountFactor']).sum() #TODO revoir la formule discountFactor pour ccswap
        pv_FC = (self.nominal_FC * sr_coupon_FC * df['discountFactor']).sum()
        res = pv_DC - pv_FC
        return res


if __name__ == '__main__':
    roll_convention = RollConvention.Following
    frequency = Frequency(1, Period.Y)
    calendar = Calendar('')
    schedule_info = ScheduleInfo(roll_convention, Frequency(1, Period.Y), calendar)
    fixing_schedule_info = ScheduleInfo(roll_convention, Frequency(2, Period.D), calendar)
    payment_schedule_info = ScheduleInfo(roll_convention, Frequency(0, Period.D), calendar, payment_period=PaymentPeriod.EndPeriod)

    cc_swap = CrossCurrencySwap(
        maturity=dt.datetime(2025, 12, 31),
        main_schedule_info=schedule_info,
        fixing_schedule_info=fixing_schedule_info,
        payment_schedule_info=payment_schedule_info,
        spread=0.01,
        day_count=DayCount.DC_ACT_360,
        coupon_DC=0.03,
        coupon_FC=0.07,
        nominal_DC=15,
        nominal_FC=25
    )
    test = cc_swap.get_price(dt.datetime(2021, 12, 31), 0.02) # rate_DC : 8% -rate_FC 6%
    print()