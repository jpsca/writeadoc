"""Odds and ends: the package logger and the progress messages."""

import logging
import random


logger = logging.getLogger("writeadoc")
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())


RANDOM_MESSAGES = [
    "Accessing hidden memories",
    "Activating hyperdrive",
    "Activating unknown hardware",
    "Adjusting the dilithium crystals",
    "Aligning the stars",
    "Bending the event horizon",
    "Bending the spoon",
    "Brewing fresh markdown",
    "Calibrating the flux capacitor",
    "Challenging everything",
    "Chasing Schrödinger's cat",
    "Counting the atoms in the universe",
    "Counting to 42 backwards",
    "Debating documentation as art",
    "Deciphering the matrix",
    "Decrypting nuclear codes",
    "Deterministically simulating the future",
    "Distilling beauty",
    "Distilling delight",
    "Distilling enjoyment",
    "Embedding energon cubes",
    "Exceeding the CPU quota",
    "Extracting meaning",
    "Filtering the ozone",
    "Finding a needle in a haystack",
    "Finding the meaning of life",
    "Fixing the ozone layer",
    "Folding sections with care",
    "Formatting with finesse",
    "Iodizing",
    "Iterating on the iteration",
    "Liquefying bytes",
    "Lowering the entropy",
    "Mixing metadata magic",
    "Merging the multiverse",
    "Optimizing the optimizer",
    "Optimizing for happiness",
    "Taking over the tri-state area",
    "Patching the space-time continuum",
    "Polishing the pixels",
    "Processing every third letter",
    "Rearranging the deck chairs on the Titanic",
    "Running with scissors",
    "Refactoring the universe",
    "Rendering emotional depth",
    "Rendering inspiration",
    "Reversing the bits polarity",
    "Revolving independence",
    "Reversing global warming",
    "Sandbagging expectations",
    "Self affirming",
    "Shaking",
    "Sifting through syntax",
    "Summoning the muses",
    "Swapping time and space",
    "Testing CO2 levels",
    "Tokenizing innovation",
]


def get_random_messages(num: int = 3) -> list[str]:
    return random.sample(RANDOM_MESSAGES, min(num, len(RANDOM_MESSAGES)))
