# setup.py
from setuptools import setup, find_packages
import os

# Function to read the README.md content


def read_readme():
    try:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


setup(
    name='balinese_textpreprocessor',  # The name users will use to pip install
    version='1.0.5',  # Start with 0.1.0, update as you make changes
    # Automatically finds 'balipkg' and any sub-packages
    packages=find_packages(),

    # Crucial for including non-code files like models and data
    package_data={
        'balinese_textpreprocessor': [
            'models/*.pkl',
            'models/*.pt',  # Include if you have PyTorch models
            # Include if you have other binary models (e.g., for spaCy)
            'models/*.bin',
            'data/lemmatization/balivocab.txt',
            'data/normalizedwords/data.xlsx',
            'data/stopwords/data.txt',
            # Add other data file types if necessary
        ],
    },
    include_package_data=True,  # Essential for using package_data

    install_requires=[
        'pandas==1.5.3',
        'numpy==1.24.2',
        'balinese-library==0.0.7',
        'nltk==3.9.1',
        'openpyxl==3.1.0'
    ],
    entry_points={
        # Optional: If you want to provide command-line scripts
        # 'console_scripts': [
        #     'analyze-balinese-text=balipkg.cli:main_function',
        # ],
    },

    author='I Made Satria Bimantara',
    author_email='satriabimantara.md@gmail.com',
    description='A Python package for Balinese Text Preprocessing',
    long_description=read_readme(),  # Reads content from README.md
    long_description_content_type='text/markdown',  # Specify content type for PyPI
    keywords=['Balinese', 'NLP', 'Text Preprocessing', 'Text Analysis'],
    classifiers=[
        # Or 4 - Beta, 5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  # Or your chosen license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        # Balinese is not a specific classifier, but Bahasa Indonesia is close
        'Natural Language :: Indonesian',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',  # Minimum Python version
)
