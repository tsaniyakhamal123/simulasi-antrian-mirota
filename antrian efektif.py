import random
import pygame
import sys
from collections import deque

# Konstanta
CUSTOMER_ARRIVAL_RATE = 0.1  # Rata-rata kedatangan pelanggan per detik
SERVICE_TIME_SECONDS = [200, 600]  # Waktu layanan untuk setiap pelanggan (dalam detik)
NUMBER_OF_CASHIERS = 7  # Jumlah kasir
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
CUSTOMER_SPEED = 7  # Kecepatan gerak pelanggan
CASHIER_FRAME_WIDTH = 120  # Lebar frame kasir
CASHIER_FRAME_HEIGHT = 150  # Tinggi frame kasir
MAX_QUEUE_LENGTH = 5  # Maksimal panjang antrian per kasir
FPS = 60  # Frames per second

# Inisialisasi Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Simulasi Antrian Mirota UGM lantai 1')

# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRANSPARENT = (0, 0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load images
try:
    customer_img = pygame.image.load('personimg.png')
    cashier_img = pygame.image.load('kasirimg.jpg')
    background_img = pygame.image.load('ubinabu.jpg')
    print("Images loaded successfully")
except pygame.error as e:
    print(f"Error loading images: {e}")
    sys.exit()

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
        self.service_time = random.randint(SERVICE_TIME_SECONDS[0] * FPS, SERVICE_TIME_SECONDS[1] * FPS)
        self.x, self.y = 50, SCREEN_HEIGHT - 50  # Posisi awal pelanggan
        self.target_x, self.target_y = target_pos
        self.in_queue = False  # Apakah pelanggan sudah berada di antrian
        self.leaving = False  # Apakah pelanggan sedang meninggalkan kasir

    def move(self):
        if not self.in_queue:
            if abs(self.x - self.target_x) > CUSTOMER_SPEED:
                self.x += CUSTOMER_SPEED if self.x < self.target_x else -CUSTOMER_SPEED
            if abs(self.y - self.target_y) > CUSTOMER_SPEED:
                self.y += CUSTOMER_SPEED if self.y < self.target_y else -CUSTOMER_SPEED

            if abs(self.x - self.target_x) <= CUSTOMER_SPEED and abs(self.y - self.target_y) <= CUSTOMER_SPEED:
                self.in_queue = True
        elif self.leaving:
            self.y -= CUSTOMER_SPEED  # Pelanggan bergerak ke atas saat meninggalkan kasir
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
        self.customers_served = 0  # Jumlah pelanggan yang telah dilayani
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


def calculate_cashier_positions(number_of_cashiers, screen_width, screen_height, cashier_frame_width, cashier_frame_height):
    # Calculate number of rows and columns
    cols = 5
    rows = (number_of_cashiers + cols - 1) // cols
    
    # Calculate starting positions
    start_x = (screen_width - cols * cashier_frame_width - (cols - 1) * 40) // 2
    start_y = (screen_height - rows * cashier_frame_height - (rows - 1) * 100) // 2

    positions = []
    for row in range(rows):
        for col in range(cols):
            if len(positions) < number_of_cashiers:
                x = start_x + col * (cashier_frame_width + 40)
                y = start_y + row * (cashier_frame_height + 100)
                positions.append((x, y))

    return positions

def main():
    clock = pygame.time.Clock()
    cashier_positions = calculate_cashier_positions(NUMBER_OF_CASHIERS, SCREEN_WIDTH, SCREEN_HEIGHT, CASHIER_FRAME_WIDTH, CASHIER_FRAME_HEIGHT)
    cashiers = [Cashier(i, pos[0], pos[1]) for i, pos in enumerate(cashier_positions)]
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
        clock.tick(FPS)

if __name__ == '__main__':
    main()