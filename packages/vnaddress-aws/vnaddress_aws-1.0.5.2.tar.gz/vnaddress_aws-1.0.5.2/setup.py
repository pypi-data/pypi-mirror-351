import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='vnaddress_aws',
    version='1.0.5.2',
    scripts=['vnas_aws'],
    author="hoanganhhy2003",
    author_email="hoanganhhy2003@gmail.com",
    description="A package for parsing Vietnamese address able to run in AWS lambda based origin version",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # url="https://github.com/vantrong291/vn_address_standardizer",
    packages=setuptools.find_packages(),
    data_files=[("vnaddress_aws",
                 ["vnaddress_aws/models/finalized_model.sav"])],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'nltk', 'joblib', 'sklearn_crfsuite', 'fuzzywuzzy', 'python-Levenshtein', 'lambda_multiprocessing'
    ],
    include_package_data=True,
)
