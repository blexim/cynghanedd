#!/usr/bin/python3

import pygtrie
import copy

DICTFILE = 'data/en_UK.txt'

word_trie = pygtrie.CharTrie()
word_dict = {}

def skeleton(s):
    return s.translate({ord(c): None for c in 'aeiou'})

def clean_ipa(line):
    [word, ipa] = line.strip().split('\t')
    return (word.lower(), ipa.lower())

for line in open(DICTFILE):
    (word, ipa) = clean_ipa(line)
    skel = skeleton(word)
    word_trie[skel] = skel
    word_dict[skel] = word_dict.get(skel, [])
    word_dict[skel].append(word)


def search(line_skeleton):
    solutions = [['']]

    for c in line_skeleton:
        new_solutions = []

        for soln in solutions:
            prefix = soln[-1] + c

            print(f'Searching for {prefix}')

            if word_trie.has_key(prefix):
                print('Found key')
                new_soln = copy.copy(soln)
                new_soln[-1] += c
                new_soln.append('')
                new_solutions.append(new_soln)
            if word_trie.has_subtrie(prefix):
                print('Found subtrie')
                new_soln = copy.copy(soln)
                new_soln[-1] += c
                new_solutions.append(new_soln)

        solutions = new_solutions

    return [soln[:-1] for soln in solutions if not soln[-1]]
