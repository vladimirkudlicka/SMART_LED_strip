import math
import random
from machine import Pin,ADC
from time import sleep_ms
#initiation
runAnimation=False

pix=None
BrightPot=None
pixLength=None
random_seed_src=None
wifiBrightness=False
lastNonWiFipotVal=0
wifiBrightnessVal=0.5
#initiation
def init_pixAnimations(NeoPixel_strip,PixLength,Brightness_pot_pin,random_seed_src_pin,sound_sens_pin):
    global pix, BrightPot, pixLength,random_seed_src,sound
    pixLenght=PixLength
    pix=NeoPixel_strip
    sound=ADC(Pin(sound_sens_pin))
    random_seed_src=ADC(Pin(random_seed_src_pin))
    BrightPot=ADC(Pin(Brightness_pot_pin))
    pix.fill((0,0,0))
    pix.write()
#noise sensor function
quiet_sound_lvl=1127.6624
def callibrate_sound_sensor():
    global quiet_sound_lvl
    data=list()
    for i in range(1000):
        data.append(sound.read_u16())
        sleep_ms(1)
    quiet_sound_lvl=sum(data)/len(data)
def sound_lvl():
    global quiet_sound_lvl
    raw=sound.read_u16()
    processed=abs(raw-quiet_sound_lvl)
    return processed
#Color generator
#soure:https://toptechboy.com/convert-hsv-to-rgb-in-micropython/ (it was modified by my to contain brightnes, saturation and I flipped the color wheel)
def getRGB(deg,sat,brightness):#sat=saturation(0-100)
    deg=360-deg
    if deg>360:
        deg-=360
    elif deg<0:
        deg+=360
    sat=sat/100
    m=1/60
    if deg>=0 and deg<60:
        R=1
        G=0
        B=m*deg
    if deg>=60 and deg<120:
        R=1-m*(deg-60)
        G=0
        B=1
    if deg>=120 and deg<180:
        R=0
        G=m*(deg-120)
        B=1
    if deg>=180 and deg<240:
        R=0
        G=1
        B=1-m*(deg-180)
    if deg>=240 and deg<300:
        R=m*(deg-240)
        G=1
        B=0
    if deg>=300 and deg<=360:
        R=1
        G=1-m*(deg-300)
        B=0
    myColor=(math.ceil(((R*sat*255)+(255*(1-sat)))*brightness),math.ceil(((G*sat*255)+(255*(1-sat)))*brightness),math.ceil(((B*sat*255)+(255*(1-sat)))*brightness))
    return myColor    
#NeoPixel modes support functions
def getBrightness(rng):
    global wifiBrightness,lastNonWiFipotVal,wifiBrightnessVal
    potVal=BrightPot.read_u16()
    #print(potVal)
    if not wifiBrightness:
        lastNonWiFipotVal=potVal
        return round((potVal/65535)*rng,2)
    else:
        if abs(potVal-lastNonWiFipotVal)>=250:
            wifiBrightness=False
            return getBrightness(rng)
        else:
            return wifiBrightnessVal
def fading(lvl,up,minBright,maxBright,fadetype):
    if up:
        lvl+=0.01
    else:
        lvl-=0.01
    if lvl>=1  and up:
        up=False
    elif lvl<=0 and not up:
        up=True
    if fadetype==1:
        bright=minBright+((maxBright-minBright)*((100**lvl)/100))
    elif fadetype==0:
        bright=minBright+((maxBright-minBright)*lvl)
    return bright,lvl,up
#NeoPixel modes
def white(temperature,fadingActive,fminBrightness,fspeed,fadetype):
    global runAnimation
    if fadingActive:
        bright=fminBrightness
        lvl=0
        up=True
        while runAnimation:
            fmaxBrightness=getBrightness(1-fminBrightness)+fminBrightness
            bright,lvl,up=fading(lvl,up,fminBrightness,fmaxBrightness,fadetype)
            color=(int(255*bright),int((255-temperature/4)*bright),int((255-temperature)*bright))
            pix.fill(color)
            pix.write() 
            sleep_ms(int((500/fspeed)))
    else:
        while runAnimation:
            brightness=0.05+0.95*getBrightness(0.95)
            color=(int(255*brightness),int((255-temperature/4)*brightness),int((255-temperature)*brightness))
            pix.fill(color)
            pix.write()
            sleep_ms(10)
