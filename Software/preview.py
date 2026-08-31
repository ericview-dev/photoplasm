import lgpio
import spidev
import time
from PIL import Image, ImageDraw
import math

RST = 27
DC  = 25
W, H = 128, 64
CX, CY, R = 64, 32, 30
STEPS = 16
START_ANGLE = -math.pi / 2

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
        for x in range(W):
            byte = 0
            for bit in range(8):
                y = page * 8 + bit
                if pixels[x, y] > 128:
                    byte |= (1 << bit)
            data(byte)

def make_frame(step):
    img = Image.new('L', (W, H), 255)
    draw = ImageDraw.Draw(img)
    wedge_angle = (2 * math.pi) / STEPS
    for s in range(step):
        start = math.degrees(START_ANGLE + s * wedge_angle)
        end   = math.degrees(START_ANGLE + (s + 1) * wedge_angle)
        draw.pieslice(
            [CX-R, CY-R, CX+R, CY+R],
            start=start, end=end, fill=0
        )
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).ellipse([CX-R, CY-R, CX+R, CY+R], fill=255)
    img.paste(255, mask=Image.eval(mask, lambda x: 255 - x))
    return img

init()
step = 1

print("Preview mode — ENTER=next  B=back  Q=quit")
print(f"Step {step}/16")
send_image(make_frame(step))

while True:
    key = input("> ").strip().lower()
    if key == '' or key == 'n':
        step = min(step + 1, STEPS)
    elif key == 'b':
        step = max(step - 1, 1)
    elif key == 'q':
        break
    print(f"Step {step}/16")
    send_image(make_frame(step))

lgpio.gpiochip_close(h)
