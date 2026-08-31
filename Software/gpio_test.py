import lgpio
import time

chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, 18)

print('turning ON')
lgpio.gpio_write(chip, 18, 1)
time.sleep(5)

print('turning OFF')
lgpio.gpio_write(chip, 18, 0)
time.sleep(2)

lgpio.gpiochip_close(chip)