def monocolor(color,fadingActive,fminBright,fspeed,fadetype):
    global runAnimation
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        while runAnimation:
            fmaxBright=getBrightness(1-fminBright)+fminBright
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            pix.fill(getRGB(color[0],color[1],bright))
            pix.write()
            sleep_ms(int(500/fspeed))
    else:
        while runAnimation:
            brightness=0.05+0.95*getBrightness(0.95)
            pix.fill(getRGB(color[0],color[1],brightness))
            pix.write()
            sleep_ms(10)
def bicolor(color1,color2,fadingActive,fminBright,fspeed,fadetype):
    global runAnimation,pixLength
    pixList=[0 for _ in range(pixLength)]
    for i in range(0,pixLength,2):
            pixList[i]=getRGB(color1[0],color1[1],1)
    for i in range(1,pixLength,2):
        pixList[i]=getRGB(color2[0],color2[1],1)
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        while runAnimation:
            fmaxBright=getBrightness(1-fminBright)+fminBright
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            for i in range(pixLength):
                pix[i]=(int(pixList[i][0]*bright),int(pixList[i][1]*bright),int(pixList[i][2]*bright))
            pix.write()
            sleep_ms(int(500/fspeed))
    else:
        while runAnimation:
            brigthness=0.05+0.95*getBrightness(0.95)
            for i in range(pixLength):
                pix[i]=(math.ceil(pixList[i][0]*brigthness),math.ceil(pixList[i][1]*brigthness),math.ceil(pixList[i][2]*brigthness))
            pix.write()
            sleep_ms(10)
def color_range(color1,color2,fadingActive,fminBright,fspeed,fadetype,reverse):
    global pixLength,runAnimation
    satStep=(color2[1]-color1[1])/(pixLength-1)
    if color1[0]<=color2[0]:
        hueStep=(color2[0]-color1[0])/(pixLength-1)
    else:
        color2[0]+=360
        hueStep=(color2[0]-color1[0])/(pixLength-1)
    pixList=[0 for _ in range(pixLength)]
    for i in range(pixLength):
        hue=color1[0]+hueStep*i
        sat=color1[1]+satStep*i
        pixList[i]=getRGB(int(hue),int(sat),1)
    if reverse:
        pixList.reverse()
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        while runAnimation:
            fmaxBright=getBrightness(1-fminBright)+fminBright
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            for i in range(pixLength):
                pix[i]=(int(pixList[i][0]*bright),int(pixList[i][1]*bright),int(pixList[i][2]*bright))
            pix.write()
            sleep_ms(int(500/fspeed))
    else:
        while runAnimation:
            brigthness=getBrightness(1)
            for i in range(pixLength):
                pix[i]=(math.ceil(pixList[i][0]*brigthness),math.ceil(pixList[i][1]*brigthness),math.ceil(pixList[i][2]*brigthness))
            pix.write()
            sleep_ms(10)
def static_rainbow(saturation,fadingActive,fminBright,fspeed,fadetype,reverse):
    global runAnimation, pixLength
    hueStep=360/pixLength
    pixList=[getRGB(hueStep*i,saturation,1) for i in range(pixLength)]
    if reverse:
        pixList.reverse()
    if fadingActive:
        bright=fminBright
        up=True
        lvl=0
        while runAnimation:
            fmaxBright=getBrightness(1-fminBright)+fminBright
            bright,lvl,up=fading(lvl,up,fminBright,fmaxBright,fadetype)
            for i in range(pixLength):
                pix[i]=(int(pixList[i][0]*bright),int(pixList[i][1]*bright),int(pixList[i][2]*bright))
            pix.write()
            sleep_ms(int(500/fspeed))
    else:
        while runAnimation:
            brigthness=0.05+0.95*getBrightness(0.95)
            for i in range(pixLength):
                pix[i]=(math.ceil(pixList[i][0]*brigthness),math.ceil(pixList[i][1]*brigthness),math.ceil(pixList[i][2]*brigthness)) 
        pix.write() 
        sleep_ms(10)
def rainbow_scrolling(speed,saturation,reverse):
    global runAnimation
    hue=0
    while runAnimation:
        brightness=getBrightness(1)
        pix.fill(getRGB(hue,saturation,brightness))
        pix.write()
        if reverse:
            hue-=1
            if hue<=0:
                hue+=359
        else:
            hue+=1
            if hue>=360:
                hue-=360
        sleep_ms(int(5000/speed))
