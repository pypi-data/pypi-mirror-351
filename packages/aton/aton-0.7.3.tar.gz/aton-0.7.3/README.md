<p align="center"><img width="40.0%" src="pics/aton.png"></p>


# Welcome to ATON

**A** **T**ext **O**ptimizer for scie**N**tific python,
or [ATON](https://pablogila.github.io/aton/),
is a package that provides powerful text-edition tools
to edit and analyse simuation data.

Just like its [ancient Egyptian deity](https://en.wikipedia.org/wiki/Aten) counterpart,
this Python package comprises several utilities to facilitate your simulation routines.
This includes a [txt](#general-text-edition) module for easy and straight-forward text edition;
an [api](#interfaces-for-ab-initio-codes) module with interfaces for simulation and HPC codes, such as [Quantum ESPRESSO](https://www.quantum-espresso.org/),
[Phonopy](https://phonopy.github.io/phonopy/) and
[CASTEP](https://castep-docs.github.io/castep-docs/);
and a [phys](#physico-chemical-constants) module with physico-chemical definitions, such as the [2022 CODATA](https://doi.org/10.48550/arXiv.2409.03787)
Recommended Values of the Fundamental Physical Constants.

The source code is available on [GitHub](https://github.com/pablogila/aton/).   
Check the [full documentation online](https://pablogila.github.io/aton/).  


---


# Installation

As always, it is recommended to install your packages in a virtual environment:  
```bash
python3 -m venv .venv
source .venv/bin/activate
```


## With pip

Install or upgrade ATON with  
```bash
pip install aton -U
```


## From source

Optionally, you can install ATON from the [GitHub repo](https://github.com/pablogila/aton/).
Clone the repository or download the [latest stable release](https://github.com/pablogila/aton/tags)
as a ZIP, unzip it, and run inside it:  
```bash
pip install .
```


---


# Documentation

The full ATON documentation is available [online](https://pablogila.github.io/aton/).  
An offline version is found at `docs/aton.html`.  
Code examples are included in the [`examples/`](https://github.com/pablogila/aton/tree/main/examples) folder.    


## General text edition

The **txt** module handles text files.
It powers more complex subpackages,
such as [aton.api](#interfaces-for-ab-initio-codes).

### [aton.txt](https://pablogila.github.io/aton/aton/txt.html)

| | |  
| --- | --- |  
| [txt.find](https://pablogila.github.io/aton/aton/txt/find.html)       | Search for specific content in text files |  
| [txt.edit](https://pablogila.github.io/aton/aton/txt/edit.html)       | Manipulate text files |  
| [txt.extract](https://pablogila.github.io/aton/aton/txt/extract.html) | Extract data from raw text strings |  


## Interfaces for *ab-initio* codes

The **api** module contains Python interfaces for several *ab-initio* codes and related.
These are powered by the [aton.txt](#general-text-edition) module and can be easily extended.

### [aton.api](https://pablogila.github.io/aton/aton/api.html)

| | |  
| --- | --- |  
| [api.qe](https://pablogila.github.io/aton/aton/api/qe.html)           | Interface for [Quantum ESPRESSO](https://www.quantum-espresso.org/)'s [pw.x](https://www.quantum-espresso.org/Doc/INPUT_PW.html) module |  
| [api.phonopy](https://pablogila.github.io/aton/aton/api/phonopy.html) | Interface for [Phonopy](https://phonopy.github.io/phonopy/) calculations |  
| [api.castep](https://pablogila.github.io/aton/aton/api/castep.html)   | Interface for [CASTEP](https://castep-docs.github.io/castep-docs/) calculations |  
| [api.slurm](https://pablogila.github.io/aton/aton/api/slurm.html) | Batch jobs via [Slurm](https://slurm.schedmd.com/) |


## Physico-chemical constants

The **phys** module contains physical constants and conversion factors,
as well as chemical information from all known elements.
Values are accessed directly as `phys.value` or `phys.function()`.

### [aton.phys](https://pablogila.github.io/aton/aton/phys.html)

| | |  
| --- | --- |  
| [phys.units](https://pablogila.github.io/aton/aton/phys/units.html)               | Physical constants and conversion factors |  
| [phys.atoms](https://pablogila.github.io/aton/aton/phys/atoms.html)               | Megadictionary with data for all chemical elements |  
| [phys.isotope](https://pablogila.github.io/aton/aton/phys/isotope.html)           | Analyse isotope data from text strings |
| [phys.export_atoms](https://pablogila.github.io/aton/aton/phys/export_atoms.html) | Update and export the `aton.phys.atoms` dict |


## System tools

Additional utility tools are available for common system tasks.

| | |  
| --- | --- |  
| [aton.file](https://pablogila.github.io/aton/aton/file.html)   | File manipulation |  
| [aton.alias](https://pablogila.github.io/aton/aton/alias.html) | Useful dictionaries for user input correction |  
| [aton.call](https://pablogila.github.io/aton/aton/call.html)   | Run bash scripts and related |   


---


# Contributing

If you are interested in opening an issue or a pull request, please feel free to do so on [GitHub](https://github.com/pablogila/aton/).  
For major changes, please get in touch first to discuss the details.  


## Code style

Please try to follow some general guidelines:  
- Use a code style consistent with the rest of the project.  
- Include docstrings to document new additions.  
- Include automated tests for new features or modifications, see [automated testing](#automated-testing).  
- Arrange function arguments by order of relevance. Most implemented functions follow something similar to `function(file, key/s, value/s, optional)`.  


## Automated testing

If you are modifying the source code, you should run the automated tests of the [`ATON/tests/`](https://github.com/pablogila/aton/tree/main/tests) folder to check that everything works as intended.
To do so, first install PyTest in your environment,
```bash
pip install pytest
```

And then run PyTest inside the `ATON/` directory,
```bash
pytest -vv
```


## Compiling the documentation

The documentation can be compiled automatically to `docs/aton.html` with [Pdoc](https://pdoc.dev/) and ATON itself, by running:
```shell
python3 makedocs.py
```

This runs Pdoc, updating links and pictures, and using the custom theme CSS template from the `css/` folder.


---


# Citation

ATON development started for the following paper, please cite if you use ATON in your work:  
[*Cryst. Growth Des.* 2024, 24, 391−404](https://doi.org/10.1021/acs.cgd.3c01112)  


# License

Copyright (C) 2025 Pablo Gila-Herranz  
This program is free software: you can redistribute it and/or modify
it under the terms of the **GNU Affero General Public License** as published
by the Free Software Foundation, either version **3** of the License, or
(at your option) any later version.  
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the attached GNU Affero General Public License for more details.  

