#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  PsYNC.py
#  
#  Copyright 2013 Rick Opper <brainstormtrooper@free.fr>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import os
import json
import time

class PsYNC():
	#global memeStorePath
	memeStorePath = 'cache/memeStore.dat'
	memeStore = None
	_Memes = {} #{('a0','b0'):{'mtime':'19731130T064000000Z','mmeta':{'name':'dummy data'}}} <-- can't read back in :-(
				#{"lid":"a1","rid":"none","mtime":"19720309T180000000Z","mmeta":{"name":"dummy data"}}
	
	def __init__(self, memepath):
		if memepath is None:
			self.memeStorePath = 'cache/memeStore.dat'
		else:
			self.memeStorePath = memepath
		self.memeStore = None
		
		if os.path.isfile(self.memeStorePath):
			print "[ii] sync: reading memes from file"
			self.readMemes()

		#self.memeStore = open(self.memeStorePath, 'w+')
		
			
	def readMemes(self):
		memetxt = open(self.memeStorePath).read()
		print memetxt
		self._Memes = json.loads(memetxt)
		
	def writeMemes(self):
		self.memeStore.write(str(self._Memes))
		
	def _local(self, rid):
		found = -1		
		for key in self._Memes.keys():
			k = key.split(',')
			if rid in k[1] and 'none' not in k[0]:
				found = k[0]
		return found
		 
	def _remote(self, lid):
		found = -1
		for key in self._Memes.keys():
			k = key.split(',')
			if lid in k[0] and 'none' not in k[1]:
				found = k[1]
		return found	
	
	def addLocal(self, details):
		"""
		adds a meme to the catalog. 
		expects to get details as lid, mtime, mmeta (a dict of whatever attributs might be needed...)
		
		"""
		if 'lid' in details.keys():
			details['mtime'] = int(time.time())
			if self._remote(details['lid']) != -1:
				newkey = details['lid'] + "," + self._remote(details['lid'])
				oldkey = 'none,' + self._remote(details['lid'])
				self._Memes[newkey] = self._Memes.pop(oldkey)
			else:
				newkey = details['lid'] + ",none"
				self._Memes[newkey] = details
				
	def addRemote(self, details):
		"""
		adds a meme to the catalog. 
		expects to get details as rid, mtime, mmeta (a dict of whatever attributs might be needed...)
		
		"""
		if 'rid' in details.keys():
			details['mtime'] = int(time.time())
			if self._exists(details['rid']) is -1:
				if self._local(details['rid']) != -1:
					newkey = self._local(details['rid']) + "," + details['rid']
					oldkey = self._remote(details['lid']) + ',none' #'none,' + self._remote(details['lid'])
					self._Memes[newkey] = self._Memes.pop(oldkey)
				else:
					newkey = 'none,' + details['rid']
					self._Memes[newkey] = details
				print "[ii] SYNC: added " + newkey + " to memedict"
			else:
				#
                # This will replace the contents...
                #
				self._Memes[self._exists(details['rid'])] = details
		
	def remove(self, lid='none', rid='none'):
		"""
		deletes an entry
		"""
		dkey = lid + "," + rid
		del self._Memes[dkey]
		
	def _missing(self):
		"""
		gets lids and rids where the other half is missing...
		"""
		missing = {0,1}
		for key in self._Memes.keys():
			k = key.split(",")
			if 'none' in k[0]:
				missing[0].append(k[1])
			if 'none' in k[1]:
				missing[1].append(k[0])
		return missing
	
	def _exists(self, item):
		
		iexists = -1
		for key in self._Memes.keys():
			k = key.split(',')
			if str(item) in k[0]:
				iexists = key
			if str(item) in k[1]:
				iexists = key
		return iexists
	
	def _contents(self, key):
		
		return self._Memes[key]
	
	def _newest(self, key):
		newest = 'ERROR'
		if 'none' not in key:
			if self._Memes[key]['ltime'] > self._Memes[key]['rtime']:
				newest = 'LOCAL'
			elif self._Memes[key]['rtime'] > self._Memes[key]['ltime']:
				newest = 'REMOTE'
			elif self._Memes[key]['ltime'] == self._Memes[key]['rtime']:
				newest = 'SAME'
		return newest