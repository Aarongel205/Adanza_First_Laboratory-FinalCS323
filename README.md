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

#### 3. How did processing delays affect the order completion?
Each worker uses time.sleep(random.uniform(0.3, 1.2)) before saving its result. Since the workers run at the same time, some workers finish faster than others depending on the random delay. Workers with shorter delays can write to the shared memory first, while workers with longer delays finish later. Because of this, the completed orders in shared_orders are not stored in the same order they were assigned. To make the final output easier to read, the master process sorts the completed orders by order_id before printing the report.

#### 4. How did you implement shared memory, and where was it initialized?
A multiprocessing.Manager object was created at module level, before the
MPI work begins, so the manager process is already running when both the master
and workers start executing:

pythonmanager = Manager()
shared_orders = manager.list()

manager.list() returns a proxy object that all processes in the same Python
interpreter tree can read and write through network sockets managed by the
Manager server process. Workers call shared_orders.append(result) inside
their processing loop; the master reads the final list after the MPI barrier
synchronises all ranks.


