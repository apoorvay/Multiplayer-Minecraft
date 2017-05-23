# Copyright (c) 2012-2014 Maciej Wasilak <http://sixpinetrees.blogspot.com/>,
#               2013-2014 Christian Amsüss <c.amsuess@energyharvesting.at>
#
# aiocoap is free software, this file is published under the MIT license as
# described in the accompanying LICENSE file.

import datetime
import logging
import RPi.GPIO as GPIO
import asyncio

import aiocoap.resource as resource
import aiocoap
import pickle

import mcpi.minecraft as minecraft
import mcpi.block as block

#initialize Minecraft playing field and get initial position of player

mc = minecraft.Minecraft.create()
initialPos = mc.player.getTilePos()
maxY = initialPos.y+1
maxX = initialPos.x+9
playerTurn = 1
gameFinished = False

#initialize GPIO pins

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

#returns current player position

def getPlayerPos():
    global gameFinished
    global playerTurn
    pPos = mc.player.getTilePos()
    if gameFinished == True:
        playerTurn = 0
    putPayload = (pPos.x, pPos.y, pPos.z, playerTurn)
    return pickle.dumps(putPayload)

#resources used by the clients to send and receive minecraft and clientID data
class MinecraftResource(resource.Resource):
    """
    Example resource which supports GET and PUT methods. It sends large
    responses, which trigger blockwise transfer.
    """

    def __init__(self):
        super(MinecraftResource, self).__init__()
        self.content = ("This is the resource's default content. It is padded "\
                "with numbers to be large enough to trigger blockwise "\
                "transfer.\n" + "0123456789\n" * 100).encode("ascii")

    async def render_get(self, request):
        
        return aiocoap.Message(payload=getPlayerPos())

    async def render_post(self, request):

        global playerTurn, gameFinished

        #update player turn - round robin
        playerTurn = playerTurn + 1
        if(playerTurn == 4):
            playerTurn = 1
            
        self.content = request.payload
        blockPos = pickle.loads(request.payload)

        #update LED
        if(blockPos[3] == 1):
            GPIO.output(29, True)
            GPIO.output(31, False)
            GPIO.output(33, False)

        elif (blockPos[3] == 2):
            GPIO.output(29, False)
            GPIO.output(31, False)
            GPIO.output(33, True)

        elif (blockPos[3] == 3):
            GPIO.output(29, False)
            GPIO.output(31, True)
            GPIO.output(33, False)

        #specify type of block to be placed
        if (blockPos[4] == 'stone'):
            curBlock = block.STONE
        elif (blockPos[4] == 'diamond'):
            curBlock = block.DIAMOND_ORE
        else:
            curBlock = block.WOOD

        #place block    
        mc.setBlocks(blockPos[0],blockPos[1],blockPos[2],blockPos[0],blockPos[1],blockPos[2],curBlock)
        nextPos = (blockPos[0], blockPos[1]+1, blockPos[2])

        #determine next position of the block for the wall
        if (nextPos[1] > maxY):
            if(nextPos[0] < maxX):
                nextPos = (blockPos[0]+1, initialPos.y, blockPos[2])
            else:
                gameFinished = True

        #10x2 wall has been built        
        if gameFinished == False:    
            mc.player.setPos(nextPos[0],nextPos[1],nextPos[2])
            payLoad = pickle.dumps(("placed", nextPos))
            
        else:
            payLoad = pickle.dumps("Game Finished")

        return aiocoap.Message(payload=payLoad)

logging.basicConfig(level=logging.INFO)
logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main():
    # Resource tree creation
    global gameFinished
    root = resource.Site()

    root.add_resource(('.well-known', 'core'), resource.WKCResource(root.get_resources_as_linkheader))

    #resource to be used by clients playing Minecraft
    root.add_resource(('minecraft',), MinecraftResource())

    asyncio.Task(aiocoap.Context.create_server_context(root))

    asyncio.get_event_loop().run_forever()

    if(gameFinished):
        asyncio.get_event_loop().stop()

if __name__ == "__main__":
    main()
