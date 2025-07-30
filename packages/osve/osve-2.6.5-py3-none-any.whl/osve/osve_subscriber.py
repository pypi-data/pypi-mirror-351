#*****************************************************************************#
# This file is subject to the terms and conditions defined in the             #
# file 'LICENSE.txt', which is part of this source code package.              #
#                                                                             #
# No part of the package, including this file, may be copied, modified,       #
# propagated, or distributed except according to the terms contained in       #
# the file 'LICENSE.txt'.                                                     #
#                                                                             #
# (C) Copyright European Space Agency, 2025                                   #
#*****************************************************************************# 


"""
Created on July, 2023

@author: Ricardo Valles Blanco (ESAC)

The OsveSubscriber class intended to provide on the fly 
simulation status and data to the main OSVE caller program.
"""

import json

from abc import abstractmethod, ABC
from ctypes import *


# Some ctypes callback definitions
class Callback(Structure):
    _fields_ = [('jsonStr', c_char_p)]


CALLBACK = CFUNCTYPE(c_int, POINTER(Callback))


class OsveSubscriberAbstract(object):
    """The OsveSubscriberAbstract class intended to provide on the fly simulation status and data to the main OSVE caller program. 
       This class shall be inherited by a child class tht must implement/override the OsveSubscriberAbstract abstract methods."""
    
    id = ""

    def __init__(self, id):
        """Initialises the OsveSubscriberAbstract instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str
        """
        
        # Store the Id in order to filter callbacks not related to this subscriber
        self.id = id

    @abstractmethod
    def onSimulationStart(self, data) -> int:
        """This callback function is called every time a simulation started.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the selected ovelay name's and unit's.
        :type data: dict

        :rtype: int
        """
        return 0

    @abstractmethod
    def onSimulationTimeStep(self, data) -> int:
        """This callback function is called every time a time step has been simulated.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the selected ovelay name's and values.
        :type data: dict

        :rtype: int
        """
        return 0
    
    @abstractmethod
    def onSimulationPtrBlockStart(self, data) -> int:
        """This callback function is called every time a PTR block execution is
           started. If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains some block data of the started block.
        :type data: dict

        :rtype: int
        """
        return 0
     
    @abstractmethod
    def onSimulationPtrBlockEnd(self, data) -> int:
        """This callback function is called every time a PTR block execution is
           finished. If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the block start date of the finished block.
        :type data: dict

        :rtype: int
        """
        return 0
    
    @abstractmethod
    def onSimulationEnd(self, data) -> int:
        """This callback function is called every time that a simulation finishes.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the simulation end time.
        :type data: dict

        :rtype: int
        """
        return 0

    @abstractmethod
    def onEventStateChaged(self, eventData) -> int:
        """This callback function is called every time that an OSVE event is risen.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the event properties.
        :type data: dict

        :rtype: int
        """
        return 0
    

class OsveEventSubscriber(OsveSubscriberAbstract):

    """The OsveEventSubscriber class is an implementation of the OsveSubscriberAbstract intended to 
    let the developer an easy handling of the OSVE Events. The developer just needs to specify 
    the datapack Id and a callback function to be called everytime an event is risen. 
    See OsveEventSubscriber.__init__() documentation for more details."""
        
    onEventStateChagedFn = None

    def __init__(self, id, onEventStateChagedFn):
        """Initialises the OsveEventSubscriber instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str

        :param onEventStateChagedFn: A callback function of type ( functionName(dictionary) -> int ), so this function
                                     is called every time an OSVE event is risen.
        :type onEventStateChagedFn: function
        """
                
        super().__init__(id)
        self.onEventStateChagedFn = onEventStateChagedFn

    def onEventStateChaged(self, data) -> int:
        """This callback function is called every time that an OSVE event is risen.
           If returned int is smaller than 0 then simulation is aborted.

        :param data: Dictionary that contains the event properties.
        :type data: dict

        :rtype: int
        """
        return self.onEventStateChagedFn(data) if not self.onEventStateChagedFn is None else 0
    

