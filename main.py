import websocket

def on_message(wsapp, message):
    print(message)

wsapp = websocket.WebSocketApp("wss://2021-utd-hackathon.azurewebsites.net", on_message=on_message)
wsapp.run_forever()
