#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import tkinter
import time
import datetime
import time
import csv
import random
from sys import stdin

# The terminal ID - can be any string.
# The broker name or IP address.
broker = "LAPTOP-L0QB3R0D"

# broker = "127.0.0.1"
# broker = "10.0.0.1"
# TLS port
port = 8883

# The MQTT client.
client = mqtt.Client()


class Terminal:

    def __init__(self):
        self.connected = True

    def readCard(self):
        while True:
            event = ord(input())
            if event == ord(" "):
                if self.connected:
                    print("rozlacz")
                    self.connected = False
                    self.disconnect_from_broker()
                else:
                    print("polacz")
                    self.connected = True
                    self.reconnect()
            else:
                client.publish("worker/name", str(event), )
    def reconnect(self):
        client.connect(broker, port)

    def connect_to_broker(self):
        client.tls_set("ca.crt")
        client.username_pw_set(username='client', password='password')
        # Connect to the broker.
        client.connect(broker, port)
        # Send message about conenction.
        client.on_message = self.process_message
        # Starts client and subscribe.
        client.loop_start()
        client.publish("worker/name", "Client connected.", )
        client.subscribe("server/name")

    def disconnect_from_broker(self):
        # Send message about disconenction.
        client.publish("worker/name", "Client disconnected.", )
        client.disconnect(broker)

        # Disconnet the client.

    def process_message(self, client, userdata, message):
        message_decoded = (str(message.payload.decode("utf-8")))
        print("Otrzymano wiadomosc")
        print(message_decoded)


def run_sender():
    terminal = Terminal()
    terminal.connect_to_broker()
    terminal.readCard()
    terminal.disconnect_from_broker()


if __name__ == "__main__":
    run_sender()
