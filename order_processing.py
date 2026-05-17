import sys
import time
import random
import threading
from mpi4py import MPI

#MPI setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

#order catalogue
ITEMS = [
    "Laptop", "Keyboard", "Mouse", "Monitor", "Headphones",
    "USB Hub", "Webcam", "Desk Lamp", "Mechanical Keyboard", "Mousepad"
]

def generate_orders(n):
    return [
        {"order_id": f"ORD-{100 + i}", "item": random.choice(ITEMS)}
        for i in range(n)
    ]

def process_order(order, worker_rank):
    delay = round(random.uniform(0.3, 1.2), 2)
    time.sleep(delay)

    return {
        "order_id": order["order_id"],
        "item": order["item"],
        "status": "COMPLETED",
        "processed_by": f"Worker-{worker_rank}",
        "processing_time": delay,
    }