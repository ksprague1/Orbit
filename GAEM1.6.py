class Vector():
    def __init__(self,x=0,y=0):
        self.x = float(x)
        self.y = float(y)
        self.m = (x**2+y**2)**0.5
    def __add__(self,other):
        return Vector(self.x + other.x,self.y + other.y)
    def __sub__(self,other):
        return Vector(self.x - other.x,self.y - other.y)
    def __mul__(self,scalar):
        return Vector(self.x *float(scalar),self.y *float( scalar))
    def dotheta(self,other):
        if self.m ==0 or other.m==0:
            return 0
        return (self.x*other.x+self.y*other.y)/(self.m*other.m)
    def Set(self,x=None,y=None):
        if x!=None:
            self.x = float(x)
        if y!=None:
            self.y = float(y)
        self.m = (self.x**2+self.y**2)**0.5
    def unit(self):
        if self.m == 0 :
            return Vector()
        return Vector(self.x/self.m,self.y/self.m)
    def string(self):
        return "(%.3f,%.3f: |%.3f|)"%(self.x,self.y,self.m)
#---------------------------END-VECTOR------------------------------------------
class body(object):
    def __init__(self,size,position,colour):
        global bodies
        bodies += [self]
        #instantiated object is added to a list of 'bodies'
        self.size = 2*size
        self.mass = 4/3.0*math.pi*size**3
        self.x = position[0]
        self.y = position[1]
        self.colour = colour
        self.v = Vector()
        self.static = False
        self.dv = Vector()
        self.bouncy = False
        #Other variables come into play later
    def delete(self):
        global bodies
        if self in bodies:
            del bodies[bodies.index(self)]
        #removes itself from the list, making python cleanup remove it
        #(the list was it's only reference)
    def crash(self,other):
        global bodies,dt
        #if both objects are bouncy, they bounce off of eachother
        if self.bouncy and other.bouncy:
            normal = Vector(self.x-other.x,self.y-other.y).unit()
            self.bounce(normal)
            other.x = self.x+normal.x*(-(self.size+other.size-0.0001))
            other.y = self.y+normal.y*(-(self.size+other.size-0.0001))
            other.bounce(normal*(-1))
            return
        #otherwise the other body is deleted and the current body takes it's mass
        #the colour is determined by the larger body in the collision
        self.colour = [self.colour,other.colour][self.mass<other.mass]
        xenerg = self.mass*self.v.x*abs(self.v.x)+other.mass*other.v.x*abs(other.v.x)
        yenerg = self.mass*self.v.y*abs(self.v.y)+other.mass*other.v.y*abs(other.v.y)
        self.mass += other.mass
        self.size = 2*(3.0*self.mass/4/math.pi)**(1/3.0)
        self.v.Set(x=0 if xenerg==0 else abs(xenerg/self.mass)**0.5*xenerg/abs(xenerg))
        self.v.Set(y=0 if yenerg==0 else abs(yenerg/self.mass)**0.5*yenerg/abs(yenerg))
        other.delete()
    def simpleaccel(self):
        global bodies,G_CONST
        if self.static:
            return
        #static etities don't accelerate or displace
        Forcex = 0
        Forcey = 0
        col = []        
        for body in bodies:
            if body == self:
                continue
            #calculate distance. . .
            distance = ((body.x-self.x)**2+(body.y-self.y)**2)**0.5
            if distance <= (self.size+body.size):
                col += [body]
                    #If they are too close make them collide
            #Fg = GMm/r^2
            Force = G_CONST*self.mass*body.mass/distance**2
            #break fg into it's x and y components and add to the net force
            Forcex += (body.x-self.x)/distance*Force
            Forcey += (body.y-self.y)/distance*Force
         #Delta V is (a)(dt) so when (a = F/m) dv = F/m*dt
        self.dv = Vector(Forcex/self.mass/2,Forcey/self.mass/2)*dt
        for body in col:
            #static bodies allways get preference when there is a crash
            if body.static:
                body.crash(self)
            else:
                self.crash(body)
    def displace(self):
        global dt
        #Important to call this only after each object has finished simpleaccel
        if self.static:
            return
        #add Delta V and move objects based on current velocity
        self.v  += self.dv
        self.x  += self.v.x*dt
        self.y  += self.v.y*dt
        
        #self.x  += self.vx +Forcex/self.mass/2
        #self.y  += self.vy + Forcey/self.mass/2
        #self.vx += Forcex/self.mass
        #self.vy += Forcey/self.mass BROKEN
    def bounce(self,normal,loss = False):
        #NORMAL MUST BE A UNIT VECTOR
        V = Vector(self.v.x,self.v.y)
        V*= loss if loss else self.bouncy*(1/(dt if dt>1 else 1))
        # Cosd = VdotNormal / |V|*|normal|
        Cosd = V.dotheta(normal)
        #Cosd will be the magnitude of V in the normal direction
        V1 = normal*(Cosd*V.m)
        V2 = V-V1
        GM = (self.dv.dotheta(normal)*(self.dv.m))
        #if the force of gravity is higer then the normal force, set them equal
        if -GM > V1.m:
            V1 = normal*(-GM)
        else:
            V1 = normal*(V1.m)
        #setting up velocity like this is important to determine when
        #the object is at rest
        self.v = V2
        self.dv += V1
