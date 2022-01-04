#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygtrie
import copy
import itertools
import time

# This is the filename of the dictionary we're going to load. It's a phonetic
# dictionary, containing the spelling and pronunciation skeleton of the words.
# The format of each line in the file is:
# <spelling> <tab> <pronunciation>
DICTFILES = ['data/mrc.txt', 'data/cmu.txt']

# We are interested in mapping between two representations of words:
#  * a "word" is the normal spelling of a word, as a string.
#  * a "skeleton" is a tuple of strings describing the consonatal skeleton of a piece of
#    text (which may be a word, or several words). The components of a skeleton are
#    strings representing consonant sounds, according to the encoding given at
#    https://websites.psychology.uwa.edu.au/school/mrcdatabase/mrc2.html#PHON
#
# Some examples:
#
# word                | skeleton
# --------------------+---------------
# cat                 | k t
# cathartic           | k T t k
# chain               | tS n

# The next three variables form our database, which handles mapping back and forth
# between words and skeletons.

# This trie stores the skeletons of all the words in the dictionary. Concretely,
# it maps skeletons to True (we're only interested in the skeletons themselves, which
# are the keys of the trie).
skeleton_trie = pygtrie.CharTrie()

# This dict maps from skeletons to the words that have that skeleton. For example,
# the words "cat", "cart" and "coat" all have the skeleton ("k", "t"), so
# skeleton_to_words[("k", "t")] is a list containing all of those words (as well
# as all the other words with the same skeleton).
skeleton_to_words = {}

# This dict maps words to their skeleton (as a string). For example, "cat"
# maps to ("k", "t").
word_to_skeleton = {}

########################################################################################

# The next few functions deal with creating the database.

# Converts a line (a sequence of words) to its skeleton. Returns None if a word
# in the sequence was not found in the dictionary
def line_to_skeleton(line):
    ret = ()
    for word in line.lower().split():
        if word not in word_to_skeleton:
            return None

        ret += word_to_skeleton[word]
    return ret

# Builds the database mapping between words and skeletons.
def build_database():
    def clean_ipa(line):
        [word, pronunciation] = line.strip().split('\t')
        phones = tuple(pronunciation.split())
        return (word.lower(), phones)

    def now():
        return time.clock_gettime(time.CLOCK_MONOTONIC)

    def status(s):
        print(s, end="", flush=True)

    status("Building database (this may take a while)")
    start_time = now()
    lines = 0

    for dictfile in DICTFILES:
        for line in open(dictfile):
            lines += 1
            if lines % 10000 == 0:
                status(".")

            (word, skeleton) = clean_ipa(line)
            word_to_skeleton[word] = skeleton

            skeleton_trie[skeleton] = True
            skeleton_to_words[skeleton] = skeleton_to_words.get(skeleton, [])
            skeleton_to_words[skeleton].append(word)

    end_time = now()

    print("\nLoaded %d words in %.01fs" % (len(word_to_skeleton), end_time - start_time))

build_database()

########################################################################################

# The next functions implement the search algorithm for finding a sequence of words
# matching a skeleton.
#
# The algorithm is split into two parts:
# * Take a skeleton and find all the ways to segment it,
# * Take a segmented skeleton and find all the word sequences matching that segemented skeleton.
#
# A segmented skeleton is a list of skeletons, with the intention that each skeleton corresponds
# to one word, so the segmented skeleton represents a sequence of words. For example,
# the segmented skeleton of the sequence ["his", "peregrinations"] would be
# [("h", "z"), ("p", "r", "g", "r", "n", "S", "n")].


