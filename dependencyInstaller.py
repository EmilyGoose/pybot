# Library dependency installer for pybot
# Misha Larionov
# github.com/MishaLarionov/pybot
# Licensed under MIT License
# See license.txt for full license

import pip, sys

libraries = ['asyncio','requests','dateparser','wikipedia', 'github3.py']

for i in libraries:
    print("Installing " + i)
    pip.main(['install', i])
    print("Installed " + i)

print("Trying to install Discord.py library")
try:
    pip.main(['install', 'git+https://github.com/Rapptz/discord.py@async'])
except:
    print("Unable to install Discord library. This probably means git isn't installed. Try doing a manual install.")
else:
    print("Successfully installed Discord.py")
    print("\nAll library dependencies installed.")
    input()
    sys.exit()
print("\nAll library dependencies not requiring git installed.")
input()
