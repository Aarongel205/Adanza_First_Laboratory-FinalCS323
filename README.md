## Reflection Questions

### 1. How did you distribute orders among worker processes?
The master process (rank 0) generates between 5 and 8 orders, then sends each
order one at a time to a worker using a round-robin strategy:

dest = (idx % num_workers) + 1   # workers occupy ranks 1 … N
comm.send(order, dest=dest, tag=1)

After all orders are sent, the master sends a None sentinel value to every
worker so each one knows when to stop listening for new tasks.