#dynamic category
def dynamic_color_range(color1,color2,speed,direction,reverse):
    global runAnimation, pixLength
    satStep=(color2[1]-color1[1])/(pixLength-1)
    if color1[0]<=color2[0]:
        hueStep=(color2[0]-color1[0])/(pixLength-1)
    else:
        color2[0]+=360
        hueStep=(color2[0]-color1[0])/(pixLength-1)

    if color1[1]>color2[1]:
        lowSat=color2[1]
        highSat=color1[1]
    if color1[1]<color2[1]:
        lowSat=color1[1]
        highSat=color2[1]

    pixList=[0 for _ in range(pixLength)]
    for i in range(pixLength):
        hue=color1[0]+hueStep*i
        sat=color1[1]+satStep*i
        pixList[i]=[hue,sat]
    if direction==1:
        satStep=-satStep
    if reverse:
        pixList.reverse()
    while runAnimation:
        brightness=0.05+0.95*getBrightness(0.95)
        for i in range(pixLength):
            if direction==0:
                pixList[i][0]+=1               
                if pixList[i][0]>color2[0]:
                    pixList[i][0]=color1[0]
            elif direction==1:
                pixList[i][0]-=1
                if pixList[i][0]<color1[0]:
                    pixList[i][0]=color2[0]
            if satStep>0:
                pixList[i][1]+=1
                if pixList[i][1]>highSat:
                    pixList[i][1]=lowSat
            elif satStep<0:
                pixList[i][1]-=1
                if pixList[i][1]<lowSat:
                    pixList[i][1]=highSat
            pix[i]=getRGB(pixList[i][0],pixList[i][1],brightness)
        pix.write()
        sleep_ms((5000/(abs(satStep*(pixLength-1))+hueStep*(pixLength-1)))/speed)
def dynamic_rainbow(saturation,speed,direction,reverse):
    global runAnimation, pixLength
    pixList=[(360/pixLength)*i for i in range(pixLength)]
    if reverse:
        pixList.reverse()               
    while runAnimation:
        brightness=0.05+0.95*getBrightness(0.95)
        for i in range(pixLength):
            if direction==0:
                pixList[i]+=1
                if pixList[i]>=359:
                    pixList[i]=0    
            elif direction==1:
                pixList[i]-=1
                if pixList[i]<=0:
                    pixList[i]=359
            pix[i]=getRGB(pixList[i],saturation,brightness)
        pix.write()
        sleep_ms(int(5000/speed))
#animation cathegory
def  running_light_full(color,tracewidth,style,speed):
    global runAnimation, pixLength
    if style==0 or style==2:
        pos=0
        up=True
    elif style==1:
        pos=pixLength-1
        up = False
    while runAnimation:
        brightness=0.05+0.95*getBrightness(0.95)
        pix.fill((0,0,0))
        if up:
            pos+=1
        else:
            pos-=1
        if pos<0 and not up and style==1:
                pos=pixLength-1
        elif pos<=0 and not up and style==2:
            up=True
        elif pos>pixLength-1 and up and style==0:
            pos=0
        elif pos>=pixLength-1 and up and style==2:
            pos=pixLength-1
            up =False
        pix[pos]=getRGB(color[0],color[1],brightness)
        if pos+tracewidth>pixLength-1:
            trace=tracewidth-(pos+tracewidth-pixLength+1)
        else:
            trace=tracewidth
        for i in range(pos+1,pos+trace+1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+i-pos)) 
        if pos-tracewidth<0:
            trace=tracewidth+(pos-tracewidth)
        else:
            trace=tracewidth
        for i in range(pos-1,pos-trace-1,-1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+pos-i))
        pix.write()
        sleep_ms(int(5000/speed))
