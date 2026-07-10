from machine import Pin,ADC
from time import sleep_ms
sound=ADC(Pin(34))
def sound_lvl():
    global sound
    quiet=1127.6624
    raw=sound.read_u16()
    processed=raw#-quiet
    return processed
values=list()
for i in range(10000):
    soundlevel=sound_lvl()
    values.append(soundlevel)
    sleep_ms(10)
avg=sum(values)/len(values)
print('Finished')
print('Average value:', avg)
#if you measured in a quiet enviroment set quiet value in the sound level function to the average value