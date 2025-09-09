import board
from board import SCK, MOSI, MISO

import busio
import digitalio
from adafruit_rgb_display.st7789 import ST7789
from PIL import Image, ImageDraw, ImageFont

from adafruit_rgb_display.gc9a01a import GC9A01A

import adafruit_bmp280

import numpy as np
import cv2 as cv
import asyncio
import os

import time
import subprocess

import adafruit_character_lcd.character_lcd as character_lcd
import adafruit_74hc595

import wws_74hc165

import serial
import usb.core
import sys
import pynmea2
import datetime
import random

import csv
import sys

spi = busio.SPI(clock=SCK, MOSI=MOSI, MISO=MISO)

# sd_mount status: EXIT_STATUS (1 or 0) for mounted microsd card
# sd_mount_date: CSV filename to write to in write_to_sd(data) function
# sd_mount_status = sys.argv[1]
sd_mount_date = sys.argv[1]

gps_ser = serial.Serial(
    "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A50285BI-if00-port0",
    9600,
    timeout=1,
)


def init_display(disp, cs, dc, reset, rotate, w, h, x_off, y_off, BAUDRATE=24000000):
    CS_PIN = cs
    DC_PIN = dc
    RESET_PIN = reset
    display = disp(
        spi,
        rotation=rotate,
        width=w,
        height=h,
        x_offset=x_off,
        y_offset=y_off,
        baudrate=BAUDRATE,
        cs=digitalio.DigitalInOut(CS_PIN),
        dc=digitalio.DigitalInOut(DC_PIN),
        rst=digitalio.DigitalInOut(RESET_PIN),
    )
    return display


def rotation(display):
    height = 0
    width = 0
    if display.rotation % 180 == 90:
        height = display.width  # swap height/width to rotate it to landscape
        width = display.height
    else:
        width = display.width  # swap height/width to rotate it to landscape
        height = display.height

    return height, width


def draw_image(disp, width, height, fill=0):
    disp.fill(0)
    disp_image = Image.new("RGB", (width, height))
    disp_draw = ImageDraw.Draw(disp_image)

    return disp_image, disp_draw


