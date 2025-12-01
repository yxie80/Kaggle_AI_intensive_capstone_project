# Import the class from the types module
from google.genai import types

# You would then use it when initializing a service or client:
# from google.genai import Client
# client = Client(retry_options=HttpRetryOptions(max_retries=5))

retry_config=types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1, # Initial delay before first retry (in seconds)
    http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
)

__all__ = ["retry_config"]
