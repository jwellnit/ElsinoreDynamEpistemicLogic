import math
import copy
import sys
import subprocess

#String List: List of Characters
characters = ["Ophelia", "p1", "p2", "p3", "p4"]
charLocDefault = {"Ophelia":"l1", "p1":"l1", "p2":"l2", "p3":"l3", "p4":"l4"}
charLoc = charLocDefault
hearsayList = ["h1"]
locs = ["l1", "l2", "l3", "l4"]

#Class: Event
class Event:
    """Contains all information for event"""

    def __init__(self, name, startTime, endTime, chars, loc, template, preconditions, interrupt, die):
        self.name = name
        self.startTime = startTime
        self.endTime = endTime
        self.chars = chars
        self.loc = loc
        self.template = template
        self.preconditions = preconditions
        self.interrupt = interrupt
        self.die = die

    def __repr__(self):
        return self.name + ":" + IntToTextTime(self.startTime) + "-" + IntToTextTime(self.endTime) + ":" + self.loc + "\n"

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

    def query(self, str):
        return self.factored[str]

    def changes(self, old):
        ret = {}
        for i in self.factored.items():
            j = old.factored[i[0]]
            r= []
            for q in i[1]:
                if not q in j:
                    r.append(q)
            ret[i[0]] = r


executeTemplate = "execute$name$($name$,$chars$$loc$,$obs$)\n"
goTemplate = "go($char$,$loc$)\n"
tellTemplate = "tellHearsay($player$,$char$,$hearsay$)\n"
beliefTemplate = "updateBeliefO($char$,$belief$,$obs$,$bool$)\n"
hearsayTemplate = "updateHearsay($player$,$hearsay$,$bool$)\n"
goalTemplate = "updateGoalO($char$,$goal$,$obs$,$bool$)\n"
busyTemplate = "setBusyO($char$,$bool$,$obs$)\n"
upsetTemplate = "setUpsetO($char$,$bool$,$obs$)\n"
shatteredTemplate = "setShatteredO($char$,$bool$,$obs$)\n"
deadTemplate = "setBDeadO($char$,$bool$,$obs$)\n"
cancelTemplate = "cancelEvent($name$)\n"
scheduleTemplate = "schedule$name$($name$)\n"


#Manual Definitions, events
e1 = Event("e1", 540, 600, ["p1", "p2"], "l2", executeTemplate, [], False, False)
e2 = Event("e2", 2160, 2220, ["p1", "p2", "p3", "p4"], "l3", executeTemplate, ["believes(b1,p2,true)", "goal(g1,p2,true)"], False, False)
e3 = Event("e3", 2160, 2220, ["p1", "p2", "p3", "p4"], "l4", executeTemplate, ["believes(b2,p3,true)", "goal(g2,p3,true)"], False, False)
m1 = Event("m1", 2880, 2880, ["Ophelia", "p3"], "null", executeTemplate, [], True, True)
go1 = Event("go1", 720, 720, ["p3"], "l2", goTemplate, [], False, False)
go2 = Event("go2", 840, 840, ["p4"], "l2", goTemplate, [], False, False)

events = [e2,e3]

#Priority Queue: Schedule
defaultSchedule = [e1, go1, go2, m1]
currentSchedule = defaultSchedule
currentEvents = []

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
                a = cancelTemplate.replace("$name$", e.name)
                AddAction(a)
    RunGame()
    return newSchedule

def RemoveFromSchedule(event, schedule):
    newSchedule = schedule.copy()
    newSchedule.remove(event)
    a = cancelTemplate.replace("$name$", event.name)
    AddAction(a)
    RunGame()
    return newSchedule

#Method: Schedule all available events
def ScheduleEvents():
    global currentSchedule
    state = worldState.query("Truth")
    for e in events:
        s = "scheduled($name$,true)".replace("$name$", e.name)
        i = "impossible($name$,true)".replace("$name$", e.name)
        c = "completed($name$,true)".replace("$name$", e.name)
        if (not s in state) and (not i in state) and (not c in state) and e.startTime > currentTime:
            sat = True
            for p in e.preconditions:
                if not p in state:
                    sat = False
            if sat:
                AddAction(scheduleTemplate.replace("$name$", e.name))
                print("got here")
                currentSchedule = AddToSchedule(e, currentSchedule)
    RunGame()
    findCurrentEvents()
    return

