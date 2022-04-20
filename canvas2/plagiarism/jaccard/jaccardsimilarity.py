import nltk
import re
from collections import deque
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist
from nltk.corpus import brown
from pathlib import Path

global frequencyList
frequencyList = FreqDist(x.lower() for x in brown.words())
global seen
seen = dict()


def parseTextFile(inputFile: str) -> list:
    """
    Parse text file and return a list of words
    """
    with open(inputFile, "r") as f:
        words = f.read().split()
    return wordCompression(words)


def parseText(inputText: str) -> list:
    """
    Parse plaintext and return a list of words
    """
    sanitizedInput = re.sub(r"[^\w\s]", "", inputText).split()
    return wordCompression(sanitizedInput)


def wordSynonym(word: str) -> str:
    if word in seen:
        return seen[word]
    else:
        synonyms = set()
        for syn in nltk.corpus.wordnet.synsets(word):
            for l in syn.lemmas():
                synonyms.add(l.name())
        stack = deque()
        for syn in synonyms:
            if not stack:
                stack.append((syn, frequencyList[syn]))
            else:
                if frequencyList[syn] > stack[-1][1]:
                    stack.pop()
                    stack.append((syn, frequencyList[syn]))
        if stack:
            seen[word] = stack[0][0]
            return seen[word]
        else:
            seen[word] = word
            return word


def wordCompression(words: list) -> list:
    """
    Parse input text as a list and return a list free of stopwords
    Ignore any non-alphanumeric characters
    Ignore any words that are among the 1000 most common words in English
    Words are lemmatized into their base form
    Resulting words get reduced to their most common synonym (this combats plagiarism by rewording)
    1000 most common words in English source: https://gist.github.com/deekayen/4148741
    """

    # Create a set from the 1000 most common words in English
    ignoreThese = set()

    stopwordsPath = Path(__file__).parent.parent / "assets" / "mostCommonWords.txt"
    with open(stopwordsPath, "r") as f:
        for line in f:
            ignoreThese.add(line.strip())

    # Clean input text by removing non-alphanumeric characters and converting to lowercase
    words = [
        word.lower()
        for word in words
        if word.isalnum() and word.lower() not in ignoreThese
    ]

    # Lemmatize words (e.g. "dogs" -> "dog")
    lemmatizer = WordNetLemmatizer()
    words = [lemmatizer.lemmatize(word) for word in words]

    # Reduce words to their most common synonym
    words = [wordSynonym(word) for word in words]

    # Filter out words that are among the 1000 most common words in English once more
    words = [word for word in words if word.isalnum()
             and word not in ignoreThese]
    return words


def shingles(words: list, k=5) -> set:
    """
    Return a list of shingles of length k
    Source: http://ethen8181.github.io/machine-learning/clustering_old/text_similarity/text_similarity.html#jaccard-similarity (k-shingling, modified)
    """
    words = " ".join(words)
    shingles = set()
    for i in range(len(words) - k + 1):
        shingles.add("".join(words[i: i + k]))
    return shingles


def shinglesString(text: str) -> str:
    """
    Return a string representation of a set of shingles
    """
    text = parseText(text)
    sh = shingles(text)
    return repr(sh)


def similarityScore(shingle1: set, shingle2: set) -> float:
    """
    Return the similarity score of two shingles
    """
    return len(shingle1 & shingle2) / len(shingle1 | shingle2)


def compareDocs(doc1: str, doc2: str, k: int) -> float:
    """
    Return the similarity score of two documents
    """
    shingles1 = shingles(parseText(doc1), k)
    shingles2 = shingles(parseText(doc2), k)
    return similarityScore(shingles1, shingles2)
