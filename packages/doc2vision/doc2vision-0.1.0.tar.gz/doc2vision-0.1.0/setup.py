from setuptools import setup, find_packages

setup(
    name='doc2vision',
    version='0.1.0',
    description='Convert PDFs and images into clean, LLM-compatible image formats',
    author='Russell Van Curen',
    author_email='russell@vancuren.com',
    packages=find_packages(),
    install_requires=[
        'contourpy==1.3.2',
        'cycler==0.12.1',
        'fonttools==4.58.1',
        'kiwisolver==1.4.8',
        'matplotlib==3.10.3',
        'numpy==2.2.6',
        'opencv-python-headless==4.11.0.86',
        'packaging==25.0',
        'pdf2image==1.17.0',
        'pillow==11.2.1',
        'pyparsing==3.2.3',
        'python-dateutil==2.9.0.post0',
        'six==1.17.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
