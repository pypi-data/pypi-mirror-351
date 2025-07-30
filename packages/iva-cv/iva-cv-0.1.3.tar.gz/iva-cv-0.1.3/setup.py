from setuptools import setup, find_packages

setup(
    name="iva-cv",
    version="0.1.3",  # Increment version
    description="Custom OpenCV with FFmpeg & GStreamer support",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="GVD-Clarify-IVA",
    author_email="herambmishra@geniusvision.in",
    url="https://geniusvision.in",
    packages=["cv2"],  # Include cv2 module
    package_data={"cv2": ["*"]},  # Include everything under cv2
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)
