#!/usr/bin env python
import sys
import os


# data-only class to store synapse configuration
class synCFG:

   
   def setDebugLevel(self,debugLevel):

      self.debugLevel = debugLevel

   def getDebugLevel(self):

      return self.debugLevel

   def __init__(self,debugLevel=3):

      self.debugLevel = debugLevel

      return