#---------------------------END-BODY--------------------------------------------
class probe(body):
    def __init__(self,size,position,colour):
        super(probe,self).__init__(size,position,colour)
        #call __init__ in 'body' class
        self.mass = 1
        #probe's mass is allways 1
        self.static = True
        self.bouncy = True
        self.escape = 10
        #escape velocity is calculated each time the probe is at rest
    def simpleaccel(self):
        if self.static == True:
            self.aim()
            #User gets to assign a velocity <= 70% of escape velocity
            c.create_line(0,18,self.v.m*10,18,tag=("tes","end"),width = 28,fill = "red")
            #red line representing the current velocity
        else:
            super(probe,self).simpleaccel()
            #this code allows the player to bounce off of boundaries
            global boundaries
            for boundary in boundaries:
                normal = boundary.touching(self)
                if normal:
                    if boundary.bouncy:
                        self.bounce(normal)
            #print self.v.m,self.dv.m
            #determine if the player is at rest            
            TOL = 0.03*dt
            if self.v.m<TOL and self.dv.m < TOL:
                self.static = True
                for other in bodies:
                    if other == self:
                        continue
                    #if at rest, escape velocity for any body
                    #it's touching is determined.
                    distance = ((other.x-self.x)**2+(other.y-self.y)**2)**0.5
                    if distance <= (self.size+other.size):
                        self.escape = 0.8*(2*G_CONST*other.mass/distance)**0.5
                        print self.escape
                        break
                else:
                    self.static = False
    def crash(self,other):
        return
    def delete(self):
        c.create_text(4500/zoom,4500/zoom,text = "You lose",fill = "red",tag = "tes")
        c.update()
        game.end()
    def aim(self):
        global pressed,dt
        max_v = self.escape
        cur_v = [self.v.x,self.v.y]
        #format for dic is affected index,value,unaffected index
        dic = {CONTROLS["right"]:[0,1,1],CONTROLS["left"]:[0,-1,1],
               CONTROLS["down"]:[1,1,0],CONTROLS["up"]:[1,-1,0]}
        #adds velocity in the direction specified by a 'dic'
        #constantly makes sure the velocity isn't past the maximum
        for a in dic:
            if a in pressed and cur_v[dic[a][0]]*dic[a][1] < max_v-.005:
                cur_v[dic[a][0]] += max_v*0.01*dic[a][1]*dt
                if cur_v[dic[a][0]]*dic[a][1] > max_v:
                    cur_v[dic[a][0]] = max_v*dic[a][1]
                if cur_v[0]**2 + cur_v[1]**2 > max_v**2:
                    cur_v[dic[a][2]] = (max_v**2 - cur_v[dic[a][0]]**2)**0.5*cur_v[dic[a][2]]/abs(cur_v[dic[a][2]])
        self.v = Vector(cur_v[0],cur_v[1])
        if CONTROLS["space"] in pressed:
            self.static = False
        c.create_line((self.x)/zoom+res[0]/2,
        (self.y)/zoom+res[1]/2,(self.x +200/max_v*self.v.x)/zoom+res[0]/2,
        (self.y+200/max_v*self.v.y)/zoom+res[1]/2,tag="tes",width=2,fill=self.colour)
        c.create_line(0,18,max_v*10,18,tag=("tes","end"),width = 28,fill = "blue")
        #line representing probe's velocity vector
