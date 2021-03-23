import random
import string


def generate_code():
    """
    generate a random code to send to the client for confirmation
    """
    return ''.join(random.choices(string.digits, k=6))
