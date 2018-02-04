from collections import defaultdict, Counter
from itertools import chain, takewhile
import argparse
import os
import string

import nltk

CHEADER = "\033[92m"
CTOKEN = "\033[91m"
CSEP = "\033[91m"
CWORD = "\033[95m"


parser = argparse.ArgumentParser(description='Ejercicios con NLTK')
parser.add_argument('-q', action='store', dest='q_', default=None,
                    help='Numero de la pregunta. Por defecto todas.')
parser.add_argument('--corpus', dest='corpus', action='store',
                    default='./corpus', help=('Directorio donde se encuentran '
                                        'el corpus. Por defecto ./corpus/'))


def print_header_question(index):
    def print_header_question_decorator(func):
        def func_wrapper(*args):
            print()
            [print(CHEADER + "{:*^100}".format(s)) for s in \
                    ["", " Presgunta %s " % index, ""]]
            print()
            return func(*args)
        return func_wrapper
    return print_header_question_decorator


def _print_sentence(token, func=str):
    start = CTOKEN + "SENTENCE: "
    token = CWORD + " {}|{} ".format(CSEP, CWORD).join(
        [func(t) for t in token])
    print(start + token)


def _print_sentence_tags(token):
    _print_sentence(token, func="-".join)


def _print_tokens(tokens, func=_print_sentence):
    for t in tokens:
        func(t)


def _print_answer(question, answer):
    print("{}{}: {}{}".format(CTOKEN, question, CWORD, str(answer)))


def _print_header(header):
    header_mod = [""] + header
    print(CHEADER + "+{}+".format("-" * 20) * len(header_mod))
    print("".join(["|{:^20}|".format(h) for h in header_mod]))
    print("+{}+".format("-" * 20) * len(header_mod))


def _print_row(row):
    print("".join(["|{:^20}|".format(r) for r in row]))
    print("+{}+".format("-" * 20) * len(row))


def _print_matrix(matrix, header):
    _print_header(header)
    count = 0
    for pk, row in matrix.items():
        if count > 20:
            input(CTOKEN + "\nPress Enter to continue...")
            _print_header(header)
            count = 0
        _print_row([pk] + [int(row[h]) for h in header])
        count += 1

def get_tokens_from_file(f_, clean_punt=True, flat=False):
    sentences = nltk.tokenize.sent_tokenize(f_.read().lower())
    stop_words = nltk.corpus.stopwords.words('english')
    tokens = [[w for w in nltk.word_tokenize(s) if w.lower() \
            not in stop_words] for s in sentences]
    if clean_punt:
        tokens = [[w for w in s if w not in string.punctuation] for s in \
                  tokens]
    if flat:
        tokens =  chain.from_iterable(tokens)
    return tokens

@print_header_question(1)
def q_1(corpus):
    with open(os.path.join(corpus, 'Data_Science.txt')) as f_:
        text = f_.read()
        clean_text = text.translate(str.maketrans("", "", string.punctuation))
        print(CWORD + clean_text)


@print_header_question(3)
def q_3(corpus):
    with open(os.path.join(corpus, 'Data_Science.txt')) as f_:
        _print_tokens(get_tokens_from_file(f_))


@print_header_question(6)
def q_6(corpus):
    with open(os.path.join(corpus, 'Data_Science.txt')) as f_:
        stem = nltk.stem.PorterStemmer()
        tokens = [[stem.stem(w) for w in s] \
                for s in get_tokens_from_file(f_)]
        _print_tokens(tokens)

MAPPER_TAG_TO_POS = dict(NN='n', VB='v', JJ='a', RB='r')

def _convert_tag_to_pos(tag):
    return MAPPER_TAG_TO_POS.get(tag[:2], 'n')


@print_header_question(8)
def q_8(corpus):
    with open(os.path.join(corpus, 'Data_Science.txt')) as f_:
        lem = nltk.stem.WordNetLemmatizer()
        tokens = get_tokens_from_file(f_)
        tokens = [[lem.lemmatize(w[0], _convert_tag_to_pos(w[1])) for w in s] \
                for s in nltk.pos_tag_sents(tokens)]
        _print_tokens(tokens)


def _multiple_pos_tag_sents(tokens):
    for t in tokens:
        zip_ = zip(nltk.pos_tag(t), nltk.pos_tag(t, tagset="universal"))
        yield [(d[0], d[1], u[1]) for d, u in zip_]


@print_header_question(10)
def q_10(corpus):
    with open(os.path.join(corpus, 'Data_Science.txt')) as f_:
        lem = nltk.stem.WordNetLemmatizer()
        tokens = get_tokens_from_file(f_)
        tokens = [t for t in _multiple_pos_tag_sents(tokens)]
        _print_tokens(tokens, func=_print_sentence_tags)


FILE_LIST = ["Data_Science.txt", "Data.txt", "Credit_Card.txt", "Science.txt"]


@print_header_question(14)
def q_14(corpus):
    tokens_by_file = list()
    for f_name in FILE_LIST:
        with open(os.path.join(corpus, f_name)) as f_:
            tokens_by_file.append(list(get_tokens_from_file(f_, flat=True)))
    total_word_count = len(set(chain(*tokens_by_file)))
    _print_answer("Numero total de palabras diferentes", total_word_count)
    _print_answer("Tamaño del vocabulario for texto", "")
    for i, l in enumerate(tokens_by_file):
        vocabulary_count = len(set(l))
        _print_answer("\t" + FILE_LIST[i], vocabulary_count)
    _print_answer("Vocabulario total", ", ".join(set(chain(*tokens_by_file))))
    counter = Counter()
    for l in tokens_by_file:
        counter.update(set(l))
    unique_words = dict(takewhile(lambda x: x[1] <= 1,
                                  counter.most_common()[::-1]))
    _print_answer("Palabras que aparecen en más de un texto", ", ".join(
        unique_words))
    repeated_words = dict(takewhile(lambda x: x[1] > 1, counter.most_common()))
    _print_answer("Palabras que aparecen en más de un texto", ", ".join(
        ["%s(%d)" % (w[0], w[1]) for w in repeated_words.items()]))


@print_header_question(15)
def q_15(corpus):
    tokens_by_file = dict()
    for f_name in FILE_LIST:
        with open(os.path.join(corpus, f_name)) as f_:
            tokens_by_file[f_name] = list(get_tokens_from_file(f_, flat=True))
    total_word_count = len(set(chain(*tokens_by_file.values())))
    _print_answer("Numero total de palabras diferentes", total_word_count)
    matrix = defaultdict(lambda: defaultdict(int))
    for f_name, tokens in tokens_by_file.items():
        for token in tokens:
            matrix[token][f_name] += 1
    _print_matrix(matrix, FILE_LIST)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.q_:
        func = locals().get("q_%s" % args.q_, None)
        if func:
            func(args.corpus)
            exit(0)
        print("La pregunta escogida no es válida.")
        exit(1)
    for name, func in [(k, v) for k, v in locals().items()]:
        if name.startswith('q_'):
            func(args.corpus)
            input("Press Enter to continue...")
