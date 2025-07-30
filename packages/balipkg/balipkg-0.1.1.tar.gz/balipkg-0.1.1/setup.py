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
    name='balipkg',  # The name users will use to pip install
    version='0.1.1',  # Start with 0.1.0, update as you make changes
    # Automatically finds 'balipkg' and any sub-packages
    packages=find_packages(),

    # Crucial for including non-code files like models and data
    package_data={
        'balipkg': [
            'models/*.pkl',
            'models/*.pt',  # Include if you have PyTorch models
            # Include if you have other binary models (e.g., for spaCy)
            'models/*.bin',
            'data/*.json',
            'data/*.csv',
            # Add other data file types if necessary
        ],
    },
    include_package_data=True,  # Essential for using package_data

    install_requires=[
        'pandas==1.5.3',       # Example: if you use pandas for data handling
        'numpy==1.24.2',       # Common dependency
        # Add any other libraries your package strictly depends on
    ],
    entry_points={
        # Optional: If you want to provide command-line scripts
        # 'console_scripts': [
        #     'analyze-balinese-text=balipkg.cli:main_function',
        # ],
    },

    author='I Made Satria Bimantara',
    author_email='satriabimantara.md@gmail.com',
    description='A Python package for Balinese narrative text analysis, including NER, alias clustering, and characterization classification.',
    long_description=read_readme(),  # Reads content from README.md
    long_description_content_type='text/markdown',  # Specify content type for PyPI
    keywords=['Balinese', 'NLP', 'Text Analysis', 'NER',
              'Characterization', 'Natural Language Processing'],
    classifiers=[
        'Development Status :: 3 - Alpha',  # Or 4 - Beta, 5 - Production/Stable
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  # Or your chosen license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        # Balinese is not a specific classifier, but Bahasa Indonesia is close
        'Natural Language :: Indonesian',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.8',  # Minimum Python version
)
