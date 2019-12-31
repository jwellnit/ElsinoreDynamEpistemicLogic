import math
import copy
import sys
import subprocess

#String List: List of Characters
characters = ["ophelia", "hamlet", "laertes", "polonius", "bernardo", "brit"]
charLocDefault = {"ophelia":"upper_hall", "hamlet":"upper_hall", "laertes":"grounds_docks", "polonius":"upper_hall", "bernardo":"lower_hall", "brit":"lower_hall"}
charLoc = charLocDefault
hearsayList = ["im_in_danger", "brit_is_a_spy", "spy_in_elsinore", "bernardo_summon"]
locs = ["upper_hall", "lower_hall", "main_hall", "grounds_docks", "courtyard", "library", "null"]

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
goneTemplate = "setGoneO($char$,$bool$,$obs$)\n"
cancelTemplate = "cancelEvent($name$)\n"
scheduleTemplate = "schedule$name$($name$)\n"


#Manual Definitions, events

#events
polonius_lecture = Event("polonius_lecture", 360, 480, ["ophelia", "polonius", "hamlet"], "upper_hall", executeTemplate, [], True, False)
castle_briefing = Event("castle_briefing", 570, 690, ["polonius", "bernardo"], "main_hall", executeTemplate, [], False, False)
laertes_leaves = Event("laertes_leaves", 630, 635, ["laertes", "brit"], "grounds_docks", executeTemplate, [], False, False)
murder = Event("murder", 3450, 3480, ["ophelia", "brit"], "null", executeTemplate, [], True, True)
hamlet_kills_polonius = Event("hamlet_kills_polonius", 2970, 3030, ["hamlet", "polonius"], "upper_hall", executeTemplate, [], False, False)
laertes_makes_plan = Event("laertes_makes_plan", 510, 730, ["laertes", "bernardo"], "lower_hall", executeTemplate, ["believes(ophelia_in_danger,laertes,true)"], False, False)
laertes_meets_brit = Event("laertes_meets_brit", 1140, 1260, ["laertes", "brit"], "upper_hall", executeTemplate, ["believes(ophelia_in_danger,laertes,true)", "believes(ophelia_in_danger,bernardo,true)"], False, False)
laertes_kills_hamlet = Event("laertes_meets_brit", 3300, 3360, ["laertes", "hamlet"], "courtyard", executeTemplate, ["believes(ophelia_in_danger,laertes,true)", "dead(polonius,true)"], False, False)
laertes_confesses_brit = Event("laertes_confesses_brit", 3300, 3360, ["laertes", "brit"], "library", executeTemplate, ["believes(ophelia_in_danger,laertes,true)", "dead(polonius,true)", "dead(hamlet,true)"], False, False)
bernardo_interrogates_hamlet = Event("bernardo_interrogates_hamlet", "null", "null", ["bernardo", "hamlet"], "lower_hall", executeTemplate, ["believes(ophelia_in_danger,bernardo,true)", "believes(i_have_been_summoned,hamlet,true)"], False, False)
bernardo_interrogates_polonius = Event("bernardo_interrogates_polonius", "null", "null", ["bernardo", "polonius"], "lower_hall", executeTemplate, ["believes(ophelia_in_danger,bernardo,true)", "believes(i_have_been_summoned,polonius,true)"], False, False)
bernardo_interrogates_brit = Event("bernardo_interrogates_brit", "null", "null", ["bernardo", "brit"], "lower_hall", executeTemplate, ["believes(ophelia_in_danger,bernardo,true)", "believes(i_have_been_summoned,brit,true)"], False, False)
brit_meets_fortinbras_2 = Event("brit_meets_fortinbras", 3060, 3120, ["brit"], "grounds_docks", executeTemplate, ["believes(brit_meets_at_docks,ophelia,true)"], False, False)
brit_meets_fortinbras_1 = Event("brit_meets_fortinbras", 1620, 1680, ["brit"], "grounds_docks", executeTemplate, ["believes(brit_meets_at_docks,ophelia,true)"], False, False)
bernardo_confronts_brit = Event("bernardo_confronts_brit", "null", "null", ["bernardo", "brit"], "lower_hall", executeTemplate, ["believes(brit_is_a_spy,bernardo,true)"], False, False)
laertes_confronts_brit = Event("bernardo_confronts_brit", "null", "null", ["laertes", "brit", "bernardo"], "upper_hall", executeTemplate, ["believes(brit_is_a_spy,laertes,true)"], False, False)

