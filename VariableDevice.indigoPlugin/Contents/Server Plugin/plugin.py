#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
#
# Based on sample code that is:
# Copyright (c) 2014, Perceptive Automation, LLC. All rights reserved.
# http://www.indigodomo.com

import indigo

## TODO
# 1. 

################################################################################
class Plugin(indigo.PluginBase):
	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = pluginPrefs.get("showDebugInfo", True)
		#self.debug = True
		
		self.states = {}
		
		self.strstates = list()
		
		self.resetStates = False
		
		self.cmdStates = {}
		
		self.watchIDs = list()
		self.devFromVar = dict()

	########################################
	#def startup(self):
		#self.debugLog("Username: %s" % self.pluginPrefs.get("username","(Not yet saved)"))
		#self.debugLog("Username: %s" % self.un)
		#self.getVehicles()

	########################################
	def startup(self):
		self.debugLog(u"startup called")
		indigo.variables.subscribeToChanges()

	def getDeviceStateList(self, dev): #Override state list
		stateList = indigo.PluginBase.getDeviceStateList(self, dev)      
		if stateList is not None:
			for var in dev.ownerProps['vars']:
				varName = indigo.variables[int(var)].name
				#self.debugLog(varName)
				if ((self.resetStates) and (varName in stateList)):
					stateList.remove(varName)
				dynamicState1 = self.getDeviceStateDictForStringType(varName,varName,varName)
				stateList.append(dynamicState1)
		return sorted(stateList)

	def deviceStartComm(self, dev):
		#self.debugLog(dev)
		devID = dev.id
		varsList = indigo.devices[dev.id].ownerProps['vars']
		for var in varsList:
			varID = int(var)
			varName = indigo.variables[varID].name
			varValue = indigo.variables[varID].value
			indigo.server.log("Monitoring variable: %s" % varName)
			self.watchIDs.append(varID)
			self.devFromVar[varID] = int(devID)
			self.strstates.append(str(varID))
			dev.stateListOrDisplayStateIdChanged()
			dev.updateStateOnServer(str(varName), u"%s" % varValue)
			state = dev.ownerProps.get("stateToDisplay","")
			if (int(varID) == int(state)):
				self.debugLog("Updating displayState: %s" % varValue)
				dev.updateStateOnServer("displayState", u"%s" % varValue)
		return True
	
	def deviceStopComm(self, dev):
		devID = dev.id
		varsList = indigo.devices[dev.id].ownerProps['vars']
		for var in varsList:
			varID = int(var)
			indigo.server.log("Stop monitoring variable: %s" % indigo.variables[varID].name)
			try:
				self.watchIDs.remove(varID)
				self.devFromVar.pop(int(varID),None)
				self.strstates.remove(str(varID))
			except ValueError:
				pass
			self.resetStates = True
			dev.stateListOrDisplayStateIdChanged()
		return True
		
	def variableUpdated (self, origVar, newVar): 
		if (newVar.id in self.watchIDs):
			varID = newVar.id
			varName = newVar.name
			varValue = newVar.value
			devID = self.devFromVar[varID]
			#self.debugLog(devID)
			self.debugLog("Update received: %s: %s" % (newVar.name, newVar.value))
			#self.debugLog("Variable is monitored by %s" % indigo.devices[devID].name)
			dev = indigo.devices[devID]
			dev.updateStateOnServer(str(newVar.name), u"%s" % varValue)
			state = dev.ownerProps.get("stateToDisplay","")
			#self.debugLog("#%s#" % int(state))
			#self.debugLog("#%s#" % int(varID))
			if (int(varID) == int(state)):
				self.debugLog("Updating displayState: %s" % varValue)
				dev.updateStateOnServer("displayState", u"%s" % varValue)
			#self.debugLog(newVar)
		#else:
			#self.debugLog("Update ignored: %s" % newVar.name)
		
	