#---------------------------END-PROBE-------------------------------------------
class boundary():
    def __init__(self,coords):
        global boundaries
        self.coords = coords
        #x1,y1,x2,y2
        dx = coords[2] - coords[0]
        dy = coords[3] - coords[1]
        #uses 2 points and a slope
        if dx == 0:
            self.slope = None
        else:
            self.slope = float(dy)/dx
        self.bouncy = False
        boundaries += [self]

    def draw(self):
        global zoom,res
        c.create_line(self.coords[0]/zoom+res[0]/2,self.coords[1]/zoom+res[1]/2,
        self.coords[2]/zoom+res[0]/2,self.coords[3]/zoom+res[1]/2,tag = "tes",
        fill=["black","red"][self.bouncy],width = 5)

    def touching(self,other):
        #uses formula for finding the distance to a line
        tol = 10.0+other.size
        if self.slope == None:
            if (other.x > self.coords[0]-tol/2 and
                other.x < self.coords[0]+tol/2  and
                (self.coords[1] >=other.y >=self.coords[3] or
                 self.coords[3]>=other.y>=self.coords[1])):
                return Vector(other.x -self.coords[0],0).unit()
            return False
        elif self.slope == 0:
            if (other.y > self.coords[1]-tol/2 and
                other.y < self.coords[1]+tol/2 and
                (self.coords[0] >=other.x >=self.coords[2] or
                 self.coords[2]>=other.x>=self.coords[0])):
                return Vector(0,other.y -self.coords[1]).unit()
            return False
        elif self.coords[0] >=other.x >=self.coords[2] or self.coords[2]>=other.x>=self.coords[0]:
            m2 = -1/self.slope
            b2 = other.y-m2*other.x
            b = self.coords[1]-self.slope*self.coords[0]
            meetup = (b-b2) / (m2-self.slope)
            meetup = [meetup,m2*meetup+b2]
            distance = ((other.x-meetup[0])**2+(other.y-meetup[1])**2 )**0.5
            if distance <tol-5.0:
                return Vector(other.x-meetup[0],other.y-meetup[1]).unit()
        return False
        #either returns the direction of the normal or False
        #y = mx+b -> b=y-mx
        #m2x+b2 = mx+b
        #(m2-m)x = b-b2
        #x = (b-b2)/(m2-m)
    def bounceold(self,other):
        if self.slope == None:
            nV = (1,0,1)
        elif self.slope == 0:
            nV = (0,1,1)
        else:
            nV = (1,-1/self.slope,(1+(1/self.slope)**2)**0.5)
        oV = (other.vx,other.vy,(other.vx**2+other.vy**2)**0.5)
        theta = math.acos(abs(nV[0]*oV[0]+nV[1]*oV[1])/(nV[2]*oV[2]))
        print math.degrees(theta)
        theta = math.pi - 2*theta
        other.vx = oV[0]*math.cos(theta)-oV[1]*math.sin(theta)
        other.vy = oV[0]*math.sin(theta)+oV[1]*math.cos(theta)
        self.bouncy = False