#schedules
#hamlet
hamlet_go_1 = Event("hamlet_go_1", 510, 510, ["hamlet"], "courtyard", goTemplate, [], False, False)
hamlet_go_2 = Event("hamlet_go_2", 690, 690, ["hamlet"], "upper_hall", goTemplate, [], False, False)
hamlet_go_3 = Event("hamlet_go_3", 720, 720, ["hamlet"], "library", goTemplate, [], False, False)
hamlet_go_4 = Event("hamlet_go_4", 810, 810, ["hamlet"], "courtyard", goTemplate, [], False, False)
hamlet_go_5 = Event("hamlet_go_5", 930, 930, ["hamlet"], "grounds_docks", goTemplate, [], False, False)
hamlet_go_6 = Event("hamlet_go_6", 990, 990, ["hamlet"], "main_hall", goTemplate, [], False, False)
hamlet_go_7 = Event("hamlet_go_7", 1170, 1170, ["hamlet"], "upper_hall", goTemplate, [], False, False)
hamlet_go_8 = Event("hamlet_go_8", 1920, 1920, ["hamlet"], "grounds_docks", goTemplate, [], False, False)
hamlet_go_9 = Event("hamlet_go_9", 2100, 2100, ["hamlet"], "upper_hall", goTemplate, [], False, False)
hamlet_go_10 = Event("hamlet_go_10", 2220, 2220, ["hamlet"], "lower_hall", goTemplate, [], False, False)
hamlet_go_11 = Event("hamlet_go_11", 2310, 2310, ["hamlet"], "upper_hall", goTemplate, [], False, False)
hamlet_go_12 = Event("hamlet_go_12", 2370, 2370, ["hamlet"], "main_hall", goTemplate, [], False, False)
hamlet_go_13 = Event("hamlet_go_13", 2610, 2610, ["hamlet"], "lower_hall", goTemplate, [], False, False)
hamlet_go_14 = Event("hamlet_go_14", 2760, 2760, ["hamlet"], "grounds_docks", goTemplate, [], False, False)
hamlet_go_15 = Event("hamlet_go_15", 2910, 2910, ["hamlet"], "upper_hall", goTemplate, [], False, False)
hamlet_go_16 = Event("hamlet_go_16", 3060, 3060, ["hamlet"], "upper_hall", goTemplate, [], False, False)
hamlet_go_17 = Event("hamlet_go_17", 3450, 3450, ["hamlet"], "grounds_docks", goTemplate, [], False, False)

#polonius
polonius_go_1 = Event("polonius_go_1", 690, 690, ["polonius"], "library", goTemplate, [], False, False)
polonius_go_2 = Event("polonius_go_2", 810, 810, ["polonius"], "upper_hall", goTemplate, [], False, False)
polonius_go_3 = Event("polonius_go_3", 1020, 1020, ["polonius"], "main_hall", goTemplate, [], False, False)
polonius_go_4 = Event("polonius_go_4", 1170, 1170, ["polonius"], "grounds_docks", goTemplate, [], False, False)
polonius_go_5 = Event("polonius_go_5", 1470, 1470, ["polonius"], "upper_hall", goTemplate, [], False, False)
polonius_go_6 = Event("polonius_go_6", 2070, 2070, ["polonius"], "main_hall", goTemplate, [], False, False)
polonius_go_7 = Event("polonius_go_7", 2130, 2130, ["polonius"], "upper_hall", goTemplate, [], False, False)
polonius_go_8 = Event("polonius_go_8", 2370, 2370, ["polonius"], "main_hall", goTemplate, [], False, False)
polonius_go_9 = Event("polonius_go_9", 2610, 2160, ["polonius"], "upper_hall", goTemplate, [], False, False)

