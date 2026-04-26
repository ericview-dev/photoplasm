import lgpio
import spidev
import time

RST = 27
DC  = 25

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, RST)
lgpio.gpio_claim_output(h, DC)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 2000000

def cmd(c):
    lgpio.gpio_write(h, DC, 0)
    spi.xfer2([c])

cmd(0xAE)  # display off

print("OLED off")
lgpio.gpiochip_close(h)
