#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import tkinter
import sqlite3
import time
import datetime
import time
import csv
from datetime import datetime
from sys import stdin

# The broker name or IP address.
broker = "LAPTOP-L0QB3R0D"
# TLS port
port = 8883
# broker = "127.0.0.1"
# broker = "10.0.0.1"

# The MQTT client.
client = mqtt.Client()


class Employee:
    def __init__(self, empId, name, cardId):
        self.id = empId
        self.name = name
        self.cardId = cardId


class Log:
    def __init__(self, cardId, empId, terminalIn, timeIn, terminalOut, timeOut, timeLogged):
        self.cardId = cardId
        self.empId = empId
        self.terminalIn = terminalIn
        self.timeIn = timeIn
        self.terminalOut = terminalOut
        self.timeOut = timeOut
        self.timeLogged = timeLogged

    def update(self, terminalOut, timeOut):
        self.terminalOut = terminalOut
        self.timeOut = timeOut
        self.timeLogged = self.timeOut -self.timeIn


class System:
    def __init__(self):
        self.cards = {}
        self.logs = []
        self.employees = []
        self.terminals = {}
        self.loadCards()
        self.loadLogs()
        self.loadEmployees()
        self.freeId = 0

    def menu(self):
        while True:
            print("MENU\n1 - przypisanie karty pracownikowi\n2 - usunięcie danych pracownika z karty\n3 - wyświetlanie "
                  "danych\n4 - generuj raport\n5 - pokaż historię logowań\n6 - powiadom terminale")
            self.saveToFile()
            action = input()
            print(action)
            if action == "1":
                self.assign()
            elif action == "2":
                self.delete()
            elif action == "3":
                self.show()
            elif action == "4":
                self.generateReport()
            elif action == "5":
                self.showLogs()
            elif action == "6":
                self.hello()

    def hello(self):
        notification = input()
        client.publish("server/name", notification)

    def show(self):
        print("\nPRACOWNICY")
        for e in self.employees:
            print(e.id, e.name, e.cardId)
        print("\nKARTY")
        for c in self.cards:
            print(c, self.cards[c][0])

    def assign(self):
        self.show()
        print("\nPodaj indeks pracownika, któremu chcesz przypisać kartę")
        empId = input()
        card = None
        for c in self.cards:
            if self.cards[c][0] is None:
                card = c
        if card is None:
            print("Brak wolnych kart")
        else:
            self.cards[card][0] = empId
            self.employees[int(empId)].cardId = card
            for log in self.logs:
                if log.empId is None and log.cardId == card:
                    log.empId = empId

    def delete(self):
        self.show()
        print("\nPodaj indeks karty, którą chcesz zwolnić")
        cardId = input()
        for e in self.employees:
            if e.cardId == cardId:
                e.cardId = None
        self.cards[cardId][0] = None

    def generateReport(self):
        print("Podaj numer pracownika, dla którego chcesz wygenerować raport")
        empId = input()
        totalTime = datetime.now() - datetime.now()

        if [empId, True] or [empId, False] in self.cards.values():
            with open(empId + '.csv', 'w', newline='') as report_file:

                report_writer = csv.writer(report_file)
                report_writer.writerow(['Czas pracy'])
                for log in self.logs:
                    if log.empId == empId:
                        report_writer.writerow([log.timeLogged])
                        totalTime = totalTime + log.timeLogged
                report_writer.writerow([])
                report_writer.writerow(["W sumie:"])
                report_writer.writerow([totalTime])
                report_file.close()
        else:
            print("Nie znaleziono pracownika")

    def showLogs(self):
        for log in self.logs:
            print(log.empId, log.cardId, log.terminalIn, log.timeIn, log.terminalOut, log.timeOut, log.timeLogged)

    def loadCards(self):
        file = open("cards.txt", "r")
        while True:
            line = file.readline()
            if not line:
                break
            tokens = line.split(" ")
            if tokens[1] == "None":
                tokens[1] = None
            tokens[2] = tokens[2].split('\n')[0]
            if tokens[2] == "True":
                tokens[2] = True
            else:
                tokens[2] = False
            self.cards.update({tokens[0]: [tokens[1], tokens[2]]})
        file.close()

    def loadLogs(self):
        file = open("logs.txt", "r")
        while True:
            line = file.readline()
            if not line:
                break
            tokens = line.split(" ")
            if tokens:
                self.logs.append(
                    Log(tokens[0], tokens[1], tokens[2], tokens[3] + " " + tokens[4], tokens[5], tokens[6] + " " +
                        tokens[7], datetime.strptime(tokens[8].replace("\n", ""), '%H:%M:%S.%f') -
                        datetime.strptime("00:00:00.000000", '%H:%M:%S.%f')))
        file.close()

    def loadEmployees(self):
        file = open("employees.txt", "r")
        while True:
            line = file.readline()
            if not line:
                break
            tokens = line.split(" ")
            if len(tokens) == 3:
                self.employees.append(Employee(tokens[0], tokens[1] + " " + tokens[2].split('\n')[0], None))
            else:
                self.employees.append(Employee(tokens[0], tokens[1] + " " + tokens[2], tokens[3].split('\n')[0]))
        file.close()

    def saveToFile(self):
        empFile = open("employees.txt", "w")
        for e in self.employees:
            empFile.write(e.id)
            empFile.write(" " + e.name)
            if e.cardId is not None:
                empFile.write(" " + str(e.cardId) + '\n')
        empFile.close()
        logFile = open("logs.txt", "w")
        for log in self.logs:
            logFile.write(str(log.cardId) + " ")
            logFile.write(str(log.empId) + " ")
            logFile.write(str(log.terminalIn) + " ")
            logFile.write(str(log.timeIn) + " ")
            logFile.write(str(log.terminalOut) + " ")
            logFile.write(str(log.timeOut) + " ")
            logFile.write(str(log.timeLogged) + '\n')
        logFile.close()
        cardsFile = open("cards.txt", "w")
        for c in self.cards:
            cardsFile.write(str(c) + " ")
            cardsFile.write(str(self.cards[c][0]) + " ")
            cardsFile.write(str(self.cards[c][1]) + '\n')
        cardsFile.close()

    def process_message(self, client, userdata, message):
        print("otrzymano wiadomosc")
        message_decoded = (str(message.payload.decode("utf-8"))).split(".")
        if "Client connected" not in message_decoded[0] and "Client disconnected" not in message_decoded[0]:
            print("logowanie karty")
            event = message_decoded[0]
            terminalId = None
            for ter in self.terminals:
                if self.terminals.get(ter) is client:
                    terminalId = ter
            print("logowanie pracownika " + str(event) + " na terminalu " + str(terminalId))
            if event not in self.cards:
                print("nieznana karta => dodaje")
                self.cards.update({event: [None, False]})
            if self.cards[event][1] is False:
                print("pracownik " + event + " przyszedl do pracy")
                self.logs.append(
                    Log(event, self.cards[event][0], terminalId, datetime.now(), None, None, None))
                self.cards[event][1] = True
            else:
                print("pracownik " + event + " wyszedl\n")
                for log in self.logs:
                    if log.cardId == event and log.timeOut is None:
                        log.update(terminalId, datetime.now())
                self.cards[event][1] = False
        else:
            print("zmiana stanu terminala")
            if "Client connected" in message_decoded[0]:
                print("polaczono klienta")
                self.terminals.update({self.freeId: client})
                self.freeId += 1
                for ter in self.terminals:
                    print(ter)
                print()
            else:
                print("rozlaczono klienta")
                for ter in self.terminals:
                    if self.terminals.get(ter) == client:
                        del self.terminals[ter]
                for ter in self.terminals:
                    print(ter)
                print()

    def connect_to_broker(self):
        print("połącz z brokerem")
        client.tls_set("ca.crt")
        client.username_pw_set(username='server', password='password')
        # Connect to the broker.
        client.connect(broker, port)
        client.on_message = self.process_message
        # Starts client and subscribe.
        client.loop_start()
        client.subscribe("worker/name")
        print(broker)

    def disconnect_from_broker(self):
        # Disconnet the client.
        client.loop_stop()
        client.disconnect()


def run_receiver():
    system = System()
    system.connect_to_broker()
    system.menu()
    system.disconnect_from_broker()


if __name__ == "__main__":
    run_receiver()
