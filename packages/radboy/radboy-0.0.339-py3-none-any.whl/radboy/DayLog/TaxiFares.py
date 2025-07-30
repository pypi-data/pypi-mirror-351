#yellow cab taxi fare calculator
#rates

class TaxiFare:
	per_1_14_mile=0.25
	flag_drop=3.50
	per_mile=per_1_14_mile*14
	airport_surcharge_pickup=3
	airport_surcharge_dropoff=3
	wait_time_per_hour_cost=35

	def __init__(self):
		pass
