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
    name='balistoryanalyzer',  # The name users will use to pip install
    version='1.0.3',  # Start with 0.1.0, update as you make changes
    # Automatically finds 'balipkg' and any sub-packages
    packages=find_packages(),

    # Crucial for including non-code files like models and data
    package_data={
        'balistoryanalyzer': [
            'pretrained_models/characterner/CRF_1/*.pkl',
            'pretrained_models/characterner/CRF_2/*.pkl',
            'pretrained_models/characterner/SatuaNER/*.pkl',
            'pretrained_models/characterner/HMM/*.pkl',
            'pretrained_models/characterner/SVM/*.pkl',
        ],
    },
    include_package_data=True,  # Essential for using package_data

    install_requires=[
        'pandas==1.5.3',
        'numpy==1.24.2',
        'balinese-library==0.0.7',
        'nltk==3.9.1',
        'openpyxl==3.1.0',
        'balinese-textpreprocessor==1.0.5',
        'hmmlearn==0.3.0',
        'scikit-learn==1.2.1',
        'scipy==1.10.0',
        'sklearn-crfsuite==0.3.6',
        'jaro-winkler==2.0.3',
        'distlib==0.3.1'
    ],
    entry_points={
        # Optional: If you want to provide command-line scripts
        # 'console_scripts': [
        #     'analyze-balinese-text=balipkg.cli:main_function',
        # ],
    },

    author='I Made Satria Bimantara',
    author_email='satriabimantara.imd@gmail.com',
    description='A Python package for Balinese Narrative Text Analysis including but not limited to: balinese character named entity recognition, alias clustering, and characterization classification (protagonist vs antagonist)',
    long_description=read_readme(),  # Reads content from README.md
    long_description_content_type='text/markdown',  # Specify content type for PyPI
    keywords=['Balinese', 'NLP', 'Text Preprocessing',
              'Narrative Text Analysis', 'Computational Linguistics'],
    classifiers=[
        # Or 4 - Beta, 5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  # Or your chosen license
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
