# Library dependency installer for pybot
# Misha Larionov
# github.com/MishaLarionov/pybot
# Licensed under MIT License
# See license.txt for full license

import pip, sys

libraries = ['asyncio','requests','dateparser','wikipedia', 'github3.py', 'lxml', 'discord.py']

for i in libraries:
    print("Installing " + i)
    pip.main(['install', i])
    print("Installed " + i)

print("\nAll library dependencies installed.")
