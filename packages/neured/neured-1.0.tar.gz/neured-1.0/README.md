NeuRED
NeuRED: Framework for Processing Time-series Neutron Radiography of Electrochemical Devices
Developed by the Applied Materials Group (AMG), Paul Scherrer Institut (PSI)

Overview
NeuRED provides tools and example frameworks for processing time-series neutron imaging datasets, particularly for energy storage and conversion devices.
It has been primarily developed for PSI internal research, but is freely available to external users under the MIT license.

Installation
pip install neured
Make sure you have Python 3.8 or newer and pip installed.
We recommend using Anaconda as the base Python distribution.

Dependencies
NeuRED automatically installs the following core dependencies:

numpy
scipy
matplotlib
opencv-python
astropy
jupyter
ipython
pyqt5
pyqtgraph

Optional (legacy only): jupyter_contrib_nbextensions
This package is no longer included by default due to its incompatibility with modern PEP 517 builds.
If you wish to activate the optional legacy Magic Selector buttons inside Jupyter notebooks, install manually:

pip install jupyter_contrib_nbextensions 

There has been a known conflict with nbextensions install with updated versions of pip. In such case, use the following command on conda prompt (as an admin):

conda install -c conda-forge jupyter_contrib_nbextensions

Then run:

jupyter contrib nbextension install --user

Please note that jupyter_contrib_nbextensions is considered deprecated.

Example notebooks and demo data
Example notebooks and demonstration data are installed with NeuRED under the folder:

<python site-packages>/neured/demo_notebooks/

You can also access the folder programmatically after installation:

import neured
from pathlib import Path
demo_path = Path(neured.__file__).parent / "demo_notebooks"
print(demo_path)

The demo_notebooks folder contains example Jupyter notebooks and demonstration datasets to get started.

Usage example
After installation, verify that the package works by opening Python and running:

go
Copy
Edit
import neured
print(neured.__version__)
For further examples, refer to the Jupyter notebooks provided in the demo_notebooks folder.

Developer information (internal PSI setup)
Internal PSI users may optionally install Anaconda3 and TortoiseGit via the software kiosk.
A recommended local working directory is:

makefile
Copy
Edit
C:\Software\NeuRED
To clone and work with the source code:

bash
Copy
Edit
git clone https://gitlab.psi.ch/your-repository-url.git
cd NeuRED
pip install -e .
This allows live development without needing repeated installation after code changes.

License
NeuRED is distributed under the MIT License.
Copyright 2025 Paul Scherrer Institute (PSI) and NeuRED contributors.

Contact
For support, bug reports, or contributions, please contact:
Dr. Pierre Boillat (pierre.boillat@psi.ch) or Dr. Jongmin Lee (jongmin.lee@psi.ch)