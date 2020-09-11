import RPi.GPIO as GPIO
from ADCDevice import ADS7830
from flask import Flask, render_template
from threading import Thread

app = Flask(__name__)

water_pumps = (11, 12, 13)
pump_states = {
    water_pumps[0] : False,
    water_pumps[1] : False,
    water_pumps[2] : False,
}
moisture_sensors = (0, 3, 6)
moisture_goal = 200

@app.route('/', methods=['GET'])
def index():
    return render_template(
        'index.html',
        plant1_moisture=adc.analogRead(moisture_sensors[0]),
        plant2_moisture=adc.analogRead(moisture_sensors[1]),
        plant3_moisture=adc.analogRead(moisture_sensors[2]),
        plant1_water_state=pump_states[water_pumps[0]],
        plant2_water_state=pump_states[water_pumps[1]],
        plant3_water_state=pump_states[water_pumps[1]]
    )

def setup():
    global adc
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(water_pumps, GPIO.OUT, initial=GPIO.HIGH)
    adc = ADS7830()
    loop_thread = Thread(target=loop)
    loop_thread.start()

def loop():
    global pump_states, running
    running = True
    while running:
        for i in range(3):
            if adc.analogRead(moisture_sensors[i]) < moisture_goal:
                GPIO.output(water_pumps[i], GPIO.LOW)
                pump_states[water_pumps[i]] = True
            else:
                GPIO.output(water_pumps[i], GPIO.HIGH)
                pump_states[water_pumps[i]] = False

def destroy():
    global running
    running = False
    adc.close()
    GPIO.cleanup()

if __name__ == '__main__':
    setup()
    try:
        app.run(port=80, host='0.0.0.0')
    except KeyboardInterrupt:
        print('Bye!')
    finally:
        destroy()
