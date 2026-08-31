import lgpio
import time

chip = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(chip, 18)

print('ramping down...')
for i in range(100, -1, -1):
    lgpio.tx_pwm(chip, 18, 1000, i)
    time.sleep(0.1)

print('ramping up...')
for i in range(0, 101):
    lgpio.tx_pwm(chip, 18, 1000, i)
    time.sleep(0.1)

print('shutting off')
lgpio.tx_pwm(chip, 18, 1000, 0)
time.sleep(0.5)
lgpio.gpiochip_close(chip)
print('done')
