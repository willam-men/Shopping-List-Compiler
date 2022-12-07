from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
import json
import numpy as np
import pandas as pd
TRAINING_LENGTH = 16
import requests


def encode(tokenizer, length, lines):
    seq = tokenizer.texts_to_sequences(lines)
    seq = pad_sequences(seq, maxlen=length, padding='post')
    return seq

def get_word(n, tokenizer):
    for word, index in tokenizer.word_index.items():
        if index == n:
            return word
    return None

def extract_string(preds, label_tokenizer):
    preds_text = []
    for i in preds:
        temp = []
        for j in range(len(i)):
            t = get_word(i[j], label_tokenizer)
            if j > 0:
                if(t == get_word(i[j-1], label_tokenizer)) or (t == None):
                    temp.append('')
                else:
                    temp.append(t)
            else:
                if (t == None):
                    temp.append('')
                else:
                    temp.append(t)
        preds_text.append(' '.join(temp))
    return preds_text


def main():
    with open('training_tokenizer.json') as f:
        data = json.load(f)
        training_tokenizer = tokenizer_from_json(data)
    with open('label_tokenizer.json') as p:
        data = json.load(p)
        label_tokenizer = tokenizer_from_json(data)
    ingredients = pd.read_csv('./data_test.txt', delimiter='\n', header=None)
    X_test = encode(training_tokenizer, TRAINING_LENGTH, ingredients[0])
    print(X_test)

    data = json.dumps({"signature_name": "serving_default", "instances": X_test[0:].tolist()})
    headers = {"content-type": "application/json"}
    json_response = requests.post('http://localhost:8501/v1/models/saved_model:predict', data=data, headers=headers)
    predictions = json.loads(json_response.text)['predictions']
    preds = np.argmax(predictions, axis=-1)
    result = extract_string(preds, label_tokenizer)
    print(result)


if __name__=="__main__":
    main()