def ResolveHearsay(char, hearsay):
    state = worldState.query(char)
    AddAction(hearsayTemplate.replace("$player$", char).replace("$hearsay$", hearsay).replace("$bool$", "false"))
    new = result.get(char + ":" + hearsay, "This character is not interested in that hearsay.")
    if new == "This character is not interested in that hearsay.":
        print (new)
        return
    for n in new:
        switch = {
        "upset" : upsetTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","Ophelia"),
        "busy" : busyTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","Ophelia"),
        "shattered" : shatteredTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","Ophelia"),
        "dead" : deadTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","Ophelia"),
        "belief" : beliefTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","Ophelia").replace("$belief$",n[1]),
        "goal" : goalTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","Ophelia").replace("$goal$",n[1])
        }
        AddAction(switch[n[0]])
    RunGame()
    ScheduleEvents()
    return

#Method: Wait
def Wait(endTime):
    global currentSchedule
    global currentTime
    global currentEvents
    while(len(currentSchedule) > 0):
        next = currentSchedule.pop(0)
        if next.endTime > endTime:
            currentSchedule.insert(0, next)
            break
        cont = ExecuteEvent(next)
        if not cont:
            return
    currentTime = endTime
    findCurrentEvents()

def findCurrentEvents():
    global currentEvents
    global currentSchedule
    currentEvents = []
    for e in currentSchedule:
        if e.startTime < currentTime:
            currentEvents.append(e)
    for e in currentEvents:
        if e.interrupt:
            currentEvents.remove(e)
            currentSchedule.remove(e)
            cont = ExecuteEvent(e)
            return

#Method: Observe
def Observe(event):
    global charLoc
    global currentSchedule
    ret = event.template
    if ret == goTemplate:
        charLoc[event.chars[0]] = event.loc
    char_string = ""
    for c in event.chars:
        char_string += c + ","
    ret = ret.replace("$name$", event.name)
    ret = ret.replace("$chars$", char_string)
    ret = ret.replace("$loc$", event.loc)
    ret = ret.replace("$obs$", "Ophelia")
    AddAction(ret)
    RunGame()
    if event.die:
        return False
    currentSchedule = RemoveFromSchedule(event, currentSchedule)
    ScheduleEvents()
    findCurrentEvents()
    return True

#Method: Execute Events
def ExecuteEvent(event):
    global charLoc
    ret = event.template
    if ret == goTemplate:
        charLoc[event.chars[0]] = event.loc
    char_string = ""
    for c in event.chars:
        char_string += c + ","
    ret = ret.replace("$name$", event.name)
    ret = ret.replace("$chars$", char_string)
    ret = ret.replace("$loc$", event.loc)
    ret = ret.replace("$obs$", "unit")
    AddAction(ret)
    RunGame()
    if event.die:
        Reset()
        return False
    ScheduleEvents()
    findCurrentEvents()
    return True

#Method: Tell Hearsay
def TellHearsay(char, hearsay):
    backup = action_sequence
    action = tellTemplate.replace("$player$", "Ophelia").replace("$hearsay$", hearsay).replace("$char$", char).replace("$bool$", "true")
    AddAction(action)
    res = RunGame()
    if res == "ERROR":
        print("This action is not possible at this time.")
        RemoveAction(action)
        return
    ResolveHearsay(char, hearsay)

#Method: Query
def Query(name):
    print(name + ": " + str(worldState.factored[name]))

#Method: Go
def Go(loc):
    global charLoc
    AddAction(goTemplate.replace("$char$", "Ophelia").replace("$loc$", loc))
    charLoc["Ophelia"] = loc
    RunGame()


