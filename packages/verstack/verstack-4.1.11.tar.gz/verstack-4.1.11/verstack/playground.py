import pandas as pd

# make classification
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=1000, n_features=100, n_informative=10, random_state=42)
X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
y = pd.Series(y, name='target')

from verstack import LGBMTuner

# timer
import time
start = time.time()

tuner = LGBMTuner(
    objective = 'binary', 
    metric='auc', 
    device_type='gpu', 
    trials=10)

tuner.fit(X, y)
stop = time.time()
print(f"Time taken: {stop - start} seconds")

import lightgbm as lgb
import time

from verstack.tools import timer

import time
import functools

def timer(func):
    """
    Decorator that times the execution of a function and prints the duration
    in a user-friendly format.
    
    Format rules:
    - Under 1 minute: prints time in seconds
    - 1-60 minutes: prints time in minutes and seconds
    - Over 60 minutes: prints time in hours, minutes, and seconds
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'verbose' in kwargs:
            verbose = kwargs['verbose']
        elif args:
            try:
                verbose = args[0].verbose
            except AttributeError:
                verbose = True
        start_time = time.perf_counter()
        # Execute the function
        result = func(*args, **kwargs)
        
        # Calculate elapsed time
        elapsed_seconds = time.perf_counter() - start_time
        
        # Format based on duration
        if elapsed_seconds < 60:
            time_str = f"{elapsed_seconds:.4f} seconds"
        elif elapsed_seconds < 3600:
            minutes = int(elapsed_seconds // 60)
            seconds = elapsed_seconds % 60
            minute_text = "minute" if minutes == 1 else "minutes"
            time_str = f"{minutes} {minute_text} and {int(seconds)} seconds"
        else:
            hours = int(elapsed_seconds // 3600)
            minutes = int((elapsed_seconds % 3600) // 60)
            seconds = elapsed_seconds % 60
            hour_text = "hour" if hours == 1 else "hours"
            minute_text = "minute" if minutes == 1 else "minutes"
            time_str = f"{hours} {hour_text}, {minutes} {minute_text} and {int(seconds)} seconds"
        if verbose:
            print(f"'{func.__name__}()' executed in {time_str}")
        return result
    
    return wrapper

@timer
def funcc(one = 1, two = 2):
    time.sleep(2)

funcc(True)

class MyClass:
    def __init__(self, verbose=True):
        self.verbose = verbose
        
    @timer
    def process_data(self, data):
        # do something...
        pass
        
obj = MyClass(verbose=True)
obj.process_data('1')