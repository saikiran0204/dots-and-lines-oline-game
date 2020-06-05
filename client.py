from socket import *
from tkinter import *
from sys import exit
from pygame import *
from time import sleep
from _thread import start_new_thread


def final():
    global players, socks
    sleep(2)
    data = socks.recv(2).decode()
    while not data.isnumeric():
        # socks.recv(7).decode()
        data = socks.recv(9).decode()
    print("game closed by ", players[int(data)])
    while True:
        try:
            data = socks.recv(1024).decode().split(':')
        except error as e:
            data = ','
        temp = data[0].split(',')
        if temp[0] == '' or temp[1] == '':
            socks.send('0'.encode())
        else:
            socks.send('1'.encode())
            break
    print("SNO\t", "name\t", "points")
    for i in range(len(data)-1):
        temp = data[i].split(',')
        print(i+1, '\t', players[int(temp[0])], '\t', temp[1])
    try:
        socks.close()
    except error:
        print(error)


def draw_vertical_line(temp_x, temp_y):
    global length_x, length_y, vertical_visited, turn, window_10
    draw.line(window_10, (255, 0, 0), (temp_x * length_x - 1, temp_y * length_y - 1),
              (temp_x * length_x - 1, temp_y * length_y + length_y - 1), 4)
    vertical_visited[temp_x].append(temp_y)


def draw_horizontal_line(temp_x, temp_y):
    global length_x, length_y, horizontal_visited, turn, window_10
    draw.line(window_10, (255, 0, 0), (temp_x * length_x - 1, temp_y * length_y - 1),
              (temp_x * length_x + length_x - 1, temp_y * length_y - 1), 4)
    horizontal_visited[temp_x].append(temp_y)


def write_turn(name):
    global font_1, rectangle, window_10
    text_3 = font_1.render(name, False, (255, 0, 255), None)
    draw.rect(window_10, (255, 255, 255), (rectangle[0] + 75, rectangle[1], rectangle[2], rectangle[3]))
    rectangle = text_3.get_rect()
    window_10.blit(text_3, (75, 0))


