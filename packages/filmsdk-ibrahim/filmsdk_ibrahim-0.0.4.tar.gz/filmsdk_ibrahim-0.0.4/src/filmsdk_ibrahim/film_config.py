import os
from dotenv import load_dotenv

load_dotenv()

class MovieConfig:
    """Configuration class containing arguments for the SDK client.
    Includes base URL configuration and exponential backoff handling.
    """
    movie_base_url: str
    movie_backoff: bool
    movie_backoff_max_time: int

    def __init__(
        self,
        movie_base_url: str = None,
        backoff: bool = True,
        backoff_max_time: int = 30,
    ):
        """Constructor for the configuration class.
        Accepts initialization values to override the defaults.

        Args:
            movie_base_url (optional):
                The base URL to use for all API calls.
                You can pass it directly or set it in an environment variable.
            movie_backoff:
                A boolean indicating whether the SDK should retry the call
                using backoff when errors occur.
            movie_backoff_max_time:
                The maximum number of seconds the SDK should keep retrying
                an API call before giving up.
        """
        self.movie_base_url = movie_base_url or os.getenv("MOVIE_API_BASE_URL")
        print(f"MOVIE_API_BASE_URL in MovieConfig init: {self.movie_base_url}")

        if not self.movie_base_url:
            raise ValueError("Base URL is required. Set the MOVIE_API_BASE_URL environment variable.")

        self.movie_backoff = backoff
        self.movie_backoff_max_time = backoff_max_time

    def __str__(self):
        """Stringify method to return the content of the config object for logging."""
        return f"{self.movie_base_url} {self.movie_backoff} {self.movie_backoff_max_time}"
