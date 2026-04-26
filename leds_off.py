import lgpio

chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, 18)
lgpio.tx_pwm(chip, 18, 1000, 0)
lgpio.gpiochip_close(chip)
print('LEDs OFF')
