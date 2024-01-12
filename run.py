# https://cloud.mail.ru/public/<xxxx>/<xxxxxxxxx>
import random
import aiohttp
import asyncio
import colorama
import argparse
import os

mcloud_alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


async def get_rnd_public_folder():
    return 'https://cloud.mail.ru/public/'
+ ''.join(random.choice(mcloud_alph) for _ in range(4)) + '/'
+ ''.join(random.choice(mcloud_alph) for _ in range(9))


async def check_availability(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                return True
            else:
                return False


def append_to_file(text):
    filename = 'output.txt'
    with open(filename, 'a') as file_object:
        file_object.write(text + '\n')


counter = 0
success = 0


async def main(worker_id):
    global counter, success
    while (1):
        try:
            url = await get_rnd_public_folder()
            is_available = await check_availability(url)
            if is_available:
                append_to_file(url)
                success += 1
                print('[' + colorama.Fore.GREEN + 'CORRECT'
                      + colorama.Fore.RESET + '] ' + url + ', logging...')
            counter += 1
            print('[' + colorama.Fore.CYAN + 'INFO' + colorama.Fore.RESET + '] '
                  + 'Checked: ' + colorama.Fore.RED + str(counter)
                  + colorama.Fore.RESET + ' | Success: '
                  + colorama.Fore.GREEN + str(success) + colorama.Fore.RESET
                  + ' | URL: ' + colorama.Fore.LIGHTBLACK_EX + url
                  + colorama.Fore.RESET, end='\r')
        except Exception as e:
            print('[' + colorama.Fore.RED + 'ERROR' +
                  colorama.Fore.RESET + '] ' + str(e))


async def run_all_workers(num_workers):
    print('[' + colorama.Fore.CYAN + 'INFO' + colorama.Fore.RESET + '] '
          + 'Starting ' + str(num_workers)
          + ' workers...')
    await asyncio.gather(*(main(i) for i in range(num_workers)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--workers", help="Number of workers", type=int)
    args = parser.parse_args()
    if args.workers:
        num_workers = args.workers
    else:
        num_workers = 1  # Change this to the number of workers you want

    os.system('cls' if os.name == 'nt' else 'clear')

    asyncio.run(run_all_workers(num_workers))