#laertes
laertes_go_1 = Event("laertes_go_1", 630, 630, ["laertes"], "courtyard", goTemplate, [], False, False)
laertes_go_2 = Event("laertes_go_2", 1020, 1020, ["laertes"], "main_hall", goTemplate, [], False, False)
laertes_go_3 = Event("laertes_go_3", 1260, 1260, ["laertes"], "courtyard", goTemplate, [], False, False)
laertes_go_4 = Event("laertes_go_4", 1380, 1380, ["laertes"], "upper_hall", goTemplate, [], False, False)
laertes_go_5 = Event("laertes_go_5", 1800, 1800, ["laertes"], "courtyard", goTemplate, [], False, False)
laertes_go_6 = Event("laertes_go_6", 2370, 2370, ["laertes"], "main_hall", goTemplate, [], False, False)
laertes_go_7 = Event("laertes_go_7", 2610, 2610, ["laertes"], "courtyard", goTemplate, [], False, False)
laertes_go_8 = Event("laertes_go_8", 2790, 2790, ["laertes"], "upper_hall", goTemplate, [], False, False)
laertes_go_9 = Event("laertes_go_9", 3240, 3240, ["laertes"], "courtyard", goTemplate, [], False, False)

#bernardo
bernardo_go_1 = Event("bernardo_go_1", 960, 960, ["bernardo"], "courtyard", goTemplate, [], False, False)
bernardo_go_2 = Event("bernardo_go_2", 1020, 1020, ["bernardo"], "main_hall", goTemplate, [], False, False)
bernardo_go_3 = Event("bernardo_go_3", 1080, 1080, ["bernardo"], "courtyard", goTemplate, [], False, False)
bernardo_go_4 = Event("bernardo_go_4", 1170, 1170, ["bernardo"], "lower_hall", goTemplate, [], False, False)
bernardo_busy = Event("bernardo_busy", 1500, 1500, ["bernardo"], "lower_hall", executeTemplate, [], False, False)
bernardo_not_busy = Event("bernardo_busy", 1770, 1770, ["bernardo"], "lower_hall", executeTemplate, [], False, False)
bernardo_go_5 = Event("bernardo_go_5", 2370, 2370, ["bernardo"], "main_hall", goTemplate, [], False, False)
bernardo_go_6 = Event("bernardo_go_6", 2610, 2610, ["bernardo"], "courtyard", goTemplate, [], False, False)
bernardo_go_7 = Event("bernardo_go_7", 3000, 3000, ["bernardo"], "lower_hall", goTemplate, [], False, False)
bernardo_go_8 = Event("bernardo_go_8", 3360, 3360, ["bernardo"], "main_hall", goTemplate, [], False, False)
bernardo_go_9 = Event("bernardo_go_9", 3480, 3480, ["bernardo"], "lower_hall", goTemplate, [], False, False)

#brit
brit_go_1 = Event("brit_go_1", 690, 690, ["brit"], "lower_hall", goTemplate, [], False, False)
brit_go_2 = Event("brit_go_2", 870, 870, ["brit"], "upper_hall", goTemplate, [], False, False)
brit_go_3 = Event("brit_go_3", 1050, 1050, ["brit"], "main_hall", goTemplate, [], False, False)
brit_go_4 = Event("brit_go_4", 1170, 1170, ["brit"], "lower_hall", goTemplate, [], False, False)
brit_go_5 = Event("brit_go_5", 1380, 1380, ["brit"], "library", goTemplate, [], False, False)
brit_go_6 = Event("brit_go_6", 1440, 1440, ["brit"], "lower_hall", goTemplate, [], False, False)
brit_go_7 = Event("brit_go_7", 1620, 1620, ["brit"], "grounds_docks", goTemplate, [], False, False)
brit_go_8 = Event("brit_go_8", 1710, 1710, ["brit"], "lower_hall", goTemplate, [], False, False)
brit_go_9 = Event("brit_go_9", 2310, 2310, ["brit"], "upper_hall", goTemplate, [], False, False)
brit_go_10 = Event("brit_go_10", 2370, 2370, ["brit"], "main_hall", goTemplate, [], False, False)
brit_go_11 = Event("brit_go_11", 2610, 2610, ["brit"], "lower_hall", goTemplate, [], False, False)
brit_go_12 = Event("brit_go_12", 2820, 2820, ["brit"], "library", goTemplate, [], False, False)
brit_go_13 = Event("brit_go_13", 2880, 2880, ["brit"], "lower_hall", goTemplate, [], False, False)
brit_go_14 = Event("brit_go_14", 3060, 3060, ["brit"], "grounds_docks", goTemplate, [], False, False)
brit_go_15 = Event("brit_go_15", 3150, 3150, ["brit"], "lower_hall", goTemplate, [], False, False)

