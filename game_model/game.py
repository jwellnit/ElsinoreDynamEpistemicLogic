import math
import copy
import sys
import subprocess

#String List: List of Characters
characters = ["ophelia", "hamlet", "laertes", "polonius", "bernardo", "brit"]
charLocDefault = {"ophelia":"upperHall", "hamlet":"upperHall", "laertes":"groundsDocks", "polonius":"upperHall", "bernardo":"lowerHall", "brit":"lowerHall"}
charLoc = charLocDefault.copy()
hearsayList = ["imInDanger", "britIsASpy", "spyInElsinore", "bernardoSummon"]
locs = ["upperHall", "lowerHall", "mainHall", "groundsDocks", "courtyard", "library", "null"]

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
goTemplate = "go($chars$$loc$)\n"
tellTemplate = "tellHearsay($player$,$char$,$hearsay$)\n"
beliefTemplate = "updateBeliefO($char$,$belief$,$obs$,$bool$)\n"
hearsayTemplate = "updateHearsay($player$,$hearsay$,$bool$)\n"
goalTemplate = "updateGoalO($char$,$goal$,$obs$,$bool$)\n"
busyTemplate = "setBusyO($char$,$bool$,$obs$)\n"
upsetTemplate = "setUpsetO($char$,$bool$,$obs$)\n"
shatteredTemplate = "setShatteredO($char$,$bool$,$obs$)\n"
deadTemplate = "setBDeadO($char$,$bool$,$obs$)\n"
goneTemplate = "setGoneO($char$,$bool$,$obs$)\n"
cancelTemplate = "cancelEvent($name$)\n"
scheduleTemplate = "schedule$name$($name$)\n"


#Manual Definitions, events

#events
poloniusLecture = Event("poloniusLecture", 360, 480, ["ophelia", "polonius", "hamlet"], "upperHall", executeTemplate, [], False, False)
castleBriefing = Event("castleBriefing", 570, 690, ["polonius", "bernardo"], "mainHall", executeTemplate, [], False, False)
laertesLeaves = Event("laertesLeaves", 630, 635, ["laertes", "brit"], "groundsDocks", executeTemplate, [], False, False)
murder = Event("murder", 3450, 3480, ["ophelia", "brit"], "null", executeTemplate, [], True, True)
hamletKillsPolonius = Event("hamletKillsPolonius", 2970, 3030, ["hamlet", "polonius"], "upperHall", executeTemplate, [], False, False)
laertesMakesPlan = Event("laertesMakesPlan", 510, 630, ["laertes", "bernardo"], "lowerHall", executeTemplate, ["believes(opheliaInDanger,laertes,true)"], False, False)
laertesMeetsBrit = Event("laertesMeetsBrit", 1140, 1260, ["laertes", "brit"], "upperHall", executeTemplate, ["believes(opheliaInDanger,laertes,true)", "believes(opheliaInDanger,bernardo,true)"], False, False)
laertesKillsHamlet = Event("laertesKillsHamlet", 3300, 3330, ["laertes", "hamlet"], "courtyard", executeTemplate, ["believes(opheliaInDanger,laertes,true)", "dead(polonius,true)"], False, False)
laertesConfessesBrit = Event("laertesConfessesBrit", 3331, 3360, ["laertes", "brit"], "library", executeTemplate, ["believes(opheliaInDanger,laertes,true)", "dead(polonius,true)", "dead(hamlet,true)"], False, False)
bernardoInterrogatesHamlet = Event("bernardoInterrogatesHamlet", "null", "null", ["bernardo", "hamlet"], "lowerHall", executeTemplate, ["believes(opheliaInDanger,bernardo,true)", "believes(iHaveBeenSummoned,hamlet,true)"], False, False)
bernardoInterrogatesPolonius = Event("bernardoInterrogatesPolonius", "null", "null", ["bernardo", "polonius"], "lowerHall", executeTemplate, ["believes(opheliaInDanger,bernardo,true)", "believes(iHaveBeenSummoned,polonius,true)"], False, False)
bernardoInterrogatesBrit = Event("bernardoInterrogatesBrit", "null", "null", ["bernardo", "brit"], "lowerHall", executeTemplate, ["believes(opheliaInDanger,bernardo,true)", "believes(iHaveBeenSummoned,brit,true)"], False, False)
britMeetsFortinbras_2 = Event("britMeetsFortinbras", 3060, 3120, ["brit"], "groundsDocks", executeTemplate, ["believes(britMeetsAtDocks,ophelia,true)"], False, False)
britMeetsFortinbras_1 = Event("britMeetsFortinbras", 1620, 1680, ["brit"], "groundsDocks", executeTemplate, ["believes(britMeetsAtDocks,ophelia,true)"], False, False)
bernardoConfrontsBrit = Event("bernardoConfrontsBrit", "null", "null", ["bernardo", "brit"], "lowerHall", executeTemplate, ["believes(britIsASpy,bernardo,true)"], False, False)
laertesConfrontsBrit = Event("bernardoConfrontsBrit", "null", "null", ["laertes", "brit", "bernardo"], "upperHall", executeTemplate, ["believes(britIsASpy,laertes,true)"], False, False)

