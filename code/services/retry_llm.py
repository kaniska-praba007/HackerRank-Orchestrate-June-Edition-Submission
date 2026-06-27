"""Retry decorator for Google Gemini API calls."""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import google.api_core.exceptions as google_exceptions

def create_retry_decorator(max_attempts=3):
    """Returns a tenacity decorator that retries on common transient Google API errors."""
    return retry(
        retry=retry_if_exception_type((
            google_exceptions.ResourceExhausted,   # 429
            google_exceptions.ServiceUnavailable,  # 503
            google_exceptions.DeadlineExceeded,    # 504
            google_exceptions.InternalServerError, # 500
        )),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(max_attempts),
        reraise=True,
    )