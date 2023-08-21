import socket,time,pygame
from random import randrange,randint
from bot import Bot
from _thread import *

server_config = open("SERVER CONFIG.txt","r")
for line in server_config:
    t = line.replace(" ","")
    linee = t.strip().split("=")
    if linee[0].strip() == "HOST":
        HOST = linee[-1]
    if linee[0].strip() == "PORT":
        PORT = int(linee[-1])
    if linee[0].strip() == "PLAYERS":
        PLAYERS = int(linee[-1])
    if linee[0].strip() == "SIZE":
        SIZE = int(linee[-1])
    if linee[0].strip() == "SIZE_snake":
        SIZE_snake = int(linee[-1])
    if linee[0].strip() == "SIZE_MAP":
        SIZE_MAP = int(linee[-1])
    if linee[0].strip() == "LIMIT_APPLES":
        LIMIT_APPLES = int(linee[-1])
    if linee[0].strip() == "BOTS":
        BOTS = int(linee[-1])
    if linee[0].strip() == "BOTS_RESPAWN_TIME":
        BOTS_RESPAWN_TIME = int(linee[-1])
    if linee[0].strip() == "START_FPS":
        start_fps = int(linee[-1])
    if linee[0].strip() == "EXTRA_MODE":
        if linee[-1].lower() == "true":
            EXTRA_MODE = True
        else:
            EXTRA_MODE = False

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = HOST or "Error"
port = PORT or "Error"
players = PLAYERS - 1 or "Error"
size = SIZE or "Error"
size_map = SIZE_MAP or "Error"
limit_apples = LIMIT_APPLES or "Error"
bots = BOTS or 0
BOTS_RESPAWN_TIME = BOTS_RESPAWN_TIME or "Error"
pos = []
botS = []
if bots > 0:
    id_bot = players + 10
    for i in range(bots):
        botS.append(Bot(size_map,SIZE_snake,id_bot))
        id_bot+=1
id = 1
UsingIds = []

apples = []
one_use_apples = []

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen(players)

print("Waiting for a connection")

def spawn_apples():
    if len(apples) > limit_apples:
        if len(apples) > limit_apples:
            del apples[limit_apples-1:]
    else:
        for _ in range(limit_apples):
            x1,y1 = randrange(1, size_map - 1, 1),randrange(1, size_map - 1, 1)
            if len(apples) > 0:
                if (x1,y1) not in apples:
                    apples.append((x1,y1))
                else:
                    x1,y1 = randrange(1, size_map - 1, 1),randrange(1, size_map - 1, 1)
            else:
                apples.append((x1,y1))

spawn_apples()

def Bot_func(bot):
    pos.append([bot.id,[(bot.x,bot.y)]])
    fps = int(start_fps)
    
    if len(one_use_apples) > 0:
        if len(one_use_apples) == 1:
            current_apple = 0
        else:
            current_apple = randint(0,len(one_use_apples)-1)
    else:
        current_apple = randint(0,limit_apples-1)
    clock = pygame.time.Clock()
    while True:
        clock.tick(fps)
        if EXTRA_MODE == True:
            fps = start_fps + (bot.length - 1)
        if len(one_use_apples) > 0:
            try:
                bot.find_best_move(pos,one_use_apples[current_apple],size_map)
            except:
                bot.find_best_move(pos,(0,0),size_map)
        else:
            try:
                bot.find_best_move(pos,apples[current_apple],size_map)
            except:
                bot.find_best_move(pos,apples[0],size_map)

        bot.move()
        if bot.x < 0 or bot.x > size_map - 1 or bot.y < 0 or bot.y > size_map - 1 or len(bot.snake) != len(set(bot.snake)):
            for i in pos:
                d = i
                if d[0] == bot.id:
                    whe = 1
                    snake = d[-1]
                    for _ in range(int(len(d[-1])/3)):
                        if snake[-whe][0] <= 0 or snake[-whe][1] <= 0 or snake[-whe][0] >= size_map or snake[-whe][1] >= size_map:
                            pass
                        else:
                            one_use_apples.append(snake[-whe])
                        whe += 1
                    pos.remove(i)

                    start_new_thread(re_spawn_bot, (bot,bot.id,))
                    return False
                
        for enemy in pos:
            id2 = enemy[0]
            if int(id2) == int(bot.id):
                pass
            else:
                for (x,y) in enemy[-1]:
                    if bot.snake[-1] == (x,y):
                        for i in pos:
                            d = i
                            if d[0] == bot.id:
                                whe = 1
                                snake = d[-1]
                                for _ in range(int(len(d[-1])/3)):
                                    if snake[-whe][0] <= 0 or snake[-whe][1] <= 0 or snake[-whe][0] >= size_map or snake[-whe][1] >= size_map:
                                        pass
                                    else:
                                        if snake[-whe][0] > 0 and snake[-whe][0] < size_map and snake[-whe][1] > 0 and snake[-whe][1] < size_map:
                                            one_use_apples.append(snake[-whe])
                                    whe+=1
                                pos.remove(i)

                                start_new_thread(re_spawn_bot, (bot,bot.id,))
                                return False
                            
        for apple in apples:
            bot.check_apple(apple)

        if bot.snake[-1] in apples:
            ind = apples.index(bot.snake[-1])
            apples[ind] = randrange(1, size_map - 1, 1),randrange(1, size_map - 1, 1)
            if len(one_use_apples) > 0:
                if len(one_use_apples) == 1:
                    current_apple = 0
                else:
                    current_apple = randint(0,len(one_use_apples)-1)
            else:
                current_apple = randint(0,limit_apples-1)

        for apple in one_use_apples:
            bot.check_apple(apple)

        if bot.snake[-1] in one_use_apples:
            ind = one_use_apples.index(bot.snake[-1])
            one_use_apples.remove(bot.snake[-1])
            if len(one_use_apples) > 0:
                if len(one_use_apples) == 1:
                    current_apple = 0
                else:
                    current_apple = randint(0,len(one_use_apples)-1)
            else:
                current_apple = randint(0,limit_apples-1)

        for i in pos:
            ind = pos.index(i)
            if int(bot.id) == int(i[0]):
                pos[ind] = bot.id,bot.snake