#schedules
#hamlet
hamletGo1 = Event("hamletGo1", 510, 510, ["hamlet"], "courtyard", goTemplate, [], False, False)
hamletGo2 = Event("hamletGo2", 690, 690, ["hamlet"], "upperHall", goTemplate, [], False, False)
hamletGo3 = Event("hamletGo3", 720, 720, ["hamlet"], "library", goTemplate, [], False, False)
hamletGo4 = Event("hamletGo4", 810, 810, ["hamlet"], "courtyard", goTemplate, [], False, False)
hamletGo5 = Event("hamletGo5", 930, 930, ["hamlet"], "groundsDocks", goTemplate, [], False, False)
hamletGo6 = Event("hamletGo6", 990, 990, ["hamlet"], "mainHall", goTemplate, [], False, False)
hamletGo7 = Event("hamletGo7", 1170, 1170, ["hamlet"], "upperHall", goTemplate, [], False, False)
hamletGo8 = Event("hamletGo8", 1920, 1920, ["hamlet"], "groundsDocks", goTemplate, [], False, False)
hamletGo9 = Event("hamletGo9", 2100, 2100, ["hamlet"], "upperHall", goTemplate, [], False, False)
hamletGo10 = Event("hamletGo10", 2220, 2220, ["hamlet"], "lowerHall", goTemplate, [], False, False)
hamletGo11 = Event("hamletGo11", 2310, 2310, ["hamlet"], "upperHall", goTemplate, [], False, False)
hamletGo12 = Event("hamletGo12", 2370, 2370, ["hamlet"], "mainHall", goTemplate, [], False, False)
hamletGo13 = Event("hamletGo13", 2610, 2610, ["hamlet"], "lowerHall", goTemplate, [], False, False)
hamletGo14 = Event("hamletGo14", 2760, 2760, ["hamlet"], "groundsDocks", goTemplate, [], False, False)
hamletGo15 = Event("hamletGo15", 2910, 2910, ["hamlet"], "upperHall", goTemplate, [], False, False)
hamletGo16 = Event("hamletGo16", 3060, 3060, ["hamlet"], "upperHall", goTemplate, [], False, False)
hamletGo17 = Event("hamletGo17", 3450, 3450, ["hamlet"], "groundsDocks", goTemplate, [], False, False)

#polonius
poloniusGo1 = Event("poloniusGo1", 690, 690, ["polonius"], "library", goTemplate, [], False, False)
poloniusGo2 = Event("poloniusGo2", 810, 810, ["polonius"], "upperHall", goTemplate, [], False, False)
poloniusGo3 = Event("poloniusGo3", 1020, 1020, ["polonius"], "mainHall", goTemplate, [], False, False)
poloniusGo4 = Event("poloniusGo4", 1170, 1170, ["polonius"], "groundsDocks", goTemplate, [], False, False)
poloniusGo5 = Event("poloniusGo5", 1470, 1470, ["polonius"], "upperHall", goTemplate, [], False, False)
poloniusGo6 = Event("poloniusGo6", 2070, 2070, ["polonius"], "mainHall", goTemplate, [], False, False)
poloniusGo7 = Event("poloniusGo7", 2130, 2130, ["polonius"], "upperHall", goTemplate, [], False, False)
poloniusGo8 = Event("poloniusGo8", 2370, 2370, ["polonius"], "mainHall", goTemplate, [], False, False)
poloniusGo9 = Event("poloniusGo9", 2610, 2160, ["polonius"], "upperHall", goTemplate, [], False, False)

