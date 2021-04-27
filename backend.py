from io import open
from conllu import parse_incr
import re
import warnings
from sklearn_crfsuite import CRF
import pickle
from moviepy.editor import VideoFileClip, concatenate_videoclips
import speech_recognition as sr

r=sr.Recognizer()
print("Please Talk")
with sr.Microphone() as source:
    audio_data=r.record(source,duration=5)
    text=r.recognize_google(audio_data)
    print("Voice to text module : "+text)

def extract_features(sentence, index):
    return {
        'word':sentence[index],
        'is_first':index==0,
        'is_last':index ==len(sentence)-1,
        'is_capitalized':sentence[index][0].upper() == sentence[index][0],
        'is_all_caps': sentence[index].upper() == sentence[index],
        'is_all_lower': sentence[index].lower() == sentence[index],
        'is_alphanumeric': int(bool((re.match('^(?=.*[0-9]$)(?=.*[a-zA-Z])',sentence[index])))),
        'prefix-1':sentence[index][0],
        'prefix-2':sentence[index][:2],
        'prefix-3':sentence[index][:3],
        'prefix-3':sentence[index][:4],
        'suffix-1':sentence[index][-1],
        'suffix-2':sentence[index][-2:],
        'suffix-3':sentence[index][-3:],
        'suffix-3':sentence[index][-4:],
        'prev_word':'' if index == 0 else sentence[index-1],
        'next_word':'' if index < len(sentence) else sentence[index+1],
        'has_hyphen': '-' in sentence[index],
        'is_numeric': sentence[index].isdigit(),
        'capitals_inside': sentence[index][1:].lower() != sentence[index][1:]
    }



ud_filename = 'ud_crf_postagger.sav'
crf_from_pickle = pickle.load(open(ud_filename, 'rb'))



#First, we pass the sentence and quickly tokenize it.
#sentences = ['She sells seashells by the seashore.', 'We should cross the road using zebra crossing.']
# sentences=["Love thy nation!","The waiter leaves the hotel.","The tree has many leaves?", 'India is my country.','Which is my side??', 'How is my dress??']

sentences = [text]

ud_sents = []
for sent in sentences:
    #sent = "Playing is my hobby."
    features = [extract_features(sent.split(), idx) for idx in range(len(sent.split()))]
    ud_results = crf_from_pickle.predict_single(features)

    #These line magics are just there to make it a neaty print, making a (word, POS) style print;
    ud_tups = [(sent.split()[idx], ud_results[idx]) for idx in range(len(sent.split()))]

    #The results come out here! Notice the difference in tags.
    ud_sents.append(ud_tups)
print('\n\tPOS Tagging Done\t\n')
for ud_tups in ud_sents:
    print(ud_tups)

print('\n\tPunctations Removed\t\n')
punctuations = [',', '?', '!', '.']
def removePunctuations(word):
    new_word = ""
    for ch in word:
        if ch in punctuations:
            continue
        else:
            new_word = new_word + ch
    return new_word

def filter(ud_sents):
    new_sents = []
    for ud_tups in ud_sents:
        new_tups = []
        for tup in ud_tups:
            word = tup[0]
            tag = tup[1]
            word = word.lower()
            word = removePunctuations(word)
            new_tups.append((word, tag))
        new_sents.append(new_tups)
        print(new_tups)
    return new_sents

ud_sents = filter(ud_sents)

print('\n\tSentence Reorodering\t\n')
#List to store reordered sentences
reordered_sent_list = []

#Looping through each sentence and reordeing it
for sent in ud_sents:
    reordered_sent = []
    verbs = []
    for tup in sent:
        if tup[1] == 'VERB':
            verbs.append(tup)
        else:
            reordered_sent.append(tup)
    reordered_sent = reordered_sent + verbs
    start_word_tup = reordered_sent[0]
    print(len(start_word_tup[0]))
    if len(start_word_tup[0]) > 2:
        if ((start_word_tup[0][0] == 'w' or start_word_tup[0][0] == 'W' and start_word_tup[0][1] == 'h' or start_word_tup[0][1] == 'H') or (start_word_tup[0] == 'how' or start_word_tup[0] == 'How')):
            reordered_sent.remove(start_word_tup)
            reordered_sent.append(start_word_tup)
    reordered_sent_list.append(reordered_sent)