def running_light_center(color,tracewidth,style,speed):
    global runAnimation,pixLength
    if pixLength%2==0:
        start1=int(pixLength/2)-1
        start2=int(pixLength/2)
    else:
        start1=int(pixLength/2)
        start2=int(pixLength/2)

    if style==0 or style==2:
        pos1=start1
        pos2=start2
        up2=True
        up1=False
    elif style==1:
        pos2=pixLength-1
        pos1=0
        up2 = False
        up1=True
    while runAnimation:
        brightness=0.05+0.95*getBrightness(0.95)
        pix.fill((0,0,0))
        if up1:
            pos1+=1
        else:
            pos1-=1
        if pos1<0 and not up1 and style==0:
                pos1=start1
        elif pos1<=0 and not up1 and style==2:
            up1=True
        elif pos1>start1 and up1 and style==1:
            pos1=0
        elif pos1>=start1 and up1 and style==2:
            pos1=start1
            up1 =False
        pix[pos1]=getRGB(color[0],color[1],brightness)
        if pos1+tracewidth>start1:
            trace=tracewidth-(pos1+tracewidth-start1)
        else:
            trace=tracewidth
        for i in range(pos1+1,pos1+trace+1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+i-pos1)) 
        if pos1-tracewidth<0:
            trace=tracewidth+(pos1-tracewidth)
        else:
            trace=tracewidth
        for i in range(pos1-1,pos1-trace-1,-1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+pos1-i))


        if up2:
            pos2+=1
        else:
            pos2-=1
        if pos2<start2 and not up2 and style==1:
                pos2=pixLength-1
        elif pos2<=start2 and not up2 and style==2:
            up2=True
        elif pos2>pixLength-1 and up2 and style==0:
            pos2=start2
        elif pos2>=pixLength-1 and up2 and style==2:
            pos2=pixLength-1
            up2 =False
        pix[pos2]=getRGB(color[0],color[1],brightness)
        if pos2+tracewidth>pixLength-1:
            trace=tracewidth-(pos2+tracewidth-pixLength+1)
        else:
            trace=tracewidth
        for i in range(pos2+1,pos2+trace+1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+i-pos2)) 
        if pos2-tracewidth<start2:
            trace=tracewidth-(start2-(pos2-tracewidth))
        else:
            trace=tracewidth
        for i in range(pos2-1,pos2-trace-1,-1):
            pix[i]=getRGB(color[0],color[1],brightness/(1+pos2-i))
        pix.write()
        sleep_ms(int(5000/speed))
#stars  mode
def stars(speed,stars_count): 
    global runAnimation,pixLength
    random.seed(random_seed_src.read_u16())
    if random.randint(0,5)==2:
        sat=100
    else:
        sat=random.randint(50,99)
    max_blvl=round(50+50*random.random())
    pos=random.randint(0,pixLength-1)
    posList=[pos]
    starList=[[pos,random.randint(0,359),sat,max_blvl,0,True]]#index,Hue,saturation,max_brigthness level,current brightnes level,up
    pix.fill((0,0,0))
    while runAnimation:
        brightness=0.05+0.95*getBrightness(0.95)
        if len(starList)<stars_count:
            if random.randint(0,stars_count-(stars_count-len(starList)))==1:
                if random.randint(0,5)==2:
                    sat=100
                else:
                    sat=random.randint(50,99)
                pos=random.randint(0,pixLength-1)
                while pos in posList:
                    pos=random.randint(0,pixLength-1)
                posList.append(pos)
                max_blvl=round(50+50*random.random()) 
                star=[pos,random.randint(0,359),sat,max_blvl,0,True]
                starList.append(star)
        starList2=[]
        for i in range(len(starList)):
            if starList[i][5]:
                starList[i][4]+=1
            else:
                starList[i][4]-=1
            if starList[i][4]>=starList[i][3] and starList[i][5]:
                starList[i][5]=False
            if starList[i][4]<=0 and not starList[i][5]:
                posList.pop(posList.index(starList[i][0]))
                pix[starList[i][0]]=(0,0,0)
                sleep_ms(1)
            else:
                pix[starList[i][0]]=getRGB(starList[i][1],starList[i][2],(starList[i][4]/100)*brightness)
                sleep_ms(1)
                starList2.append(starList[i])    
        starList=starList2.copy() 
        #print(starList)
        #print(posList)   
        pix.write()
        sleep_ms(int(500/speed))
#soundbar cathegory
def soundbar_monocolor(color,max_soundval,orientation):
    global runAnimation, pixLength 
    if orientation==2:
        if pixLength%2==0:
            start1=int(pixLength/2)-1
            start2=int(pixLength/2)
            pixLength2=start1+1
        else:
            start1=int(pixLength/2)
            start2=int(pixLength/2)
            pixLength2=start1+1
        sound_lvl_step=max_soundval/pixLength2
        while runAnimation:
            max_brightness=0.05+0.95*getBrightness(0.95)
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength2:
                length=pixLength2
            if length==0:
                i=start2-1
            for i in range(start2,start2+length):
                pix[i]=getRGB(color[0],color[1],max_brightness)
            if i+1<pixLength:
                pix[i+1]=getRGB(color[0],color[1],bright)
            if length==0:
                i=start1+1
            for i in range(start1,start1-length,-1):
                pix[i]=getRGB(color[0],color[1],max_brightness)
            if i-1>=0:
                pix[i-1]=getRGB(color[0],color[1],bright)
            pix.write()
            sleep_ms(5)
    else:
        sound_lvl_step=max_soundval/pixLength
        while runAnimation:
            max_brightness=0.05+0.95*getBrightness(0.95)
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength:
                length=pixLength
            if length==0:
                if orientation==0:
                    a=-1
                    i=-1
                else:
                    a=pixLength
                    i=-1
            for i in range(0,length):
                if orientation==0:
                    a=i
                else:
                    a=pixLength-1-i
                pix[a]=getRGB(color[0],color[1],max_brightness)
            if orientation==0:
                if a+1<pixLength:
                    pix[a+1]=getRGB(color[0],color[1],bright)
            else:
                if a-1>=0:
                    pix[a-1]=getRGB(color[0],color[1],bright)
            pix.write()
            sleep_ms(5)
