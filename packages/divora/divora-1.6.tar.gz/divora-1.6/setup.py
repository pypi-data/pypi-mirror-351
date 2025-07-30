from setuptools import setup

long_description = """
A simple way to train and own your AI models.
"""


setup(
    name="divora",
    packages=["divora"], 
    version="1.6",
    description="A simple way to train and own your AI models. All made possible by Divora Technologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shiloh Pendergraff",
    author_email="shilohpendergraff@gmail.com",
    url="https://divoratech.com",
    keywords=["deep learning", "tensorflow", "text generation"],
    classifiers=[],
    license="MIT",
    entry_points={
        "console_scripts": ["divora=divora.dv:cmd"],
    },
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "tensorflow>=2.5.1",
        "regex",
        "requests",
        "tqdm",
        "numpy",
        "toposort",
    ],
)