#laertes
laertesGo1 = Event("laertesGo1", 630, 630, ["laertes"], "courtyard", goTemplate, [], False, False)
laertesGo2 = Event("laertesGo2", 1020, 1020, ["laertes"], "mainHall", goTemplate, [], False, False)
laertesGo3 = Event("laertesGo3", 1260, 1260, ["laertes"], "courtyard", goTemplate, [], False, False)
laertesGo4 = Event("laertesGo4", 1380, 1380, ["laertes"], "upperHall", goTemplate, [], False, False)
laertesGo5 = Event("laertesGo5", 1800, 1800, ["laertes"], "courtyard", goTemplate, [], False, False)
laertesGo6 = Event("laertesGo6", 2370, 2370, ["laertes"], "mainHall", goTemplate, [], False, False)
laertesGo7 = Event("laertesGo7", 2610, 2610, ["laertes"], "courtyard", goTemplate, [], False, False)
laertesGo8 = Event("laertesGo8", 2790, 2790, ["laertes"], "upperHall", goTemplate, [], False, False)
laertesGo9 = Event("laertesGo9", 3240, 3240, ["laertes"], "courtyard", goTemplate, [], False, False)

#bernardo
bernardoGo1 = Event("bernardoGo1", 960, 960, ["bernardo"], "courtyard", goTemplate, [], False, False)
bernardoGo2 = Event("bernardoGo2", 1020, 1020, ["bernardo"], "mainHall", goTemplate, [], False, False)
bernardoGo3 = Event("bernardoGo3", 1080, 1080, ["bernardo"], "courtyard", goTemplate, [], False, False)
bernardoGo4 = Event("bernardoGo4", 1170, 1170, ["bernardo"], "lowerHall", goTemplate, [], False, False)
bernardoBusy = Event("bernardoBusy", 1500, 1500, ["bernardo"], "lowerHall", executeTemplate, [], False, False)
bernardoNotBusy = Event("bernardoNotBusy", 1770, 1770, ["bernardo"], "lowerHall", executeTemplate, [], False, False)
bernardoGo5 = Event("bernardoGo5", 2370, 2370, ["bernardo"], "mainHall", goTemplate, [], False, False)
bernardoGo6 = Event("bernardoGo6", 2610, 2610, ["bernardo"], "courtyard", goTemplate, [], False, False)
bernardoGo7 = Event("bernardoGo7", 3000, 3000, ["bernardo"], "lowerHall", goTemplate, [], False, False)
bernardoGo8 = Event("bernardoGo8", 3360, 3360, ["bernardo"], "mainHall", goTemplate, [], False, False)
bernardoGo9 = Event("bernardoGo9", 3480, 3480, ["bernardo"], "lowerHall", goTemplate, [], False, False)

#brit
britGo1 = Event("britGo1", 690, 690, ["brit"], "lowerHall", goTemplate, [], False, False)
britGo2 = Event("britGo2", 870, 870, ["brit"], "upperHall", goTemplate, [], False, False)
britGo3 = Event("britGo3", 1050, 1050, ["brit"], "mainHall", goTemplate, [], False, False)
britGo4 = Event("britGo4", 1170, 1170, ["brit"], "lowerHall", goTemplate, [], False, False)
britGo5 = Event("britGo5", 1380, 1380, ["brit"], "library", goTemplate, [], False, False)
britGo6 = Event("britGo6", 1440, 1440, ["brit"], "lowerHall", goTemplate, [], False, False)
britGo7 = Event("britGo7", 1620, 1620, ["brit"], "groundsDocks", goTemplate, [], False, False)
britGo8 = Event("britGo8", 1710, 1710, ["brit"], "lowerHall", goTemplate, [], False, False)
britGo9 = Event("britGo9", 2310, 2310, ["brit"], "upperHall", goTemplate, [], False, False)
britGo10 = Event("britGo10", 2370, 2370, ["brit"], "mainHall", goTemplate, [], False, False)
britGo11 = Event("britGo11", 2610, 2610, ["brit"], "lowerHall", goTemplate, [], False, False)
britGo12 = Event("britGo12", 2820, 2820, ["brit"], "library", goTemplate, [], False, False)
britGo13 = Event("britGo13", 2880, 2880, ["brit"], "lowerHall", goTemplate, [], False, False)
britGo14 = Event("britGo14", 3060, 3060, ["brit"], "groundsDocks", goTemplate, [], False, False)
britGo15 = Event("britGo15", 3150, 3150, ["brit"], "lowerHall", goTemplate, [], False, False)

