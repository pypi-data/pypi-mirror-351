'''
Author: Kevin Zhu
Wordle is owned by the NYT. This class aims to mimic its behavior for python users and is not the actual Wordle.
Please visit https://www.nytimes.com/games/wordle/index.html to play the actual game online.
'''

import random
import time

from collections import Counter
from importlib.resources import open_text

from kzutil import GREEN, YELLOW, WHITE, GREY, RESET

class Wordle:

    '''
    A class that provides a game like Wordle and allows for users to play in Python.

    The aim is to guess a 5-letter word within 6 attempts.

    When you guess the word, you will be given a color-coded result with the following key:

    - Green is the correct letter in the correct spot
    - Yellow is the correct letter but it is in a different spot
    - Gray/White means that the letter is not in the word
    '''

    '''
    Parameters
    ---------
    list word_list, optional:
        a custom list of words to use that can be picked from

    list additional_guess_list, optional:
        a custom list of guesses to use that can be picked from, which must also include all words in word_list

    Raises
    ------
        ValueError: if word_list is [] and guess_list is not []
        ValueError: not all words in word_list are a part of guess_list
    '''

    def __init__(self, word_list = None, guess_list = None):
        if guess_list is not None and word_list is not None:
            if guess_list != [] and word_list == []:
                raise ValueError('word_list cannot be [] if guess_list not also [].')

            elif (guess_list is None and word_list is not None) or (guess_list != [] and not all(word in guess_list for word in word_list)):
                raise ValueError('If word_list is provided, all valid words in word_list must also be in guess_list')

        self.USE_DEFAULT_WORDS = word_list is None
        self.word_list = []
        if word_list is None:
            with open_text('mywordle.data', 'possible_words.txt') as file:
                text = file.read()
                self.word_list = text.splitlines()

        else:
            self.word_list = word_list

        self.guess_list = []
        if word_list is None:
            with open_text('mywordle.data', 'possible_guesses.txt') as file:
                text = file.read()
                self.guess_list = text.splitlines()

        if guess_list is not None:
            self.guess_list += guess_list

        self.word = ''

        self.keyboard = {}

    def play(self, target_word = None, challenge_mode = False, word_length = None, num_guesses = None, allow_any_word = False):

        '''
        Plays the game Wordle, with the target either being a random word or user-set target_word!

        Parameters
        ----------
        string target_word, optional unless if self.word_list = []:
            a word in the list of valid words to use as the target word if allow_any_word is False
            If allow_any_word is True, it must be a string without digits

        boolean challenge_mode, defaults to False:
            if True, players must follow all of the information they were given before--
            letters in green must be in the same place, yellow must appear, and grey must not appear.

        int word_length, defaults to 5:
            the length of the word to take from self.word_list
            if there is a word_list, it defaults to None

        int num_guesses, defaults to 6:
            the amount of guesses the player has to win

        boolean allow_any_word, defaults to False:
            allows any string of characters to be the word_list, thus also allowing any string of characters to be the guess

        Returns
        -------
            A boolean of whether or not the player won

        Raises
        ------
            ValueError: if word_list is not provided while self.word_list is empty
            ValueError: if the word is not valid or if it has digits
            ValueError: if the a custom word is not provided and the word list is empty
            ValueError: num_guesses or word_length are not positive
            ValueError: if the word_length is not found in self.word_list
        '''

        if self.USE_DEFAULT_WORDS:
            word_length = word_length or 5

        num_guesses = num_guesses or 6

        if not target_word and self.word_list == []:
            raise ValueError('Since the word list is empty, please provide a custom word')

        if target_word and not allow_any_word and not self.is_valid_guess(target_word):
            raise ValueError('Invalid custom word')

        elif target_word and any(char.isdigit() for char in target_word):
            raise ValueError('Custom word has digits')

        if not num_guesses or num_guesses <= 0:
            raise ValueError('num_guesses must be positive')

        if word_length and word_length <= 0:
            raise ValueError('word_length must be positive')

        if not target_word:
            if word_length and word_length > 0:
                new_word_list = [word for word in self.word_list if len(word) == word_length]
                if new_word_list == []:
                    raise ValueError(f'word_length of {word_length} did not yield to any words')

            else:
                new_word_list = self.word_list

        self.word = target_word or new_word_list[random.randint(0, len(new_word_list) - 1)]
        self.word = self.word.upper()
        formatted_word = WHITE + '\'' + ' '.join(list(self.word)) + '\'' + RESET

        self.keyboard = [
            {'Q': WHITE, 'W': WHITE, 'E': WHITE, 'R': WHITE, 'T': WHITE, 'Y': WHITE, 'U': WHITE, 'I': WHITE, 'O': WHITE, 'P': WHITE},
                {'A': WHITE, 'S': WHITE, 'D': WHITE, 'F': WHITE, 'G': WHITE, 'H': WHITE, 'J': WHITE, 'K': WHITE, 'L': WHITE},
                    {'Z': WHITE, 'X': WHITE, 'C': WHITE, 'V': WHITE, 'B': WHITE, 'N': WHITE, 'M': WHITE}
        ]

        print('-' * 20)
        print(f'Welcome to Wordle! The word to guess is {len(self.word)} characters long.')
        print(f'Guess \'\\\' to give up.')

        guesses = []
        challenge_mode_info = []
        win = False

        for i in range(num_guesses):
            while True:
                print('-' * 20)
                self.print_keyboard()

                for j in range(len(guesses)):
                    print(f'{j + 1}: {guesses[j]}')

                guess = input(f'{i + 1}: {WHITE}').upper().replace(' ', '')

                if guess == '\\':
                    print(f'{RESET}You gave up! The word was {formatted_word}.')
                    time.sleep(1)
                    return False

                print(RESET, end = '')

                if len(guess) != len(self.word):
                    print(f'Invalid length, please input a {len(self.word)} character word')

                elif any(not char.isalpha() for char in guess):
                    print('Only provide a-z. Symbols, numbers, or spaces are not allowed, please try again')

                elif not allow_any_word and not self.is_valid_guess(guess):
                    print('allow_any_word is False, please provide a valid word from self.guess_list')

                else:
                    if challenge_mode and not self.complete_challenge(guess, challenge_mode_info):
                        print('Because challenge_mode is on, which means your guesses must match the clues given in previous guesses')

                    else:
                        break

                time.sleep(1)

            result = self.guess_word(guess)

            full_guess = ''
            for char, color in zip(list(guess), list(result)):
                formatted_char = f'{color}{char}{RESET} '
                print(formatted_char, end = '', flush = True)
                full_guess += formatted_char
                time.sleep(0.4)
            print()

            guesses.append(full_guess)
            challenge_mode_info.append(zip(list(guess), list(result)))

            if ''.join(result) == GREEN * len(self.word):
                win = True
                time.sleep(1)

                break

            time.sleep(1)

        if win:
            print(f'Congratulations! The word was {formatted_word}. You got it in {i + 1} guesses!')

        else:
            print(f'Sorry, you ran out of guesses! The word was {formatted_word}')

        print('Your guesses: ')
        print('\n'.join(guesses))

        time.sleep(1)
        return win

    def is_valid_word(self, word):

        '''
        Determines if this word is valid.

        Parameters
        ----------
        string word:
            the word to check

        Returns
        -------
        boolean
            whether or not this word is valid
        '''

        return self.word_list == [] or word.lower() in self.word_list

    def is_valid_guess(self, word):
        '''
        Determines if this guess is valid.

        Parameters
        ----------
        string word:
            the word to check

        Returns
        -------
        boolean
            whether or not this word is valid
        '''

        return self.guess_list == [] or word.lower() in self.guess_list

    def guess_word(self, guess, target_word = None):

        '''
        Determines whether how close the guess is to the target word.

        Parameters
        ----------
        string guess:
            a valid 5 letter word
        string target_word, optional:
            an optional word to use for the target (defaults to self.word)

        Returns
        -------
        list
            a list of colors depending on each character's value
        '''

        word = target_word or self.word
        result = []
        target_characters = list(word)
        guess_characters = list(guess)

        for i in range(len(word)):
            if guess_characters[i] == target_characters[i]:
                result.append(GREEN)
                self.update_keyboard(target_characters[i], GREEN)
                target_characters[i] = None

            else:
                result.append(None)

        for i in range(len(word)):
            if result[i] is None and guess_characters[i] in target_characters:
                result[i] = YELLOW
                self.update_keyboard(guess_characters[i], YELLOW)
                target_characters[target_characters.index(guess_characters[i])] = None

            elif result[i] is None:
                result[i] = GREY
                self.update_keyboard(guess_characters[i], GREY)

        return result

    def complete_challenge(self, guess, challenge_mode_info):

        '''
        Determines if this guesses matches challenge mode.

        Parameters
        ----------
            string guess:
                the guess to check
            list challenge_mode_info:
                all previous guesses with a list with a tuple of the letter and the color.

        Returns
        ------
            boolean of whether or not the challenge_mode conditions were met
        '''

        if challenge_mode_info == []:
            return True

        for previous_guess_info in challenge_mode_info:
            guess_letter_counts = Counter(guess)
            required_yellow_counts = Counter()

            # enforce green and count yellow
            for index, ((letter, color), guess_letter) in enumerate(zip(previous_guess_info, guess)):
                if color == GREEN:
                    if guess_letter != letter:
                        return False

                    guess_letter_counts[letter] -= 1

                elif color == YELLOW:
                    required_yellow_counts[letter] += 1

            # enforce yellow and grrey
            for letter in required_yellow_counts.keys():
                if letter not in guess_letter_counts.keys() or guess_letter_counts[letter] < required_yellow_counts[letter]:
                    return False

            for index, (letter, color) in enumerate(previous_guess_info):
                if color == YELLOW:
                    if letter == guess[index]:
                        return False

                    guess_letter_counts[letter] -= 1

                elif color == GREY:
                    if letter in guess_letter_counts.keys() and guess_letter_counts[letter] > 0:
                        return False # additional letters that have not been used and are grey may not be used

        return True

    def update_keyboard(self, key, color):

        '''
        Changes the keyboard to reflect the current game.

        Parameters
        ----------
        string key:
            the 1 letter key to update

        string color:
            the ANSI color to update the key with
        '''

        for row in self.keyboard:
            if key in row:
                if color == GREEN:
                    row[key] = GREEN
                    break

                if row[key] != GREEN and color == YELLOW:
                    row[key] = color
                    break

                if row[key] != GREEN and row[key] != YELLOW:
                    row[key] = color
                    break

    def print_keyboard(self):

        '''
        Prints the keyboard with the correct positioning and color coding.
        '''

        indent = ''
        for row in self.keyboard:
            print(indent, end = '')
            for key in row.keys():
                print(row[key] + key + RESET + ' ', end = '')
            print()
            indent += ' '