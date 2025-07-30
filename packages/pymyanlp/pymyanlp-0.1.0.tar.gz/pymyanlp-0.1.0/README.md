# PyMyaNLP

## Installation

```bash
pip install pymyanlp
```

# Sentiment Analyzer

# Agglutinative Nature

## TODO

1. Stop word detection and removal
2. Manually create sentiment lexicon
3. Write documentation in Burmese

## Sentiment Lexicon

### Rules

1. No repeated words
2. Words must root (aka unsegmentable)
3. or words must be direct pairs of segmented roots (သတ်၊ ဖြတ်)


# Burmese Phonology

The syllable structure of Burmese is C(G)V((V)C), which is to say the onset consists of a consonant optionally followed by a glide, and the rime consists of a monophthong alone, a monophthong with a consonant, or a diphthong with a consonant. The only consonants that can stand in the coda are /ʔ/ and /ɴ/. Some representative words are:

- CV မယ် /mɛ̀/ 'miss'
- CVC မက် /mɛʔ/ 'crave'
- CGV မြေ /mjè/ 'earth'
- CGVC မျက် /mjɛʔ/ 'eye'
- CVVC မောင် /màʊɰ̃/ (term of address for young men)
- CGVVC မြောင်း /mjáʊɰ̃/ 'ditch'

A minor syllable has some restrictions:

- It contains /ə/ as its only vowel
- It must be an open syllable (no coda consonant)
- It cannot bear tone
- It has only a simple (C) onset (no glide after the consonant)
- It must not be the final syllable of the word

Some examples of words containing minor syllables:

- ခလုတ် /kʰə.loʊʔ/ 'knob/switch'
- ပလွေ /pə.lwè/ 'flute'
- သရော် /θə.jɔ̀/ 'mock'
- ကလက် /kə.lɛʔ/ 'be wanton/be frivolous'
- ထမင်းရည် /tʰə.mə.jè/ '(cooked)rice-water'

# Preprocessing

I have cloned the dependency libraries into the `./lib` folder for ease
of access and crawling. In the future, we should just take the files
needed and organize better.

## Tokenization / Word Segmentation

Conditional Random Fields

## Part of Speech Tagging

myWord by YeThK is used for POS speech tagging, it provides us the
annotated corpus and lexicon.

In the future we should train a spaCy pipeline using myPOS v3 data but for now we will use an available RDRPOSTagger.

POS tagger fails to identify ရန်ဖြစ်/v properly in most cases.

Some words may have completely different forms in the two systems, and others will vary in terms of pronunciation, tone, vowel length, etc.

J Watkins defines the follow different types of Burmese:

- OB Old Burmese: the language of the 11th-13th century inscriptions
- WB written Burmese - the orthographical form of the modem language
- CB colloquial Burmese
- MB modem Burmese = colloquial Burmese
- FB formal Burmese

## Spelling Checker

## Stopword Removal

# Use Cases

## Summary Keyword Extraction

### Model: Modified TF-IDF Keyword Ranking

- Tokenize
- Tag POS
- Extract Verbs, Adjectives, Nouns and Adverbs
- Generate TF-IDF score on the widespread corpus
- Penalize scores

## Sentiment Analysis

### Sentiment Lexicon

Building up the sentiment lexicon is pretty much a guess work.

### Sentiment Word Extraction

Due to the nature of Burmese, non reducing and reducing compound words can be ambiguous in their word separation. This case should be considered.

1. Noun-verb: အကျိုး/n ပျက်စီး/v
2. Verb-verb: ခိုး/v ယူ/v

This could be avoided with a sufficiently powerful POS tagger so that we are not just looking at the word, we are looking at the part of speech as well.

E.g. ညာမပြောနဲ့ကွာ။ Both ညာ/v (lie) ညာ/n (right) exists.

It might be very useful to have an algorithm that transforms a sentiment word of a certain form, let's say colloquial form, to literary form, where at the simplest level of modifications is removing the consonant pair, လိမ်ညာ => ညာ and use the sentiment lexicon of the same form to match.
