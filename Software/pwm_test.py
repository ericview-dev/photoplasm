import lgpio
import time

# Open GPIO chip
chip = lgpio.gpiochip_open(0)

# Hardware PWM on GPIO18
# Frequency: 1000Hz, Duty cycle: 50%
lgpio.tx_pwm(chip, 18, 1000, 50)

print("PWM running at 50% - LEDs should be at half brightness")
time.sleep(5)

# Turn off
lgpio.tx_pwm(chip, 18, 1000, 0)
print("PWM off")

lgpio.gpiochip_close(chip)
