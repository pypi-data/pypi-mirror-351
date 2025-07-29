import setuptools

setuptools.setup(
    name="clevermaps-jupyter-widget",
    version="0.0.1",
    author="Karel Psota",
    author_email="karel.psota@clevermaps.io",
    description="CleverMaps Jupyter widget",
    packages=['cm_jupyter_widget'],
    package_data={'cm_jupyter_widget': ['index.js', 'index.css']},
    include_package_data=True,
    install_requires=[
	'anywidget'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)
