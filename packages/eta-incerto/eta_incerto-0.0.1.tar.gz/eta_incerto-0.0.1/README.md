# ETA Incerto

Insert a short project description here

## Usage

## Installation

To install the project along with its development dependencies, execute the following command:

    poetry install

Followed by

    poetry add git+https://git.ptw.maschinenbau.tu-darmstadt.de/eta-fabrik/public/eta-components.git#main

Followed by

    poetry run pre-commit install

After this you are ready to perform the first commits to the repository.

Pre-commit ensures that the repository accepts your commit, automatically fixes some code styling problems and provides some hints for better coding.

### Adding dependencies
Adding dependencies to the project can be done via

    poetry add <package-name>@latest