#---------------------------END-BOUNDARY----------------------------------------
class gamemode1():
    photo = []
    def __init__(self,planets = 6):
        c.delete("tes","end")
        c.create_text(res[0]/2,res[1]/2,text="LOADING. . .")
        c.update()
        #Add that loading screen 
        global bodies,boundaries
        self.input = None
        self.fctn = self.update
        self.high_scores = OnlineScore.get_score()
        self.high_score = int(self.high_scores[0][1])*100
        self.key  = "b3jd0d;]e9"
        self.score = 0
        self.bg = 3931
        if gamemode1.photo == []:
            photo  = PhotoImage(file="back.gif")
            h = res[1]/photo.height()
            photo = photo.zoom(int(4*h+0.5),int(4*h+0.5))
            photo = photo.subsample(4,4)
            gamemode1.photo = [photo,0]
        #need to find a way to resize this
        bodies = []
        boundaries = []
        #create evenly spaced planets
        for BODY in range(planets):  
            BODY = body(random.randint(60,80),[10240*BODY/planets-5120,random.randint(1,7380)-3690],random.choice(colours))
            BODY.static = True
            BODY.bouncy = True
        #body(30,[1200,0],"black").v = Vector(0,1.5)
        #body(5,[1300,0],"pink").v = Vector(0,-1.1)#.static = True
        #satelite(bodies[0],distance = 800)
        #satelite(bodies[1])
        self.player = probe(10,[100,200],"green")
        self.player.bouncy = 0.7
    def update(self):
        global bodies,zoom,res
        c.delete("tes")
        #make the background
        c.create_image(gamemode1.photo[1],0, image = gamemode1.photo[0],tag = "tes",anchor = NW)
        #time.sleep(0.03)
        for b in bodies:
            b.simpleaccel()
        #player bounces off of top and bottom of screen
        if abs(self.player.y) > 3640:
            self.player.bounce(Vector(0,-self.player.y).unit(),loss=1)
        for b in bodies:
            b.displace()
            drend = c.create_oval((b.x+b.size)/zoom+res[0]/2,
            (b.y+b.size)/zoom+res[1]/2,(b.x - b.size)/zoom+res[0]/2,
            (b.y - b.size)/zoom+res[1]/2,tag="tes",width=0,fill = b.colour)
        #for boundary in boundaries:
            #boundary.draw()
        fall = 3*dt
        if self.player.x > 4123:
            #print player.x,res[0]*zoom/2
            fall = self.player.x-4120
        for b in bodies:
            b.x-=fall
            if b.x < -5120:
                b.delete()
                if b.bouncy == True:
                #print random.randint(1,res[1]*zoom)-res[1]*zoom/2
                    S = random.choice(range(60,80)+[200,300])
                    Body = body(S,[6120,
                    random.randint(1,7380)-3690]
                    ,random.choice(colours))
                    Body.static = True
                    Body.bouncy = True
                    satelite(Body,distance = random.randint(1,100))
        self.score += int(fall)
        if self.score > self.high_score:
            self.high_score = self.score
        c.create_text(50,40,text = str(self.score/100),tag=("tes","end"),fill = "red")
        c.create_text(50,60,text="High Score: "+str(self.high_score/100),tag=("tes","end"),fill="red")
        gamemode1.photo[1] -= fall*0.05
        if gamemode1.photo[1] < -self.bg:
            gamemode1.photo[1] = 0
    def end(self,event=None):
        c.delete("end")
        if self.fctn != self.end:
            self.fctn = self.end
            self.input = self.end
            self.name = ""
            if self.highscore() == False:
                self.score = -100
        if self.score <0:
            c.create_text(res[0]/2,res[1]/2,text="PRESS ENTER TO BEGIN"
                +self.name,fill="blue",tag = "end",
                font=("datetimes",int(180/zoom),"bold"),anchor = N)
            if event != None and str(event.keysym) == "Return":
                self.input = None
                self.__init__()
        else:
            c.create_text(res[0]/2,res[1]/2,text="YOUR NAME: "
                +self.name,fill="blue",tag = "end",
                font=("datetimes",int(180/zoom),"bold"),anchor = N)
        if event != None and self.score >0:
            if str(event.keysym) == "BackSpace" and len(self.name) >0:
                self.name = self.name[:-1]
            elif str(event.keysym) == "Return" and len(self.name.strip()) >0:
                OnlineScore.write_score(self.score/100,self.name.strip(),key=self.key)
                self.input = None
                self.__init__()
            elif len(self.name) <= 50:
                if str(event.keysym) != "Return"and str(event.keysym) != "BackSpace":
                    self.name+= str(event.char)
            
    def highscore(self):
        made_it = False
        txt_idx = 0
        self.high_scores = OnlineScore.get_score()
        for idx in range(len(self.high_scores)):
            if  self.score/100 > int(self.high_scores[idx][1]) and not made_it:
                made_it = True
                c.create_text(10,20*txt_idx,text="YOU".ljust(52)
                +str(self.score/100),fill="blue",tag = "tes",
                font=("Courier",int(180/zoom),"bold"),anchor = NW)
                txt_idx+=1
            c.create_text(10,20*txt_idx,text=self.high_scores[idx][0].ljust(52)
            +self.high_scores[idx][1],fill="red",tag = "tes",
            font=("Courier",int(180/zoom),"bold"),anchor = NW)
            txt_idx+=1
        if not made_it:
            c.create_text(10,20*(txt_idx+1),text="YOU".ljust(52)
                +str(self.score/100),fill="blue",tag = "tes",
                font=("Courier",int(180/zoom),"bold"),anchor = NW)
        return made_it
