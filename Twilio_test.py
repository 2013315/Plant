from twilio.rest import Client

account_sid = "account_sid"
auth_token = "auth_token"

client = Client(account_sid, auth_token)

bod = "Hello from the raspberry pi"

asdf = input("Enter phone number: ")

target = "+61" + asdf

message = client.api.account.messages.create(

to= target,

from_="+twilio_phone_number",

body= bod)