events = [laertesMakesPlan,laertesMeetsBrit,laertesKillsHamlet,laertesConfessesBrit,bernardoInterrogatesHamlet,bernardoInterrogatesPolonius,bernardoInterrogatesBrit,britMeetsFortinbras_2,britMeetsFortinbras_1,bernardoConfrontsBrit,laertesConfrontsBrit]
cancelevents = [poloniusLecture,castleBriefing,laertesLeaves,murder,hamletKillsPolonius,laertesMakesPlan,laertesMeetsBrit,laertesKillsHamlet,laertesConfessesBrit,bernardoInterrogatesHamlet,bernardoInterrogatesPolonius,bernardoInterrogatesBrit,britMeetsFortinbras_2,britMeetsFortinbras_1,bernardoConfrontsBrit,laertesConfrontsBrit]


#Priority Queue: Schedule
defaultSchedule = [poloniusLecture,castleBriefing,laertesLeaves,hamletKillsPolonius,murder]

currentEvents = []

ostari_path = sys.argv[1]
template_path = sys.argv[2]

f = open(template_path, "r")
template = f.read()
f.close()

action_sequence = ""

worldState = World("")

#Value: Loop
currentLoop = 1

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

#Method: AddAction
def AddAction(action):
    global action_sequence
    action_sequence += action

#Method: AddAction
def RemoveAction(action):
    global action_sequence
    action_sequence = action_sequence[::-1].replace(action[::-1], "")[::-1]

def AddToSchedule(event, schedule):
    newSchedule = schedule.copy()
    if event.startTime == "null":
        event.startTime = currentTime+5
        event.endTime = currentTime+10
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
            character = False
            for c in e.chars:
                if c in event.chars:
                    character = True
            if ((e.startTime < event.endTime) and (e.endTime > event.startTime)) and (e != event) and character:
                newSchedule.remove(e)
                a = cancelTemplate.replace("$name$", e.name)
                AddAction(a)
    RunGame()
    return newSchedule

#add to movement to schedule
#hamlet
defaultSchedule = AddToSchedule(hamletGo1, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo2, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo3, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo4, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo5, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo6, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo7, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo8, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo9, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo10, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo11, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo12, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo13, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo14, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo15, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo16, defaultSchedule)
defaultSchedule = AddToSchedule(hamletGo17, defaultSchedule)

#polonius
defaultSchedule = AddToSchedule(poloniusGo1, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo2, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo3, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo4, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo5, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo6, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo7, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo8, defaultSchedule)
defaultSchedule = AddToSchedule(poloniusGo9, defaultSchedule)

#laertes
defaultSchedule = AddToSchedule(laertesGo1, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo2, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo3, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo4, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo5, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo6, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo7, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo8, defaultSchedule)
defaultSchedule = AddToSchedule(laertesGo9, defaultSchedule)

#bernardo
defaultSchedule = AddToSchedule(bernardoGo1, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo2, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo3, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo4, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoBusy, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoNotBusy, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo5, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo6, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo7, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo8, defaultSchedule)
defaultSchedule = AddToSchedule(bernardoGo9, defaultSchedule)

#brit
defaultSchedule = AddToSchedule(britGo1, defaultSchedule)
defaultSchedule = AddToSchedule(britGo2, defaultSchedule)
defaultSchedule = AddToSchedule(britGo3, defaultSchedule)
defaultSchedule = AddToSchedule(britGo4, defaultSchedule)
defaultSchedule = AddToSchedule(britGo5, defaultSchedule)
defaultSchedule = AddToSchedule(britGo6, defaultSchedule)
defaultSchedule = AddToSchedule(britGo7, defaultSchedule)
defaultSchedule = AddToSchedule(britGo8, defaultSchedule)
defaultSchedule = AddToSchedule(britGo9, defaultSchedule)
defaultSchedule = AddToSchedule(britGo10, defaultSchedule)
defaultSchedule = AddToSchedule(britGo11, defaultSchedule)
defaultSchedule = AddToSchedule(britGo12, defaultSchedule)
defaultSchedule = AddToSchedule(britGo13, defaultSchedule)
defaultSchedule = AddToSchedule(britGo14, defaultSchedule)
defaultSchedule = AddToSchedule(britGo15, defaultSchedule)

