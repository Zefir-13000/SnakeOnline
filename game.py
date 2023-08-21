import socket, pygame

pygame.init()

game_config = open("CLIENT_CONFIG.txt","r")
for line in game_config:
    linee = line.strip().split("=")
    if linee[0].strip() == "HOST":
        HOST = linee[-1].strip()
    if linee[0].strip() == "PORT":
        PORT = int(linee[-1].strip())
    if linee[0].strip() == "RES":
        RES = int(linee[-1].strip())


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = HOST or "Error"
        self.port = PORT or "Error"
        self.addr = (self.host, self.port)
        self.id,self.x,self.y,self.apples,self.SIZE,self.size_map,self.size,self.start_fps,self.extra_mode = self.connect()
        self.SIZE = int(self.SIZE)
        self.size = int(self.size)
        self.size_map = int(self.size_map)
        self.start_fps = int(self.start_fps)

    def connect(self):
        self.client.connect(self.addr)
        data = self.client.recv(5048).decode("utf-8").rstrip()
        data = data.split(":")
        return data[0],data[1],data[2],eval(data[3]),data[4],data[5],data[6],data[7],data[8]

    def send(self, data):
        try:
            self.client.sendall(data.encode("utf-8"))
            reply = self.client.recv(10048).decode("utf-8").rstrip()
            rep = reply.split(":")
            return rep[0],rep[1],rep[2],rep[3]
        except socket.error as e:
            return str(e)

class Player:
    def __init__(self,snake,SIZE_Snake):
        self.score_apple = 0
        self.SIZE_Snake = SIZE_Snake
        self.dx = 0
        self.dy = 0
        self.length = 1
        self.snake = snake
        self.x,self.y = self.snake[-1]

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.snake.append((self.x, self.y))
        self.snake = self.snake[-self.length:]

    def check_die(self,size):
        if self.x < 0 or self.x > size - 1 or self.y < 0 or self.y > size - 1 or len(self.snake) != len(set(self.snake)):
            del self.snake

