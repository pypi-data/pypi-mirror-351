from setuptools import setup, find_packages

setup(
    name='poridhi-cloud',
    version='0.3.0',
    description='Python SDK for Poridhi Cloud Infrastructure',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Poridhi Engineering',
    author_email='imnulhaquerumantalukder1999@gmail.com',
    url='https://github.com/poridhiEng/poridhi-cloud.git',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'websocket-client>=1.2.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='cloud infrastructure sdk machine learning',
    python_requires='>=3.7',
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'sphinx',
            'twine'
        ]
    }
)