from setuptools import setup, find_packages

setup(
    name='vshareqrcode',
    version='0.1.0',
    description='Share any file over LAN using QR code and local server',
    author='Vansh Sharma',
    author_email='vanshsharma7832@gmail.com',
    packages=find_packages(),  # <-- very important
    install_requires=[
        'qrcode',
        'colorama'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)
