import math
import copy
import sys
import subprocess

#String List: List of Characters
characters = ["Ophelia", "p1", "p2", "p3", "p4"]
charLoc = {"Ophelia":"l1", "p1":"l1", "p2":"l2", "p3":"l3", "p4":"l4"}

#Class: Event
class Event:
    """Contains all information for event"""

    def __init__(self, name, startTime, endTime, chars, loc, template):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.chars = chars
        self.loc = loc
        self.template = template

class World:
    """Contains all information for the current state of the world"""

    def __init__(self, raw):
        self.raw = raw
        new = raw[:-1].replace("Done.", "")
        new = new.replace(" looks like:", "")
        new = new.split(repr("\r\n").replace("'", ""))
        for c in new.copy():
            if c == "":
                new.remove(c)
            if c == " ":
                new.remove(c)
        factored = {}
        for c in new:
            s = c.split(":")
            s[1] = s[1].replace("[", "").replace("]", "").split('","')
            for i in range(len(s[1])):
                s[1][i] = s[1][i].replace('"', "")
            factored[s[0]]=s[1]
        self.factored = factored

    def query(str):
        return self.factored[str]

    def changes(self, old):
        ret = {}
        for i in self.factored.items():
            j = old.factored[i[0]]
            r= []
            for q in i[1]:
                if !j.contains(q):
                    r.append(q)
            ret[i[0]] = r


executeTemplate = "execute$name$($name$, $chars$ $loc$, $obs$)"
goTemplate = "go($chars$ $loc$)"

#Manual Definitions, events
e1 = Event("e1", 540, 600, ["p1", "p2"], "l2", executeTemplate)
e2 = Event("e2", 2160, 2220, ["p1", "p2", "p3", "p4"], "l3", executeTemplate)
e3 = Event("e3", 2160, 2220, ["p1", "p2", "p3", "p4"], "l4", executeTemplate)
m1 = Event("m1", 2880, 2880, ["Ophelia", "p3"], "null", executeTemplate)
go1 = Event("go1", 720, 720, ["p3"], "l2", goTemplate)
go2 = Event("go2", 840, 840, ["p4"], "l2", goTemplate)

#Priority Queue: Schedule
defaultSchedule = [e1, go1, go2, m1]
currentSchedule = defaultSchedule

def AddToSchedule(event, schedule):
    newSchedule = schedule.copy()
    if len(newSchedule) == 0:
        newSchedule.append(event)
    else:
        added = False
        for i in range(len(schedule)):
            if schedule[i].endTime >= event.endTime:
                newSchedule.insert(i, event)
                added = True
                break
        if added == False:
            newSchedule.append(event)
        for e in schedule:
            if ((e.startTime < event.endTime) and (e.endTime >= event.endTime)) or ((event.startTime < e.endTime) and (event.endTime >= e.endTime)):
                newSchedule.remove(e)
    return newSchedule

def RemoveFromSchedule(event, schedule):
    newSchedule = schedule.copy()
    newSchedule.remove(event)
    return newSchedule

#Method: Schedule all available events

#Method: Wait
def Wait(endTime):
    global currentSchedule
    while(len(currentSchedule) > 0):
        next = currentSchedule.pop(0)
        if next.endTime > endTime:
            break
        ExecuteEvent(next)


#Method: Observe
def Observe(event):
    ret = event.template
    char_string = ""
    for c in event.chars:
        char_string += c + ","
    ret = ret.replace("$name$", event.name)
    ret = ret.replace("$chars$", char_string)
    ret = ret.replace("$loc$", event.loc)
    ret = ret.replace("$obs$", "Ophelia")
    AddAction(ret)
    RunGame()

#Method: Execute Events
def ExecuteEvent(event):
    ret = event.template
    char_string = ""
    for c in event.chars:
        char_string += c + ","
    ret = ret.replace("$name$", event.name)
    ret = ret.replace("$chars$", char_string)
    ret = ret.replace("$loc$", event.loc)
    ret = ret.replace("$obs$", "unit")
    AddAction(ret)
    RunGame()

#Method: Tell Hearsay

#Method: Query

#Method: Reset
#def Reset():


#Hash: player/hearsay -> belief/goal

#Value: Time
currentTime = 480

dayHash = {"Thursday": 0, "Friday": 1440, "Saturday": 2880, "Sunday": 4320}
dayHashR = {0: "Thursday", 1440: "Friday", 2880: "Saturday", 4320: "Sunday"}

def TextTimeToInt(time):
    time_list = time.split(":")
    day = dayHash[time_list[0]]
    hour = int(time_list[1])*60
    minute = int(time_list[2])
    return day+hour+minute

def IntToTextTime(time):
    day = dayHashR[math.floor(time/1440)*1440]
    return day + ":" + str(math.floor((time%1440)/60)) + ":" + str((time%1440)%60)

#Value: Loop
currentLoop = 1

#More general tasks
#IO processing, terminal based, nothing fancy

#Triggereing an action in Ostari - may not be possible during run time, might require a run at each step
#Current plan is to keep template writting for each action taken, run it, return the results as the new
#world state, and then add more actions to it and rerun as the player makes more decisions, simulating
#runtime action taking. This template is restored to the default on a loop reset.

#Method: AddAction
def AddAction(action):
    global action_sequence
    action_sequence += action


#Method: RunGame
def RunGame():
    content = template.replace("$$", action_sequence)
    fname = "elsinore_ostari_loop"+ str(currentLoop) + ".cfg"
    f = open(fname,"w")
    f.write(content)
    f.close()
    out = str(subprocess.check_output([ostari_path, fname]))
    ind = out.find(":")
    out = out[ind+1:]
    ret = World(out)


#Reading beliefs and actions from ostari, also possibly not doable in runtime - simply output from run game

#Method QueryOutput

ostari_path = sys.argv[1]
template_path = sys.argv[2]

f = open(template_path, "r")
template = f.read()
f.close()

action_sequence = ""

worldState = World("")

ExecuteEvent(m1)
