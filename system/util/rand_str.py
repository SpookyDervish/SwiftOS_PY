from secrets import choice
from string import ascii_letters


def generate_random_string(length: int):
    characters = ascii_letters
    return ''.join(choice(characters) for _ in range(length))