#---------------------------END-GAMEMODE1---------------------------------------
def keypress(event):
    global bodies,zoom,game
##    for body in bodies:
##        if str(event.char) == "p":
##            print "%.2f,%.2f"%(body.x,body.y)
##    if str(event.char) == "=" and zoom >0.1:
##        zoom -=0.1
##    if str(event.char) == "-":
##        zoom +=0.1
    pressed[str(event.keysym)] = str(event.char)
    if game.input != None:
        game.input(event)
    elif str(event.char) == 'r':
        game.__init__()
def keyrelease(event):
    if str(event.keysym) in pressed:
        del pressed[str(event.keysym)]

def callback(event):
    c.focus_set()
    print dt
    #print photo[1]
def dot_rend():
    global bodies,zoom,res
    for body in bodies:
        body.simpleaccel()
        #body.accelerate()
        #drend2=c.create_text(dot[0],dot[1]-20,text=names[dot[3]],
        #tag="tes",fill = colours[dot[2]])
    for body in bodies:
        body.displace()
        drend = c.create_oval((body.x+body.size)/zoom+res[0]/2,
        (body.y+body.size)/zoom+res[1]/2,(body.x - body.size)/zoom+res[0]/2,
        (body.y - body.size)/zoom+res[1]/2,tag="tes",width=0,fill = body.colour)
        #print dots,dot
    for boundary in boundaries:
        boundary.draw()
                
def gamegen2():
    global bodies,boundaries
    bodies = []
    boundaries = []
    boundary([1000,-100,1000,100])
    planet_circle(5,180)
    probe(5,[50,0],"green").bouncy = 0.99
def planet_circle(density,r):
    sph = density**2
    index = 0.5
    for s4 in range(int(sph**0.5*2/index + 1)):
        num4 = sph**0.5*math.sin(math.radians(360/(sph**0.5*2/index + 1)*s4))
        down4 = num4 ** 2
        if down4 > sph:
            print "fuk",down4,sph
            continue
        s2 = (sph- down4)**0.5
        #print num4,s2,"|",s4
        s0 = -s2
        body(50,[s2*r,num4*r],"red").static = True
        body(50,[s0*r,num4*r],"red").static = True
def satelite(b,distance = 0):
    distance += b.size*4
    other = body(b.size/5+1,[b.x+distance,b.y],"pink")
    Force = G_CONST*b.mass*other.mass/distance**2
    accel = Force/other.mass/2
    other.v = Vector(b.v.x,b.v.y+(accel*distance)**0.5)
    return other
