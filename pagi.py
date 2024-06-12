import random
import pygame
import sys
from collections import deque

# Constants
CUSTOMER_ARRIVAL_RATE = 1/20  # Average customer arrival rate per second
SERVICE_TIME = [200, 600]  # Service time for each customer (in frames)
NUMBER_OF_CASHIERS = 10  # Total number of cashiers
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
CUSTOMER_SPEED = 7  # Customer movement speed
CASHIER_FRAME_WIDTH = 300
CASHIER_FRAME_HEIGHT = 300
MAX_QUEUE_LENGTH = 5 # Maximum queue length per cashier

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Queue Simulation at Mirota UGM 1st Floor at Night')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load images
customer_img = pygame.image.load('personimg.png')
cashier_img = pygame.image.load('kasirimg.jpg')
background_img = pygame.image.load('ubinabu.jpg')

# Resize images
CUSTOMER_SIZE = (40, 40)
CASHIER_SIZE = (50, 50)
customer_img = pygame.transform.scale(customer_img, CUSTOMER_SIZE).convert_alpha()
cashier_img = pygame.transform.scale(cashier_img, CASHIER_SIZE).convert_alpha()
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Font
font = pygame.font.Font(None, 36)

class Customer:
    def __init__(self, arrival_time, target_pos):
        self.arrival_time = arrival_time
        self.service_time = random.randint(SERVICE_TIME[0], SERVICE_TIME[1])
        self.x, self.y = 50, SCREEN_HEIGHT - 50  # Initial position of the customer
        self.target_x, self.target_y = target_pos
        self.in_queue = False  # Whether the customer is in queue
        self.leaving = False  # Whether the customer is leaving the cashier

    def move(self):
        if not self.in_queue:
            if abs(self.x - self.target_x) > CUSTOMER_SPEED:
                self.x += CUSTOMER_SPEED if self.x < self.target_x else -CUSTOMER_SPEED
            if abs(self.y - self.target_y) > CUSTOMER_SPEED:
                self.y += CUSTOMER_SPEED if self.y < self.target_y else -CUSTOMER_SPEED

            if abs(self.x - self.target_x) <= CUSTOMER_SPEED and abs(self.y - self.target_y) <= CUSTOMER_SPEED:
                self.in_queue = True
        elif self.leaving:
            self.y -= CUSTOMER_SPEED  # Customer moves up when leaving the cashier
        else:
            if abs(self.y - self.target_y) > CUSTOMER_SPEED:
                self.y += CUSTOMER_SPEED if self.y < self.target_y else -CUSTOMER_SPEED

    def draw(self, screen):
        screen.blit(customer_img, (self.x, self.y))

class Cashier:
    def __init__(self, id, base_x, base_y):
        self.id = id
        self.queue = deque()
        self.current_customer = None
        self.remaining_service_time = 0
        self.customers_served = 0  # Number of customers served
        self.base_x = base_x
        self.base_y = base_y

    def add_customer(self, customer):
        if len(self.queue) < MAX_QUEUE_LENGTH:
            customer.target_x = self.base_x + 25  # Adjusting target position
            customer.target_y = self.base_y + 50 + len(self.queue) * 35
            self.queue.append(customer)
            return True
        return False

    def serve_customer(self):
        if not self.current_customer and self.queue:
            self.current_customer = self.queue.popleft()
            self.remaining_service_time = self.current_customer.service_time
        
        if self.current_customer:
            self.remaining_service_time -= 1
            if self.remaining_service_time <= 0:
                self.customers_served += 1  # Increment the served customers count
                self.current_customer.leaving = True
                self.current_customer = None

        # Move customers in the queue forward if the current customer has left
        for i, customer in enumerate(self.queue):
            customer.target_y = self.base_y + 50 + i * 35

    def draw(self, screen):
        # Create a transparent surface for the frame
        frame_surface = pygame.Surface((CASHIER_FRAME_WIDTH, CASHIER_FRAME_HEIGHT), pygame.SRCALPHA)
        frame_surface.fill(TRANSPARENT)
        pygame.draw.rect(frame_surface, WHITE, frame_surface.get_rect(), 2)
        screen.blit(frame_surface, (self.base_x - 10, self.base_y - 10))
        
        screen.blit(cashier_img, (self.base_x, self.base_y))
        queue_text = font.render(f'Queue: {len(self.queue)}', True, BLACK)
        screen.blit(queue_text, (self.base_x, self.base_y + 60))
        served_text = font.render(f'Served: {self.customers_served}', True, BLACK)
        screen.blit(served_text, (self.base_x, self.base_y + 90))

        for customer in self.queue:
            customer.move()
            customer.draw(screen)

def distribute_customer(customer, cashiers):
    # List kasir yang kosong
    empty_cashiers = [c for c in cashiers if not c.current_customer]
    
    if empty_cashiers:
        # Jika ada kasir kosong, tempatkan pelanggan di salah satunya
        chosen_cashier = random.choice(empty_cashiers)
        chosen_cashier.add_customer(customer)
        return True
    else:
        # Jika semua kasir sedang melayani pelanggan, pilih kasir dengan antrian terpendek
        shortest_queue = min(cashiers, key=lambda c: len(c.queue))
        return shortest_queue.add_customer(customer)

def main():
    clock = pygame.time.Clock()

    # Set up cashiers with new vertical positions
    cashiers = []
    frame_positions = [(1000, 50), (700, 50), (400, 50), (100, 50)]  # Right to left positions
    
    for frame_id, (frame_x, frame_y) in enumerate(frame_positions):
        num_cashiers = frame_id + 1
        for i in range(num_cashiers):
            cashier_x = frame_x
            cashier_y =  frame_y + i * (CASHIER_FRAME_HEIGHT // num_cashiers) * 1.5
            cashiers.append(Cashier(len(cashiers), cashier_x, cashier_y))

    customers = []

    next_customer_time = pygame.time.get_ticks() + random.expovariate(CUSTOMER_ARRIVAL_RATE) * 1000
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = pygame.time.get_ticks()

        if current_time >= next_customer_time:
            customer = Customer(current_time, (0, 0))
            if distribute_customer(customer, cashiers):
                customers.append(customer)
            next_customer_time = current_time + random.expovariate(CUSTOMER_ARRIVAL_RATE) * 1000
        
        # Draw background
        screen.blit(background_img, (0, 0))

        for cashier in cashiers:
            cashier.serve_customer()
            cashier.draw(screen)

        for customer in customers:
            customer.move()
            customer.draw(screen)

        # Remove customers that have left the screen
        customers = [customer for customer in customers if customer.y + CUSTOMER_SIZE[1] > 0]

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    main()