class Game:
    def __init__(self, w, h):
        self.net = Network()
        self.fps = int(self.net.start_fps)
        self.size = int(self.net.size)
        self.size_map = int(self.net.size_map)
        self.width = w
        self.height = h
        self.player = Player([(int(self.net.x), int(self.net.y))],self.net.SIZE)
        self.snake = []
        self.players = []
        self.ouapples = []
        self.apples = []
        self.apples.append(self.net.apples)
        self.dirs = {'W': True, 'S': True, 'A': True, 'D': True, }
        self.screen = pygame.display.set_mode((w,h))
        pygame.display.set_caption("Snakes!!!")

    def run(self):
        clock = pygame.time.Clock()
        run = True
        while run:
            clock.tick(self.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_RIGHT]:
                if self.dirs["D"]:
                    self.player.dx,self.player.dy = 1,0
                    self.dirs = {'W': True, 'S': True, 'A': False, 'D': True, }

            elif keys[pygame.K_LEFT]:
                if self.dirs["A"]:
                    self.player.dx,self.player.dy = -1,0
                    self.dirs = {'W': True, 'S': True, 'A': True, 'D': False, }

            elif keys[pygame.K_UP]:
                if self.dirs["W"]:
                    self.player.dx,self.player.dy = 0,-1
                    self.dirs = {'W': True, 'S': False, 'A': True, 'D': True, }

            elif keys[pygame.K_DOWN]:
                if self.dirs["S"]:
                    self.player.dx,self.player.dy = 0,1
                    self.dirs = {'W': False, 'S': True, 'A': True, 'D': True, }


            self.player.move()
            self.player.check_die(self.size_map)

            self.players = []
            self.apples = []

            data = str(self.net.id) + ":" + str(self.player.snake)
            pos_players,apples,ouapples,length_snake=self.send_data(data)
            self.player.length = int(length_snake)
            if eval(self.net.extra_mode) == True:
                self.fps = self.net.start_fps + (self.player.length - 1)
            self.apples = eval(apples)
            self.ouapples = eval(ouapples)

            pos_players1,apples1,ouapples1 = self.camera(eval(pos_players),eval(apples),eval(ouapples))
            for player in pos_players1:
                idg = player[0]
                if idg == int(self.net.id):
                    self.snake = player[1]
            self.screen.fill(pygame.Color('black'))

            for player in pos_players1:
                idg = player[0]
                if idg == int(self.net.id):
                    self.draw_player(player,self.screen)
                    self.checkk_die(player,idg)
                else:
                    self.draw_enemies(player,self.screen)
                    self.checkk_die(player,idg)

            self.draw_walls(self.screen)
            self.draw_apples(apples1)
            self.draw_apples(ouapples1)
            self.draw_score()

            pygame.display.update()

    def camera(self,poss,apples,ouapples):
        res_snake = []
        res_apples = []
        res_ouapples = []

        target_x = round(self.size/2)
        target_y = round(self.size/2)

        for player in poss:
            id = player[0]
            snake = player[1]
            new_snake = []
            for el in snake:
                new_snake.append(list(el))
            res_snake.append([id,new_snake])

        for apple in apples:
            res_apples.append(list(apple))
        for apple in ouapples:
            res_ouapples.append(list(apple))

        self_snake = self.player.snake
        if self_snake[-1][0] < target_x:
            if self_snake[-1][1] > target_y:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[0] += target_x-self_snake[-1][0]
                        part[1] -= self_snake[-1][1]-target_y

                for apple in res_apples:
                    apple[0] += target_x-self_snake[-1][0]
                    apple[1] -= self_snake[-1][1]-target_y
                for apple in res_ouapples:
                    apple[0] += target_x-self_snake[-1][0]
                    apple[1] -= self_snake[-1][1]-target_y

            elif self_snake[-1][1] < target_y:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[0] += target_x-self_snake[-1][0]
                        part[1] += target_y-self_snake[-1][1]

                for apple in res_apples:
                    apple[0] += target_x-self_snake[-1][0]
                    apple[1] += target_y-self_snake[-1][1]
                for apple in res_ouapples:
                    apple[0] += target_x-self_snake[-1][0]
                    apple[1] += target_y-self_snake[-1][1]

            else:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[0] += target_x-self_snake[-1][0]
                for apple in res_apples:
                    apple[0] += target_x-self_snake[-1][0]
                for apple in res_ouapples:
                    apple[0] += target_x-self_snake[-1][0]

        elif self_snake[-1][0] > target_x:
            if self_snake[-1][1] > target_y:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[0] -= self_snake[-1][0]-target_x
                        part[1] -= self_snake[-1][1]-target_y
                for apple in res_apples:
                    apple[0] -= self_snake[-1][0]-target_x
                    apple[1] -= self_snake[-1][1]-target_y
                for apple in res_ouapples:
                    apple[0] -= self_snake[-1][0]-target_x
                    apple[1] -= self_snake[-1][1]-target_y

            elif self_snake[-1][1] < target_y:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[0] -= self_snake[-1][0]-target_x
                        part[1] += target_y-self_snake[-1][1]
                for apple in res_apples:
                    apple[0] -= self_snake[-1][0]-target_x
                    apple[1] += target_y-self_snake[-1][1]
                for apple in res_ouapples:
                    apple[0] -= self_snake[-1][0]-target_x
                    apple[1] += target_y-self_snake[-1][1]

            else:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[0] -= self_snake[-1][0]-target_x
                for apple in res_apples:
                    apple[0] -= self_snake[-1][0]-target_x
                for apple in res_ouapples:
                    apple[0] -= self_snake[-1][0]-target_x

        else:
            if self_snake[-1][1] > target_y:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[1] -= self_snake[-1][1]-target_y
                for apple in res_apples:
                    apple[1] -= self_snake[-1][1]-target_y
                for apple in res_ouapples:
                    apple[1] -= self_snake[-1][1]-target_y

            elif self_snake[-1][1] < target_y:
                for snake in res_snake:
                    for part in snake[-1]:
                        part[1] -= self_snake[-1][1]-target_y
                for apple in res_apples:
                    apple[1] -= self_snake[-1][1]-target_y
                for apple in res_ouapples:
                    apple[1] -= self_snake[-1][1]-target_y
            else:
                pass

        return res_snake,res_apples,res_ouapples

    def draw_score(self):
        font = pygame.font.Font(None, 20)
        label = font.render(f"Score: {self.player.length -1}",True,(0,255,255))
        self.screen.blit(label, (10, 10))

    def draw_player(self,snake,sc):
        for i,j in snake[-1]:
            pygame.draw.rect(sc, pygame.Color('green'),(i*self.net.SIZE, j*self.net.SIZE, self.net.SIZE,self.net.SIZE))
        pygame.draw.rect(sc, pygame.Color('yellow'), (snake[-1][-1][0]*self.net.SIZE,snake[-1][-1][1]*self.net.SIZE,self.net.SIZE,self.net.SIZE))

    def draw_enemies(self,enemy,sc):
        for i,j in enemy[-1]:
            pygame.draw.rect(sc, pygame.Color('red'),(i*self.net.SIZE, j*self.net.SIZE, self.net.SIZE,self.net.SIZE))
        pygame.draw.rect(sc, pygame.Color('orange'), (enemy[-1][-1][0]*self.net.SIZE,enemy[-1][-1][1]*self.net.SIZE,self.net.SIZE,self.net.SIZE))

    def draw_walls(self,sc):
        if self.player.snake[-1][0] < round(self.net.size/2):
            for i in range(self.net.size_map+3):
                pygame.draw.rect(sc, pygame.Color('red'),((11-self.player.snake[-1][0])*self.net.SIZE, i*self.net.SIZE, self.net.SIZE,self.net.SIZE))
        if self.player.snake[-1][1] < round(self.net.size/2):
            for i in range(self.net.size_map+3):
                pygame.draw.rect(sc, pygame.Color('red'),(i*self.net.SIZE, (11-self.player.snake[-1][1])*self.net.SIZE, self.net.SIZE,self.net.SIZE))
        if self.player.snake[-1][1] > self.net.size_map-13:
            for i in range(self.net.size_map+3):
                pygame.draw.rect(sc, pygame.Color('red'),(i*self.net.SIZE, (self.net.size_map-self.player.snake[-1][1]+12)*self.net.SIZE, self.net.SIZE,self.net.SIZE))
        if self.player.snake[-1][0] > self.net.size_map-13:
            for i in range(self.net.size_map+3):
                pygame.draw.rect(sc, pygame.Color('red'),((self.net.size_map-self.player.snake[-1][0]+12)*self.net.SIZE, i*self.net.SIZE, self.net.SIZE,self.net.SIZE))

    def draw_apples(self,apples):
        for apple in apples:
            pygame.draw.rect(self.screen,pygame.Color('blue'),(apple[0]*self.net.SIZE, apple[1]*self.net.SIZE, self.net.SIZE,self.net.SIZE))

    def checkk_die(self,enemy,id):
        if int(id) == int(self.net.id):
            return None
        else:
            try:
                for (x,y) in enemy[-1]:
                    if tuple(self.snake[-1]) == (x,y):
                        try:
                            pos_players,apples,ouapples,length_snake=self.send_data(str(self.net.id) + ":" + str(self.player.snake))
                            self.ouapples = eval(ouapples)
                            self.die()
                        except:
                            self.net.client.close()
            except:
                pass

    def die(self):
        self.net.client.close()

    def send_data(self,data):
        reply,apples,ouapples,length_snake = self.net.send(data)
        return reply.rstrip(),apples.rstrip(),ouapples.rstrip(),length_snake.rstrip()


if __name__ == '__main__':
    game = Game(RES,RES)
    game.run()
