from StaticData.Calendar.Calendar import *


class FRA:
    def __init__(self, ** kwargs):
        self.maturity = kwargs.get('maturity', None)
        self.main_schedule_info = kwargs.get('main_schedule_info', None)
        self.fixing_schedule_info = kwargs.get('fixing_schedule_info', None)
        self.payment_schedule_info = kwargs.get('payment_schedule_info', None)
        self.spread = kwargs.get('spread', 0)
        self.day_count = kwargs.get('day_count', None)

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
        pv_floating = ((df['forwardRate'] + self.spread) * df['deltaTime'] * df['discountFactor']).sum()
        pv_fixed = (df['deltaTime'] * df['discountFactor'] * one_rate / (1 + one_rate  * df['deltaTime'])).sum()
        res = pv_floating - pv_fixed


        pv_fixed = interest_period.dict_compute_flow(
            nominal=(self.rate_fixed * delta_t / (1 + self.rate_fixed * delta_t)))
        pv_floating = interest_period.dict_compute_flow(
            nominal=((self.rate_floating + self.spread) * delta_t / (1 + self.rate_floating * delta_t)))
        res = pv_fixed - pv_floating
        return res
