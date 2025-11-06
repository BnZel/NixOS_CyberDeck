from __init__ import *

def init_network(choice=0):
    import network, time

    network_creds = {
        0:["SSID1", "PASS1"],
        1:["SSID2", "PASS2"]
    }

    if choice > len(network_creds):
        print(f"There are only {len(network_creds)}")
        return sta_if.isconnected()
    else:
        print(f"Connecting to {str(network_creds[choice][0])}")

        sta_if = network.WLAN(network.STA_IF); sta_if.active(True)
        sta_if.connect(str(network_creds[choice][0]),str(network_creds[choice][1]))

        timeout = 10
        while not sta_if.isconnected() and timeout > 0:
            print(f"{timeout} Attempt to connect...")
            time.sleep(1)
            timeout -= 1

        print(f"\n\nWiFi Connection: {sta_if.isconnected()}\nIP: {sta_if.ipconfig('addr4')}\n\n")

    return sta_if.isconnected()

def init_pot(pin_num):
    pot_AX = ADC(Pin(pin_num,Pin.IN))
    pot_AX.width(ADC.WIDTH_10BIT)
    pot_AX.atten(ADC.ATTN_11DB)    # 11DB for 3.3v
    return pot_AX

# https://github.com/orgs/micropython/discussions/16382
def oled_text_scaled(oled, text, x, y, scale, character_width=8, character_height=8):
    # temporary buffer for the text
    width = character_width * len(text)
    height = character_height
    temp_buf = bytearray(width * height)
    temp_fb = ssd1306.framebuf.FrameBuffer(temp_buf, width, height, ssd1306.framebuf.MONO_VLSB)

    # write text to the temporary framebuffer
    temp_fb.text(text, 0, 0, 1)

    # scale and write to the display
    for i in range(width):
        for j in range(height):
            pixel = temp_fb.pixel(i, j)
            if pixel:  # If the pixel is set, draw a larger rectangle
                oled.fill_rect(x + i * scale, y + j * scale, scale, scale, 1)

def init_oled(width=128,height=64):
    i2c = SoftI2C(scl=Pin(22), sda=Pin(23))
    oled = ssd1306.SSD1306_I2C(width, height, i2c, 0x3c)
    ssd1306.SSD1306_I2C.text_scaled = oled_text_scaled
    return oled

# only if starting values are at 0  
def map_range_(x, in_max, out_max):
    return x * out_max // in_max

