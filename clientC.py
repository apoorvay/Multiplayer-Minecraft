#!/usr/bin/env python3

# This file is part of the Python aiocoap library project.
#
# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

"""This is a usage example of aiocoap that demonstrates how to implement a
simple client. See the "Usage Examples" section in the aiocoap documentation
for some more information."""

import logging
import asyncio
import pickle
import sys, argparse
from aiocoap import *

gameFinished = False

#add argument to get server's IP addr
logging.basicConfig(level=logging.INFO)
parser = argparse.ArgumentParser()
parser.add_argument('-i', required = True, dest = 'serverIp')
arguments = parser.parse_args()

#runs until game is finished
async def main():

    #send GET request to server
    protocol = await Context.create_client_context()

    url = 'coap://'+arguments.serverIp+'/minecraft'
    request = Message(code=GET, uri=url)

    try:
        response = await protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)

    position = pickle.loads(response.payload)

    #if token ID in GET request match client ID then place a POST request to place block
    if (position[3] == 3):

        await asyncio.sleep(2)
        
        payload = (position[0], position[1], position[2], position[3], 'wood')
        pickled_payload = pickle.dumps(payload)        
        request = Message(code=POST, payload=pickled_payload)
        request.opt.uri_host = arguments.serverIp
        request.opt.uri_path = ("minecraft",)

        response = await protocol.request(request).response

        print('Result: %s\n%r'%(response.code, pickle.loads(response.payload)))

    #get message from server that game is finished
    elif position[3] == 0:
        global gameFinished
        print ('Game Finished \n')
        gameFinished = True

    
if __name__ == "__main__":

    #stop running when game is finished
    while(gameFinished == False):
        asyncio.get_event_loop().run_until_complete(main())
