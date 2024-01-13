import secrets
import aiohttp
import asyncio
import colorama
import argparse
import os
import time
import json
import itertools

o_filename = 'output.txt'
state_filename = 'state.json'
cloud_mail_mirror = 'https://cloud.mail.ru/public/'

mcloud_alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
speed_meter = 0
speed = 0
start_time = 0
avg_speed = []
avg_speed_sum = 0
mode = 0  # 0 - random, 1 - sequential

# to save:
counter = 0
success = 0
seq_client = 0
seq_success = 0


def save_state():
    global counter, success, seq_client, seq_success
    state = {
        'counter': str(counter),
        'success': str(success),
        'seq_client': str(seq_client),
        'seq_success': str(seq_success),
    }
    with open(state_filename, 'w') as outfile:
        json.dump(state, outfile)


def load_state():
    global counter, success, seq_client, seq_success
    with open(state_filename) as json_file:
        data = json.load(json_file)
        counter = int(data['counter'])
        success = int(data['success'])
        seq_client = int(data['seq_client'])
        seq_success = int(data['seq_success'])


async def get_rnd_public_folder():
    global mcloud_alph
    return cloud_mail_mirror\
        + ''.join(secrets.choice(mcloud_alph) for i in range(4)) + '/'\
        + ''.join(secrets.choice(mcloud_alph) for i in range(9))\



def get_combination(alphabet, number, length):
    result = []
    while number > 0:
        number, i = divmod(number, len(alphabet))
        result.append(alphabet[i])
    return ''.join(result).rjust(length, alphabet[0])


async def get_seq_public_folder():
    global mcloud_alph, seq_client, cloud_mail_mirror
    seq_client += 1
    seq = get_combination(mcloud_alph, seq_client, 13)
    return cloud_mail_mirror + seq[0:4] + '/' + seq[4:13]


def get_number_from_link(link):
    global cloud_mail_mirror, mcloud_alph
    seq = link.replace(cloud_mail_mirror, '').replace('/', '')
    seq = seq[::-1]  # reverse the sequence
    number = 0
    for char in seq:
        number = number * len(mcloud_alph) + mcloud_alph.index(char)
    print('[' + colorama.Fore.CYAN + 'INFO' + colorama.Fore.RESET + '] '
          + 'URL: ' + colorama.Fore.LIGHTBLACK_EX + link
            + colorama.Fore.RESET + ' | Seq: '
            + colorama.Fore.LIGHTBLUE_EX + str(number)
            + colorama.Fore.RESET)


