with open("key_word_map.txt", "w") as key_word_map_file:
    key_word_map_file.write("key_word_map = {\n")

    with open("corpus.txt", "r") as corpus_file:
        key = 0
        for word in corpus_file:
            key_word_map_file.write(
                f'    "{format(key, ' b').strip()}": "{word.strip().lower()}",\n'
            )
            key += 1

    key_word_map_file.write(f'    "{str(1) * 16}": "."\n')
    key_word_map_file.write("}\n")
