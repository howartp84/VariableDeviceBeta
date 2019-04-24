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

	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		# Since the dialog closed we want to set the debug flag - if you don't directly use
		# a plugin's properties (and for debugLog we don't) you'll want to translate it to
		# the appropriate stuff here.
		if not userCancelled:
			self.debug = valuesDict.get("showDebugInfo", False)
			if self.debug:
				indigo.server.log("Debug logging enabled")
			else:
				indigo.server.log("Debug logging disabled")


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
		varsList = dev.ownerProps['vars']
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
			icon = dev.ownerProps.get("iconType","")
			if (int(varID) == int(state)):
				self.debugLog("Updating displayState: %s" % varValue)
				if (int(varID) == int(state)):
					self.debugLog("Updating displayState: %s" % varValue)
					#self.debugLog(str(icon))
					#dev.updateStateOnServer("displayState", u"%s" % varValue)
					if (icon == 'Generic'):
						dev.updateStateOnServer("displayState", u"%s" % varValue)
						dev.updateStateImageOnServer(indigo.kStateImageSel.Auto)
					elif (icon == 'Power'):
						dev.updateStateOnServer("displayState", u"%s" % varValue)
						if ((varValue == 'on') or (varValue == 'true') or (varValue == 'yes')):
							dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
						else:
							dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
					elif (icon == 'Motion'):
						dev.updateStateOnServer("displayState", u"%s" % varValue)
						if ((varValue == 'on') or (varValue == 'true') or (varValue == 'yes')):
							dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)
						else:
							dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensor)
					elif (icon == 'TempF'):
						dev.updateStateOnServer("displayState", str(varValue), uiValue=str(varValue) + u" 'F")
						dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
					elif (icon == 'TempC'):
						dev.updateStateOnServer("displayState", str(varValue), uiValue=str(varValue) + u" 'C")
						dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
					elif (icon == 'Humidity'):
						dev.updateStateOnServer("displayState", u"%s" % varValue, uiValue=u"%s %" % varValue)
						dev.updateStateImageOnServer(indigo.kStateImageSel.HumiditySensor)
					elif (icon == 'LumLux'):
						dev.updateStateOnServer("displayState", u"%s" % varValue, uiValue=u"%s lux" % varValue)
						dev.updateStateImageOnServer(indigo.kStateImageSel.LightSensor)
					elif (icon == 'LumPC'):
						dev.updateStateOnServer("displayState", u"%s" % varValue, uiValue=u"%s %" % varValue)
						dev.updateStateImageOnServer(indigo.kStateImageSel.LightSensor)
		if (state) == "":
			dev.updateStateOnServer("displayState", "")
			dev.updateStateImageOnServer(indigo.kStateImageSel.None)
		elif (str(state) not in varsList):
			#dev.updateStateOnServer("displayState", "")
			dev.setErrorStateOnServer('Select state')
			dev.updateStateImageOnServer(indigo.kStateImageSel.Error)
		#self.debugLog(dev)		
		return True
	
	def deviceStopComm(self, dev):
		devID = dev.id
		varsList = dev.ownerProps['vars']
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
			icon = dev.ownerProps.get("iconType","")
			if (int(varID) == int(state)):
				self.debugLog("Updating displayState: %s" % varValue)
				#self.debugLog(str(icon))
				#dev.updateStateOnServer("displayState", u"%s" % varValue)
				if (icon == 'Generic'):
					dev.updateStateOnServer("displayState", u"%s" % varValue)
					dev.updateStateImageOnServer(indigo.kStateImageSel.Auto)
				elif (icon == 'Power'):
					dev.updateStateOnServer("displayState", u"%s" % varValue)
					if ((varValue == 'on') or (varValue == 'true') or (varValue == 'yes')):
						dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
					else:
						dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				elif (icon == 'Motion'):
					dev.updateStateOnServer("displayState", u"%s" % varValue)
					if ((varValue == 'on') or (varValue == 'true') or (varValue == 'yes')):
						dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)
					else:
						dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensor)
				elif (icon == 'TempF'):
					dev.updateStateOnServer("displayState", str(varValue), uiValue=str(varValue) + u" 'F")
					dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
				elif (icon == 'TempC'):
					dev.updateStateOnServer("displayState", str(varValue), uiValue=str(varValue) + u" 'C")
					dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
				elif (icon == 'Humidity'):
					dev.updateStateOnServer("displayState", u"%s" % varValue, uiValue=u"%s %" % varValue)
					dev.updateStateImageOnServer(indigo.kStateImageSel.HumiditySensor)
				elif (icon == 'LumLux'):
					dev.updateStateOnServer("displayState", u"%s" % varValue, uiValue=u"%s lux" % varValue)
					dev.updateStateImageOnServer(indigo.kStateImageSel.LightSensor)
				elif (icon == 'LumPC'):
					dev.updateStateOnServer("displayState", u"%s" % varValue, uiValue=u"%s %" % varValue)
					dev.updateStateImageOnServer(indigo.kStateImageSel.LightSensor)

		#else:
			#self.debugLog("Update ignored: %s" % newVar.name)
		
	