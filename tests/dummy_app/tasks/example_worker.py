from time import sleep

import dramatiq


@dramatiq.actor
def example_worker(msg):
    print(msg)
    sleep(15)
