from setuptools import setup, find_packages

setup(
    name='vshare',  # PyPI pe unique hona chahiye
    version='0.1.0',
    description='Share any file over LAN using QR code and local server',
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author='Vansh Sharma',
    author_email='your_email@example.com',
    url='https://github.com/yourusername/vshare',  # optional
    packages=find_packages(),
    install_requires=[
        'qrcode',
    ],
    entry_points={
        'console_scripts': [
            'vshare=vshare.__main__:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