# retrieve barometric sensor data
# display it onto the round display
async def bmp280_task():
    gca_draw.rectangle(
        (0, 0, disp_gc9a01.width, disp_gc9a01.height // 2 - 30), fill=(155, 50, 0)
    )
    gca_txt_bmp_temp = (
        "    Temp: {:.1f} C".format(bmp280.temperature)
        + "\nPres: {:.1f} hPa".format(bmp280.pressure)
        + "\n    Alt: {:.2f} M".format(bmp280.altitude)
    )
    gca_draw.text(
        (disp_gc9a01.width // 2 - 70, disp_gc9a01.height // 2 - 100),
        gca_txt_bmp_temp,
        font=gca_bmp_font,
        fill=(255, 255, 0),
    )

    disp_gc9a01.image(gca_image)


# NOTE: currently not used
#       might return if needed...
async def cam_task():
    if btn_toggle.value is True:
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting...")
            os._exit(1)

        resize = cv.resize(
            frame, (disp_gc9a01.width, disp_gc9a01.height), interpolation=cv.INTER_AREA
        )
        rgb = cv.cvtColor(resize, cv.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        disp_gc9a01.image(pil)


async def async_main():
    await asyncio.gather(bmp280_task(), cpu_task(), gps_task())


# monitors systems cpu temperature, cpu load, memory usage
# and displays them onto the round display
async def cpu_task():
    st7789_draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # REFERENCE:
    # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
    hostname = subprocess.check_output("hostname", shell=True).decode("utf-8")
    cpu_temp = subprocess.check_output(
        "cat /sys/class/thermal/thermal_zone1/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'",
        shell=True,
    ).decode("utf-8")
    cpu_load = subprocess.check_output(
        "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'",
        shell=True,
    ).decode("utf-8")
    mem = subprocess.check_output(
        "free -m | awk 'NR==2{printf \"Mem: %s/%s MB %.2f%%\", $3,$2,$3*100/$2 }'",
        shell=True,
    ).decode("utf-8")

    st7789_draw.text((x, y + 10), hostname, font=st7789_font, fill="#FFFFFF")
    st7789_draw.text((x, y + 40), cpu_temp, font=st7789_font, fill="#FFFF00")
    st7789_draw.text((x, y + 70), cpu_load, font=st7789_font, fill="#00FF00")
    st7789_draw.text((x, y + 100), mem, font=st7789_font, fill="#000FF0")

    # display it by 90 deg
    disp_st7789.image(st7789_image)


# display gps GPRMC
# data onto LCD
async def gps_task():

    dt = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    data = gps_ser.readline().decode("ascii", errors="replace")

    if data[0:6] == "$GPRMC":
        lcd.clear()

        try:
            gps_data = pynmea2.parse(data)

            lon = gps_data.longitude
            lat = gps_data.latitude
            dir_lat = gps_data.lat_dir
            dir_lon = gps_data.lon_dir

            # based on how much is batched
            # write to sd or locally
            # clear and continue process
            if len(gps_batch) is LEN:
                # write_to_sd(gps_batch)
                write_to_local(gps_batch)
                gps_batch.clear()
            else:
                gps_batch.append(
                    {
                        "datetime": dt,
                        "longitude": lon,
                        "lon_dir": dir_lon,
                        "latitude": lat,
                        "lat_dir": dir_lat,
                    }
                )
                print(gps_batch)
                lcd.message = "{0:.3f} {1:.3f}".format(lon, lat)

        # ignoring the checksum error when GPS
        # is having issues collecting appropriate data
        except (pynmea2.ChecksumError, pynmea2.ParseError) as gps_e:
            print(f"Error parsing data {repr(gps_e)}")

    lcd.message = "\n{0}".format(dt)


# opens and writes local CSV file
# within the ./mnt/microsd directory
def write_to_local(data):
    with open(f"{sd_mount_date}", "a+") as gps_file:

        print(f"writing {data}")
        gps_writer = csv.DictWriter(gps_file, fieldnames=field_names, delimiter=",")

        if not os.path.exists(sd_mount_date):
            gps_write.writeheader()
        gps_writer.writerows(data)


# NOTE: ON HOLD........
#       microsd card currently has issues
#       mounting it causes system-wide crashes
#       however fdisk -l recognizes it
#       fsck is able to run sometimes
def write_to_sd(data):
    if int(sd_mount_status) == 0:
        print(f"opening {sd_mount_date}")
        with open(f"{sd_mount_date}", "a+") as gps_file:
            print(f"writing {data}")
            gps_writer = csv.DictWriter(gps_file, fieldnames=field_names, delimiter=",")

            if not os.path.exists(sd_mount_date):
                gps_writer.writeheader()

            gps_writer.writerows(data)


if __name__ == "__main__":

    # REMINDER: THIS SCRIPT IS IN ONLY SPI MODE!
    #           (SINCE THE FT232H UART/MPSSE OPERATES IN ONE SPECIFIC MODE)

    # -----74HC165 IS INPUT ONLY-----
    # _74hc165_isr_latch = board.D5
    # _74hc165_isr = wws_74hc165.ShiftRegister74HC165(spi, _74hc165_isr_latch, 1)

    # -----74HC595 IS OUTPUT ONLY-----
    _74hc595_isr_latch = digitalio.DigitalInOut(board.D6)
    _74hc595_isr = adafruit_74hc595.ShiftRegister74HC595(spi, _74hc595_isr_latch, 1)

    # connecting LCD to 74HC595
    lcd_rs = _74hc595_isr.get_pin(0)
    lcd_en = _74hc595_isr.get_pin(1)
    lcd_d7 = _74hc595_isr.get_pin(2)
    lcd_d6 = _74hc595_isr.get_pin(3)
    lcd_d5 = _74hc595_isr.get_pin(4)
    lcd_d4 = _74hc595_isr.get_pin(5)

    lcd_backlight = _74hc595_isr.get_pin(6)

    lcd_columns = 16
    lcd_rows = 2

    lcd = character_lcd.Character_LCD_Mono(
        lcd_rs,
        lcd_en,
        lcd_d4,
        lcd_d5,
        lcd_d6,
        lcd_d7,
        lcd_columns,
        lcd_rows,
        lcd_backlight,
    )
    lcd_backlight.value = True
    lcd.message = "BOOTING\nUP..."

    # clear old outputs for incoming ones
    #    subprocess.run(["clear"])

    # switch for camera mode for round display
    #    btn_toggle = digitalio.DigitalInOut(board.D4)
    #    btn_toggle.direction = digitalio.Direction.INPUT

    # list connected USB devices
    #    print("ls /dev/video* : ",subprocess.check_output("ls /dev/video* | grep -oP '/dev/video\d+' | tr '\n' ' ' | sed 's/ $//'",shell=True))
    print(
        "ls /dev/ttyUSB* : ",
        subprocess.check_output(
            "ls /dev/ttyUSB* | grep -oP '/dev/ttyUSB\d+' | tr '\n' ' ' | sed 's/ $//'",
            shell=True,
        ),
    )

    # writing to csv file
    field_names = ["datetime", "longitude", "lon_dir", "latitude", "lat_dir"]
    # write_to_sd("hello world!")

    # camera check
    #    cap = cv.VideoCapture(-1)
    #    if not cap.isOpened():
    #        print("Cannot open camera...")
    #    cap.set(cv.CAP_PROP_FPS,30)

    # barometer setup for round display
    bmp280_cs = digitalio.DigitalInOut(board.D7)
    bmp280 = adafruit_bmp280.Adafruit_BMP280_SPI(spi, bmp280_cs)
    bmp280.sea_level_pressure = 1017.0
    gca_bmp_font = ImageFont.truetype("./DS-DIGIT.TTF", 20)

    # ----------------set up round display ----------------
    disp_gc9a01 = init_display(
        GC9A01A, board.C6, board.C5, board.C4, 180, 240, 240, 0, 0
    )
    gca_image, gca_draw = draw_image(disp_gc9a01, disp_gc9a01.width, disp_gc9a01.height)

    gca_draw.rectangle(
        (0, 0, disp_gc9a01.width, disp_gc9a01.height // 2 - 30),
        # upper rectangle
        fill=(155, 50, 0),
    )
    gca_draw.rectangle(
        (
            0,
            90,
            disp_gc9a01.width // 2,
            disp_gc9a01.height //
            # left rectangle
            10 + 150,
        ),
        fill=(105, 50, 150),
    )
    gca_draw.rectangle(
        (120, 90, disp_gc9a01.width // 2 + 150, disp_gc9a01.height // 10 + 150),
        fill=(10, 50, 100),
    )  # right rectangle

    gca_font = ImageFont.truetype("./DS-DIGIT.TTF", 21)
    gca_txt_ip = subprocess.check_output(
        "ip -4 addr | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127\.0\.0\.1'",
        shell=True,
    ).decode("utf-8")
    gca_draw.text(
        (disp_gc9a01.width // 2 - 50, disp_gc9a01.height // 2 + 70),
        gca_txt_ip,
        font=gca_font,
        fill=(255, 255, 0),
    )
    disp_gc9a01.image(gca_image)
    # ------------------------------------------------------

    # ---------------- set up tft display ----------------
    x = 0
    y = -2
    disp_st7789 = init_display(
        ST7789, board.C3, board.C2, board.C1, 90, 135, 240, 53, 40
    )
    height, width = rotation(disp_st7789)
    st7789_image, st7789_draw = draw_image(disp_st7789, width, height)
    st7789_font = ImageFont.truetype("./DS-DIGIT.TTF", 23)
    # ------------------------------------------------------

    lcd.clear()

    # writing gps data in N batches
    # to avoid wearing out sdcard
    # and causing system crashes
    # by constantly opening and closing file
    gps_batch = []
    LEN = 5

    # gracefully exit when CTRL+C
    try:
        while True:
            asyncio.run(async_main())

    # offload camera, lcd, and exit
    except KeyboardInterrupt:
        #       cap.release()
        lcd.clear()
        lcd.backlight = False
        sys.exit(0)
        print("\nCancelled...")
