from datetime import datetime


# returns the current date
def __get_date():
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return date


# Write a entry in the log.txt file
def write_log(*texts):
    with open("log.txt", "a") as log:
        log.write(__get_date() + ":\n")

        # For every paragraph a new line is written in the log
        for text in texts:
            log.write(str(text) + "\n")

        log.write("\n")