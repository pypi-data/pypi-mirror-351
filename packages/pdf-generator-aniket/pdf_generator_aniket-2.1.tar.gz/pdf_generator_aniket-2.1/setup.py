from setuptools import setup, find_packages

setup(
    name="pdf-generator-aniket",
    version="2.1",
    author="Aniket Chaturvedi",
    author_email="chaturvedianiket007@gmail.com",
    description="A user-friendly PDF generation tool built with Python and Tkinter. Supports customizable pages, watermarks, text placement, color modes, and now allows setting a target PDF file size. Ideal for automating batch PDF creation with flexible options.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Aniketc068/pdf_generator",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "reportlab",
        "Pillow",
        "pywin32",
        "chardet"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.7',
    entry_points={
        'gui_scripts': [
            'pdf-generator = pdf_generator:main',
        ],
    },
)
