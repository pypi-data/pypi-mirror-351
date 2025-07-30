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

This module contains the OSVE class that handles the simulation
through AGM and EPSng.
"""

from ctypes import *
from ctypes import wintypes
import json

from osve.osve_subscriber import CALLBACK, Callback
from .utils import build_lib_path, get_platform


# TODO: Support multiple OSVE instances without conflicting callbacks
THE_OSVE_REFERENCE = None

@CALLBACK
def onCallback(data) -> int:
    global THE_OSVE_REFERENCE
    return THE_OSVE_REFERENCE.process_message(data.contents.jsonStr)


class osve():
    """The OSVE class intended to handle the simulation"""

    subscribers = {}
    externalConstraints = {}
    loggers = {}

    def __init__(self, if_shared_lib_path=None):
        global THE_OSVE_REFERENCE
        THE_OSVE_REFERENCE = self

        self.lib_path = build_lib_path() if if_shared_lib_path is None else if_shared_lib_path
    
    def __load_library(self):
        try:
            self.my_platform = get_platform()

            if (self.my_platform.startswith("windows")):
                self.libs = WinDLL(self.lib_path)

            else:
                self.libs = CDLL(self.lib_path)
            
            self._handle = self.libs._handle
        
        except Exception as e:
            print("ERROR: OSVE Library could not be loaded", flush=True)
            print(e, flush=True)

    def __unload_library(self):
        """Release resources used by OSVE.

        This method will release and free the resources used by OSVE
        when using step by step execution. Returns 0 if successfull.

        Note: We need to do it be able to execute the osve several time
        within the same python run.
        :rtype: int
        """
        try:
            
            del self.libs

            if (self.my_platform.startswith("windows")):
                kernel32 = WinDLL('kernel32', use_last_error=True)    
                kernel32.FreeLibrary.argtypes = [wintypes.HMODULE]
                return kernel32.FreeLibrary(self._handle)
            
            else:
                dl_unload = CDLL(None).dlclose
                dl_unload.argtypes = [c_void_p]
                dl_unload.restype = c_int
                return dl_unload(self._handle)
            
        except Exception as e:
            print("ERROR: OSVE Library could not be unloaded", flush=True)
            print(e, flush=True)
            return None

    def execute(self, root_scenario_path, session_file_path):
        """Runs the full simulation.

        This method will run the simulation with the inputs specified
        on the session file. All simulation steps performed in one call.
        Return 0 if the execution has been successful, other int otherwise.
        (This doesn't mean that there are no constraints violations)

        :param root_scenario_path: Provide the top level path of the
            scenario file_path to be used to resolve the relative paths.
        :type root_scenario_path: str
        :param session_file_path: Provide the location and name of the
            session file containing all the scenarios files.
        :type session_file_path: str
        :rtype: int
        """
        try:
            self.__load_library()

            if len(self.subscribers) \
                or len(self.externalConstraints) \
                or len(self.loggers):
            
                self.libs.setCallBack.argtypes = [CALLBACK]
                self.libs.setCallBack.restype = c_int
                self.libs.setCallBack(onCallback)

            self.libs.osve_execute.argtypes = [c_char_p, c_char_p]
            self.libs.osve_execute.restype = c_int
            value = self.libs.osve_execute(bytes(root_scenario_path, 'utf-8'), bytes(session_file_path, 'utf-8'))

            self.__unload_library()

            return value
        
        except Exception as e:
            print("ERROR: OSVE execute() error:", flush=True)
            print(e, flush=True)
            return -1

    def init_step(self, root_scenario_path, session_file_path):
        """Initialise the simulation.

        This method will initialise the OSVE environment for performing
        the simulation step by step. Returns a Json string with the
        initialisation results.

        :param root_scenario_path: Provide the top level path of the
            scenario file_path to be used to resolve the relative paths.
        :type root_scenario_path: str
        :param session_file_path: Provide the location and name of the
            session file containing all the scenarios files.
        :type session_file_path: str
        :rtype: str
        """
        try:
            self.__load_library()
            self.libs.osve_initStep.argtypes = [c_char_p, c_char_p]
            self.libs.osve_initStep.restype = c_char_p
            res = self.libs.osve_initStep(bytes(root_scenario_path, 'utf-8'), bytes(session_file_path, 'utf-8'))
            return res.decode('utf-8')
        except Exception as e:
            print("ERROR: OSVE init_step() error:", flush=True)
            print(e, flush=True)
            return ""

    def execute_step(self):
        """Runs the simulation previously initialised.

        This method will run the simulation previously initialised with
        the init_step method. Returns a Json string with the
        execution results.

        :rtype: str
        """
        try:
            self.libs.osve_executeStep.argtypes = []
            self.libs.osve_executeStep.restype = c_char_p
            res = self.libs.osve_executeStep()
            return res.decode('utf-8')
        except Exception as e:
            print("ERROR: OSVE execute_step() error:", flush=True)
            print(e, flush=True)
            return ""

    def write_files(self, segment_timeline_json_path, segment_timeline_txt_path):
        """Writes generated outputs.

        This method will write the outputs generated by the execute_step
        method call. Returns a Json string with the write results.

        :param segment_timeline_json_path: The file path to write the
            timeline in JSON format.
        :type segment_timeline_json_path: str
        :param segment_timeline_txt_path: The file path to write the
            timeline in text format.
        :type segment_timeline_txt_path: str
        :rtype: str
        """
        try:
            self.libs.osve_writeFiles.argtypes = [c_char_p, c_char_p]
            self.libs.osve_writeFiles.restype = c_char_p
            res = self.libs.osve_writeFiles(bytes(segment_timeline_json_path, 'utf-8'),
                                            bytes(segment_timeline_txt_path, 'utf-8'))
            return res.decode('utf-8')
        except Exception as e:
            print("ERROR: OSVE write_files() error:", flush=True)
            print(e, flush=True)
            return ""

    def write_json_log(self, json_log_file_path):
        """Writes the execution log.

        This method will write the execution log in JSON format,
        this call will clear the log buffer. Returns 0 if successfull.

        :param json_log_file_path: The file path to write the log
            in JSON format.
        :type json_log_file_path: str
        :rtype: int
        """
        try:
            self.libs.osve_writeJsonLog.argtypes = [c_char_p]
            self.libs.osve_writeJsonLog.restype = c_int
            return self.libs.osve_writeJsonLog(bytes(json_log_file_path, 'utf-8'))
        except Exception as e:
            print("ERROR: OSVE write_json_log() error:", flush=True)
            print(e, flush=True)
            return ""

    def close(self):
        """Release resources used by OSVE.

        This method will release and free the resources used by OSVE
        when using step by step execution. Returns 0 if successfull.

        :rtype: int
        """
        try:
            self.libs.osve_close.argtypes = []
            self.libs.osve_writeJsonLog.restype = c_int
            return self.libs.osve_close()
        except Exception as e:
            print("ERROR: OSVE close() error:", flush=True)
            print(e, flush=True)
            return -1

    def get_app_version(self):
        """Returns the OSVE Application version.

        This method will return null terminated characters string
        containing the version of the OSVE Application version.
        This version is updated any time the core of the module
        is updated.

        :rtype: str
        """
        try:
            self.__load_library()
            self.libs.osve_getAppVersion.restype = c_char_p
            version = self.libs.osve_getAppVersion()
            self.__unload_library()
            return version.decode('utf-8')
        except Exception as e:
            print("ERROR: OSVE get_app_version() error:", flush=True)
            print(e, flush=True)
            return ""
        
    def get_agm_version(self):
        """Returns the AGM module version.

        This method will return null terminated characters string
        containing the version of the AGM module contained into OSVE.

        :rtype: str
        """
        try:
            self.__load_library()
            self.libs.osve_getAgmVersion.restype = c_char_p
            version = self.libs.osve_getAgmVersion()
            self.__unload_library()
            return version.decode('utf-8')
        except Exception as e:
            print("ERROR: OSVE get_agm_version() error:", flush=True)
            print(e, flush=True)
            return ""

    def get_eps_version(self):
        """Returns the EPS module version.

        This method will return null terminated characters string
        containing the version of the EPS module contained into OSVE.

        :rtype: str
        """
        try:
            self.__load_library()
            self.libs.osve_getEpsVersion.restype = c_char_p
            version = self.libs.osve_getEpsVersion()
            self.__unload_library()
            return version.decode('utf-8')
        except Exception as e:
            print("ERROR: OSVE get_eps_version() error:", flush=True)
            print(e, flush=True)
            return ""

    def register_subscriber(self, subscriber):
        self.subscribers[subscriber.id] = subscriber
    
    def register_external_constraint(self, ext_constraint):
        self.externalConstraints[ext_constraint.id] = ext_constraint

    def register_logger(self, logger):
        self.loggers[logger.id] = logger
    
    def process_message(self, jsonStr) -> int:
    
        if len(self.subscribers) \
            or len(self.externalConstraints) \
            or len(self.loggers):
            
            msg_data = json.loads(jsonStr.decode('utf-8'))

            if msg_data["type"] == "LOGGER":
                # Is a logger callback, notify registered loggers 
                for logger_id in self.loggers:
                    logger = self.loggers[logger_id]
                    logger.onMsgReceived(msg_data["severity"], 
                                        msg_data["module"], 
                                        msg_data["time"],
                                        msg_data["text"])
                    
            elif msg_data["id"] in self.subscribers:
                
                # Is a subscriber callback, notify subscriber

                subscriber = self.subscribers[msg_data["id"]]
                res = 0

                if msg_data["type"] == "OSVE_SIMULATION_START":
                    res = subscriber.onSimulationStart(msg_data)

                elif msg_data["type"] == "OSVE_SIMULATION_STEP":
                    res = subscriber.onSimulationTimeStep(msg_data)

                elif msg_data["type"] == "OSVE_SIMULATION_PTR_BLOCK_START":
                    res = subscriber.onSimulationPtrBlockStart(msg_data)

                elif msg_data["type"] == "OSVE_SIMULATION_PTR_BLOCK_END":
                    res = subscriber.onSimulationPtrBlockEnd(msg_data)

                elif msg_data["type"] == "OSVE_SIMULATION_END":
                    res = subscriber.onSimulationEnd(msg_data)

                elif msg_data["type"] == "OSVE_EVENT_STATE_CHANGED":
                    res = subscriber.onEventStateChaged(msg_data)
                
                else:
                    raise Exception("Osve.process_message, OsveSubscriber, unimplemented callback type: " + str(msg_data["type"]))
                
                if res != 0:
                    return res
                
            elif msg_data["id"] in self.externalConstraints:

                # Is a external constraint callback, notify subscriber

                extConstraint = self.externalConstraints[msg_data["id"]]
                res = 0
                
                # Update the execution step: "Load and checkings (CHK)" or "Simulation (SIM)"
                extConstraint.step = msg_data["step"]

                if msg_data["type"] == "EC_configureConstraintChecks":
                    res = extConstraint.configureConstraintChecks()

                elif msg_data["type"] == "EC_resetConstraintFlags":
                    extConstraint.resetConstraintFlags()

                elif msg_data["type"] == "EC_notifyEnvironmentInitialised":
                    res = extConstraint.notifyEnvironmentInitialised()

                elif msg_data["type"] == "EC_update": 
                    res = extConstraint.update(msg_data["time"], 
                                            [
                                                msg_data["q0"],
                                                msg_data["q1"],
                                                msg_data["q2"],
                                                msg_data["q3"]
                                            ])

                elif msg_data["type"] == "EC_cleanup":
                    extConstraint.cleanup()

                elif msg_data["type"] == "EC_getInError":
                    res = extConstraint.getInError(msg_data["skipChecks"], 
                                                msg_data["showMessages"], 
                                                msg_data["checkConstraints"], 
                                                msg_data["breakFound"])
                
                else:
                    raise Exception("Osve.process_message, ExternalConstraint, unimplemented callback type: " + str(msg_data["type"]))
                
                if res != 0:
                    return res

            else:
                raise Exception("Osve.process_message, unknown Subscriber Id or External Constraint Id: " + str(msg_data["id"]))
                
        return 0