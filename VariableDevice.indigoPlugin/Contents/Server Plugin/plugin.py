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

		self.watchIDs = list()
		self.devFromVar = dict()

		self.uiValue = dict()
		self.uiIcon = dict()

	########################################
	def startup(self):
		self.debugLog(u"startup called")
		indigo.variables.subscribeToChanges()

		self.uiValue["Generic"] = u""
		self.uiValue["Power"] = u""
		self.uiValue["PowerOn"] = u""
		self.uiValue["Motion"] = u""
		self.uiValue["MotionOn"] = u""
		self.uiValue["TempF"] = u" \u00b0F"
		self.uiValue["TempC"] = u" \u00b0C"
		self.uiValue["Humidity"] = u" %"
		self.uiValue["LumLux"] = u" lux"
		self.uiValue["LumPC"] = u" %"

		self.uiIcon["Generic"] = indigo.kStateImageSel.Auto
		self.uiIcon["Power"] = indigo.kStateImageSel.PowerOff
		self.uiIcon["PowerOn"] = indigo.kStateImageSel.PowerOn
		self.uiIcon["Motion"] = indigo.kStateImageSel.MotionSensor
		self.uiIcon["MotionOn"] = indigo.kStateImageSel.MotionSensorTripped
		self.uiIcon["TempF"] = indigo.kStateImageSel.TemperatureSensorOn
		self.uiIcon["TempC"] = indigo.kStateImageSel.TemperatureSensorOn
		self.uiIcon["Humidity"] = indigo.kStateImageSel.HumiditySensor
		self.uiIcon["LumLux"] = indigo.kStateImageSel.LightSensor
		self.uiIcon["LumPC"] = indigo.kStateImageSel.LightSensor




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
		self.debugLog(u"deviceStartComm called")
		#self.debugLog(dev)
		devID = dev.id
		varsList = dev.ownerProps['vars']
		for var in varsList:
			varID = int(var)
			varName = indigo.variables[varID].name
			varValue = indigo.variables[varID].value
			state = dev.ownerProps.get("stateToDisplay","")
			if (state == ""):
				state = 0
			icon = dev.ownerProps.get("iconType","")
			indigo.server.log(u"{}{}".format("Monitoring variable: ",varName))
			self.watchIDs.append(varID)
			self.devFromVar[varID] = int(devID)
			self.strstates.append(str(varID))
			dev.stateListOrDisplayStateIdChanged()
			dev.updateStateOnServer(str(varName), varValue)
			if (int(varID) == int(state)):
				self.debugLog("Updating displayState: %s" % varValue)
				if ((varValue == 'on') or (varValue == 'true') or (varValue == 'yes')):
					icon = icon + "On"
				dev.updateStateOnServer("displayState", varValue, uiValue=u'{} {}'.format(varValue, self.uiValue[icon]))
				dev.updateStateImageOnServer(self.uiIcon[icon])
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
			dev.updateStateOnServer(str(newVar.name), varValue)
			state = dev.ownerProps.get("stateToDisplay","")
			if (state == ""):
				state = 0
			icon = dev.ownerProps.get("iconType","")
			if (int(varID) == int(state)):
				self.debugLog("Updating displayState: %s" % varValue)
				if ((varValue == 'on') or (varValue == 'true') or (varValue == 'yes')):
					icon = icon + "On"
				dev.updateStateOnServer("displayState", varValue, uiValue=u'{} {}'.format(varValue, self.uiValue[icon]))
				dev.updateStateImageOnServer(self.uiIcon[icon])
