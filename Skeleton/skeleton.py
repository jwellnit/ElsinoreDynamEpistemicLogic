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

executeTemplate = "execute$name$($name$, $chars$, $loc$, observer(unit))"
goTemplate = "go($chars$, $loc$)"

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

def AddToSchedule(event):


#Method: Schedule all available events

#Method: Wait
def Wait(endTime):


#Method: Observe

#Method: Execute Events


#Method: Tell Hearsay

#Method: Query

#Method: Reset

#Hash: player/hearsay -> belief/goal

#Value: Time
currentTime = 480

def TextTimeToInt(time):
    time_list =

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


#Method: RunGame

#Reading beliefs and actions from ostari, also possibly not doable in runtime - simply output from run game

#Method QueryOutput
