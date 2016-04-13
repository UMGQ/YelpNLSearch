from __future__ import print_function

import nltk




def extract_entity_names(t):
    entity_names = []
    
    if hasattr(t, 'label') and t.label():
        if t.label() in ['PERSON' , 'GPE' , 'ORGANIZATION', 'FACILITY']: 
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))
                
    return entity_names

def do_query_NLP(request_text):
    #with open('sample.txt', 'r') as f:
    #    sample = f.read()
    sample = str(request_text)
         
    sentences = nltk.sent_tokenize(sample)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=False)


    entity_names = []
    for tree in chunked_sentences:
        # Print results per sentence
        # print extract_entity_names(tree)
        print(tree)
        entity_names.extend(extract_entity_names(tree))


    # Print all entity names
    #print entity_names

    # Print unique entity names

    name_dict = {}

    for name in entity_names:
        n_list = name.split()
        name_dict[n_list[0]] = name



    chunking_list =  list(tree.flatten())

    print(name_dict)
    #print(chunking_list)

    location = 'N/A'

    if len(chunking_list) > 1:
        for index in range(1, len(chunking_list)):
            if chunking_list[index][0] in name_dict and chunking_list[index-1][1] == 'IN':
                location = name_dict[chunking_list[index][0]]
    f = open('out.txt', 'w')
    f.write(location)
    f.close()

    return location




