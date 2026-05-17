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

def process_order(order, worker_rank):