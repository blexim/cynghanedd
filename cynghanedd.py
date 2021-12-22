#!/usr/bin/python3

import pygtrie
import copy
import itertools
import gruut_ipa

DICTFILE = 'data/en_UK.txt'

ipa_skeleton_trie = pygtrie.CharTrie()
ipa_skeleton_to_words = {}
word_to_ipa = {}

def word_skeleton(word):
    return ipa_skeleton(word_to_ipa[word.lower()])

def line_skeleton(line):
    ret = ''
    for word in line.split():
        ret += word_skeleton(word)
    return ret

def ipa_skeleton(ipa):
    pronunciation = gruut_ipa.Pronunciation.from_string(ipa)
    return ''.join(str(phoneme) for phoneme in pronunciation if phoneme.is_consonant)

def clean_ipa(line):
    [word, ipa] = line.strip().split('\t')
    return (word.lower(), ipa.lower())

for line in open(DICTFILE):
    (word, ipa) = clean_ipa(line)
    word_to_ipa[word] = ipa

    skel = ipa_skeleton(ipa)
    ipa_skeleton_trie[skel] = skel
    ipa_skeleton_to_words[skel] = ipa_skeleton_to_words.get(skel, [])
    ipa_skeleton_to_words[skel].append(word)

def search(line_skeleton):
    solutions = [[ '' ]]

    for c in line_skeleton:
        new_solutions = []

        for soln in solutions:
            prefix = soln[-1] + c

            if ipa_skeleton_trie.has_key(prefix):
                new_soln = copy.copy(soln)
                new_soln[-1] += c
                new_soln.append('')
                new_solutions.append(new_soln)
            if ipa_skeleton_trie.has_subtrie(prefix):
                new_soln = copy.copy(soln)
                new_soln[-1] += c
                new_solutions.append(new_soln)

        solutions = new_solutions

    return [soln[:-1] for soln in solutions if not soln[-1]]

def expand(solutions):
    expanded_solns = [itertools.product(*[ipa_skeleton_to_words[skel] for skel in solution]) for solution in solutions]
    return itertools.chain(*expanded_solns)
