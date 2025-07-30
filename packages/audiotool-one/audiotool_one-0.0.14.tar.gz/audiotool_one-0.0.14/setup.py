from setuptools import setup, find_packages
from setuptools import setup, Extension
import io
from os import path

this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


version_file = "audiotool/version.py"


def get_version():
    with open(version_file, "r") as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


setup(
    name="audiotool-one",
    version=get_version(),
    keywords=["deep learning", "script helper", "tools"],
    description="audiotool is a DeepLearning utility library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="GPL-3.0",
    classifiers=[
        # Operation system
        "Operating System :: OS Independent",
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        # Topics
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        # Pick your license as you wish
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(),
    entry_points={
        "console_scripts": ["audiotool = audiotool.main_speaker_extract:main"]
    },
    include_package_data=True,
    author="Q",
    author_email="aa@qq.com",
    url="https://ccc.cc/a",
    platforms="any",
    install_requires=[
        "pyannote.audio",
        "torchaudio",
        "torch",
        "pydub",
        "numpy",
        "rotary_embedding_torch",
        "modelscope",
        "funasr",
        "umap-learn",
        "yamlargparse",
        "torchinfo",
        'kaldi_native_fbank',
        'silero_vad',
        'pyaudio',
        'hdbscan'
    ],
)