class ExternalConstraintAbstract(object):
    """The ExternalConstraintAbstract class intended to provide control over the attitude checking 
       processes performed by AGM"""
    
    id = ""
    step = "UNKNOWN"

    def __init__(self, id):
        """Initialises the ExternalConstraintAbstract instance.

        :param id: Shall match a External Constraint Id element in "extConstraintIds" 
                   optional list of the "attitudeSimulationConfiguration" section of the session file.
        :type id: str
        """
        
        # Store the Id in order to filter callbacks not related to this external constraint
        self.id = id

    @abstractmethod
    def configureConstraintChecks(self) -> int:
        """This callback function is called by AGM to notify external constraints
           to load and validate it's specific configuration.
           To abort execution return an integer smaller than zero.

        :rtype: int
        """
        return 0

    @abstractmethod
    def resetConstraintFlags(self):
        """This callback function is called by AGM to notify external constraints
           that all the flagged constraints shall be resetted.
        """

    @abstractmethod
    def notifyEnvironmentInitialised(self) -> int:
        """This callback function is called by AGM to notify external constraints
           to that everything looks ready to start simulation.
           To abort execution return an integer smaller than zero.

        :rtype: int
        """
        return 0
    
    @abstractmethod
    def update(self, time, sc_quats) -> int:
        """This callback function is called by AGM to notify external constraints
           that spacecraft attitude data has been updated and constraints shall be
           reevaluated.
           To abort execution return an integer smaller than zero.

        :param time: The current time in format: YYYY-MM-DDTHH:mm:SSZ
        :type time: str

        :param sc_quats: The spacecracft quaternions relative to J2000
        :type sc_quats: list of double

        :rtype: int
        """
        return 0

    @abstractmethod
    def cleanup(self):
        """This callback function is called by AGM to notify external constraints
           that all computed and temporary data shall be cleaned up.
        """

    @abstractmethod
    def getInError(self, skipChecks, showMessages, checkConstraints, breakFound) -> int:
        """This callback function is called by AGM at the end of every timestep to 
           check if any constraint has been violated. In this case this external
           constrain shall returns an integer greater than 0 then OSVE will consider that 
           this external constrain has violations, otherwise not.

        :param skipChecks: Indicates if constraint checks shall be skipped or not, depends on the simulation stage.
        :type skipChecks: bool

        :param showMessages: Indicates if the external constaints shall do logging or not, depends on the simulation stage.
        :type showMessages: bool

        :param checkConstraints: Defines the way constraints are checked during the update of the timeline at each current time.
                                0 => NONE: No constraints are checked at all.
                                1 => ALWAYS: Constraints are checked for every call as if it was the first time (no memory).
                                2 => CONTINUOUS: Constraints are checked assuming the calls are continuous in time (with memory).
        :type checkConstraints: int

        :param breakFound: Indicates if the external constaints if there are any contraint violated at current time.
        :type breakFound: bool

        :rtype: int
        """
        return 0
    

class OsveLoggerAbstract(object):
    """The OsveLoggerAbstract class intended to provide runtime access to logging messages reported by OSVE"""
    
    id = ""

    def __init__(self, id):
        """Initialises the OsveLoggerAbstract instance.

        :param id: Shall match a datapack "filePath" of type "CALLBACK" in order to link this subscriber to a datapack.
        :type id: str
        """
        
        # Store the Id in order to filter callbacks not related to this logger
        self.id = id

    @abstractmethod
    def onMsgReceived(self, severity, module, time, text):
        return 0


class OsvePtrAbstract(OsveSubscriberAbstract, OsveLoggerAbstract):

    """The OsvePtrAbstract class intended to provide on the fly simulation status and data to the main OSVE caller program
       but in this case the data will be provided grouped by PTR Block, and reported every time a block ends. 
       This class shall be inherited by a child class tht must implement/override the OsvePtrAbstract abstract methods."""
    
    current_block = "" # To store ref of current block, consider it finished once changed
    block_steps = []  # To store every timestep data for current PTR block
    block_events = []  # To store risen events during current PTR block
    block_logs = []  # To store logged messages during current PTR block
    on_simulation = False

    def __init__(self, id):
        super().__init__(id)

    def onSimulationStart(self, data) -> int:
        self.reset()
        self.on_simulation = True
        return 0

    def onSimulationTimeStep(self, data) -> int:
        if self.on_simulation:
            self.block_steps.append(data)
        return 0

    def onSimulationPtrBlockStart(self, data) -> int:
        
        ret = 0
        
        if self.on_simulation:
            ret = self.onPtrBlockStart(data)

        return 0
    
    def onSimulationPtrBlockEnd(self, data) -> int:
        
        ret = 0
        
        if self.on_simulation:
            
            data["block_steps"] = self.block_steps
            data["block_events"] = self.block_events
            data["block_logs"] = self.block_logs

            ret = self.onPtrBlockEnd(data)

            self.reset()

        return ret
    
    def onSimulationEnd(self, data) -> int:
        self.on_simulation =False
        return 0

    def onEventStateChaged(self, data) -> int:
        if self.on_simulation:
            self.block_events.append(data)
        return 0

    def onMsgReceived(self, severity, module, time, text):
        if self.on_simulation:
            self.block_logs.append({"severity": severity, "module": module, "time": time, "text": text})
        return 0

    @abstractmethod
    def onPtrBlockStart(self, blockData) -> int:
        """This callback function is called every time a PTR block execution is
           started. It provides as an argument a dictionary with the every
           timestep data, risen events and logs.
           If returned int is smaller than 0 then simulation is aborted.

        :param blockData: Dictionary that contains the some block data.
        :type blockData: dict

        :rtype: int
        """
        return 0
    
    @abstractmethod
    def onPtrBlockEnd(self, blockData) -> int:
        """This callback function is called every time a PTR block execution is
           finished. It provides as an argument a dictionary with the every
           timestep data, risen events and logs.
           If returned int is smaller than 0 then simulation is aborted.

        :param blockData: Dictionary that contains the produced block data.
        :type blockData: dict

        :rtype: int
        """
        return 0
    
    def reset(self):
        self.block_steps = []
        self.block_events = []
        self.block_logs = []
