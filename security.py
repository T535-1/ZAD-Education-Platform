
import streamlit as st
import time

def rate_limit(per_second: int, key: str):
    """
    A simple decorator to limit the call rate of a function.
    Uses st.session_state to track call times without external dependencies.

    Args:
        per_second (int): Maximum number of calls allowed per second.
        key (str): A unique key to identify the function being limited in the session state.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Initialize the tracking list in session state if it doesn't exist
            if f"rate_limit_{key}" not in st.session_state:
                st.session_state[f"rate_limit_{key}"] = []

            # Get the list of previous call timestamps
            call_times = st.session_state[f"rate_limit_{key}"]
            
            # Get the current time
            now = time.time()
            
            # Remove timestamps that are older than one second
            call_times = [t for t in call_times if now - t < 1]
            
            # Check if the number of calls in the last second exceeds the limit
            if len(call_times) >= per_second:
                st.error("Too many requests. Please wait a moment and try again.")
                return None # Or raise an exception
            
            # Record the current call time
            call_times.append(now)
            st.session_state[f"rate_limit_{key}"] = call_times
            
            # Call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- Example Usage (for demonstration) ---
# @rate_limit(per_second=2, key="login_attempt")
# def attempt_login(username, password):
#     # Your login logic here
#     print(f"Attempting login for {username}")
#     return True
