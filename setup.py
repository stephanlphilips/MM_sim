from setuptools import setup, find_packages
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        "micromagnet_simulator.lib.calcGxGyGz",
        ["micromagnet_simulator/lib/calcGxGyGz.pyx"],
        include_dirs=[numpy.get_include()],
        language='c++'
    )]

setup(name="micromagnet_simulator",
	description='Simple umagnet calculator for spin qubits',
	ext_modules = cythonize(extensions),
	author='Stephan Philips',
	version="1.0",
	packages = find_packages(),
	install_requires=[ 'shapely', 'gdspy'])
