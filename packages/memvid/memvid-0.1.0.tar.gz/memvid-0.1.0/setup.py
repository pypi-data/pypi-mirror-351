from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="memvid",
    version="0.1.0",
    author="Memvid Team",
    author_email="team@memvid.ai",
    description="Video-based AI memory library for fast semantic search and retrieval",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/olow304/memvid",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "qrcode[pil]==8.2",
        "opencv-python==4.11.0.86",
        "pyzbar==0.1.9",
        "sentence-transformers==4.1.0",
        "numpy==1.26.4",
        "openai==1.82.0",
        "tqdm==4.67.1",
        "faiss-cpu==1.7.4",
        "Pillow==11.2.1",
        "python-dotenv==1.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "pdf": [
            "PyPDF2==3.0.1",
        ],
        "web": [
            "fastapi>=0.100.0",
            "gradio>=4.0.0",
        ],
    },
)