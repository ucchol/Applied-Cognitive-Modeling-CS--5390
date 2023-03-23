# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 20:23:48 2023

@author: arahman3
"""

import pyibl
import numpy as np

# Set global variables
PARTICIPANTS = 1000
DECAY = 0.5
NOISE = 0.25
TEMPERATURE = 1.0
DEFAULT_OUTPUT_FILE = "boxplot-data_Signaling.csv"
TARGET_COUNT = 2
TRIALS = 50
def reset_agent(agent, noise=NOISE, temperature=TEMPERATURE, decay=DECAY):
    agent.reset(False)
    agent.noise = noise
    agent.decay = decay
    agent.temperature = temperature
def run(output_file=DEFAULT_OUTPUT_FILE):
    selection_agent = pyibl.Agent("Selection Agent", optimized_learning=False)
    attack_agent = pyibl.Agent("Attack Agent", ["attack", "warning"], 
                            optimized_learning=False)
    with open(output_file, "w") as f:
        print("Subject,Trial,Selected,Warning,Covered,Action,Outcome", file=f)
        attack_successful = 0
        attack_failed = 0
        attack_withdraw = 0
        for p in range(PARTICIPANTS):
            COVERAGE = np.random.choice([0,1], size=(50,), p=[.5,.5])
            total = 0
            reset_agent(selection_agent)
            reset_agent(attack_agent)
            # Populate instances for t=0
            selection_agent.populate(110, 0)
            selection_agent.populate(110, 1)
            attack_agent.populate(-30, {"attack": False, "warning":0})
            attack_agent.populate(110, {"attack": True, "warning":0})
            attack_agent.populate(-55, {"attack": True, "warning":0})
            
            ##
            attack_agent.populate(-20, {"attack": False, "warning":1})
            attack_agent.populate(105, {"attack": True, "warning":1})
            attack_agent.populate(-60, {"attack": True, "warning":1})
            ##
            
            for t in range(TRIALS):
                selected = selection_agent.choose(0, 1)
                warned = 0 # Signal
                if COVERAGE[t] == 1:
                    warned = 1
                else:
                    warned = np.random.choice([0,1], size=(1,), p=[.5,.5])[0]
                    
                attack = attack_agent.choose({"attack": True, "warning": warned},
                                            {"attack": False, "warning": warned})["attack"]
                covered = selected == COVERAGE[t]
                if not attack:
                    payoff = 0
                    attack_withdraw += 1
                else:
                    if covered:
                        payoff = -50
                        attack_failed += 1
                    else:
                        payoff = 100
                        attack_successful += 1
                total += payoff
                attack_agent.respond(payoff)
                selection_agent.respond(payoff)
                print(f"{p+1},{t+1},{selected},{int(warned)},{int(covered)},{int(attack)},{payoff}",file = f)
    return [attack_failed / (TRIALS * PARTICIPANTS), attack_successful / (TRIALS * PARTICIPANTS), attack_withdraw / (TRIALS * PARTICIPANTS)]


a = run()
print("attack on covered box, attacks on uncovered box, withdraw action",a[0], a[1], a[2])