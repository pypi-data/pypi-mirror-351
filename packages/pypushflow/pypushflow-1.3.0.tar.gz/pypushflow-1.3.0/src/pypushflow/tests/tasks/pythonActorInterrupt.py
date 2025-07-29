from time import sleep


def run(**kwargs):
    counter = kwargs.setdefault("counter", 0)
    print(f"SLEEP counter={counter} ...")
    sleep(kwargs.get("sleep_time", 0))
    print(f"DONE counter={counter}")
    kwargs["counter"] += 1
    return kwargs
