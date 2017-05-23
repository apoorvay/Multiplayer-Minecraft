# Multiplayer-Minecraft
Multiplayer Minecraft Game using a COAP server

Before running server or clients, copy the MCPI folder to the location of the server and client files </br>
Have python3.5 installed. </br>
Have Minecraft: Pi edition running and start a new game. </br>

SERVER RPI

Initialization: Run from command line using: python3 MineServer.py </br>
Command line arguments (to establish a connection to the message broker) </br>


Libraries Used: </br>
logging:	To log and debug the server connection </br>
RPi.GPIO:	To control LED </br>
asyncio: 	To implement asynchronous task running </br>
aiocoap:	Messaging mechanism between server and clients </br>
pickle:		To send data over aiocoap connection </br>
mcpi:		To interface with Minecraft </br>


CLIENT RPi:

Initialization: Run from command line using: </br>
python3 clientA -i 'ipaddress' </br>
python3 clientB -i 'ipaddress' </br>
python3 clientC -i 'ipaddress' </br>

Libraries Used: </br>
asyncio: 	To implement asynchronous task running </br>
aiocoap:	Messaging mechanism between server and clients </br>
pickle:		To send data over aiocoap connection </br>
argparse: 	To parse the command line arguments </br>
logging:	To log and debug the server connection </br>
