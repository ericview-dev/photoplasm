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

def reset():
    lgpio.gpio_write(h, RST, 1)
    time.sleep(0.1)
    lgpio.gpio_write(h, RST, 0)
    time.sleep(0.1)
    lgpio.gpio_write(h, RST, 1)
    time.sleep(0.1)

def cmd(c):
    lgpio.gpio_write(h, DC, 0)
    spi.xfer2([c])

def data(d):
    lgpio.gpio_write(h, DC, 1)
    spi.xfer2([d])

reset()
cmd(0xAE)
cmd(0x20); cmd(0x00)
cmd(0x40)
cmd(0xA1)
cmd(0xC8)
cmd(0xAF)

for page in range(8):
    cmd(0xB0 + page)
    cmd(0x00)
    cmd(0x10)
    for _ in range(128):
        data(0xFF)

print("Done — check OLED for white fill")
lgpio.gpiochip_close(h)

X

