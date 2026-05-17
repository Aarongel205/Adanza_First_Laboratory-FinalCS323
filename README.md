## Reflection Questions

#### 1. How did you distribute orders among worker processes?
The master process (rank 0) generates between 5 and 8 orders, then sends each
order one at a time to a worker using a round-robin strategy:

dest = (idx % num_workers) + 1   # workers occupy ranks 1 … N
comm.send(order, dest=dest, tag=1)

After all orders are sent, the master sends a None sentinel value to every
worker so each one knows when to stop listening for new tasks.

#### 2. What happens if there are more orders than workers?
Because the assignment uses a pull-style loop, each worker keeps receiving tasks until it gets the sentinel value. This helps distribute the orders naturally even if there are more orders than workers. In a round-robin setup, some workers may receive more tasks than others. For example, if there are 7 orders and 3 workers, two workers will process 3 orders while one worker will process 2. No orders are missed because the master only sends the sentinel after all orders have already been assigned.

