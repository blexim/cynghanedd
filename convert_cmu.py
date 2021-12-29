#!/usr/bin/env python3

import sys

consonants = ['CH', 'DH', 'DX', 'EL', 'EM', 'EN', 'HH', 'JH', 'NX', 'NG', 'SH', 'TH', 'WH', 'ZH',
        'B', 'D', 'F', 'G', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y', 'Z']
ignored_consonants = []
vowels = ['AXR', 'AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'EH', 'ER', 'EY', 'IH', 'IX',
        'IY', 'OW', 'OY', 'UH', 'UW', 'UX']

consonant_remap_table = {
        'B': 'b',
        'CH': 'tS',
        'D': 'd',
        'DH': 'D',
        'DX': 't',
        'EL': 'l',
        'EM': 'm',
        'EN': 'n',
        'F': 'f',
        'G': 'g',
        'H': 'h',
        'HH': 'h',
        'JH': 'dZ',
        'K': 'k',
        'L': 'l',
        'M': 'm',
        'N': 'n',
        'NX': 'n',
        'NG': '9',
        'P': 'p',
        'Q': '', #glottal stop
        'R': 'r',
        'S': 's',
        'SH': 'S',
        'T': 't',
        'TH': 'T',
        'V': 'v',
        'W': 'w',
        'WH': 'w',
        'Y': 'j',
        'Z': 'z',
        'ZH': 'Z'
        }


def convert_line(line):
    if line.startswith(';;;'):
        return ('', ())

    [spelling, pronunciation] = line.split('  ')
    phones = pronunciation.split()
    word_consonants = tuple(consonant_remap_table[phone] for phone in phones if phone in consonants)

    return (spelling.lower(), word_consonants)


def convert_file(filename):
    for line in open(filename, encoding="latin-1"):
        (spelling, phonemes) = convert_line(line)
        if phonemes:
            print(f'{spelling}\t{" ".join(phonemes)}')

if __name__ == '__main__':
    import sys
    convert_file(sys.argv[1])
