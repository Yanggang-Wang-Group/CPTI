# CPTI-generator
a workflow to do constant potential thermodynamic integration (CPTI) in VASP

## Download and Install

CPTI-generator only supports Python 3.6 and above.

One can download the source code of cpti by
```bash
git clone https://github.com/Yanggang-Wang-Group/CPTI.git
```
then you may install CPTI-generator easily by:
```bash
cd CPTI
pip install .
```
To test if the installation is successful, you may execute
```bash
cpti -h
```
## Workflows and usage
CPTI-generator currently contains the two main functions:
* `cpti run`: Main process of the Generator.
* `cpti noderun` run cpti on the node, check `cpti.sh` for more details.
* `cpti init_conf` : Generating a series of configuration along a reaction coordinate.
For detailed usage and parameters, please check it out by `cpti run -h` and `cpti init_conf -h` in shell.
## Examples
* [Run](examples/run)
* [init_conf](examples/init_conf)
