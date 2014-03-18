#!/usr/bin/env python
# title          : pyblockchain
#description     : BlockChain.info API library
#author          : Justin Allen
#date            : 20130813
#version         : 0.1.0
#notes           :
#license         : GNU GPL2 http://www.gnu.org/licenses/
#python_version  : 3  
#==============================================================================

import requests
import urllib
import json
from os.path import expanduser
import configparser

	
def CreateDepositeAddress(recvAddr, shared='false', callback=''):
	url = "https://blockchain.info/api/receive"
	data = {'method':'create', 'address':recvAddr, 'shared':shared, 'callback':callback}

	response = requests.post(url,params=data)
	response_dict = response.json()

	destaddr = response_dict['destination']
	fee = response_dict['fee_percent']
	sendaddr = response_dict['input_address']


	if destaddr != recvAddr :
		print("ERROR: Destination address in response is not receiving address we sent!")
		return	

	if callback== '' and shared == 'false' : 
		return sendaddr

	if shared == 'false':
		cburl = response_dict['callback_url']
		return sendaddr,cburl

	if callback == '': 
		return sendaddr,fee

	return sendaddr,fee,cburl



class Wallet: 
	guid		= ''
	isAccount 	= 0
	isKey 		= 0
	password1 	= ''
	password2 	= ''
	url 		= ''

	def __init__(self, guid = '', password1 = '', password2 = ''):

		if guid.count('-') > 0:
			self.isAccount = 1
			if password1 == '': # wallet guid's contain - 
				raise ValueError('No password with guid.')
		else:
			self.isKey = 1


		self.guid = guid
		self.url = 'https://blockchain.info/merchant/' + guid + '/'

		self.password1 = password1
		self.password2 = password2

##
##	def Save(self, file = expanduser('~/wallet.dat')):
##		config = configparser.RawConfigParser()
##		config.add_section('wallet')
##		config.set('wallet','guid',self.guid)
##		config.set('wallet','isAccount',self.isAccount)
##		config.set('wallet','isKey',self.isKey)
##		config.set('wallet','password1',self.password1)
##		config.set('wallet','password2',self.password2)
##		config.set('wallet','url',self.url)
##
##		with open(file,'w') as configfile:
##			config.write(configfile)
##
##
##	def Load(self,file = expanduser('~/wallet.dat')):
##		config = configparser.ConfigParser()
##		config.read(file)
##
##		self.guid		= config.get('wallet','guid')
##		self.isAccount 	= config.get('wallet','isAccount')
##		self.isKey 		= config.get('wallet','isKey')
##		self.password1 	= config.get('wallet','password1', raw=1)
##		self.password2 	= config.get('wallet','password2', raw=1)
##		self.url 		= config.get('wallet','url', raw=1)
##


	def Call(self, method, data = {}):
		if self.password1 != '':
			data['password'] = self.password1 
		if self.password2 != '':
			data['seccond_password'] = self.password2

		response = requests.post(self.url + method,params=data)

		json = response.json()
		if 'error' in json:
			raise RuntimeError('ERROR: ' + json['error'])

		return json


	def GetBalance(self):
		response = self.Call('balance')
		return response['balance']


	def GetAddressBalance(self,addr = '', confirmed = 0):
		data = {"address": addr , "confirmed": confirmed }

		response = self.Call('address_balance', data)
		return response['balance']


	def GetAddresses(self):
		response = self.Call('list')
		return response['addresses']


	def NewAddress(self, label = ''):
		if self.isKey:
			raise ValueError('Key\'s cannot generate addresses?') 

		response = ''

		if label != '':
			response = self.Call('new_address', {"label": label})
		else:
			response = self.Call('new_address')

		return response['address']


	def SendPayment(self, toaddr, amount , fromaddr = '', shared = 0, fee = 0.0000, note = ''):
		data = {}
		data['address'] = toaddr
		data['amount'] = amount
		data['fee'] = fee


		if fromaddr != '':
			data['from'] = fromaddr

		if shared == 1:
			data['shared'] = 'true'

		if note != '':
			data['note'] = note

		response = self.Call('payment',data)

		return 




	def SendManyPayment(self, txs = {} , fromaddr = '', shared = 0, fee = 0.0000, note = ''):
		responses = {}

		for tx in txs:
			SendPayment(self, tx[0], tx[1] , fromaddr , shared , fee , note )

		return 
