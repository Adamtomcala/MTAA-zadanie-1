import logging
import time
import re

rx_media = re.compile("^m=")
rx_to = re.compile("^To:")
rx_from = re.compile("^From:")
rx_id = re.compile("^Call-ID:")
calls = {}
members = []


def delete_call(src, dest):
    if src in calls:
        del calls[src]
    if dest in calls:
        del calls[dest]


def find_media(data):
    media = []
    for line in data:
        if rx_media.search(line):
            media.append(line)
    return media


def create_name(data):
    start_index = data.index("sip:")
    end_index = data.index("@")
    return data[start_index + 4: end_index]


def iterate(data):
    src, dest = "", ""
    for line in data:
        if rx_to.search(line):
            dest = create_name(line)
        elif rx_from.search(line):
            src = create_name(line)

    return src, dest


def find_call_id(data):
    for line in data:
        if rx_id.search(line):
            return line[9:]


def inicialization(ipaddress):
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', filename='proxy.log', level=logging.INFO,
                        datefmt='%H:%M:%S')
    logging.info(time.strftime(">>> Server zacal bezat o: %a, %d %b %Y %H:%M:%S <<<", time.localtime()))

    logging.info(">>> Na IP adrese: %s <<<\n" % ipaddress)


def register(data):
    src, des = iterate(data)
    if src not in members:
        logging.info(">>> Registracna sprava od pouzivatela %s <<<\n" % src)
        members.append(src)


def start_call(data):
    media = find_media(data)
    src, dest = iterate(data)
    call_id = find_call_id(data)

    if call_id not in calls:
        calls[call_id] = [src]
        if len(media) == 1:
            logging.info(">>> Pouzivatel %s vytaca pouzivatela %s (audio), call-id %s <<<\n" % (src, dest, call_id))
        elif len(media) == 2:
            logging.info(">>> Pouzivatel %s vytaca pouzivatela %s (audio + video), call-id %s  <<<\n" %
                         (src, dest, call_id))
    else:
        for member in calls[call_id]:
            if member == dest:
                if len(media) == 2:
                    arr = media[1].split()

                    if arr[1] == "0":
                        logging.info(">>> Pouzivatel %s ukoncil videohovor s pouzivatelom %s, , call-id %s  <<<\n" %
                                     (src, dest, call_id))
                    else:
                        logging.info(">>> Pouzivatel %s chce zacat videohovor s pouzivatelom %s, , call-id %s  <<<\n" %
                                     (src, dest, call_id))
                return

        # logging.info(">>> Pouzivatel %s vytaca pouzivatela %s <<<\n" % (src, dest))

    # print(calls)


def ack(data):
    if "transport" not in data[0]:
        return

    src, dest = iterate(data)
    call_id = find_call_id(data)
    call = calls[call_id]

    for member in call:
        if member == dest:
            return

    calls[call_id].append(dest)
    logging.info(">>> Pouzivatel %s zdvihol hovor, call-id %s <<<\n" % (dest, call_id))
    # print(calls)


def code(data):
    # print(data)
    src, dest = iterate(data)
    call_id = find_call_id(data)
    media = find_media(data)
    # Hovor odmietnuty
    if "603" in data[0]:
        logging.info(">>> Pouzivatel %s odmietol hovor, call-id %s <<<\n" % (dest, call_id))
        del calls[call_id]
    # Hovor zruseny volajucim
    elif "487" in data[0]:
        logging.info(">>> Pouzivatel %s zrusil hovor, call-id %s <<<\n" % (src, call_id))
        del calls[call_id]
    elif "200" in data[0]:
        if len(media) == 2:
            arr = media[1].split()
            if arr[1] == "0":
                logging.info(">>> Pouzivatel %s potvrdil ukoncenie videohovoru, call-id %s <<<\n" % (dest, call_id))
            else:
                logging.info(">>> Pouzivatel %s potvrdil zacatie videohovoru, call-id %s <<<\n" % (dest, call_id))


def non_invite(data):
    src, dest = iterate(data)
    call_id = find_call_id(data)
    if "BYE" in data[0]:
        logging.info(">>> Pouzivatel %s ukoncil hovor s pouzivatelom %s, call-id %s <<<\n" % (src, dest, call_id))
        del calls[call_id]
    # print(calls)


def change_code(status):
    arr = status.split()

    if arr[1] == "487":
        arr[2] = "ZRUSENE"
    elif arr[1] == "603":
        arr[2] = "ODMIETNUTE"
    elif arr[1] == "486":
        arr[2] = "OBSADENE"
    elif arr[1] == "408":
        arr[2] = "NEDOSTUPNY"

    return " ".join(arr)
