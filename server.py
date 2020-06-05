from socket import *
from _thread import start_new_thread
from random import randint
from time import sleep
from socket import error


class Players:
    def __init__(self, name, conn):
        self.name = name
        self.connection = conn
        self.points = 0
        self.first = name[0]


def left(x, y, room_num):
    global horizontal_line, vertical_line
    if y in horizontal_line[room_num][x - 1] and y in vertical_line[room_num][x - 1] and y + 1 in \
            horizontal_line[room_num][x - 1]:
        return True


def right(x, y, room_num):
    global horizontal_line, vertical_line
    if y in horizontal_line[room_num][x] and y in vertical_line[room_num][x + 1] and y + 1 in \
            horizontal_line[room_num][x]:
        return True


def send_msg(room_num, x, y, name):
    global rooms
    msg = "d " + str('%02d' % x) + " " + str('%02d' % y) + " " + name
    for i in range(len(rooms[room_num])):
        rooms[room_num][i].connection.send(msg.encode())


def check_vertical(x, y, room_num, turn):
    global rooms
    if 1 < x < 19 and right(x, y, room_num) and left(x, y, room_num):
        rooms[room_num][turn].points += 2
        send_msg(room_num, x, y, rooms[room_num][turn].first)
        send_msg(room_num, x - 1, y, rooms[room_num][turn].first)
    elif x > 1 and left(x, y, room_num):
        rooms[room_num][turn].points += 1
        send_msg(room_num, x - 1, y, rooms[room_num][turn].first)
    elif x < 19 and right(x, y, room_num):
        rooms[room_num][turn].points += 1
        send_msg(room_num, x, y, rooms[room_num][turn].first)


def down(x, y, room_num):
    global horizontal_line, vertical_line
    if y + 1 in horizontal_line[room_num][x] and y in vertical_line[room_num][x] and y in \
            vertical_line[room_num][x + 1]:
        return True


def up(x, y, room_num):
    global horizontal_line, vertical_line
    if y - 1 in vertical_line[room_num][x] and y - 1 in horizontal_line[room_num][x] and y - 1 in \
            vertical_line[room_num][x + 1]:
        return True


def check_horizontal(x, y, room_num, turn):
    global rooms
    if 1 < y < 19 and down(x, y, room_num) and up(x, y, room_num):
        rooms[room_num][turn].points += 2
        send_msg(room_num, x, y, rooms[room_num][turn].first)
        send_msg(room_num, x, y - 1, rooms[room_num][turn].first)
    elif y < 19 and down(x, y, room_num):
        rooms[room_num][turn].points += 1
        send_msg(room_num, x, y, rooms[room_num][turn].first)
    elif y > 1 and up(x, y, room_num):
        rooms[room_num][turn].points += 1
        send_msg(room_num, x, y - 1, rooms[room_num][turn].first)


def final(room_num, turn):
    global rooms
    msg = ""
    temp = []
    for i in range(number_of_players[room_num]):
        temp.append(i)
    for i in range(number_of_players[room_num]):
        for j in range(i + 1, number_of_players[room_num]):
            if rooms[room_num][i].points < rooms[room_num][j].points:
                rooms[room_num][i], rooms[room_num][j] = rooms[room_num][j], rooms[room_num][i]
                temp[i], temp[j] = temp[j], temp[i]
    for i in range(number_of_players[room_num]):
        try:
            rooms[room_num][i].connection.send("quit     ".encode())
        except error:
            pass
        temp_1 = str(temp[i]) + "," + str(rooms[room_num][i].points) + ":"
        msg += temp_1
    for i in range(number_of_players[room_num]):
        try:
            temp_3 = '%02d' % turn
            rooms[room_num][i].connection.send(temp_3.encode())
            rooms[room_num][i].connection.send(msg.encode())
            data = rooms[room_num][i].connection.recv(1).decode()
            while data == '0':
                rooms[room_num][i].connection.send(msg.encode())
                data = rooms[room_num][i].connection.recv(1).decode()
        except error as e:
            print("error", e)
    sleep(5)
    for i in range(number_of_players[room_num]):
        try:
            rooms[room_num][i].connection.send("silly".encode())
        except error:
            pass
    del number_of_players[room_num]
    del rooms[room_num]


def game_initial(room_num):
    global number_of_players, rooms, vertical_line, horizontal_line
    sleep(6)
    turn = 0
    while room_num in rooms.keys():
        msg = "turn " + "%04d" % turn
        try:
            for i in range(len(rooms[room_num])):
                if i == turn:
                    rooms[room_num][i].connection.send("@@you    ".encode())
                else:
                    rooms[room_num][i].connection.send(msg.encode())
        except KeyError:
            final(room_num, turn)
        except error:
            final(room_num, turn)
        data = rooms[room_num][turn].connection.recv(1024).decode()
        data = data.split()
        try:
            if data[0] == 'quit':
                final(room_num, turn)
            else:
                x = int(data[1])
                y = int(data[2])
                if data[0] == "h":
                    horizontal_line[room_num][x].append(y)
                    check_horizontal(x, y, room_num, turn)
                    msg = "hor " + data[1] + " " + data[2]
                elif data[0] == "v":
                    vertical_line[room_num][x].append(y)
                    check_vertical(x, y, room_num, turn)
                    msg = "ver " + data[1] + " " + data[2]
                for i in range(len(rooms[room_num])):
                    if i != turn:
                        rooms[room_num][i].connection.send(msg.encode())
        except IndexError:
            final(room_num, turn)
        except IOError:
            final(room_num, turn)
        turn += 1
        try:
            if turn == len(rooms[room_num]):
                turn = 0
        except KeyError:
            pass


def second(conn, node, room_no, number_players):
    global number_of_players, rooms
    name = node.name
    message = str(number_players) + ','
    for i in rooms[room_no]:
        if node != i:
            try:
                i.connection.send(name.encode())
            except error as e:
                pass
            message += i.name + ','
    conn.send(message.encode())
    if number_players == len(rooms[room_no]):
        game_initial(room_no)


def first(conn):
    name = conn.recv(1024).decode()
    node = Players(name, conn)
    data = conn.recv(1024).decode()
    if data[0] == "R":
        room_num = int(data[2:])
        while True:
            if room_num in rooms.keys():
                conn.send("1".encode())
                if len(rooms[room_num]) < number_of_players[room_num]:
                    conn.send("1".encode())
                    rooms[room_num].append(node)
                    second(conn, node, room_num, number_of_players[room_num])
                else:
                    conn.send("0".encode())
                break
            else:
                conn.send("0".encode())
                data = conn.recv(1024).decode()
                room_num = int(data[2:])

    elif data[0] == "C":
        room_num = randint(111111, 999999)
        while room_num in rooms.keys():
            room_num = randint(111111, 999999)
        rooms[room_num] = [node]
        number_of_players[room_num] = int(data[2:])
        room_no = str(room_num)
        print(room_num)
        conn.send(room_no.encode())
        temp = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        temp_1 = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
        horizontal_line[room_num] = list(temp)
        vertical_line[room_num] = list(temp_1)
        conn.send("1".encode())
        second(conn, node, room_num, number_of_players[room_num])


host = "127.0.0.1"
port = 2020
rooms = dict()
number_of_players = dict()
horizontal_line = dict()
vertical_line = dict()
socks = socket()
socks.bind((host, port))
socks.listen(5)
while True:
    connection, address = socks.accept()
    start_new_thread(first, (connection,))
