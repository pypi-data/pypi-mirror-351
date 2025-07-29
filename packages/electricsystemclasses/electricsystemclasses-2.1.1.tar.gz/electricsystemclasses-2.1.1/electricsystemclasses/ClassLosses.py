# Copyright 2025 ropimen
#
# This file is licensed under the Server Side Public License (SSPL), Version 1.0.
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
# https://www.mongodb.com/legal/licensing/server-side-public-license
#
# This file is part of ElectricSystemClasses.
#
# ElectricSystemClasses is a Python package providing a collection of classes for simulating electric systems.

#class grid, it has no power limits

from electricsystemclasses.simulation import SimulationGlobals

class Losses:
    #class level counter
    all_losses = []

    def __init__(self, id):
        self.id = id
        self.power_history = [0]
        self.iter = None

        Losses.all_losses.append(self)

    def percentLoss(self, power, perc_loss):
        if self.iter != SimulationGlobals.current_step_index:
            self.iter = SimulationGlobals.current_step_index
            self.power_history.append(power*perc_loss/100)
        else:
            self.power_history[-1] += power*perc_loss/100
        return power - (power * perc_loss/100)

    def fixedLoss(self, power, loss):
        if self.iter != SimulationGlobals.current_step_index:
            self.iter = SimulationGlobals.current_step_index
            self.power_history.append(loss)
        else:
            self.power_history[-1] += loss 
        return power - loss

    def update(self):

        i = SimulationGlobals.current_step_index

        if len(self.power_history) < i + 2:
            self.power_history.append(0)

    @classmethod
    def updateAllLosses(cls):
        for loss in cls.all_losses:
            loss.update()

    #class method to get the all generators
    @classmethod
    def getAllLosses(cls):
        return cls.all_losses