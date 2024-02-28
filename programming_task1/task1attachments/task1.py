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
    repetition_number = 15

    def send_bit_n_times(bit: int, repetition_number: int) -> None:
        for _ in range(repetition_number):
            channel.send(bit)

    # Signal the start of the communication.
    for _ in range(repetition_number):
        channel.send(1)

    # Remove "." from the sentence.
    sentence = sentence[:-1]

    # Send the bits for each word in the sentence.
    for word in sentence.split():
        bits = word_key_map[word.lower()]
        for bit in bits:
            send_bit_n_times(int(bit), repetition_number)

    # Signal the end of the communication.
    # Four most significant bits (1111) signify the end of the communication.
    # This works because 111 is the highest possible MSBs for a 16-bit key
    # (within the context of the corpus.txt file).
    #
    # For instance, the last word in the corpus "zulus" has a 16-bit
    # key "1110001011111101" (notice that the first four MSBs are "1110").
    for _ in range(4):
        send_bit_n_times(1, repetition_number)


def receiver(channel: Channel) -> str:
    buffer_size = 15
    buffer_queue = []  # Size: 10
    buffer_read_cooldown = 0
    max_bits = 3000
    raw_bits_read = 0

    def add_bit_to_buffer(bit: int) -> None:
        nonlocal buffer_read_cooldown
        nonlocal raw_bits_read

        if len(buffer_queue) == buffer_size:
            buffer_queue.pop(0)

        buffer_queue.append(bit)
        buffer_read_cooldown += 1
        raw_bits_read += 1

    def read_buffer_identity(buffer_queue: list) -> int:
        nonlocal buffer_read_cooldown

        if buffer_read_cooldown < buffer_size:
            return 0

        count_ones = buffer_queue.count(1)
        count_zeros = buffer_queue.count(0)

        buffer_read_cooldown = 0

        return 1 if count_ones > count_zeros else 0

    # Wait for the start signal.
    while True:
        add_bit_to_buffer(channel.get())
        read_bit = read_buffer_identity(buffer_queue)

        if read_bit == 1:
            break

    # Read the "bits" of the message.
    sentence = []
    while True:
        if raw_bits_read > max_bits:
            break

        curr_bit_string = ""
        for _ in range(16):
            # Fill the buffer queue with [buffer_size] bits.
            for _ in range(buffer_size):
                add_bit_to_buffer(channel.get())

            curr_bit_string += str(read_buffer_identity(buffer_queue))
            if curr_bit_string == "1111":
                break

        word = key_word_map[curr_bit_string]
        if word == ".":
            break

        sentence.append(word)

    return (" ".join(sentence) + ".").capitalize()


if __name__ == "__main__":
    node_main(sender=sender, receiver=receiver)
