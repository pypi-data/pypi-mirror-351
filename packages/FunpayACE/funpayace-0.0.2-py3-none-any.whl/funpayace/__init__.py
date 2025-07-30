import threading
import random
import aiohttp
import asyncio


class FunpayAce:
    def __init__(self, golden_key):
        self.golden_key = golden_key

    def forever_online(self):
        """
        Запускает вечный онлайн в отдельном потоке с собственным event loop.
        """

        def run_loop_in_thread():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._forever_online())

        thread = threading.Thread(target=run_loop_in_thread, daemon=True)
        thread.start()

    async def _forever_online(self):
        print(f"[FunpayACE] ForeverOnline has been launched.")
        async with aiohttp.ClientSession(cookies={"golden_key": self.golden_key}) as session:
            while True:
                try:
                    async with session.post("https://funpay.com/runner/") as resp:
                        if resp.status == 200:
                            print(f"[FunpayACE] ForeverOnline ping successful.")
                        else:
                            print(f"[FunpayACE] ForeverOnline ping failed with status {resp.status}.")
                except Exception as e:
                    print(f"[FunpayACE] ForeverOnline error: {e}")

                await asyncio.sleep(random.randint(45, 100))
