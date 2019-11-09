#String List: List of Character

#Class: Event

#Class: Schedule ?? need someway to represent the schedule, class may not be necessary

#Method: Schedule all available events

#Method: Wait

#Method: Observe

#Method: Execute Events

#Method: Tell Hearsay

#Method: Query

#Method: Reset

#Hash: player/hearsay -> belief/goal

#Value: Time

#Value: Loop

#More general tasks
#IO processing, terminal based, nothing fancy

#Triggereing an action in Ostari - may not be possible during run time, might require a run at each step
#Current plan is to keep template writting for each action taken, run it, return the results as the new
#world state, and then add more actions to it and rerun as the player makes more decisions, simulating
#runtime action taking. This template is restored to the default on a loop reset.

#Reading beliefs and actions from ostari, also possibly not doable in runtime - simply output from run game
