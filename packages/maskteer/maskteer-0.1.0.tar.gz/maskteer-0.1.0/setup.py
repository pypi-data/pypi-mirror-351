from setuptools import setup, find_packages

setup(
    name='maskteer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['pyyaml'],
    author='Masashi Morita',
    author_email='masashi.morita.mm@gmail.com',
    description='Automatically mask sensitive information from logs or outputs for Django, Flask, and FastAPI applications.',
    url='https://github.com/masashimorita/masketeer',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