async def check_availability(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return True
            else:
                return False


def append_to_file(text):
    filename = o_filename
    with open(filename, 'a') as file_object:
        file_object.write(text + '\n')


async def save_state_on_time():
    while (1):
        await asyncio.sleep(10)
        save_state()


async def main(worker_id):
    global counter, success, speed_meter, speed, start_time, \
        avg_speed, avg_speed_sum, seq_success
    task = asyncio.create_task(save_state_on_time())

    while (1):
        try:
            if mode == 0:
                url = await get_rnd_public_folder()
            elif mode == 1:
                url = await get_seq_public_folder()
            else:
                print('[' + colorama.Fore.RED + 'ERROR' + colorama.Fore.RESET
                      + '] ' + 'Invalid mode')
                exit()
            is_available = await check_availability(url)
            if is_available:
                append_to_file(url)
                if mode == 0:
                    success += 1
                elif mode == 1:
                    seq_success += 1
                print('[' + colorama.Fore.GREEN + 'CORRECT'
                      + colorama.Fore.RESET + '] ' + url + ', logging...')
            speed_meter += 1
            counter += 1
            if (time.time() - start_time) >= 1:
                speed = speed_meter
                speed_meter = 0
                start_time = time.time()
                avg_speed.append(speed)
            if len(avg_speed) > 10:
                avg_speed.pop(0)
            avg_speed_sum = sum(avg_speed)
            avg_speed_avg = avg_speed_sum / \
                len(avg_speed) if len(avg_speed) > 0 else 0
            avg_speed_avg = round(avg_speed_avg, 1)

            print('[' + colorama.Fore.CYAN + 'INFO' + colorama.Fore.RESET + '] '
                  + (('Checked: ' + colorama.Fore.RED + str(counter)
                      + colorama.Fore.RESET)
                      if mode == 0
                     else ('Checked: ' + colorama.Fore.RED + str(seq_client)
                           + colorama.Fore.RESET))
                  + ((' | Success: '
                      + colorama.Fore.GREEN + str(success)
                      + colorama.Fore.RESET) if mode == 0
                     else (' | Success: ' + colorama.Fore.GREEN
                           + str(seq_success) + colorama.Fore.RESET))
                  + ' | URL: ' + colorama.Fore.LIGHTBLACK_EX + url
                  + colorama.Fore.RESET
                  + ' | Speed: '
                  + colorama.Fore.LIGHTBLUE_EX + str(avg_speed_avg)
                  + 'url/s\t\t' + colorama.Fore.RESET, end='\r')
        except Exception as e:
            print('[' + colorama.Fore.YELLOW + 'WARNING' +
                  colorama.Fore.RESET + '] ' + str(e) + ' at ' + url
                  + ', worker #' + str(worker_id))


async def run_all_workers(num_workers):
    print('[' + colorama.Fore.CYAN + 'INFO' + colorama.Fore.RESET + '] '
          + 'Starting ' + str(num_workers)
          + ' workers...')
    global start_time
    start_time = time.time()
    await asyncio.gather(*(main(i) for i in range(num_workers)))


async def try_gathered():
    with open(o_filename, 'r') as file:
        lines = file.readlines()
        for url in lines:
            try:
                is_available = await check_availability(url)
                if is_available:
                    print('[' + colorama.Fore.GREEN + 'CORRECT'
                          + colorama.Fore.RESET + '] ' + url, end='')
                else:
                    print('[' + colorama.Fore.RED + 'FAILED'
                          + colorama.Fore.RESET + '] ' + url, end='')
            except Exception as e:
                print('[' + colorama.Fore.YELLOW + 'WARNING' +
                      colorama.Fore.RESET + '] ' + str(e))


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser()

        parser.add_argument("-w", "--workers",
                            help="Number of workers", type=int)
        parser.add_argument(
            "-c", "--check",
            help="Check gathered links. May be provided with file using -o flag",
            action="store_true")
        parser.add_argument(
            "-o", "--output", help="Output filename", type=str)
        parser.add_argument(
            "-s", "--sequential", help="Sequential mode", action="store_true")
        parser.add_argument(
            "-e", "--extract", help="Extract sequential number from link",
            type=str)
        args = parser.parse_args()

        if args.output:
            o_filename = args.output

        if args.workers:
            num_workers = args.workers
        else:
            num_workers = 1  # Change this to the number of workers you want

        if args.extract:
            get_number_from_link(args.extract)
            exit()

        os.system('cls' if os.name == 'nt' else 'clear')

        try:
            load_state()
        except:
            print('[' + colorama.Fore.YELLOW + 'WARNING' +
                  colorama.Fore.RESET + '] '
                  + 'No state file found, starting from scratch...')

        if args.check:
            asyncio.run(try_gathered())
            exit()

        if args.sequential:
            mode = 1

        asyncio.run(run_all_workers(num_workers))

    except KeyboardInterrupt:
        save_state()
        print('\n[' + colorama.Fore.YELLOW + 'WARNING' +
              colorama.Fore.RESET + '] '
              + 'KeyboardInterrupt, saving current state...')
        exit()

    except Exception as e:
        print('[' + colorama.Fore.RED + 'ERROR' + colorama.Fore.RESET + '] '
              + str(e))
        exit()