for sent in reordered_sent_list:
    print(sent)

print('\n\tStop Word Eliminator\t\n')

stop_words = ['to', 'm', 'mustn', 'myself', 'a', 'because', 'no', 'don', 'had', "don't", "doesn't", 'once', 'is', 'own', "you've", 'each', 'into', 'both', "weren't", "mightn't", 'nor', 'are', 'were', 'too', 've', 'has', 'hasn', 'very', 'against', 'did',  'other', 'not', 'haven', "that'll", 'being', 'll', 'or', "hasn't", 'an', 'the', 'so', "didn't", 'was', 'shouldn', 'aren', "couldn't", 'by', 'ma', 'been', 'having', 's', 'as', "needn't", 'weren', "wasn't", "you'd", 'for', 'doesn', 'couldn', 'while', 'didn', "shouldn't", 'wouldn', 'am', 'and', 'off', 'such', 'hadn', "you'll", 'mightn', 'wasn', "isn't", 'but', "she's", 'isn', 'have', 'o', "hadn't", "won't", 'further', "shan't", 'doing', 'just', "mustn't", 'd', "aren't", "should've", 'be', 'does', 'shan', "it's", 'than', 'most',  'y', 'needn', "haven't", 're', 'if', "you're", "wouldn't", 't', 'ain','much','wow','alas','hurray','bravo','congratulations','congrats','ahem','aha','eureka']
isl_sent_list = []
for reordered_sent in reordered_sent_list:
    isl_sent = []
    for tup in reordered_sent:
        if stop_words.count(tup[0]) == 0:
            isl_sent.append(tup)
    isl_sent_list.append(isl_sent)

for isl_sent in isl_sent_list: 
    print(isl_sent)

print('\n\tLemmatization\t\n')


def inflect_noun_singular(word):
    irregular_dict = pickle.load(open('lemma_dictionary.sav','rb'))
    consonants = "bcdfghjklmnpqrstwxyz"
    vowels = "aeiou"
    word = str(word).lower()
    if len(word) < 2:
        return word
    if word.endswith('s'):
        if len(word) > 3:
            #Leaves, wives, thieves
            if word.endswith('ves'):
                if len(word[:-3]) > 2:
                    return word.replace('ves','f')
                else:
                    return word.replace('ves','fe')
            #Parties, stories
            if word.endswith('ies'):
                return word.replace('ies','y')
            #Tomatoes, echoes
            if word.endswith('es'):
                if word.endswith('ses') and word[-4] in vowels:
                    return word[:-1]
                if word.endswith('zzes'):
                    return word.replace('zzes','z')
                return word[:-2]
            if word.endswith('ys'):
                return word.replace('ys','y')
            if word.endswith('ss'):
                return word
        return word[:-1]
        if word in irregular_dict:
            return irregular_dict[word]
    return word

lemma_filename = 'lemma_dictionary.sav'
lemma_dict_from_pickle = pickle.load(open(lemma_filename, 'rb'))

def lemmatize2(word, pos, lemmatize_plurals=True):
        if word is None:
            return ''
        if pos is None:
            pos = ''
        word = str(word).lower()
        pos = str(pos).upper()
        if pos == "NOUN" and lemmatize_plurals:
            return inflect_noun_singular(word)
        if word in lemma_dict_from_pickle:
            if pos in lemma_dict_from_pickle[word]:
                return lemma_dict_from_pickle[word][pos]
        return word

lema_isl_sent_list = []
for isl_sent in isl_sent_list:
    print(isl_sent)
    isl_sent_lem = []
    for word_tuple in isl_sent:
        isl_sent_lem.append(lemmatize2(word_tuple[0], word_tuple[1]))
    lema_isl_sent_list.append(isl_sent_lem)

for sent in lema_isl_sent_list:
    print(sent)

print('\n\tVideo Conversion Module\t\n')


for isl_sent in lema_isl_sent_list:
    video_array = []
    print(isl_sent)
    for word_tuple in isl_sent:
        video_array.append(VideoFileClip("video_files/" + word_tuple + ".mp4"))
        print("video_files/" + word_tuple + ".mp4")

    print(video_array[0])

    final_clip = concatenate_videoclips(video_array)
    final_clip.write_videofile("my_concatenation.mp4")
