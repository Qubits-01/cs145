from sys import stderr
from typing import Tuple
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
    start_signal_repetition_number = 30
    message_repetition_number = 30

    # print("Sending start signal...", file=stderr)

    def send_bit_n_times(bit: int, repetition_number: int) -> None:
        for _ in range(repetition_number):
            channel.send(bit)

    # print("Start signal sent.", file=stderr)

    # print("Sending message...", file=stderr)

    # Signal the start of the communication.
    send_bit_n_times(1, start_signal_repetition_number)

    # Remove "." from the sentence.
    sentence = sentence[:-1]

    # Send the bits for each word in the sentence.
    for word in sentence.split():
        bits = word_key_map[word.lower()]
        for bit in bits:
            send_bit_n_times(int(bit), message_repetition_number)

    # print("Message sent.", file=stderr)

    # print("Sending end signal...", file=stderr)

    # Signal the end of the communication.
    # Four most significant bits (1111) signify the end of the communication.
    # This works because 111 is the highest possible MSBs for a 16-bit key
    # (within the context of the corpus.txt file).
    #
    # For instance, the last word in the corpus "zulus" has a 16-bit
    # key "1110001011111101" (notice that the first four MSBs are "1110").
    for _ in range(4):
        send_bit_n_times(1, message_repetition_number)

    # print("✅ End signal sent.", file=stderr)


def receiver(channel: Channel) -> str:
    bit_flip_probability = 0.1  # 10% bit flip probability
    offset = 5
    start_signal_repetition_number = 30
    start_signal_buffer_queue = []
    message_repetition_number = 30
    message_buffer_queue = []
    start_signal_max_bits = 1500  # If the start signal was not read properly.
    raw_start_signal_bits_read = 0
    message_max_bits = 3000  # If the message end indicator was not read properly.
    raw_message_bits_read = 0

    def add_bit_to_buffer(
        bit: int,
        buffer_queue: list = message_buffer_queue,
        max_len: int = message_repetition_number,
    ) -> None:
        if len(buffer_queue) == max_len:
            buffer_queue.pop(0)

        buffer_queue.append(bit)

    ### Read the buffer queue and return the identity of the buffer.
    ### The identity of the buffer is determined by the number of ones
    ### and zeroes in the buffer.
    def get_ones_zeroes_count(buffer_queue: list) -> Tuple[int, int]:
        n_ones = buffer_queue.count(1)
        return n_ones, len(buffer_queue) - n_ones

    def read_message_buffer_identity(
        buffer_queue: list = message_buffer_queue,
    ) -> int:
        n_ones, n_zeroes = get_ones_zeroes_count(buffer_queue)
        return 1 if n_ones > n_zeroes else 0

    # print("Waiting for start signal...", file=stderr)

    # Wait for the start signal.
    while True:
        if raw_start_signal_bits_read > start_signal_max_bits:
            exit("Start signal not received.")

        add_bit_to_buffer(
            channel.get(),
            start_signal_buffer_queue,
            start_signal_repetition_number,
        )

        if len(start_signal_buffer_queue) == start_signal_repetition_number:
            n_ones, _ = get_ones_zeroes_count(start_signal_buffer_queue)
            required_ones = int(
                ((1 - bit_flip_probability) * start_signal_repetition_number) - offset
            )

            if n_ones >= required_ones:
                break

        raw_start_signal_bits_read += 1

    # print("Start signal received.", file=stderr)

    # print("Reading message...", file=stderr)
    # Read the "bits" of the message.
    sentence = []
    while True:
        if raw_message_bits_read > message_max_bits:
            break

        curr_bit_string = ""
        for _ in range(16):
            # Fill the buffer queue with [message_repetition_number] bits.
            for _ in range(message_repetition_number):
                add_bit_to_buffer(channel.get())

            curr_bit_string += str(read_message_buffer_identity())
            if curr_bit_string == "1111":
                break

        word = key_word_map[curr_bit_string]
        if word == ".":
            break

        sentence.append(word)

        raw_message_bits_read += 1

    # print("✅ Message received.", file=stderr)
    # print(f'message: {(" ".join(sentence) + ".").capitalize()}', file=stderr)

    return (" ".join(sentence) + ".").capitalize()


if __name__ == "__main__":
    node_main(sender=sender, receiver=receiver)