events = [polonius_lecture,castle_briefing,laertes_leaves,murder,hamlet_kills_polonius,laertes_makes_plan,laertes_meets_brit,laertes_kills_hamlet,laertes_confesses_brit,bernardo_interrogates_hamlet,bernardo_interrogates_polonius,bernardo_interrogates_brit,brit_meets_fortinbras_2,brit_meets_fortinbras_1,bernardo_confronts_brit,laertes_confronts_brit]

#Priority Queue: Schedule
defaultSchedule = [polonius_lecture,castle_briefing,laertes_leaves,hamlet_kills_polonius,murder]
currentSchedule = defaultSchedule
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
currentSchedule = AddToSchedule(hamlet_go_1, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_2, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_3, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_4, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_5, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_6, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_7, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_8, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_9, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_10, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_11, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_12, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_13, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_14, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_15, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_16, currentSchedule)
currentSchedule = AddToSchedule(hamlet_go_17, currentSchedule)

#polonius
currentSchedule = AddToSchedule(polonius_go_1, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_2, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_3, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_4, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_5, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_6, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_7, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_8, currentSchedule)
currentSchedule = AddToSchedule(polonius_go_9, currentSchedule)

#laertes
currentSchedule = AddToSchedule(laertes_go_1, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_2, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_3, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_4, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_5, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_6, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_7, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_8, currentSchedule)
currentSchedule = AddToSchedule(laertes_go_9, currentSchedule)

#bernardo
currentSchedule = AddToSchedule(bernardo_go_1, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_2, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_3, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_4, currentSchedule)
currentSchedule = AddToSchedule(bernardo_busy, currentSchedule)
currentSchedule = AddToSchedule(bernardo_not_busy, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_5, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_6, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_7, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_8, currentSchedule)
currentSchedule = AddToSchedule(bernardo_go_9, currentSchedule)

#brit
currentSchedule = AddToSchedule(brit_go_1, currentSchedule)
currentSchedule = AddToSchedule(brit_go_2, currentSchedule)
currentSchedule = AddToSchedule(brit_go_3, currentSchedule)
currentSchedule = AddToSchedule(brit_go_4, currentSchedule)
currentSchedule = AddToSchedule(brit_go_5, currentSchedule)
currentSchedule = AddToSchedule(brit_go_6, currentSchedule)
currentSchedule = AddToSchedule(brit_go_7, currentSchedule)
currentSchedule = AddToSchedule(brit_go_8, currentSchedule)
currentSchedule = AddToSchedule(brit_go_9, currentSchedule)
currentSchedule = AddToSchedule(brit_go_10, currentSchedule)
currentSchedule = AddToSchedule(brit_go_11, currentSchedule)
currentSchedule = AddToSchedule(brit_go_12, currentSchedule)
currentSchedule = AddToSchedule(brit_go_13, currentSchedule)
currentSchedule = AddToSchedule(brit_go_14, currentSchedule)
currentSchedule = AddToSchedule(brit_go_15, currentSchedule)

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
        if (not s in state) and (not i in state) and (not c in state) and e.startTime > currentTime:
            sat = True
            for p in e.preconditions:
                if not p in state:
                    sat = False
            if sat:
                AddAction(scheduleTemplate.replace("$name$", e.name))
                print("got here")
                currentSchedule = AddToSchedule(e, currentSchedule)
        if (e in currentSchedule) and (i in state):
            RemoveFromSchedule(e)
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
"laertes:im_in_danger" : [("cancel", "laertes_leaves"), ("belief", "ophelia_in_danger")],
"laertes:brit_is_a_spy" : [("belief", "brit_is_a_spy")],
"bernardo:im_in_danger" : [("belief", "ophelia_in_danger")],
"bernardo:spy_in_elsinore" : [("belief", "ophelia_in_danger")],
"bernardo:brit_is_a_spy" : [("belief", "brit_is_a_spy")],
"polonius:bernardo_summon" : [("belief", "i_have_been_summoned")],
"hamlet:bernardo_summon" : [("belief", "i_have_been_summoned")],
"hamlet:spy_in_elsinore" : [("belief", "i_have_been_summoned")],
"brit:bernardo_summon" : [("belief", "i_have_been_summoned")]
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
