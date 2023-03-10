from twilio.rest import Client

account_sid = "AC62ad5a185580daf01c769d76cee034e0"
auth_token = "30d8eeb419e7f83dd633e4f962e52b26"

client = Client(account_sid, auth_token)

bod = "Hello from the raspberry pi"

asdf = input("Enter phone number: ")

target = "+61" + asdf

message = client.api.account.messages.create(

to= target,

from_="+12766246028",

body= bod)