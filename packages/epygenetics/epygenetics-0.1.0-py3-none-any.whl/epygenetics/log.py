import logging
import time

def start_logs():
    today = time.strftime("%Y-%m-%d")
    logging.basicConfig(
        filename=f"./logs/{today}_gen.log",
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def log_config(param:dict)->None:
    logging.info("new execution _________________________________________________________________________________________________")
    for key,val in param.items():
        logging.info(f"{key}:{val}")


def log_row(generation:int, metrics:dict) -> None:
    row:str=f"{str(generation)[:8]:<8}\t"
    for key,value in metrics.items():
        row = row + f"{str(value)[:8]:8}\t"
    logging.info(row)
