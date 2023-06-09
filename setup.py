from setuptools import setup

setup(
    name='netrohomeapi',
    packages=['netrohomeapi'],
    version='0.1.2',
    license='MIT',
    description='Python wrapper for NetroHome API',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    author='George Bark',
    author_email='georgebark2000@gmail.com',
    url='https://github.com/GeorgeBark/netrohomeapi',
    download_url='https://github.com/GeorgeBark/netrohomeapi/archive/refs/tags/v0.1.2.tar.gz',
    install_requires=[
        'aiohttp',
        'pydantic'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
