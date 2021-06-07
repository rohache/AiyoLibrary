from Product.Bond import *
from Product.Swap import *


if __name__ == '__main__':
    maturity = dt.datetime(2021, 12, 31)
    yearly_coupon = 0
    coupon_frequency = Frequency(1, Period.Z)
    calendar = Calendar('')
    roll_convention = RollConvention.Following
    day_count = DayCount.DC_30_360
    payment_period = PaymentPeriod.EndPeriod

    bond_zc = Bond(
        maturity=maturity,
        yearly_coupon=yearly_coupon,
        coupon_frequency=coupon_frequency,
        calendar=calendar,
        roll_convention=roll_convention,
        day_count=day_count,
        payment_period=payment_period,
    )

    price = bond_zc.get_price(dt.datetime.now(), 0.01)

    ir_swap = InterestRateSwap(
        maturity=maturity,
        payment_frequency=Frequency(1, Period.M),
        calendar=calendar,
        roll_convention=roll_convention,
        day_count=day_count,
        payment_period=payment_period,
        spread=0.001,
    )
    ir_swap.get_price(dt.datetime.now(), 0.01)



    print()