currentSchedule = defaultSchedule.copy()

def RemoveFromSchedule(event, schedule):
    newSchedule = schedule.copy()
    newSchedule.remove(event)
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
        if (not s in state) and (not i in state) and (not c in state) and (e.startTime == "null" or e.startTime > currentTime):
            sat = True
            for p in e.preconditions:
                if not p in state:
                    sat = False
            if sat:
                AddAction(scheduleTemplate.replace("$name$", e.name))
                currentSchedule = AddToSchedule(e, currentSchedule)
    for e in cancelevents:
        s = "scheduled($name$,true)".replace("$name$", e.name)
        i = "impossible($name$,true)".replace("$name$", e.name)
        c = "completed($name$,true)".replace("$name$", e.name)
        if (e in currentSchedule) and (i in state):
            currentSchedule = RemoveFromSchedule(e, currentSchedule)
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
        if n[0] == "schedule":
            AddToSchedule(n[1])
        else:
            switch = {
            "upset" : upsetTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia"),
            "busy" : busyTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia"),
            "shattered" : shatteredTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia"),
            "dead" : deadTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia"),
            "goal" : goalTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia").replace("$goal$",n[1]),
            "belief" : beliefTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia").replace("$belief$",n[1]),
            "gone" : goneTemplate.replace("$char$",char).replace("$bool$","true").replace("$obs$","ophelia"),
            "cancel" : cancelTemplate.replace("$name$",n[1]),
            "hearsay" : hearsayTemplate.replace("$hearsay$", n[1]).replace("$bool$","true").replace("$player$","ophelia")
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
    ret = ret.replace("$obs$", "ophelia")
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
    print(event.name)
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
    action = tellTemplate.replace("$player$", "ophelia").replace("$hearsay$", hearsay).replace("$char$", char).replace("$bool$", "true")
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
    AddAction(goTemplate.replace("$chars$", "ophelia,").replace("$loc$", loc))
    charLoc["ophelia"] = loc
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

    charLoc = charLocDefault.copy()
    currentEvents = []

    for i in worldState.query("ophelia"):
        if "knows" in i:
            h = i.replace("knows(", "").replace(",true)", "")
            AddAction(hearsayTemplate.replace("$player$", "ophelia").replace("$hearsay$", h).replace("$bool$", "true"))

    currentLoop += 1
    RunGame()

#Hash: player/hearsay -> belief/goal
result = {
"laertes:imInDanger" : [("cancel", "laertesLeaves"), ("belief", "opheliaInDanger")],
"laertes:britIsASpy" : [("belief", "britIsASpy")],
"bernardo:imInDanger" : [("belief", "opheliaInDanger")],
"bernardo:spyInElsinore" : [("belief", "opheliaInDanger")],
"bernardo:britIsASpy" : [("belief", "britIsASpy")],
"polonius:bernardoSummon" : [("belief", "iHaveBeenSummoned")],
"hamlet:bernardoSummon" : [("belief", "iHaveBeenSummoned")],
"hamlet:spyInElsinore" : [("belief", "iHaveBeenSummoned")],
"brit:bernardoSummon" : [("belief", "iHaveBeenSummoned")]
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

#More general tasks
#IO processing, terminal based, nothing fancy

#Triggereing an action in Ostari - may not be possible during run time, might require a run at each step
#Current plan is to keep template writting for each action taken, run it, return the results as the new
#world state, and then add more actions to it and rerun as the player makes more decisions, simulating
#runtime action taking. This template is restored to the default on a loop reset.

RunGame()

inp = ""
while (inp != "quit"):
    print("Current Time: " + IntToTextTime(currentTime))
    print("Current Schedule: " + str(currentSchedule))
    print("Current Events: " + str(currentEvents))
    print("Your Knowlegde: " + str(worldState.query("ophelia")))
    print("World State: " + str(worldState.query("Truth")))
    print("Locations: " + str(charLoc))
    print("""Available Actions:
    wait(<day:hour:minute>)
    go(<place>)
    tellHearsay(<character>, <hearsay>)
    observe(<event>)
    query(<character (including ophelia) or "Truth">)
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
            if currentTime > 3480:
                print("You solved your murder!")
                break
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
