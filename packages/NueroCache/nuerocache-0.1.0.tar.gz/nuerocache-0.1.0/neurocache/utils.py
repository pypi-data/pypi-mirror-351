\
import logging

def get_logger(name):
    # This is a basic placeholder. 
    # The config.py already sets up basicConfig, which might be sufficient.
    # If more complex logging configurations are needed per module, this can be expanded.
    return logging.getLogger(name)

# Example utility function (can be expanded)
def format_timestamp(dt_object):
    if dt_object:
        return dt_object.strftime("%Y-%m-%d %H:%M:%S UTC")
    return None
