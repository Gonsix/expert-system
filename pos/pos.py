
import sys
import nltk
import pandas as pd
import numpy as np

RED = '\033[31m'
GREEN = '\033[32m'
BLUE = '\033[34m'
END = '\033[0m'

df = None # global

def main():
    global df
### Initial running
    with open("./K1_dataset.txt") as f:
        K1_txt = f.read()

    with open("./K2_dataset.txt") as f:
        K2_txt = f.read()

    with open("./Q_dataset.txt") as f:
        Q_txt = f.read()

    df = pd.DataFrame([
        ["K1", K1_txt], 
        ["K2", K2_txt],
        ["Q", Q_txt]
    ],
    columns=['author', 'message'],)

    df.insert(2,"word_pos_list",[ create_word_pos_list(message) for message in df['message']],True)


    while True:
        input_num = input('''Select the operation
    1: Serch by word/ word + POS (e.g absolutely JJ)
    2: Identify the suspected
    3: Exit
==> ''')
        if input_num == '1':
            query = input("Input Query: ")
            search(query)
        elif input_num == '2':
            pos_patterns, pos_vectors = count_pos_patterns(df['word_pos_list'])
            df['pos_vec'] = pos_vectors
            K_df = df.loc[0:1]
            Q_df = df.loc[2]
            most_suspected = predict(Q_df, K_df)
            print(BLUE + f"Most suspected :{most_suspected}" + END )
            sys.exit(0)

        elif input_num == '3':
            sys.exit(0)


'''
This function returns a list of tuples of (word, PoS) from a document.
'''
def create_word_pos_list(message):
    tokenized_txt = nltk.word_tokenize(message)
    return nltk.pos_tag(tokenized_txt)

WINDOW_SIZE = 2
def count_pos_patterns(documents):
    width = WINDOW_SIZE
    pos_patterns = []
    pos_vectors = [[] for _ in range(len(documents))]
    for docId, document in enumerate(documents):
        len_doc = len(document)
        for i in range(len_doc - (width-1)):
            key_str = ""
            key_str += document[i][0] # word

            for j in range(1, width):
                key_str += " " + document[i+j][1] # POS

            if key_str not in pos_patterns:
                pos_patterns.append(key_str)
                # パターンが現れたドキュメント -> 1 , それ以外　-> 0
                for i in range(len(pos_vectors)): # loop for K1, K2, Q
                    if i == docId:
                        pos_vectors[i].append(1)
                    else:
                        pos_vectors[i].append(0)

            else: 
                idx = pos_patterns.index(key_str)
                pos_vectors[docId][idx] += 1

    return (pos_patterns, pos_vectors)


# start からend までのIDの配列を返す
def extract_features(freq_vector, start=0, end=20):

    setX = set(freq_vector) # 最大値を順に取り出すため set を作成

    count = 0

    result = []

    while count<end:
        try:
            max_value = max(setX)
        except ValueError:
            return result

        max_index = freq_vector.index(max_value)
        # max_word = words[max_index]

        setX.remove(max_value)

        if count>= start:
            result.append(max_index)
        count += 1
    return result



# return the score of how many types of pattern are appered in both vectors?
def get_similarity(feature_vector1,feature_vector2): 
    return len(set(feature_vector1) & set(feature_vector2))



def predict(Q_df,K_df):
    start = 0
    end = 20
    suspected = [author for author in K_df['author'] ]
    while(len(suspected) > 1):
        print("Suspected : ", end="")
        print(set(suspected))
        Q_features = extract_features(Q_df['pos_vec'], start, end)
        similarityWithQ = {}

        for author, reference_vector in (K_df['author'], K_df['pos_vec']):
            if author in suspected: #
                feature_vector = extract_features(reference_vector,start, end)
                score = get_similarity(feature_vector,Q_features)
                similarityWithQ[author]=score

        # innocent_list に含まれない著者の中から1人を選ぶ

        innocent = min(similarityWithQ, key=similarityWithQ.get)
        if input(f'Do you want to rule out {innocent} in top {end} patterns ? (y/n) ') == 'y':
            suspected.remove(innocent)
        end += 20
    return suspected[0]

def search(query_string):
    query = query_string.split()
    print("query : ", query)
    for docId, document in enumerate(df['word_pos_list']):
        for idx, (word, pos), in enumerate(document):
            # print(f'(word, pos): {word}, {pos}')
            if word.casefold() == query[0].casefold(): # undistinguith Upper or Lower case
                # check the following words matche the sequence of words
                foundFlg = True
                # print("Following ", query[1:])

                if len(query)>1:

                    for i, query_following in enumerate(query[1:]):
                        w_following = document[idx+1+i][0] # follwoing word in the document
                        pos_following = document[idx+1+i][1] # follwoing pos in the document
                        if query_following.casefold() == w_following.casefold() or query_following == pos_following:
                            continue
                        foundFlg = False
                    
                if foundFlg is True:
                    if docId == 0:
                        print("K1:  ", end="")
                    elif docId == 1:
                        print("K2:  ", end="")
                    elif docId == 2:
                        print("Q :  ", end="")


                    # 前後6 文字　出力
                    pid = idx - 6
                    for _ in range(6):
                        if pid < 0:
                            print("    ", end="")
                        elif pid >= 0:
                            print(document[pid][0], end=" ")
                        pid += 1

                    print(GREEN + word + END, end=" ")

                    sid = idx + 1
                    for _ in range(6):
                        if sid < len(document):
                            print(document[sid][0], end=" ")
                        else:
                            print("    ", end="")
                        sid += 1

                    print()
    print()

def identify_suspected():
    pass

if __name__=='__main__':
    
    main()
