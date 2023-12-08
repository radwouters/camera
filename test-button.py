import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) # 
while True: # Run forever
    if GPIO.input(27) == GPIO.LOW:
        print("Button was pushed!")