with open("word_key_map.txt", "w") as word_key_map_file:
    word_key_map_file.write("word_key_map = {\n")

    with open("corpus.txt", "r") as corpus_file:
        key = 0
        for word in corpus_file:
            word_key_map_file.write(
                f'    "{word.strip().lower()}": "{format(key, ' b').strip()}",\n'
            )
            key += 1

    word_key_map_file.write(f'    ".": "{str(1) * 16}"\n')
    word_key_map_file.write("}\n")
