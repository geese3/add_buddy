from setuptools import setup

APP = ['auto_neighbor_gui.py']
DATA_FILES = []
OPTIONS = {
    'packages': [
        'PyQt5', 'selenium', 'undetected_chromedriver', 'dotenv', 'pyperclip', 'imp'
    ],
    'includes': [
        'PyQt5.QtWidgets', 'PyQt5.QtCore', 'selenium', 'undetected_chromedriver', 'dotenv', 'pyperclip', 'imp'
    ],
    'iconfile': None,  # 아이콘이 필요하면 경로를 지정하세요
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