#Method: Reset
def Reset():
    global currentSchedule
    global currentTime
    global action_sequence
    global currentLoop
    global charLoc
    global currentEvents

    print("You died.")

    currentTime = 480
    currentSchedule = defaultSchedule.copy()
    action_sequence = ""

    charLoc = charLocDefault
    currentEvents = []

    for i in worldState.query("Ophelia"):
        if "knows" in i:
            h = i.replace("knows)", "").replace(",true)", "")
            AddAction(hearsayTemplate.replace("$player$", "Ophelia").replace("$hearsay$", h))

    currentLoop += 1
    RunGame()

#Hash: player/hearsay -> belief/goal
result = {
"p2:h1" : [("belief","b1"), ("goal","g1"), ("upset", "")],
"p3:h1" : [("belief","b2"), ("goal","g2")]
}

#Value: Time
currentTime = 480

dayHash = {"Thursday": 0, "Friday": 1440, "Saturday": 2880, "Sunday": 4320}
dayHashR = {0: "Thursday", 1440: "Friday", 2880: "Saturday", 4320: "Sunday"}

def TextTimeToInt(time):
    time_list = time.split(":")
    day = dayHash.get(time_list[0], "Fail")
    if day == "Fail":
        return day
    hour = int(time_list[1])*60
    minute = int(time_list[2])
    if day+hour+minute > 5760 or day+hour+minute < 0 or day+hour+minute < currentTime:
        return "Fail"
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

#Method: AddAction
def RemoveAction(action):
    global action_sequence
    print(action_sequence[::-1].replace(action[::-1], "")[::-1])
    #action_sequence = action_sequence[::-1].replace(action[::-1], "")[::-1]

#Method: RunGame
def RunGame():
    global worldState
    content = template.replace("$$", action_sequence)
    fname = "elsinore_ostari_loop"+ str(currentLoop) + ".cfg"
    f = open(fname,"w")
    f.write(content)
    f.close()
    out = str(subprocess.check_output([ostari_path, fname]))
    ind = out.find(":")
    out = out[ind+1:]
    if not ("Truth" in out):
        return("ERROR")
    worldState = World(out)


#Reading beliefs and actions from ostari, also possibly not doable in runtime - simply output from run game

#Method QueryOutput

ostari_path = sys.argv[1]
template_path = sys.argv[2]

f = open(template_path, "r")
template = f.read()
f.close()

action_sequence = ""

worldState = World("")

RunGame()

inp = ""
while (inp != "quit"):
    print("Current Time: " + IntToTextTime(currentTime))
    print("Current Schedule: " + str(currentSchedule))
    print("Current Events: " + str(currentEvents))
    print("Locations: " + str(charLoc))
    print("""Available Actions:
    wait(<day:hour:minute>)
    go(<place>)
    tellHearsay(<character>, <hearsay>)
    observe(<event>)
    query(<character (including Ophelia) or "Truth">)
    quit""")
    inp = input("Next Action: ")
    if inp == "quit":
        break
    formatted = inp.replace(")", "").split("(")
    if formatted[0] == "wait":
        if TextTimeToInt(formatted[1]) == "Fail":
            print("This is not a valid action")
        else:
            Wait(TextTimeToInt(formatted[1]))
    elif formatted[0] == "go":
        if formatted[1] in locs:
            Go(formatted[1])
        else:
            print("This is not a valid action")
    elif formatted[0] == "tellHearsay":
        args = formatted[1].split(", ")
        print(args)
        if len(args) == 2 and args[0] in characters and args[1] in hearsayList:
            TellHearsay(args[0], args[1])
        else:
            print("This is not a valid action")
    elif formatted[0] == "observe":
        test = False
        event = ""
        for e in currentEvents:
            if formatted[1] == e.name:
                test = True
                event = e
        if test:
            Observe(e)
        else:
            print("This is not a valid action")
    elif formatted[0] == "query":
        if formatted[1] in characters or formatted[1] == "Truth":
            print(worldState.query(formatted[1]))
        else:
            print("This is not a valid action")
    else:
        print("This is not a valid action")