def default():
    global bodies,zoom,res,dt,t
    c.delete("tes")
    #datetime.sleep(0.001)
    for b in bodies:
        b.simpleaccel()
    for b in bodies:
        b.displace()
        drend = c.create_oval((b.x+b.size)/zoom+res[0]/2,
        (b.y+b.size)/zoom+res[1]/2,(b.x - b.size)/zoom+res[0]/2,
        (b.y - b.size)/zoom+res[1]/2,tag="tes",width=0,fill = b.colour)
from Tkinter import *
import random,datetime,math,OnlineScore,time
controls = {"w":[1,-2],"s":[1,2],"a":[0,-2],"d":[0,2]}
pressed = {}
root = Tk()
if root.winfo_screenwidth()/float(root.winfo_screenheight()) > 512/369.0:
    zoom = 7380.0/root.winfo_screenheight()
    c = Canvas(root, width=root.winfo_screenheight()*512/369.0, height=root.winfo_screenheight())
    adj = 'left'
else:
    adj = 'top'
    zoom = 10240.0/root.winfo_screenwidth()
    c = Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenwidth()*369.0/512)
print zoom
Button(root,text = """---------GAEM 1.6---------
Aim with Arrow Keys,
Blast Off with Spacebar
Don't go too far left
Don't hit the pink planets!
You can land on the others""",font = ('Terminal',8),command=root.destroy).pack(side=adj)
root.attributes("-fullscreen", True)
c.bind("<KeyPress>", keypress)
c.bind("<KeyRelease>", keyrelease)
c.bind("<Button-1>", callback)
c.configure(background='violet')
root.configure(background='navy')
c.pack(side=adj)
colours = ["red","orange","yellow","green","blue","magenta","purple","sienna"]
bodies = []
boundaries = []
G_CONST = 0.03#6.67408e-11
def DeltaT(dt):
    global t
    dt*=0.99
    dt += (datetime.datetime.now() - t).microseconds/500000.0
    if dt>5:
        dt = 5.0
    t = datetime.datetime.now()
    return dt
def StaticT(dt):
    return 1
#zoom = 10
#gamegen2()
res = [10240.0/zoom,7380.0/zoom]
game = gamemode1()
CONTROLS = {"up":"Up","down":"Down","left":"Left","right":"Right","space":"space"}
fil = open("settings.txt","r")
DT = fil.readline().split("=")[1].strip() == "True"
for f in fil:
    f = f.split("=")
    f[0] = f[0].strip().lower()
    if f[0] in CONTROLS:
        CONTROLS[f[0]] = f[1].strip()
fil.close()
print DT,CONTROLS
DT = DeltaT if DT else StaticT
c.focus_set()
dt = 1
t = datetime.datetime.now()
game.fctn()
c.update()
#time.sleep(0.1)
dt = (datetime.datetime.now() - t).microseconds/50000.0
t = datetime.datetime.now()
print dt
while True:
    game.fctn()
    #time.sleep(0.1)
    #default()
    c.update()
    dt = DT(dt)
root.resizable(0, 0)
root.mainloop()
'''def accelerate(self):
        global bodies,G_CONST
        Forcex = 0
        Forcey = 0
        for body in bodies:
            distance = ((body.x-self.x)**2+(body.y-self.y)**2)**0.5
            Force = G_CONST*self.mass*body.mass/distance**2
            Forcex += (body.x-self.x)/distance*Force
            Forcey += (body.y-self.y)/distance*Force
        #print abs(Forcex**2+Forcey**2 - Force**2) <0.0000000000001
            #BROKEN?
        accelx = Forcex/self.mass
        accely = Forcey/self.mass
        cur_update = datetime.datetime()
        deltaT = 1#cur_update-self.last_update
        vfx = self.vx+accelx*deltaT
        vfy = self.vy+accely*deltaT
        deltaDx = (self.vx+vfx)*0.5*deltaT
        deltaDy = (self.vy+vfy)*0.5*deltaT
        self.x  += deltaDx
        self.y  += deltaDy
        self.vx = vfx
        self.vy = vfy
        self.last_update = cur_update'''
