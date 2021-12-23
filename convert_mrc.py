#!/usr/bin/env python3

import sys
import re

consonants = ['tS', 'dZ', 'p', 'b', 't', 'd', 'k', 'm', 'n',
        'l', 'r', 'f', 'v', 's', 'z', 'g', '9', 'T',
        'D', 'S', 'Z', 'j']
ignored_consonants = ['h', 'w']
vowels = ['eI', 'aI', 'oI', '@U', 'aU', 'I@', 'e@', 'u@',
        'i', 'A', 'O', 'u', '3', 'I', 'e', '&', 'V', '0', '@']

pattern = re.compile('|'.join(consonants + ignored_consonants + vowels))

def convert_line(line):
    nlet = int(line[:2])
    toks = line.split('|')
    spelling = toks[0][-nlet:]
    pronunciation = toks[2]
    phonemes = pattern.findall(pronunciation)
    word_consonants = tuple(phoneme for phoneme in phonemes if phoneme in consonants)

    return (spelling, word_consonants)


def convert_file(filename):
    for line in open(filename):
        (spelling, phonemes) = convert_line(line)
        if phonemes:
            print(f'{spelling}\t{" ".join(phonemes)}')

if __name__ == '__main__':
    import sys
    convert_file(sys.argv[1])
