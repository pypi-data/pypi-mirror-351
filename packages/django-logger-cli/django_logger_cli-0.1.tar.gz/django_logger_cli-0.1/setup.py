from setuptools import setup, find_packages

setup(
    name='django_logger_cli',
    version='0.1',
    description='🛠️ A CLI tool to generate Django-style logger configurations.',
    author='Manukrishna S',
    author_email='manukrishna.s2001@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click>=8.2.1'

    ],
    entry_points={
        'console_scripts': [
            'django-logger=Logger.cli:cli',
        ],
    },
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
)
