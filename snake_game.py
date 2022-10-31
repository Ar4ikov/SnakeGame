import pygame
import random
import math
import pathlib

basement = pathlib.Path(__file__).parent.absolute()

SCREEN_SIDE = 720
CELL_SIZE = 20
FPS = 12

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class SnakeGame:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        pygame.init()
        pygame.display.set_caption('Snake Game')

        self.screen_side = math.ceil(SCREEN_SIDE / CELL_SIZE) * CELL_SIZE
        print(self.screen_side)

        self.screen = pygame.display.set_mode((self.screen_side, self.screen_side))
        self.clock = pygame.time.Clock()

        self.snake = Snake(self.screen_side, self.screen_side // 2, self.screen_side // 2)
        self.food = Food(self.screen_side)

        self.font = pygame.font.Font(str(basement / 'digital-7.ttf'), 50)
        self.eat_food_sound = pygame.mixer.Sound(str(basement / 'eat_food.ogg'))

        self.is_running = True

    @staticmethod
    def clean_up():
        pygame.quit()

    def main_loop(self):
        while self.is_running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.is_running = False

                    if event.key == pygame.K_LEFT:
                        self.snake.change_direction('left')

                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction('right')

                    elif event.key == pygame.K_UP:
                        self.snake.change_direction('up')

                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction('down')

            self.screen.fill(BLACK)

            self.snake.move()

            if self.snake.check_collision():
                self.snake.reset()

            if self.snake.check_eat(self.food):
                self.eat_food_sound.play()
                self.snake.grow()
                self.food.respawn(self.snake)

            if self.snake.check_win():
                self.snake.reset()
                self.food.respawn(self.snake)

            self.snake.draw(self.screen)
            self.food.draw(self.screen)

            score_text = self.font.render(str(len(self.snake.snake_body)), True, WHITE)
            self.screen.blit(score_text, (self.screen_side - 50, 10))

            pygame.display.flip()
            pygame.display.update()

        self.clean_up()


class Snake(pygame.sprite.Sprite):
    def __init__(self, screen_side, x, y):
        super().__init__()

        self.screen_side = screen_side
        self.x, self.y = x, y

        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill((0, 255, 0))

        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.snake_body = [self.rect.copy()]

        self.direction = 'down'
        self.speed = 1

        self.is_alive = True

    def move(self):
        # move every part of snake
        for i in range(len(self.snake_body) - 1, 0, -1):
            self.snake_body[i] = self.snake_body[i - 1].copy()

        # move head
        if self.direction == 'up':
            self.snake_body[0].y -= CELL_SIZE

        elif self.direction == 'down':
            self.snake_body[0].y += CELL_SIZE

        elif self.direction == 'left':
            self.snake_body[0].x -= CELL_SIZE

        elif self.direction == 'right':
            self.snake_body[0].x += CELL_SIZE

        self.rect = self.snake_body[0]

    def draw(self, screen):
        for rect in self.snake_body:
            pygame.draw.rect(screen, GREEN, rect, 5)

    def change_direction(self, direction):
        if direction == 'up' and self.direction != 'down':
            self.direction = 'up'

        elif direction == 'down' and self.direction != 'up':
            self.direction = 'down'

        elif direction == 'left' and self.direction != 'right':
            self.direction = 'left'

        elif direction == 'right' and self.direction != 'left':
            self.direction = 'right'

    def grow(self):
        self.snake_body.insert(0, self.snake_body[0])

    def check_collision(self):
        # teleport snake to other size if it goes out of bounds
        if self.rect.x > self.screen_side - CELL_SIZE:
            self.rect.x = 0

        elif self.rect.x < 0:
            self.rect.x = self.screen_side - CELL_SIZE

        elif self.rect.y > self.screen_side - CELL_SIZE:
            self.rect.y = 0

        elif self.rect.y < 0:
            self.rect.y = self.screen_side - CELL_SIZE

        # # check if snake collides with itself
        if self.rect in self.snake_body[1:]:
            self.is_alive = False
            return True

        return False

    def check_eat(self, food):
        if self.rect.colliderect(food.rect):
            return True
        else:
            return False

    def check_win(self):
        if len(self.snake_body) == (self.screen_side / CELL_SIZE) ** 2:
            return True
        else:
            return False

    def reset(self):
        self.rect = pygame.Rect(self.x, self.y, CELL_SIZE, CELL_SIZE)
        self.snake_body = [self.rect]
        self.direction = 'right'
        self.is_alive = True

    def get_head(self):
        return self.snake_body[-1]

    def get_body(self):
        return self.snake_body[:-1]


class Food(pygame.sprite.Sprite):
    def __init__(self, screen_side):
        super().__init__()

        self.screen_side = screen_side

        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill((255, 0, 0))

        self.rect = pygame.Rect(0, 0, CELL_SIZE, CELL_SIZE)
        self.rect.x = random.randint(0, self.screen_side // CELL_SIZE - 1) * CELL_SIZE
        self.rect.y = random.randint(0, self.screen_side // CELL_SIZE - 1) * CELL_SIZE

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

    def respawn(self, snake):
        # spawn food in empty space
        while True:
            self.rect.x = random.randint(0, self.screen_side // CELL_SIZE - 1) * CELL_SIZE
            self.rect.y = random.randint(0, self.screen_side // CELL_SIZE - 1) * CELL_SIZE

            if self.rect not in snake.get_body():
                break

    def get_pos(self):
        return self.rect.x, self.rect.y


# Run the game
if __name__ == "__main__":
    game = SnakeGame()
    game.main_loop()
