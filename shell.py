import argparse
import discord
import asyncio


class Shell:
    def __init__(self, client: discord.Client):
        self.client = client

        self.parser = argparse.ArgumentParser(description='disync CLI')
        # subparsers
        subparsers = self.parser.add_subparsers(dest='action', help='Action to perform')
        ## exit
        exit_parser = subparsers.add_parser('exit', help='Exit disync', aliases=['quit'])

    def parse(self, args: list):
        return self.parser.parse_args(args=args)

    async def get_input(self, prompt):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input, prompt)

    async def run(self) -> None:
        while True:
            try:
                commands = (await self.get_input("disync> ")).split(";")
                for command in commands:
                    args = None
                    try:
                        args = self.parse(command.split())
                    except SystemExit:
                        pass
                    if args:
                        response = await self.execute(args)
                        print(response)
            except KeyboardInterrupt:
                break
            except SystemExit:
                break
            except EOFError:
                break

    async def execute(self, args) -> str:
        match args.action:
            case 'exit':
                raise SystemExit
            case _:
                return f"Unknown action: {args.action}"
