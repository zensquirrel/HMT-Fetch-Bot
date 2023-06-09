import os


def set_stat_file():
    with open('stat.csv', 'w') as file:
        file.write('chat_id, wartenummer, time')


def main():
    set_stat_file()


if __name__ == "__main__":
    main()
