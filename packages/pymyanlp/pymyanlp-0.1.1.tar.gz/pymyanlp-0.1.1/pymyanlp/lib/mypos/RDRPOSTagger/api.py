import sys
import os

# Ensures relative imports to work without chdir :)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from multiprocessing import Pool
from Utility.Config import NUMBER_OF_PROCESSES
from pSCRDRtagger.RDRPOSTagger import (
    RDRPOSTagger,
    unwrap_self_RDRPOSTagger,
)

from SCRDRlearner.SCRDRTree import Node, FWObject, getConcreteValue, getCondition


class InMemoryRDRPOSTagger(RDRPOSTagger):
    def tagRawCorpus(self, DICT, rawCorpusPath):
        lines = rawCorpusPath.split("\n")
        # Change the value of NUMBER_OF_PROCESSES to obtain faster tagging process!
        pool = Pool(processes=NUMBER_OF_PROCESSES)
        taggedLines = pool.map(
            unwrap_self_RDRPOSTagger,
            zip([self] * len(lines), [DICT] * len(lines), lines),
        )
        # Ricky: just return the tagged lines instead of saving
        # to a file
        return taggedLines

    # copied object
    def constructSCRDRtreeFromRDRfile(self, rulesFilePath):
        self.root = Node.Node(FWObject(False), "NN", None, None, None, [], 0)
        currentNode = self.root
        currentDepth = 0

        rulesFile = open(
            rulesFilePath, "r", encoding="utf-8", errors="ignore"
        )  # Ricky: use utf-8 encoding
        lines = rulesFile.readlines()

        for i in range(1, len(lines)):
            line = lines[i]
            depth = 0
            for c in line:
                if c == "\t":
                    depth = depth + 1
                else:
                    break

            line = line.strip()
            if len(line) == 0:
                continue

            temp = line.find("cc")
            if temp == 0:
                continue

            condition = getCondition(line.split(" : ", 1)[0].strip())
            conclusion = getConcreteValue(line.split(" : ", 1)[1].strip())

            node = Node.Node(condition, conclusion, None, None, None, [], depth)

            if depth > currentDepth:
                currentNode.exceptChild = node
            elif depth == currentDepth:
                currentNode.elseChild = node
            else:
                while currentNode.depth != depth:
                    currentNode = currentNode.father
                currentNode.elseChild = node

            node.father = currentNode
            currentNode = node
            currentDepth = depth


# copied object
def readDictionary(inputFile):
    dictionary = {}
    lines = open(
        inputFile, "r", encoding="utf-8", errors="ignore"
    ).readlines()  # Ricky: use utf-8 encoding
    for line in lines:
        wordtag = line.strip().split()
        dictionary[wordtag[0]] = wordtag[1]
    return dictionary


def pSCRDRtagger(input_text: str, model_path: str, lexicon_path: str):
    r = InMemoryRDRPOSTagger()
    # print("\n=> Read a POS tagging model from " + model_path)
    r.constructSCRDRtreeFromRDRfile(model_path)
    # print("\n=> Read a lexicon from " + lexicon_path)
    DICT = readDictionary(lexicon_path)
    # print("\n=> Perform POS tagging on " + input_text)
    lines = r.tagRawCorpus(DICT, input_text)
    tagged_words = []
    for l in lines:
        tagged_words.extend(
            [
                ("".join(splt[:-1]), splt[-1])
                for p in l.split(" ")
                if (splt := p.split("/"))
            ]
        )
    return tagged_words
