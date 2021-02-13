from setuptools import setup, find_packages
from setuptools.extension import Extension
import numpy

setup(name="micromagnet_simulator",
	description='Simple umagnet calculator for spin qubits',
	author='Stephan Philips',
	version="1.0",
	packages = find_packages(),
	install_requires=['gdspy', 'magpylib'])
