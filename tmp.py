import asyncio

async def print_word(word: str, deps : int):
    print(word, deps)

handlers = [
    lambda word: print_word(word,5),  
    lambda word: print_word(word,6),  
]

async def print_words():
    for handler in handlers:
        await handler('hello')

asyncio.run(print_words())