# This function takes a skeleton and finds all the ways to segment it such that the segmented
# skeletons have solutions in the dictionary.
def search(line_skeleton):
    # Our algorithm proceeeds like this:
    # We keep track of a set of partial solutions. Each partial solution is a segmented skeleton,
    # where the final segment is not yet complete. We consider one phoneme in the input skeleton
    # at a time and try to extend all of the partial solutions we're currently tracking with that
    # phoneme.
    #
    # At each step, each partial solution [w1, w2, ..., wN] has the property that each of the
    # segments w1 ... w(N-1) is the skeleton of some word in the dictionary, and wN is
    # a _prefix_ of the skeleton of some word in the dictionary.
    #
    # To extend a partial solution [w1, w2, ..., wN] with a phoneme P, we have two rules:
    # * If wN + P is a skeleton in our dictionary, [w1, w2, ..., wN + P] is a real segmented
    #   skeleton of some sequence of words. We start tracking the partial solution
    #   [w1, w2, ..., wN + P, ''].
    # * If wN + P is a _prefix_ of some skeleton in our dictionary, we start tracking the
    #   partial solution [w1, w2, ..., wN + P].
    #
    # If neither of the two cases above holds, the partial solution can't be extended and so
    # we forget about it.
    #
    # It's fairly easy to see that partial solutions extended according to the above rules
    # maintain the property we require (every segment except the last is the skeleton of some
    # word in the dictionary, and the final segment is a prefix of the skeleton of some word
    # in the dictionary).
    solutions = [[ () ]]

    for c in line_skeleton:
        new_solutions = []

        for soln in solutions:
            # Try to extend this partial solution.
            prefix = soln[-1] + (c,)

            if skeleton_trie.has_key(prefix):
                # Case 1: extending the final segment with this phoneme produces a
                # skeleton in the dictionary.
                new_soln = copy.copy(soln)
                new_soln[-1] = prefix
                new_soln.append(())
                new_solutions.append(new_soln)
            if skeleton_trie.has_subtrie(prefix):
                # Case 2: extending the final segment produces a _prefix_ of a skeleton in
                # the dictionary.
                new_soln = copy.copy(soln)
                new_soln[-1] = prefix
                new_solutions.append(new_soln)

        solutions = new_solutions

    # Now we return just those partial solutions which are complete (i.e. those whose final
    # segment is empty).
    return [soln[:-1] for soln in solutions if not soln[-1]]

# This function takes a sequence of segmented skeletons (a "solution" to the search problem) and
# lazily generates sequences of words with those segmented skeletons. We do this lazily because
# the number of returned word sequences can be quite large.
def expand(solutions):
    def expand_skeleton(skeleton):
        for word in skeleton_to_words[skeleton]:
            yield word

    def expand_solution(solution):
        return itertools.product(*[expand_skeleton(skel) for skel in solution])

    expanded_solutions = [expand_solution(solution) for solution in solutions]
    return itertools.chain(*expanded_solutions)

def first_words(solutions):
    ret = set()

    for solution in solutions:
        ret.update(skeleton_to_words[solution[0]])

    return ret

def choose_word(solutions, word):
    skeleton = word_to_skeleton[word]
    remaining_solutions = [ solution[1:] for solution in solutions if solution[0] == skeleton ]
    return remaining_solutions

def complete_cyng(words, skeleton, solution):
    while solution and solution[0]:
        next_words = ' '.join(sorted(first_words(solution)))
        print(next_words)
        print("Pick a word (or enter comma to go back a step): ", end="", flush=True)
        word = sys.stdin.readline().strip()
        while word == ",":
            word, words, solution = back_cynghanedd(words, skeleton)
        words.append(word)

        solution = choose_word(solution, word)
    return words, solution

def run_cynghanedd():
    print("Enter the first half line as a skeleton: ", end="", flush=True)
    line = sys.stdin.readline().strip()
    skeleton = line.split()

    solution = search(skeleton)

    words = []

    words, solution = complete_cyng(words, skeleton, solution)

    return words, skeleton, solution


def back_cynghanedd(old_words, skeleton):
    solution = search(skeleton)

    print(old_words[:-1])
    words = []
    i = 0
    current_iteration = len(old_words)
    print("Current iteration is ", end="")
    print(current_iteration)

    while i < (current_iteration - 1):
        next_words = ' '.join(sorted(first_words(solution)))
        word = old_words[i]
        i += 1
        words.append(word)
        solution = choose_word(solution, word)
    next_words = ' '.join(sorted(first_words(solution)))
    print(next_words)
    print("Pick a word: ", end="", flush=True)
    word = sys.stdin.readline().strip()

    return word, words, solution


if __name__ == '__main__':
    import sys

    words, skeleton, solution = run_cynghanedd()
    
    answer = ""
    while not (answer == "n"):
        print(' '.join(words))
        print("Restart cynghanedd? y/n (or comma to go back): ", end="", flush=True)
        answer = sys.stdin.readline().strip()
        if answer not in ('y','n',','):
            print("Please answer y/n (or comma to go back a step")
        if answer == 'y':
            print("New Skeleton")
            words, skeleton, solution = run_cynghanedd()
        if answer == ',':
            word = ','
            while word == ',':
                word, words, solution = back_cynghanedd(words, skeleton)
            words.append(word)

            solution = choose_word(solution, word)

            words, solution = complete_cyng(words, skeleton, solution)
            
