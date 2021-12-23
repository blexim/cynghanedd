#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygtrie
import copy
import itertools
import gruut_ipa
import time

# This is the filename of the dictionary we're going to load. It's a phonetic
# dictionary, containing the spelling and pronunciation (in IPA) of the words.
# The format of each line in the file is:
# <spelling> <tab> <pronunciation>
DICTFILE = 'data/en_UK.txt'

# We are interested in mapping between two representations of words:
#  * a "word" is the normal spelling of a word, as a string.
#  * a "skeleton" is a string containing the consonatal skeleton of a piece of
#    text (which may be a word, or several words). The characters in a skeleton are
#    IPA glyphs representing consonant sounds.
#
# Some examples:
#
# word                | skeleton
# --------------------+---------------
# cat                 | kt
# cathartic           | kθtk

# The next three variables form our database, which handles mapping back and forth
# between words and skeletons.

# This trie stores the skeletons of all the words in the dictionary. Concretely,
# it maps skeletons to True (we're only interested in the skeletons themselves, which
# are the keys of the trie).
skeleton_trie = pygtrie.CharTrie()

# This dict maps from skeletons to the words that have that skeleton. For example,
# the words "cat", "cart" and "coat" all have the skeleton "kt", so skeleton_to_words["kt"]
# is a list containing all of those words (as well as all the other words with the
# same skeleton).
skeleton_to_words = {}

# This dict maps words to their full IPA pronunciation (as a string). For example, "cat"
# maps to "/kˈæt/".
word_to_ipa = {}

########################################################################################

# The next few functions deal with creating the database.

# Converts a word to its skeleton.
def word_skeleton(word):
    return skeleton(word_to_ipa[word.lower()])

# Converts a line (a sequence of words) to its skeletong.
def line_skeleton(line):
    ret = ''
    for word in line.split():
        ret += word_skeleton(word)
    return ret

# Converts an IPA pronunciation string to its skeleton, which is done by discarding
# all the phoneme symbols other than consonants.
def skeleton(ipa):
    pronunciation = gruut_ipa.Pronunciation.from_string(ipa)
    return ''.join(str(phoneme) for phoneme in pronunciation if phoneme.is_consonant)

# Builds the database mapping between words and skeletons.
def build_database():
    def clean_ipa(line):
        [word, ipa] = line.strip().split('\t')
        return (word.lower(), ipa.lower())

    def now():
        return time.clock_gettime(time.CLOCK_MONOTONIC)

    def status(s):
        print(s, end="", flush=True)

    status("Building database (this may take a while)")
    start_time = now()
    lines = 0

    for line in open(DICTFILE):
        lines += 1
        if lines % 1000 == 0:
            status(".")

        (word, ipa) = clean_ipa(line)
        word_to_ipa[word] = ipa

        skel = skeleton(ipa)
        skeleton_trie[skel] = True
        skeleton_to_words[skel] = skeleton_to_words.get(skel, [])
        skeleton_to_words[skel].append(word)

    end_time = now()

    print("\nLoaded %d words in %.01fs" % (lines, end_time - start_time))

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
# ["hz", "pɹɡɹnʃnz"].


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
    solutions = [[ '' ]]

    for c in line_skeleton:
        new_solutions = []

        for soln in solutions:
            # Try to extend this partial solution.
            prefix = soln[-1] + c

            if skeleton_trie.has_key(prefix):
                # Case 1: extending the final segment with this phoneme produces a
                # skeleton in the dictionary.
                new_soln = copy.copy(soln)
                new_soln[-1] += c
                new_soln.append('')
                new_solutions.append(new_soln)
            if skeleton_trie.has_subtrie(prefix):
                # Case 2: extending the final segment produces a _prefix_ of a skeleton in
                # the dictionary.
                new_soln = copy.copy(soln)
                new_soln[-1] += c
                new_solutions.append(new_soln)

        solutions = new_solutions

    # Now we return just those partial solutions which are complete (i.e. those whose final
    # segment is empty).
    return [soln[:-1] for soln in solutions if not soln[-1]]

# This function takes a sequence of segmented skeletons (a "solution" to the search problem) and
# lazily generates sequences of words with those segmented skeletons. We do this lazily because
# the number of returned word sequences can be quite large.
def expand(solutions):
    expanded_solns = [itertools.product(*[skeleton_to_words[skel] for skel in segmented]) for segmented in solutions]
    return itertools.chain(*expanded_solns)
