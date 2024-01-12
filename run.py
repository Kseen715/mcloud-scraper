# https://cloud.mail.ru/public/<xxxx>/<xxxxxxxxx>
import random
import aiohttp
import asyncio
import colorama

mcloud_alph = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


async def get_rnd_public_folder():
    return 'https://cloud.mail.ru/public/' + ''.join(random.choice(mcloud_alph) for _ in range(4)) + '/' + ''.join(random.choice(mcloud_alph) for _ in range(9))


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


async def main():
    counter = 0
    success = 0
    while (1):
        url = await get_rnd_public_folder()
        is_available = await check_availability(url)
        if is_available:
            append_to_file(url)
            success += 1
        counter += 1
        print('Checked: ' + colorama.Fore.RED + str(counter)
              + colorama.Fore.RESET + ' | Success: '
              + colorama.Fore.GREEN + str(success) + colorama.Fore.RESET
              + ' | URL: ' + colorama.Fore.LIGHTBLACK_EX + url + colorama.Fore.RESET, end='\r')


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
