import random
import matplotlib.pyplot as plt

# Konstanta
CUSTOMER_ARRIVAL_RATE = 1/20  # Rata-rata kedatangan pelanggan per detik
SERVICE_TIME_SECONDS = [200, 600]  # Waktu layanan untuk setiap pelanggan (dalam detik)
NUMBER_OF_CASHIERS = 10  # Jumlah kasir
MAX_QUEUE_LENGTH = 5  # Maksimal panjang antrian per kasir
SIMULATION_TIME_SECONDS = 30 * 60  # Simulasi selama 30 menit
TIME_INTERVAL = 1  # Interval waktu untuk mencatat kepadatan antrian (dalam detik)

# Inisialisasi kasir
class Cashier:
    def __init__(self):
        self.queue = []
        self.current_customer = None
        self.remaining_service_time = 0
        self.customers_served = 0

    def add_customer(self, customer):
        if len(self.queue) < MAX_QUEUE_LENGTH:
            self.queue.append(customer)
            return True
        return False

    def serve_customer(self):
        if not self.current_customer and self.queue:
            self.current_customer = self.queue.pop(0)
            self.remaining_service_time = self.current_customer['service_time']

        if self.current_customer:
            self.remaining_service_time -= 1
            if self.remaining_service_time <= 0:
                self.customers_served += 1
                self.current_customer = None

cashiers = [Cashier() for _ in range(NUMBER_OF_CASHIERS)]
customers = []

# Fungsi untuk menambahkan pelanggan ke antrian kasir
def distribute_customer(customer, cashiers):
    empty_cashiers = [c for c in cashiers if not c.current_customer]
    
    if empty_cashiers:
        chosen_cashier = random.choice(empty_cashiers)
        chosen_cashier.add_customer(customer)
    else:
        shortest_queue = min(cashiers, key=lambda c: len(c.queue))
        shortest_queue.add_customer(customer)

# Data untuk plotting
time_points = []
queue_lengths = []

# Simulasi
current_time = 0
next_customer_time = random.expovariate(CUSTOMER_ARRIVAL_RATE)

while current_time < SIMULATION_TIME_SECONDS:
    if current_time >= next_customer_time:
        customer = {
            'arrival_time': current_time,
            'service_time': random.randint(SERVICE_TIME_SECONDS[0], SERVICE_TIME_SECONDS[1])
        }
        distribute_customer(customer, cashiers)
        next_customer_time = current_time + random.expovariate(CUSTOMER_ARRIVAL_RATE)

    for cashier in cashiers:
        cashier.serve_customer()

    if current_time % TIME_INTERVAL == 0:
        total_queue_length = sum(len(cashier.queue) for cashier in cashiers)
        time_points.append(current_time / 60)  # Konversi ke menit
        queue_lengths.append(total_queue_length)

    current_time += 1

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(time_points, queue_lengths, label='Total Queue Length')
plt.xlabel('Time (minutes)')
plt.ylabel('Queue Length')
plt.title('Queue Length Over Time')
plt.legend()
plt.grid(True)
plt.show()