# https://stackoverflow.com/questions/70643627/python-equivalent-for-arduinos-map-function    
def read_adc(adc_pin, sample=24, in_min=0, in_max=0, out_min=0, out_max=0):
    cumul = 0
    if in_max is 0 and out_max is 0:
        return adc_pin
    else:
        for _ in range(sample):
            cumul += adc_pin.read()
        return (cumul - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def map_(adc_pin, id, from_low=0, from_high=0, to_low=0, to_high=0, sample=24, smooth=False):
    x_ = adc_pin.read()

    if from_high == 0 and to_high == 0:
        return x_
    else:
        if sample > 1:
            sum_ = 0
            for i in range(sample):
                sum_ += adc_pin.read()
            x_ = sum_ // sample
        
        # NOTE: unusual behaviour where some readings
        #       slowly reduce and others do not respond
        if smooth:
            if id not in pot_ID:
                pot_ID[id] = x_
            x_ = smoothing(x_, pot_ID[id])
            pot_ID[id] = x_

    z = (x_ - from_low) * (to_high - to_low) // (from_high - from_low) + to_low 
    return z

# exponential smoothing
def smoothing(s0, prev_s_t, alpha=0.1):
    # 0 < alpha < 1
    if alpha >= 0 and alpha <= 1:
        prev_s_t = alpha * s0 + (1-alpha) * prev_s_t
        return int(prev_s_t)
    return s0

def init_v_motors():
    v_mtr_1 = PWM(Pin(16), freq=1000, duty=512)
    v_mtr_2 = PWM(Pin(17), freq=1000, duty=512)
    v_mtr_3 = PWM(Pin(21), freq=1000, duty=512)
    v_mtr_4 = PWM(Pin(13), freq=1000, duty=512)
    v_mtr_5 = PWM(Pin(12), freq=1000, duty=512)

    return v_mtr_1, v_mtr_2, v_mtr_3, v_mtr_4, v_mtr_5

def init_mpu9250():
    i2c = SoftI2C(scl=Pin(22), sda=Pin(23))

    mpu9250 = MPU9250(i2c)
    sensor = mpu9250

    # check if "calibration_variables.txt" exists within root directory
    # read file and set precalibrated values
    # otherwise create the text file and calibrate
    try:
        with open("calibration_variables.txt","r") as file_calib_vars:

            print("file exists, reading...")
            cali_var_lines = file_calib_vars.readlines()

            offset = cali_var_lines[0]
            scale = cali_var_lines[1]

            print(f"\nOFFSET: {offset}\nSCALE: {scale}\n")

            ak8963 = AK8963(
                i2c,
                offset=offset,
                scale=scale
            )

    except OSError:
        print("file does not exist, creating 'calibration_variables.txt'...\nCalibrating MPU9250 Magnetometer...")

        file_calib_vars = open("calibration_variables.txt","a")
        ak8963 = AK8963(i2c)
        ak8963.calibrate()

        offset, scale = ak8963.calibrate(count=256, delay=200)
        file_calib_vars.write(f"{offset}\n{scale}")
        print(f"\nOFFSET: {offset}\nSCALE: {scale}\n")

        file_calib_vars.close()

        # NOTE: for some reason default params don't get recognized
        #       so fyi explicitly define them to avoid headaches
        sensor = MPU9250(i2c, None, ak8963)

    print("Done.")
    return sensor

def establish_connection(ip=0):
    '''
    Attempts to connect to server to send glove data to
    '''
    global addr
    ips = ['IP1', 'IP2']
    try: 
        sockaddr = socket.getaddrinfo(str(ips[ip]),1234)[0][-1]
        print(f"\nConnecting to {sockaddr}...")

        soc = socket.socket()
        soc.connect(sockaddr)

        print(soc.recv(1024))

        addr = ips[ip]
        
        return soc

    except OSError as e:
        print(f"Connection failed: {e}\nClosing socket...")
        soc.close()
        return None

def sock_send_data(sock):
    '''
    Sends potentiometer data and MPU9250's accelerometer data
    '''
    if sock is not None:
        display_stats(oled,sock)

        x,y,z = mpu9250.acceleration

        return sock.send(f"{map_(pot_A2,from_low=450,from_high=740,to_high=100)},\
                        {map_(pot_A3,from_high=350,to_high=100)},\
                        {map_(pot_D33,from_high=350,to_high=100)},\
                        {map_(pot_A4,from_low=320,from_high=420,to_high=100)},\
                        {map_(pot_D32,from_high=300,to_high=100)},\
                        {x},\
                        {y},\
                        {z}".encode()
                        )

def display_stats(oled,sock=None):
    data = {
        "A2":map_(pot_A2,"A2",from_low=450,from_high=740,to_high=100,smooth=False),
        "A3":map_(pot_A3,"A3",from_high=350,to_high=100,smooth=False),
        "D33":map_(pot_D33,"D33",from_high=350,to_high=100,smooth=False),
        "A4":map_(pot_A4,"A4",from_low=320,from_high=420,to_high=100,smooth=False),
        "D32":map_(pot_D32,"D32",from_high=300,to_high=100,smooth=False)
        }

    oled.fill(0)
    x_pos = 0
    y_pos = 0
    for index, (key,value) in enumerate(data.items()):
        oled.text(f"{key}:{value}",x_pos,y_pos)

        if (index % 2 == 0):
            x_pos = 64
        else:
            x_pos = 0
            y_pos += 10
    
    x,y,z = tuple(map(lambda x: round(x, 2), mpu9250.acceleration))
    oled.text(f"{x},{y},{z}",0,35)

    if sock is None:
        oled.text(f"Server: None",12,55)
    else:
        oled.text(f"{addr}",15,55)

    oled.show()

def test_hardware(test_case=0):
    '''
    Debug just the hardware without connecting to the server\n
    0: potentiometer\n
    1: mpu9250\n
    2: all
    '''
    component_x = {
        0: f"A2: {read_adc(pot_A2,1)} | A3: {read_adc(pot_A3,1)} | A4: {read_adc(pot_A4,1)} | D32: {read_adc(pot_D32,1)} | D33: {read_adc(pot_D33,1)}".encode(),
        1: f"ACCEL: {mpu9250.acceleration} | GYRO: {mpu9250.gyro} | MAG: {mpu9250.magnetic} | TEMP: {mpu9250.temperature}".encode(),
        2: f"A2: {read_adc_(pot_A2,1)} | A3: {read_adc_(pot_A3,1)} | A4: {read_adc_(pot_A4,1)} | D32: {read_adc_(pot_D32,1)} | D33: {read_adc_(pot_D33,1)} | ACCEL: {mpu9250.acceleration} | GYRO: {mpu9250.gyro} | MAG: {mpu9250.magnetic} | TEMP: {mpu9250.temperature}"
    }

    return print(component_x[test_case])


net_stat = init_network(0)

# continue whether or not it's connected to wifi
# or connected to local server so 
# it can be used for field testing
if net_stat or not net_stat:

    pot_ID = {}
    pot_A2 = init_pot(34)
    pot_A3 = init_pot(39)
    pot_A4 = init_pot(36)
    pot_D32 = init_pot(32)
    pot_D33 = init_pot(33)
 
    # init_v_motors() 
    
    oled = init_oled()
    oled.text("Sensor Glove",5,25)
    oled.show()

    mpu9250 = init_mpu9250() 
    print(f"MPU9250 ID: {hex(mpu9250.whoami)}")
    
    sock = establish_connection(1)

    while True: 
        if sock is None:
            # test_hardware(2)
            display_stats(oled)
        else: 
            sock_send_data(sock)      

        sleep(0.1)