import websocket
def on_error(wsapp,message):
    print(message)
def on_message(wsapp,message):
    print(message)
    d=eval(message)
    #print(d["operations"][0]["revenueStructure"][0]["flowPerDay"])
    a=str(d["flowRateIn"]/len(d["operations"]))
    output="["
    for i in range(0,len(d["operations"])):
        output=output+"{\"operationId\":\""+d["operations"][i]["id"]+"\",\"flowRate\":"+a+"},"
    output=output[:-1]
    output=output+"]"
    print(output)
    wsapp.send(output)

wsapp=websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net",on_message=on_message, on_error=on_error)
wsapp.run_forever()
#wsapp.connect("wss://2021-utd-hackathon.azurewebsites.net",onmessage=onmessage)


#print(wsapp.recv())
