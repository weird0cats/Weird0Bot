from mcstatus import JavaServer #type:ignore
#Channels
statuschannel_id=1290139409328377938
bot_log_id=1290477621976764530
#Ip & port
lnk="weird0cats.playmc.be"
server=JavaServer.lookup(lnk)
ip=server.address.host
port=server.address.port
#offline message
offlinemsg="The server's probably offline"
#version
version="1.0"