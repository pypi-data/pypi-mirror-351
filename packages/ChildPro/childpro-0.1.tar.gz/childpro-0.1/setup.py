# setup.py

from setuptools import setup, find_packages

setup(
    name="ChildPro",  # Name of the package
    version="0.1",    # Version of the package
    description="Audio Preprocessing Tool for ASR",  # A short description of your program
    author="Your Name",  # Author name
    author_email="your-email@example.com",  # Your email address
    url="https://github.com/yourusername/ChildPro",  # URL of the repository
    packages=find_packages(),  # Automatically find and include packages in the directory
    entry_points={  # This makes your program executable via `pip` (i.e., `childpro`)
        'console_scripts': [
            'childpro = audio_processing.preprocess:preprocess_audio',
        ],
    },
    install_requires=[  # List of dependencies to be installed by `pip`
        'pydub',  # Example, your project requires pydub
        'numpy',  # Example, add other dependencies here
    ],
    classifiers=[  # Optional but recommended for PyPI
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Specify required Python version
)
