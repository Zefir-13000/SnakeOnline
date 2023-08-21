from random import randrange

class Bot:
    def __init__(self,size,SIZE,id):
        self.id = id
        self.size = size
        self.SIZE = SIZE
        self.dx = 0
        self.dy = 0
        self.length = 1
        self.snake = [(randrange(1, size - 1, 1), randrange(1, size - 1, 1))]
        self.x,self.y = self.snake[-1]

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.snake.append((self.x, self.y))
        self.snake = self.snake[-self.length:]

    def check_die(self,size):
        if self.x < 0 or self.x > size - 1 or self.y < 0 or self.y > size - 1 or len(self.snake) != len(set(self.snake)):
            return False

    def check_apple(self,apple):
        if self.snake[-1] == apple:
            self.length += 1

    def find_best_move(self,snakes,apple,size):
        best_score = -10000
        best_move = (0,0)
        dx = 1
        dy = 0
        y,x = self.snake[-1][1],self.snake[-1][0]
        new_x = x + dx
        new_y = y + dy
        score = 0
        if (new_x,new_y) in set(self.snake):
            score = score - 1000
        else:
            for snakee in snakes:
                if (new_x,new_y) in snakee[-1]:
                    score -= 1000
        if new_x < 0 or new_x > size - 1 or new_y < 0 or new_y > size - 1:
            score = score - 100
        if apple[0] > self.snake[-1][0]:
            score += 10
        if score > best_score:
            best_move = (dx,dy)
            self.dx,self.dy = best_move
            best_score = score

        dx = -1
        dy = 0
        score = 0
        new_x = x + dx
        new_y = y + dy
        if (new_x,new_y) in set(self.snake):
            score = score - 1000
        else:
            for snakee in snakes:
                if (new_x,new_y) in snakee[-1]:
                    score -= 1000
        if new_x < 0 or new_x > size - 1 or new_y < 0 or new_y > size - 1:
            score = score - 1000
        if apple[0] < self.snake[-1][0]:
            score += 10
        if score > best_score:
            best_move = (dx,dy)
            self.dx,self.dy = best_move
            best_score = score

        dx = 0
        dy = 1
        score = 0
        new_x = x + dx
        new_y = y + dy
        if (new_x,new_y) in set(self.snake):
            score = score - 1000
        else:
            for snakee in snakes:
                if (new_x,new_y) in snakee[-1]:
                    score -= 1000
        if new_x < 0 or new_x > size - 1 or new_y < 0 or new_y > size - 1:
            score = score - 1000
        if apple[1] > self.snake[-1][1]:
            score += 10
        if score > best_score:
            best_move = (dx,dy)
            self.dx,self.dy = best_move
            best_score = score

        dx = 0
        dy = -1
        score = 0
        new_x = x + dx
        new_y = y + dy
        if (new_x,new_y) in set(self.snake):
            score = score - 1000
        else:
            for snakee in snakes:
                if (new_x,new_y) in snakee[-1]:
                    score -= 1000
        if new_x < 0 or new_x > size - 1 or new_y < 0 or new_y > size - 1:
            score = score - 1000
        if apple[1] < self.snake[-1][1]:
            score += 10
        if score > best_score:
            best_move = (dx,dy)
            self.dx,self.dy = best_move
            best_score = score
        return best_move
