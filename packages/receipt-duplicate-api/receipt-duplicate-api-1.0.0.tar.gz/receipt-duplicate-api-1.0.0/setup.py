from setuptools import setup, find_packages

setup(
    name="receipt-duplicate-api",
    version="1.0.0",
    description="Production-ready FastAPI app for receipt duplicate detection using NLP, hashing, and CNNs",
    author="Your Name",
    author_email="your.email@example.com",
    python_requires='==3.11.4',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi==0.110.0",
        "uvicorn==0.29.0",
        "sentence-transformers==2.2.2",
        "torch==2.1.2",
        "torchvision==0.16.2",
        "Pillow==10.2.0",
        "imagehash==4.3.1",
        "numpy==1.26.4",
        "pydantic==2.6.4",
        "typing-extensions==4.11.0",
        "python-multipart==0.0.9",
        "gunicorn==21.2.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    entry_points={
        "console_scripts": [
            # Optionally you can add CLI entry points here
            # e.g. "run-receipt-api=receipt_duplicate_api.main:app"
        ],
    },
)
