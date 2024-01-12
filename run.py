import random
import aiohttp
import asyncio
import colorama
import argparse
import os
import time

o_filename = 'output.txt'
cloud_mail_mirror = 'https://cloud.mail.ru/public/'

mcloud_alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
counter = 0
success = 0
speed_meter = 0
speed = 0
start_time = 0
avg_speed = []
avg_speed_sum = 0


async def get_rnd_public_folder():
    global mcloud_alph
    return cloud_mail_mirror\
        + ''.join(random.choice(mcloud_alph) for _ in range(4)) + '/' \
        + ''.join(random.choice(mcloud_alph) for _ in range(9))


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


async def main(worker_id):
    global counter, success, speed_meter, speed, start_time, \
        avg_speed, avg_speed_sum
    while (1):
        try:
            url = await get_rnd_public_folder()
            is_available = await check_availability(url)
            if is_available:
                append_to_file(url)
                success += 1
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
                  + 'Checked: ' + colorama.Fore.RED + str(counter)
                  + colorama.Fore.RESET + ' | Success: '
                  + colorama.Fore.GREEN + str(success) + colorama.Fore.RESET
                  + ' | URL: ' + colorama.Fore.LIGHTBLACK_EX + url
                  + colorama.Fore.RESET + ' | Speed: '
                  + colorama.Fore.LIGHTBLUE_EX + str(avg_speed_avg)
                  + 'urls/s\t\t' + colorama.Fore.RESET, end='\r')
        except Exception as e:
            print('[' + colorama.Fore.RED + 'ERROR' +
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
                print('[' + colorama.Fore.RED + 'ERROR' +
                      colorama.Fore.RESET + '] ' + str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-w", "--workers", help="Number of workers", type=int)
    parser.add_argument(
        "-c", "--check",
        help="Check gathered links. May be provided with file using -o flag",
        action="store_true")
    parser.add_argument(
        "-o", "--output", help="Output filename", type=str)
    args = parser.parse_args()

    if args.output:
        o_filename = args.output

    if args.workers:
        num_workers = args.workers
    else:
        num_workers = 1  # Change this to the number of workers you want

    os.system('cls' if os.name == 'nt' else 'clear')

    if args.check:
        asyncio.run(try_gathered())
        exit()

    asyncio.run(run_all_workers(num_workers))
