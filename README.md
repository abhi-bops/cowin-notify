# cowin-notify
A python script to check for free slots and notify via Whatsapp. Currently hardcoded to check for free slots in District:Bengaluru BBMP; Age Group: 18+, Dose: First dose

# Usage
python3 cowin-notify.py [PhoneNumWith+InternationalCode] [WhatsappAPIKeyFromCallMeBot.com]

# Notes
- Does not do any polling, it's upto the user to implement it as wrap around the script (bash for loops)
- To get the Whatsapp key api , use https://www.callmebot.com/blog/free-api-whatsapp-messages/ .
- Prints more info in the command line
- Message sent to whatsapp is limited
