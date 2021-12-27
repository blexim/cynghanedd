# Cynghanedd assistant

This is a program to help write poetry using
[Cynghanedd](https://en.wikipedia.org/wiki/Cynghanedd).

## Getting started

First create a
[Python virtual environment](https://aaronlelevier.github.io/virtualenv-cheatsheet/) and
install the program's dependencies:

```
$ virtualenv env
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```

Now you can run the assistant:

```
(env) $ ./cynghanedd.py
```

## Using the assistant

When you run the assistant, it will ask you for the half line you want to match
against. This can be given as a sequence of English words, or as a "consonant skeleton"
(a sequence of consonant phones separated by spaces, encoded using
 [these rules](https://websites.psychology.uwa.edu.au/school/mrcdatabase/mrc2.html#PHON)).

The assistant will then present you with a list of options for the first word in the
matching half line. Choose one of those and you'll be asked for the next word, until the
half line is complete.

### Example

```
(env) $ ./cynghanedd.py 
Building database (this may take a while).........
Loaded 95181 words in 0.3s
Enter the first half line (as normal text, or as a skeleton): k tS r
ache acher aching ack acquire acre actuary anchor arc ark auk awake awaking awoke car care catch catcher catchier catching catchy caw cawing choir co co- coach coaching cohere coir coo cooee cooing cor core corps couch couching coup cow cower cowing coy coyer cur curr cutcherry echo echoing eiche eke eking encore eye-catching eyecatching hack hacking hake hank hanker hanky hark harking hawick hawk hawker hawking heck hick hike hiker hiking hock hockey hocking hoik hong kong honk honking hook hookah hooker hooking hooky hough hunk ichor ike ink inkier inking inky irk irking k kay kea ketch key keying kier king kitsch kiwi kwacha oak occur ochre ok okay okaying orc qua quay queer quire unco wake waking walk walkaway walker walking wank wanking weak weaker week whack whacker whacking wick wicker wink winking woke wonky work worker working
Pick a word: catch  
aerie aero aery airing airy area aria arrah array arraying arrear arrow arrowy aura awry earring eerie eerier eery era erring error eyrie eyry hairier hairy harangue haranguing haring harrier harrow harrowing harry harrying hearer hearing hero herring hirer hiring hoarier hoary hooray horror houri hurrah hurrahing hurray hurrier hurry hurrying ra rah rang rare raw ray raying re re- rear rehear rewire rhea ring ringer ringing roar roe rou_e rouen row rower rowing roy rue ruing rung rye warier waring warring warrior wary wearer wearier wearing weary wearying where'er wherry whirring wirier wiring wiry worrier worry worrying wrier wring wringer wringing wrong wronging wrung wry
Pick a word: wiry
catch wiry
```

## Building a custom dictionary

The phonetic dictionary used to search for matching words are stored in the `data/` directory.
You can customise this dictionary by modifying the `convert_mrc.py` script, then running it
like this:

```
$ ./convert_mrc.py data/mrc2.dct > data/mrc.txt
```

For example, you might want to ignore the consonant "w" when matching words. You could do this
by adding "w" to the list `ignored_consonants` in `convert_mrc.py`, then running the script
as shown above. From then on, every time you run `cynghanedd.py` it will ignore "w" when searching
for matches.

