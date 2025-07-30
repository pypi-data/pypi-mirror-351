"""
xianxia_quotes

A small utility to generate xianxia-style proverbs, e.g.:
    “Even a dragon will lose to a snake in its lair”
"""
import random

# Constants: grouped by habitat
HABITAT_ANIMALS = {
    "land": [
        "dragon", "tiger", "lion", "serpent", "fox", "wolf", "panther",
        "bear", "elephant", "rhinoceros", "leopard", "stallion", "boar",
        "mongoose", "buffalo", "yak", "stag", "manticore", "gryphon",
        "wyvern", "unicorn", "basilisk", "chimera", "hippopotamus",
        "puma", "lemur", "tapir", "armadillo", "porcupine", "badger",
    ],
    "air": [
        "eagle", "phoenix", "crane", "crow", "hawk", "falcon", "moth",
        "vulture", "peacock",
    ],
    "water": [
        "otter", "stingray", "orca", "narwhal", "seahorse", "kraken",
    ],
    "mythic": [  # Mythical/mixed creatures that can appear in multiple habitats
        "dragon", "phoenix", "gryphon", "wyvern", "unicorn", "basilisk",
        "chimera", "manticore", "kraken",
    ],
}

# Contexts mapped to one or more habitats
CONTEXTS = {
    "in its lair": ["land", "mythic"],
    "in the mountain": ["land"],
    "in the forest": ["land"],
    "in the sky": ["air"],
    "at dawn": ["land", "air"],
    "under the moon": ["land", "air"],
    "by the river": ["land", "water"],
    "at high tide": ["water"],
    "beneath the waves": ["water"],
    "on the ice": ["land", "water"],
    "in the jungle": ["land"],
    "on the floating isle": ["air", "mythic"],
    "within the volcano": ["land", "mythic"],
    "at the waterfall": ["land", "water"],
    "in the mist": ["land", "water"],
    "in the swamp": ["land", "water"],
    "on the ridge": ["land"],
    "at the crossroads": ["land"],
    "in the canyon": ["land"],
    "among the reeds": ["land", "water"],
    "within the palace": ["land"],
    "on the battlements": ["land"],
    "under the glacier": ["land", "water"],
    "within the labyrinth": ["land"],
    "by the geyser": ["land"],
    "on the salt flats": ["land"],
    "in the wind-swept plains": ["land"],
}

VERBS = [
    "lose to", "bow before", "fall to", "be humbled by", "be outmatched by",
    "yield to", "falter before", "submit to", "be overshadowed by",
    "be outfoxed by", "be outpaced by", "be outmaneuvered by", "respect",
    "cower before", "be surprised by", "be bested by", "be tricked by",
    "be ensnared by", "be dethroned by", "be outwitted by",
    "be outclassed by", "be dominated by", "be flanked by",
    "be overpowered by", "be outmatched in strength by", "be confounded by",
    "be unseated by", "be eclipsed by", "be outplayed by", "be overrun by",
    "be startled by", "be cornered by", "be outworked by", "be checked by",
    "be silenced by",
]


def quote_stream():
    """
    An infinite generator of habitat-aware xianxia-style proverbs.

    Yields:
        str: A proverb like
             "Even a dragon will lose to a wolf in the forest"
    """
    contexts = list(CONTEXTS.items())
    while True:
        context, habitats = random.choice(contexts)
        # Collect all animals valid in the chosen habitats
        valid_animals = set()
        for habitat in habitats:
            valid_animals.update(HABITAT_ANIMALS.get(habitat, []))

        # Skip if fewer than two candidates
        if len(valid_animals) < 2:
            continue

        # Cast to list so random.sample works
        subject, target = random.sample(list(valid_animals), 2)
        verb = random.choice(VERBS)
        yield f"“Even a {subject} will {verb} a {target} {context}”"


def single_quote():
    """
    Return a single xianxia-style proverb.
    """
    return next(quote_stream())


def main():
    """
    Entry point: print one random proverb.
    """
    print(single_quote())


if __name__ == "__main__":
    main()
