from setuptools import setup, find_packages

setup(
    name='multi-script-cli',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        devopsinit=scripts.devopsinit:cli
        devopsci=scripts.devopsci:cli
        devopscd=scripts.devopscd:cli
    ''',
)