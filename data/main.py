import pygame
import random

# Konstanten
WIDTH, HEIGHT = 800, 600
BUS_SPEED = 5
PASSENGER_COUNT = 5

# Farben
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Initialisierung
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bus Simulator")
clock = pygame.time.Clock()


# Bus Klasse
class Bus:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 50, 30)
        self.passengers = 0

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= BUS_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += BUS_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= BUS_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += BUS_SPEED

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)


# Passagier Klasse
class Passenger:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH), random.randint(0, HEIGHT), 20, 20)

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)


# Haltestelle Klasse
class Stop:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH), random.randint(0, HEIGHT), 40, 40)

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


# Objekte erstellen
bus = Bus()
passengers = [Passenger() for _ in range(PASSENGER_COUNT)]
stop = Stop()

# Spielschleife
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    bus.move(keys)

    # Kollision mit Passagieren
    for passenger in passengers[:]:
        if bus.rect.colliderect(passenger.rect):
            passengers.remove(passenger)
            bus.passengers += 1

    # Kollision mit Haltestelle
    if bus.rect.colliderect(stop.rect) and bus.passengers > 0:
        bus.passengers = 0
        passengers = [Passenger() for _ in range(PASSENGER_COUNT)]

    # Zeichnen
    bus.draw()
    stop.draw()
    for passenger in passengers:
        passenger.draw()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
