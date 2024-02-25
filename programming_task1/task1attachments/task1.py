from cs145lib.task1 import Channel, node_main

word_key_map = {}  # Exclusively for the sender function only.
key_word_map = {}  # Exclusively for the receiver function only.

# Load the word_key_map and key_word_map from the key_word_map.txt file.
# The key_word_map is a dictionary that maps a 16-bit key to a word.
# The word_key_map is a dictionary that maps a word to a 16-bit key.
with open("corpus.txt", "r") as corpus_file:
    key = 0
    for word in corpus_file:
        word_key_map[word.strip().lower()] = format(key, "016b")
        key_word_map[format(key, "016b")] = word.strip().lower()
        key += 1

    # Add the "1111": "." key-value pair to the key_word_map.
    key_word_map["1111"] = "."


def sender(channel: Channel, sentence: str) -> None:
    # Signal the start of the communication.
    channel.send(1)

    # Remove "." from the sentence.
    sentence = sentence[:-1]

    # Send the bits for each word in the sentence.
    for word in sentence.split():
        bits = word_key_map[word.lower()]
        for bit in bits:
            channel.send(int(bit))

    # Signal the end of the communication.
    # Four most significant bits (1111) signify the end of the communication.
    # This works because 111 is the highest possible MSBs for a 16-bit key
    # (within the context of the corpus.txt file).
    #
    # For instance, the last word in the corpus "zulus" has a 16-bit
    # key "1110001011111101" (notice that the first four MSBs are "1110").
    for _ in range(4):
        channel.send(1)


def receiver(channel: Channel) -> str:
    # Wait for the first "1"
    while channel.get() == 0:
        pass

    # Read the bits (by chunks of 16 bits) and convert them to words.
    sentence = []
    while True:
        curr_bit_string = ""
        for _ in range(16):
            curr_bit_string += str(channel.get())
            if curr_bit_string == "1111":
                break

        word = key_word_map[curr_bit_string]
        if word == ".":
            break

        sentence.append(word)

    return (" ".join(sentence) + ".").capitalize()


if __name__ == "__main__":
    node_main(sender=sender, receiver=receiver)
