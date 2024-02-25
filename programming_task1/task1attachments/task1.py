from cs145lib.task1 import Channel, node_main


def sender(channel: Channel, sentence: str) -> None:
    # TODO implement this
    ...


def receiver(channel: Channel) -> str:
    # TODO implement this
    return ""


if __name__ == "__main__":
    node_main(sender=sender, receiver=receiver)
