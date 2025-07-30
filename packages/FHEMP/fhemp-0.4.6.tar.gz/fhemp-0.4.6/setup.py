from setuptools import setup, find_packages

setup(
    name='FHEMP',
    version='0.4.6',
    description='Гомоморфное шифрование на основе матричных полиномов',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='EvZait',
    # author_email='evzait03@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
    'numpy',
    ],
    python_requires='>=3.8',
)

entry_points={
    'console_scripts': [
        'FHEMP=FHEMP.cli:main',
    ]
},

