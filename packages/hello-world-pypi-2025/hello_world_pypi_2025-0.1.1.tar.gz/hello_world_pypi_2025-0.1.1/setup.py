from setuptools import setup, find_packages

setup(
    name='hello-world-pypi-2025',
    version='0.1.1',
    author='Abolfazl Abbasi',
    author_email='a.abbasi5775@gmail.com',
    description='A hello with name for hello world in PyPi',
    long_description=open('README.md').read(), 
    long_description_content_type='text/markdown',  
    url='https://github.com/abbasi0abolfazl/hello_world_pypi.git',  
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha', 
        'Intended Audience :: Developers',
        'Natural Language :: English',
    ],
    python_requires='>=3.6',
    extras_require={
        'dev': [
            'check-manifest',
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hello=hello_package.say_hello:main', 
        ],
    },
)