def soundbar_color_range(color1,color2,max_soundval,orientation,reversed):
    global runAnimation,pixLength
    if color2[0]<color1[0]:
            color2[0]+=360 
    if orientation==2:
        if pixLength%2==0:
            start1=int(pixLength/2)-1
            start2=int(pixLength/2)
            pixLength2=start1+1
        else:
            start1=int(pixLength/2)
            start2=int(pixLength/2)
            pixLength2=start1+1
        sound_lvl_step=max_soundval/pixLength2
        satStep=(color2[1]-color1[1])/(pixLength2-1)
        hueStep=(color2[0]-color1[0])/(pixLength2-1)
        while runAnimation:
            max_brightness=0.05+0.95*getBrightness(0.95)
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength2:
                length=pixLength2
            if length==0:
                i=start2-1
            for i in range(start2,start2+length):
                if reversed:
                    hue=color2[0]-hueStep*(i-start2)
                    sat=color2[1]-satStep*(i-start2)
                else:
                    hue=color1[0]+hueStep*(i-start2)
                    sat=color1[1]+satStep*(i-start2)
                pix[i]=getRGB(hue,sat,max_brightness)
            if i+1<pixLength:
                if reversed:
                    hue=color2[0]-hueStep*(i-start2+1)
                    sat=color2[1]-satStep*(i-start2+1)
                else:
                    hue=color1[0]+hueStep*(i-start2+1)
                    sat=color1[1]+satStep*(i-start2+1)
                pix[i+1]=getRGB(hue,sat,bright)
            if length==0:
                i=start1+1  
            for i in range(start1,start1-length,-1):
                if reversed:
                    hue=color2[0]-hueStep*(start1-i)
                    sat=color2[1]-satStep*(start1-i)
                else:
                    hue=color1[0]+hueStep*(start1-i)
                    sat=color1[1]+satStep*(start1-i)
                pix[i]=getRGB(hue,sat,max_brightness)
            if i-1>=0:
                if reversed:
                    hue=color2[0]-hueStep*(start1-i+1)
                    sat=color2[1]-satStep*(start1-i+1)
                else:
                    hue=color1[0]+hueStep*(start1-i+1)
                    sat=color1[1]+satStep*(start1-i+1)
                pix[i-1]=getRGB(hue,sat,bright)
            pix.write()
            sleep_ms(5)
    else:
        sound_lvl_step=max_soundval/pixLength
        satStep=(color2[1]-color1[1])/(pixLength-1)
        hueStep=(color2[0]-color1[0])/(pixLength-1)
        while runAnimation:
            max_brightness=0.05+0.95*getBrightness(0.95)
            pix.fill((0,0,0))
            sound_val=sound_lvl()
            length=sound_val//sound_lvl_step
            bright=max_brightness*0.1+0.9*max_brightness*sound_val%sound_lvl_step
            if length>pixLength:
                length=pixLength
            if length==0:
                if orientation==0:
                    a=-1
                    i=-1
                else:
                    a=pixLength
                    i=-1
            for i in range(0,length):
                if orientation==0:
                    a=i
                else:
                    a=pixLength-1-i
                if reversed:
                    hue=color2[0]-hueStep*i
                    sat=color2[1]-satStep*i
                else:
                    hue=color1[0]+hueStep*i
                    sat=color1[1]+satStep*i
                pix[a]=getRGB(hue,sat,max_brightness)
            if orientation==0:
                if a+1<pixLength:
                    if reversed:
                        hue=color2[0]-hueStep*(i+1)
                        sat=color2[1]-satStep*(i+1)
                    else:
                        hue=color1[0]+hueStep*(i+1)
                        sat=color1[1]+satStep*(i+1)
                    pix[a+1]=getRGB(hue,sat,bright)
            else:
                if a-1>=0:
                    if reversed:
                        hue=color2[0]-hueStep*(i+1)
                        sat=color2[1]-satStep*(i+1)
                    else:
                        hue=color1[0]+hueStep*(i+1)
                        sat=color1[1]+satStep*(i+1)
                    pix[a-1]=getRGB(hue,sat,bright)
            pix.write()
            sleep_ms(5)
