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

    #distribute orders
    for idx, order in enumerate(orders):
        dest = (idx % num_workers) + 1
        comm.send(order, dest=dest, tag=1)
        print(f"  [DISPATCH] {order['order_id']} -> Worker-{dest}", flush=True)

    for w in range(1, size):
        comm.send(None, dest=w, tag=1)
    
    print(f"\n  All orders dispatched. Waiting for workers to finish...\n", flush=True)

    shared_orders = []
    lock = threading.Lock()

    #create result from workers
    for _ in range(num_orders):
        result = comm.recv(source=MPI.ANY_SOURCE, tag=2)
        with lock:
            shared_orders.append(result)
        print(
            f"  [RECEIVED] {result['order_id']} from {result['processed_by']} "
            f"in {result['processing_time']}s",
            flush=True,
        )
    #print final report
    print(f"\n{'='*60}", flush=True)
    print(f"  MASTER — Final Order Report ({len(shared_orders)} orders)", flush=True)
    print(f"{'='*60}", flush=True)
    for r in sorted(shared_orders, key=lambda x: x["order_id"]):
        print(
            f"  {r['order_id']} | {r['item']:<22} | "
            f"{r['status']} | {r['processed_by']} | "
            f"{r['processing_time']}s",
            flush=True,
        )
    print(f"{'='*60}\n", flush=True)
 
    if len(shared_orders) == num_orders:
        print("  [OK] All orders accounted for — output is consistent.\n", flush=True)
    else:
        print(
            f"  [WARN] Expected {num_orders} orders but got {len(shared_orders)}.\n",
            flush=True,
        )
else:
    print(f"  [Worker-{rank}] Ready and waiting for orders.", flush=True)

    while True:
        order = comm.recv(source=0, tag=1)
 
        if order is None:   # STOP sentinel
            break
 
        print(
            f"  [Worker-{rank}] Received {order['order_id']} ({order['item']}). Processing...",
            flush=True,
        )
 
        result = process_order(order, rank)
 
        print(
            f"  [Worker-{rank}] Done with {result['order_id']} in {result['processing_time']}s",
            flush=True,
        )
 
        # Send result back to master
        comm.send(result, dest=0, tag=2)

        print(f"  [Worker-{rank}] All tasks complete.", flush=True)
