import lgpio
import spidev
import time
from PIL import Image, ImageDraw, ImageFont

RST = 27
DC  = 25

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, RST)
lgpio.gpio_claim_output(h, DC)

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 2000000

def reset():
    lgpio.gpio_write(h, RST, 1); time.sleep(0.1)
    lgpio.gpio_write(h, RST, 0); time.sleep(0.1)
    lgpio.gpio_write(h, RST, 1); time.sleep(0.1)

def cmd(c):
    lgpio.gpio_write(h, DC, 0)
    spi.xfer2([c])

def data(d):
    lgpio.gpio_write(h, DC, 1)
    spi.xfer2([d])

def init():
    reset()
    cmd(0xAE)
    cmd(0x20); cmd(0x00)
    cmd(0x40)
    cmd(0xA1)
    cmd(0xC8)
    cmd(0xAF)

def send_image(img):
    pixels = img.load()
    for page in range(8):
        cmd(0xB0 + page)
        cmd(0x00)
        cmd(0x10)
        for x in range(128):
            byte = 0
            for bit in range(8):
                y = page * 8 + bit
                if pixels[x, y] > 128:
                    byte |= (1 << bit)
            data(byte)

init()

img = Image.new('L', (128, 64), 0)
draw = ImageDraw.Draw(img)
font = ImageFont.load_default()
draw.text((10, 20), "HTGAA26", font=font, fill=255)

send_image(img)
print("Done")
lgpio.gpiochip_close(h)
