from setuptools import setup, find_packages

setup(
    name='woxchain-python',
    version='0.1.0',
    description='Official Python SDK for Woxchain',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Woxchain Dev Team',
    author_email='team@woxchain.com',
    url='https://github.com/woxchain/woxchain-python',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
