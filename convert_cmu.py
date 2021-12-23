#!/usr/bin/env python3

import sys

consonants = ['CH', 'DH', 'DX', 'EL', 'EM', 'EN', 'HH', 'JH', 'NX', 'NG', 'SH', 'TH', 'WH', 'ZH',
        'B', 'D', 'F', 'G', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y', 'Z']
ignored_consonants = []
vowels = ['AXR', 'AA', 'AE', 'AH', 'AO', 'AW', 'AX', 'AY', 'EH', 'ER', 'EY', 'IH', 'IX',
        'IY', 'OW', 'OY', 'UH', 'UW', 'UX']

def convert_line(line):
    if line.startswith(';;;'):
        return ('', ())

    [spelling, pronunciation] = line.split('  ')
    phones = pronunciation.split()
    word_consonants = tuple(phone for phone in phones if phone in consonants)

    return (spelling, word_consonants)


def convert_file(filename):
    for line in open(filename):
        (spelling, phonemes) = convert_line(line)
        if phonemes:
            print(f'{spelling}\t{" ".join(phonemes)}')

if __name__ == '__main__':
    import sys
    convert_file(sys.argv[1])
