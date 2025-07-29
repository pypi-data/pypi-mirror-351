import argparse
from . import __version__

def main():
    parser = argparse.ArgumentParser(description="Ferramenta FK7Python")
    parser.add_argument('--version', action='version', version=f"fk7py {__version__}")
    args = parser.parse_args()