def write_in_box(x, y, name):
    global font_2, length_x, length_y, turn
    if turn == 1:
        draw.rect(window_10, (0, 0, 255), (x * length_x + 2, y * length_y + 2, length_x-3, length_y-3))
    else:
        draw.rect(window_10, (255, 255, 0), (x * length_x + 2, y * length_y + 2, length_x-3, length_y-3))
    text = font_2.render(name, False, (0, 0, 25), None)
    text_rect = text.get_rect()
    text_rect.center = (x * length_x + length_x // 2, y * length_y + length_y // 2)
    window_10.blit(text, text_rect)


def receive_data():
    global turn, socks, running
    while True:
        try:
            data = socks.recv(9).decode()
            data = data.split()
            if data[0] == "turn":
                write_turn(players[int(data[1])])
                turn = 0
            elif data[0] == "@@you":
                write_turn("your turn")
                turn = 1
            elif data[0] == "ver":
                draw_vertical_line(int(data[1]), int(data[2]))
            elif data[0] == "hor":
                draw_horizontal_line(int(data[1]), int(data[2]))
            elif data[0] == "d":
                write_in_box(int(data[1]), int(data[2]), data[3])
            if data[0] == "quit":
                running = False
                break
        except IOError:
            final()
        except IndexError:
            final()


def round_of_pos(number):
    if number[-1] > 5:
        number[-2] += 1
    number[-1] = 0
    sum_1 = 0
    for i in number:
        sum_1 = sum_1 * 10 + i
    return sum_1


def get_position(position):
    global horizontal_visited, vertical_visited, length_x, length_y, socks
    if 765 > position[0] > length_x - 5 and 575 > position[1] > length_y - 5:
        x = round_of_pos([int(i) for i in str(position[0])])
        y = round_of_pos([int(i) for i in str(position[1])])
        temp_y = y // length_y
        temp_x = x // length_x
        if x % length_x == 0:  # vertical
            if temp_y in vertical_visited[temp_x]:
                return False, False
            draw_vertical_line(temp_x, temp_y)
            msg = "v " + str('%02d' % temp_x) + " " + str('%02d' % temp_y)
            socks.send(msg.encode())
        elif y % length_y == 0:
            if temp_y in horizontal_visited[temp_x]:
                return False, False
            draw_horizontal_line(temp_x, temp_y)
            msg = "h " + str('%02d' % temp_x) + " " + str('%02d' % temp_y)
            socks.send(msg.encode())
    return False, False


def game_initial():
    global horizontal_visited, vertical_visited, window_10, length_x, length_y, font_1, socks, running
    start_new_thread(receive_data, ())
    print("Game starts in 5 seconds")
    for i in range(5, 0, -1):
        print(i)
        sleep(1)
    window_10 = display.set_mode((830, 630))
    display.set_caption("Game")
    window_10.fill((255, 255, 255))
    for i in range(1, 20):
        horizontal_visited.append([])
        vertical_visited.append([])
        for j in range(1, 20):
            if i != 19 and j != 19:
                draw.rect(window_10, (0, 255, 255), (i * length_x + 2, j * length_y + 2, length_x - 4, length_y - 4))
            draw.circle(window_10, (255, 0, 0), (i * length_x, j * length_y), 3)
    text_2 = font_1.render("Turn:", False, (255, 0, 255), None)
    window_10.blit(text_2, (0, 0))
    while running:
        display.update()
        for even in event.get():
            if even.type == QUIT:
                running = False
            elif turn:
                if even.type == MOUSEBUTTONDOWN:
                    get_position(even.pos)
    socks.send("quit".encode())
    final()
    quit()


def print_players():
    global players
    data = socks.recv(1).decode()
    if data == "1":
        print("Added to room")
    else:
        print("Room is full")
        exit()
    data = socks.recv(1024).decode().split(',')
    number_of_players = int(data[0])
    for i in range(1, len(data)):
        if data[i] != '':
            players.append(data[i])
            print(str(data[i]) + " connected")
    remaining = number_of_players - len(data) + 1
    players.append("you")
    for i in range(remaining):
        data = socks.recv(30).decode()
        players.append(data)
        print(str(data) + " connected")
    game_initial()


def server_room(frame, window, number_of_players):
    number_of_players = number_of_players.get()
    frame.destroy()
    data = "C " + number_of_players
    socks.send(data.encode())
    print("YOur room number is:", socks.recv(6).decode())
    window.destroy()
    print_players()


def enter_room(frame, window, room_no):
    room_no = room_no.get()
    frame.destroy()
    data = "R " + room_no
    socks.send(data.encode())
    while True:
        try:
            data = socks.recv(1).decode()
            print(data)
            if data == "1":
                window.destroy()
                print_players()
            else:
                frame_3 = Frame(window)
                Label(frame_3, text="Entered wrong room number:").grid(row=0, column=0)
                room_no = Entry(frame_3)
                room_no.grid(row=0, column=1)
                Button(frame_3, text="enter",
                       command=lambda frame=frame_3, window=window, room_no=room_no: enter_room(frame, window,
                                                                                                room_no)).grid(
                    row=1, column=1)
                frame_3.grid(row=0, column=0)
                frame_3.mainloop()
        except error:
            pass
        except OSError:
            pass


def create_room(frame, window):
    frame.destroy()
    try:
        frame_3 = Frame(window)
    except error:
        print("frame error")
    Label(frame_3, text="Enter number of players that are playing").grid(row=0, column=0)
    number_of_players = Entry(frame_3)
    number_of_players.grid(row=0, column=1)
    Button(frame_3, text="Create",
           command=lambda frame=frame_3, window=window, number_of_players=number_of_players: server_room(frame, window,
                                                                                                         number_of_players)).grid(
        row=1, column=1)
    frame_3.grid(row=0, column=0)
    frame_3.mainloop()


def second(name, window, frame):
    global socks
    name = name.get()
    frame.destroy()
    socks.send(name.encode())
    frame_2 = Frame(window)
    Button(frame_2, text="Create Room", command=lambda frame=frame_2, window=window: create_room(frame, window)).grid(
        row=0, column=0)
    Label(frame_2, text="OR").grid(row=1, column=0)
    Label(frame_2, text="Enter room number").grid()
    room_no = Entry(frame_2)
    room_no.grid(row=2, column=1)
    Button(frame_2, text="Enter",
           command=lambda frame=frame_2, window=window, room_no=room_no: enter_room(frame_2, window, room_no)).grid(
        row=3, column=1)
    frame_2.grid(row=1, column=0)
    frame_2.mainloop()


def first():
    window = Tk()
    frame_1 = Frame(window)
    Label(frame_1, text="Enter your name(limit of 8 characters):").grid(row=0, column=0)
    name = Entry(frame_1)
    name.grid(row=0, column=1)
    Button(frame_1, text="Enter",
           command=lambda name=name, window=window, frame=frame_1: second(name, window, frame)).grid(row=1, column=1)
    frame_1.grid(row=0, column=0)
    frame_1.mainloop()


init()
running = True
rectangle = [0, 0, 0, 0]
font_1 = font.SysFont('freesansbold.ttf', 40)
font_2 = font.SysFont('freesansbold.ttf', 32)
players = []
turn = 0
length_x = 40
length_y = 30
horizontal_visited = [[]]
vertical_visited = [[]]
socks = socket()
host = "3.135.90.78"
port = 18930
socks.connect((host, port))
first()