def re_spawn_bot(bot,id):
    time.sleep(BOTS_RESPAWN_TIME)
    new_bot = Bot(size_map,SIZE_snake,id)
    start_new_thread(Bot_func,(new_bot,))

def find_XY_for_snake():
    xq,yq = randrange(1, size_map - 1, 1),randrange(1, size_map - 1, 1)
    if len(pos) > 0:
        for i in range(len(pos)):
            d = pos[i][-1]
            xx,yy = (d[-1][0],d[-1][1])
            if (xq,yq) != (xx,yy):
                if len(apples) > 0:
                    for apple in apples:
                        if (xq,yq) != apple:
                            return xq,yq
                else:
                    return xq,yq

            else:
                xq,yq = randrange(1, size_map - 1, 1),randrange(1, size_map - 1, 1)
                continue
    else:
        if len(apples) > 0:
            for apple in apples:
                if (xq,yq) != apple:
                    return xq,yq
    return xq,yq



def Game(conn,id):
    client = conn
    length_snake = 1
    hod = 0
    run = True
    while run:
        if hod > players+5:
            client.sendall("Sorry, server is full\n".encode("utf-8"))
            client.close()
        elif id in UsingIds:
            id += 1
            hod += 1
            continue
        elif id > players:
            id = 0
            hod += 1
            continue
        else:
            UsingIds.append(id)
            run = False

    x,y = find_XY_for_snake()


    conn.sendall(f"{id}:{x}:{y}:{apples}:{SIZE_snake}:{size_map}:{SIZE}:{start_fps}:{EXTRA_MODE}\n".encode("utf-8"))
    pos.append([id,[(x,y)]])

    runG = True
    try:
        while runG:
            try:
                recved = client.recv(10048).decode("utf-8").strip()
                if not recved:
                    client.close()
                    for i in range(len(pos)):
                        d = pos[i]
                        idd2 = d[0]
                        if id == idd2:
                            whe = 1
                            snake = d[-1]
                            for _ in range(int(len(d[-1])/3)):
                                if snake[-whe][0] <= 0 or snake[-whe][1] <= 0 or snake[-whe][0] >= size_map or snake[-whe][1] >= size_map:
                                    pass
                                else:
                                    if snake[-whe][0] > 0 and snake[-whe][0] < size_map and snake[-whe][1] > 0 and snake[-whe][1] < size_map:
                                        one_use_apples.append(snake[-whe])
                                whe+=1
                            del pos[i]
                data = recved.split(":")
                idd = data[0]

                for i in range(len(pos)):
                    d = pos[i]
                    idd2 = d[0]
                    if int(idd) == idd2:
                        pos[i] = int(data[0]),eval(data[1])
                        snake_player = eval(data[1])
                        if snake_player[-1] in apples:
                            ind = apples.index(snake_player[-1])
                            apples[ind] = randrange(1, size_map - 1, 1),randrange(1, size_map - 1, 1)
                            length_snake += 1
                        if snake_player[-1] in one_use_apples:
                            one_use_apples.remove(snake_player[-1])
                            length_snake += 1


                client.sendall(f"{pos}:{list(set(apples))}:{one_use_apples}:{length_snake}\n".encode("utf-8"))
            except:
                break

    finally:
        UsingIds.remove(id)
        print(f"Disconnected {id}, Total connects: {len(UsingIds)}, Ids = {UsingIds}")



if len(botS) > 0:
    for bot in botS:
        start_new_thread(Bot_func,(bot,))

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    start_new_thread(Game, (conn,id,))
    id += 1
