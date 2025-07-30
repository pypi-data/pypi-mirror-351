# mywordle

mywordle is a library that brings Wordle to Python with exceptional customization and personlization.

Millions of people enjoy Wordle every day online.
However, people cannot access it on Python, with existing libraries not providing sufficient customization.
This library brings this game to Python and lets them put their own twist to it.

- HomePage: https://github.com/kzhu2099/My-Wordle
- Issues: https://github.com/kzhu2099/My-Wordle/issues

[![PyPI Downloads](https://static.pepy.tech/badge/mywordle)](https://pepy.tech/projects/mywordle)

Author: Kevin Zhu

## Features

- Allows users to play Wordle
- 25,000+ target words of different lengths with 370,000 words available
- Customization:
    - challenge mode
    - number of guesses
    - length of words
    - custom word list / guess list
- Helpful layout

## Installation

To install mywordle, use pip: ```pip install mywordle```.

However, many prefer to use a virtual environment.

macOS / Linux:

```sh
# make your desired directory
mkdir /path/to/your/directory
cd /path/to/your/directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install mywordle
source .venv/bin/activate
pip install mywordle

deactivate # when you are completely done
```

Windows CMD:

```sh
# make your desired directory
mkdir C:path\to\your\directory
cd C:path\to\your\directory

# setup the .venv (or whatever you want to name it)
pip install virtualenv
python3 -m venv .venv

# install mywordle
.venv\Scripts\activate
pip install mywordle

deactivate # when you are completely done
```

## Information

Wordle is a game that is now owned by the NYT.
The aim is to guess a 5-letter word within 6 attempts.
When you guess the word, you will be given a color-coded result with the following key:

- Green is the correct letter in the correct spot
- Yellow is the correct letter but it is in a different spot
- Gray/White means that the letter is not in the word.

## Basic Gameplay

This game aims to mimic Wordle with thousands of available words.
To use it is very simple! Simply run:

```python
from mywordle import Wordle

game = Wordle()
game.play()
```

Guesses and words are not case sensitive.

You may pass in a ```target_word``` for the target, as long as it is part of ```self.word_list```, which includes words of any length.

```self.word_list``` is a list of words that are starting points for the random generation.

```self.guess_list``` is a list of words that players may use to guess with.

To check if a word falls into either list, use ```is_valid_word``` or ```is_valid_guess```

This means that you can guess with ```xylyl``` but it won't ever appear unless if you use ```game.play('xylyl')```.

Finally, for an extra challenge, set ```challenge_mode = True``` in ```play()``` which requires you to follow all clues given in previous words.

See examples for more information on how to use the game.

## Customization

Wordle has many variants, and this library's distinction is customization.

You may alter ```num_guesses``` to be a different amount, like 7.

If ```target_word``` is not in ```self.word_list```, you may set ```allow_any_word = True``` to allow any string of characters.

For example, if you want to have the word ```abcdefgh```, guessed, you may do the following:

```python
game.play('abcdefgh', num_guesses = 7, allow_any_word = True)
```

Or, if you want all 8 letter words in the default list, you may play like so:

```python
game = Wordle()
game.play(word_length = 8)
```

```word_length``` pulls from ```self.word_list``` and takes a random word with the value provided.
If ```target_word``` is passed with this, word_length is ignored.

You can input your own ```word_list``` and/or ```guess_list``` for most control.

```word_list```: This is a list of words from which the target word will be randomly selected.
The words in this list can have varying lengths.

When provided, ```self.words``` is overidden and becomes this..
```guess_list```: If ```word_list``` is provided, this must include the entirety of that list.
Otherwise, it serves as additional words that are valid guesses to the default.

If ```guess_list``` is an empty list, any word can be a guess.
If ```word_list``` is an empty list, both must be an empty list.
This is equivalent of always having ```play(allow_any_word = True ... )```, but you MUST provide a ```target_word```.

For example, if you have a list of your own words that you want to use, you can have the following:

```python
game = Wordle(['magazine', 'apples', 'oranges'], []) # allows any guesses to be made
game = Wordle(['magazine', 'apples', 'oranges'], ['magazine', 'apples', 'oranges', ...]) # restricts guesses to the guess_list
game.play()

game2 = Wordle([], []) # allows any word to be the target and any word to be guessed, but you must provide the a target_word
game2.play('custom')
```

Because though the word lengths may be different, the word length must be given away, which can be an indicator of what the word is.

You may also pass in ```word_length``` in ```play()```. Usually, it defaults to 5. If there is a ```word_list```, it defaults to ```None```, picking any word from ```self.words```.

Ensure that the player doesn't have access to the list or it is sufficiently large enough.

## Disclaimer

This project is a personal and non-commercial recreation of the popular Wordle game. The Wordle game is owned and operated by The New York Times (NYT). This library is intended for personal, educational, and entertainment use only. The library mimics the behavior of the official game but does not include any of the official NYT branding, features, or content. The use of this library is strictly for non-commercial purposes. By using this library, you acknowledge that you are responsible for complying with any applicable laws regarding personal and non-commercial use. The author and contributors do not hold any rights to the Wordle name, game, or related intellectual property.

## License

The License is an MIT License found in the LICENSE file.