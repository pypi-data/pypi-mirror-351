from setuptools import setup, find_packages

setup(
    name="discord-booster",
    version="0.8",
    packages=find_packages(),
    install_requires=[
        "requests",
        "colorama"
    ],
    entry_points={
        'console_scripts': [
            'discord_booster=discord_booster:main',
        ],
    },
)
