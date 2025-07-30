from setuptools import setup, find_packages

setup(
    name="iva-cv",  # PyPI package name can remain 'iva-cv'
    version="0.1.2",
    description="Custom OpenCV with FFmpeg & GStreamer support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="GVD-Clarify-IVA",
    author_email="herambmishra@geniusvision.in",
    url="https://geniusvision.in",
    packages=find_packages(),
    package_data={"cv2": ["cv2*.so"]},  # Updated from 'iva_cv' to 'cv2'
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)
