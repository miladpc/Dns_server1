from setuptools import setup, find_packages

setup(
    name='dns-server',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'dnslib',
    ],
    entry_points={
        'console_scripts': [
            'dns_server = dns_server:main',   #این تابع باید در dns_server.py وجود داشته باشد
        ],
    },
    description='A simple DNS server for gaming applications',
    author='Milad',
    author_email='your.miladjalali1388@gmail.com',
    url='https://github.com/miladpc/dns.git',   #لینک به پروژه
)
