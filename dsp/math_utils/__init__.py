import math

def round_to_sig_fig(x, sig_figs):
    if x == 0:
        return 0  # Special case for zero
    else:
        # Calculate the rounding factor based on significant figures
        factor = math.pow(10, sig_figs - math.ceil(math.log10(abs(x))))
        return round(x * factor) / factor
