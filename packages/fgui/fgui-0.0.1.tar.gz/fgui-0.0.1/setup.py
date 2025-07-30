from setuptools import setup, find_packages

setup(
    name='fgui',
    version='0.0.1',
    author="aigcst",
    description="",
    # packages=find_packages(),
    packages=['fgui'], # 项目目录
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'fgui = fgui.main:main'
        ]
    }
)