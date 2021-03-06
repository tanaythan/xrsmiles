from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from models import *
from django.core import urlresolvers
from StringIO import StringIO
from xml.dom import minidom
import json, os, pycurl

def index(request):
	list_of_charities = Charity.objects.order_by('-charity_name')
	lines = open('charities/templates/main.html', 'r').read().splitlines()
	output = ""
	for line in lines:
		output += line
	output += ''.join(['<a href = ' + str(c.id) + '>' + c.charity_name + '</a>' for c in list_of_charities][::-1])
	output = "</nav></section></div></body></html>" + output
	return HttpResponse(output)

def show(request, charity_id):
	charity = Charity.objects.get(pk=charity_id)
	if request.method == 'POST':
		form = RequestForm(request.POST)
		if form.is_valid():
			value = form.cleaned_data['amount']
			secret = form.cleaned_data['secret']
			address = form.cleaned_data['address']
			pay(value, address, secret, charity.ripple_id)
			form.save()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	form =  RequestForm()
	form.fields['is_transaction_complete'].widget = forms.HiddenInput()
	form.fields['is_valid'].widget = forms.HiddenInput()
	return render(request, 'create.html', {'form' : form, 'charity' : charity})

def pay(value, source, secret, dest):
	#get valid client id
	idtag = StringIO()
	c1 = pycurl.Curl()
	c1.setopt(c1.URL, "http://127.0.0.1:5990/v1/uuid/")
	c1.setopt(c1.WRITEDATA, idtag)
	c1.perform()
	c1.close()
	idtag = json.loads(idtag.getvalue())['uuid']

	#json data
	data = {
  		'secret' : secret,
  		'client_resource_id' :  idtag , 
  		'payment' : { 
    		'source_account' : source ,
    		'source_tag' : '', 
    		'source_amount' : {
        		'value' : str(value) ,
        		'currency' : 'XRP' ,
        		'issuer' : ''
    		},
    		'source_slippage' : '0',
    		'destination_account' : dest ,
    		'destination_tag' : '' , 
    		'destination_amount' : {
        		'value' : str(value) ,
        		'currency' : 'XRP' ,
        		'issuer' : ''
    		},
    		'invoice_id' : '',
    		'paths' : '[]', 
    		'flag_no_direct_ripple' : 'false',
    		'flag_partial_payment' : 'false'
  		}
  	}

	#curl payment
	c2 = pycurl.Curl()
	c2.setopt(pycurl.POST, 1)
	c2.setopt(pycurl.URL, "http://127.0.0.1:5990/v1/accounts/rfyy7dowjDEXs2Qc68WDEziF1KDWwtrarL/payments/")
	c2.setopt(pycurl.HTTPHEADER, ["Content-Type: application/json"])
	c2.setopt(pycurl.POSTFIELDS, json.dumps(data))
	c2.perform()
	c2.close()


"""
TODO: Get this working
def sendBTC(request): 
	address = request.address
	receiving = "1KBGCThhCs1ohCaxCkwasgVMHDNFbrd3RU"
	amt=request.amount
	date= request.date
	charityName= charity_name

	validation=userinfo.validateaddress(address)
	if validation.isvalid:
		print "address is not valid."
		userinfo.isvalid=False
	elif amt<0:
		print "amount is negative."
		userinfo.isvalid=False
	else:
		print "address is valid."
		userinfo.sendfrom(getaccount(address), receiving, amt, 0, "sent from " +charityName, amt+ " sent to" + receiving)
		payment=userinfo.getreceivedbyaddress(receiving)
		if(payment==amt):
			print "payment received."
			userinfo.is_transaction_complete= True
			userinfo.isvalid=True
		else:
			print "payment not received."
"""

# Create your views here.
