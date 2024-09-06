import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import gutenberg
import msvcrt

nltk.download('punkt')
nltk.download('gutenberg')

train_data = gutenberg.sents()

first_possible_words = {}
second_possible_words = {}
transitions = {}

def expandDict(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)

def get_next_probability(given_list):  # returns dictionary
    probability_dict = {}
    given_list_length = len(given_list)
    for item in given_list:
        probability_dict[item] = probability_dict.get(item, 0) + 1
    for key, value in probability_dict.items():
        probability_dict[key] = value / given_list_length
    return probability_dict

def trainMarkovModel():
    for line in train_data:
        tokens = [word.lower() for word in line]
        tokens_length = len(tokens)
        for i in range(tokens_length):
            token = tokens[i]
            if i == 0:
                first_possible_words[token] = first_possible_words.get(token, 0) + 1
            else:
                prev_token = tokens[i - 1]
                if i == tokens_length - 1:
                    expandDict(transitions, (prev_token, token), 'END')
                if i == 1:
                    expandDict(second_possible_words, prev_token, token)
                else:
                    prev_prev_token = tokens[i - 2]
                    expandDict(transitions, (prev_prev_token, prev_token), token)

    first_possible_words_total = sum(first_possible_words.values())
    for key, value in first_possible_words.items():
        first_possible_words[key] = value / first_possible_words_total

    for prev_word, next_word_list in second_possible_words.items():
        second_possible_words[prev_word] = get_next_probability(next_word_list)

    for word_pair, next_word_list in transitions.items():
        transitions[word_pair] = get_next_probability(next_word_list)

def next_word(tpl, top_n=5):
    if isinstance(tpl, str):  # it is the first word of the string.. return from the second word
        d = second_possible_words.get(tpl)
        if d is not None:
            sorted_words = sorted(d.items(), key=lambda item: item[1], reverse=True)
            return [word for word, prob in sorted_words[:top_n]]
    elif isinstance(tpl, tuple):  # incoming words are a combination of two words.. find the next word now based on transitions
        d = transitions.get(tpl)
        if d is None:
            return []
        sorted_words = sorted(d.items(), key=lambda item: item[1], reverse=True)
        return [word for word, prob in sorted_words[:top_n]]
    return None  # wrong input.. return nothing

trainMarkovModel()  # generate first, second words list and transitions

########## demo code below ################
print("Usage: start typing.. program will suggest words. Press tab to choose the first suggestion or keep typing\n")

c = ''
sent = ''
last_suggestion = []
while c != b'\r':  # stop when user presses enter
    if c != b'\t':  # if the previous character was tab, then after auto-completion don't wait for user input.. just show suggestions
        c = msvcrt.getch()
    else:
        c = b' '
    if c != b'\t':  # don't print tab etc
        print(str(c.decode('utf-8')), end='', flush=True)
    sent += str(c.decode('utf-8'))  # create word on space
    if c == b' ':
        tkns = sent.split()
        if len(tkns) < 2:  # only first space encountered yet
            last_suggestion = next_word(tkns[0].lower())
            print(last_suggestion, end='  ', flush=True)
        else:  # send a tuple
            last_suggestion = next_word((tkns[-2].lower(), tkns[-1].lower()))
            print(last_suggestion, end='  ', flush=True)
    if c == b'\t' and len(last_suggestion) > 0:  # print last suggestion on tab
        print(last_suggestion[0], end='  ', flush=True)
        sent += " " + last_suggestion[0]