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

#Master
if rank == 0:
    num_workers = size - 1
    if num_workers < 1:
        print("ERROR: Need at least 2 MPI processes (1 master + 1 worker).", flush=True)
        comm.Abort(1)
 
    num_orders = random.randint(5, 8)
    orders = generate_orders(num_orders)
 
    print(f"\n{'='*60}", flush=True)
    print(f"  MASTER (rank 0) — generated {num_orders} orders", flush=True)
    print(f"  Workers available: {num_workers}", flush=True)
    print(f"{'='*60}", flush=True)

    for o in orders:
        print(f"  [ORDER] {o['order_id']} -> {o['item']}", flush=True)
    print(f"{'='*60}\n", flush=True)

    for idx, order in enumerate(orders):
        dest = (idx % num_workers) + 1
        comm.send(order, dest=dest, tag=1)
        print(f"  [DISPATCH] {order['order_id']} -> Worker-{dest}", flush=True)