# Euro NCAP Rating 2026

This repository provides tools for calculating Euro NCAP rating scores for 2026. It includes utilities for data conversion, score computation, and visualization of results.

## Installation

Euro NCAP Rating 2026 can be installed using pip.

### Prerequisites

Before installing the package, ensure you have the following prerequisites:

- **Python**: Version 3.10 or higher is required. You can download Python from the [official website](https://www.python.org/).

#### Using a Virtual Environment (Recommended)

It is recommended to use a Python virtual environment to isolate dependencies and avoid conflicts with other Python projects. 

You only need to create the virtual environment once; after that, simply activate it whenever you work on the project.

**On Linux/macOS:**

```bash
python3 -m venv venv  # Create once
source venv/bin/activate  # Activate each time
```

**On Windows (Command Prompt):**

```cmd
python -m venv venv  # Create once
venv\Scripts\activate.bat  # Activate each time
```

**On Windows (PowerShell):**

```powershell
python -m venv venv  # Create once
venv\Scripts\Activate.ps1  # Activate each time
```

Once the virtual environment is activated, you can proceed with the installation steps below.

**From PyPi**

The recommended way to install the package is via PyPi, which is the default package index for Python.
Note that the package is not available on PyPi yet, so you can install it from the GitHub repository or a local repository.

```bash
pip install euroncap-rating-2026
```


**From GitHub repository**

It is also possible to install the package from a local repository or from GitHub, provided you have access to the Git repository.

Ensure you have the following additional prerequisites installed:

- **Git**: Required for installation from the GitHub repository. You can download Git from the [official website](https://git-scm.com/).

You can install the project with the command:

```bash
pip install euroncap_rating_2026@git+https://github.com/Euro-NCAP/euroncap_rating_2026
```



## Usage


**Generate the input template:**

    ```bash
    euroncap_rating_2026 generate_template
    ```

    This create a  `template.xlsx` file to your current directory.

**Fill in the required fields in the template (see Input Format section).**

**Compute scores:**

    ```bash
    euroncap_rating_2026 compute --input_path $PATH_TO_XLSX_FILE
    ```

The complete application help test is shown below:

```bash
euroncap_rating_2026 --help
usage: euroncap_rating_2026 <command> [options]

Euro NCAP Rating Calculator 2026 application to compute NCAP scores.

positional arguments:
  {compute,generate_template}
                        Sub-commands
    compute             Compute NCAP scores from an input Excel file.
    generate_template   Generate template.xlsx file to the current working directory.

options:
  -h, --help            show this help message and exit

euroncap_rating_2026 -h for help
```

Score computation usage:

```bash
euroncap_rating_2026 compute --input_file example.xlsx
```

## Input Format

The application expects the input file to be in `.xlsx` format. A template file is provided at [`data/template.xlsx`](data/template.xlsx) to guide users in preparing their input.

- **Input Requirements**: Users must provide values for all cells in the template that are highlighted with a **light grey background**. These cells represent the required input data for the application to compute the scores.

  ![Input Template Example](.img/grey_cell.png)

## Output Format

The output is an updated `.xlsx` file where all scoring cells are filled with computed scores.

The output file is saved with the naming convention `DATE_TIME_report.xlsx`, where `DATE_TIME` is replaced with the current date and time in the format `YYYY-MM-DD_HH-MM-SS`. For example, an output file generated on March 15, 2026, at 14:30:45 would be named `2026-03-15_14-30-45_report.xlsx`.

This naming convention ensures that each output file is unique and timestamped for easy identification.

- **Output Details**: The cells updated by the application are highlighted with a **yellow background** in the output file, making it easy to identify the computed results.

  ![Output Template Example](.img/yellow_cell.png)


## Development

### Configuration Options

For development, different configuration options are available. The application can be run in debug mode, which provides additional logging and a GUI for debugging purposes.

The application supports two configuration options:

1. **`log_level`**: Controls the logging level of the application (e.g., `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
2. **`enable_debug_gui`**: Enables or disables the debug GUI for the application. Debug GUI requires `tkinter` library to be installed alongside Python.

    If `tkinter` is not available on your system, you will encounter an error when attempting to use the debug GUI. To resolve this, follow the instructions below to install it:

    - **Windows**: Install Python's Tkinter module via the Python installer.
    - **Mac**: Tkinter is included with Python on macOS. Ensure you have Python installed.
    - **Linux**: Run `sudo apt-get install python3-tk` to install Tkinter.

Configuration options can be specified using environment variables. 

- `EURONCAP_RATING_2026_LOG_LEVEL`: Sets the logging level.
- `EURONCAP_RATING_2026_ENABLE_DEBUG_GUI`: Enables the debug GUI when set to `1`.

You can set the following environment variables before running the application:

**On Linux/macOS:**

```bash
export EURONCAP_RATING_2026_LOG_LEVEL=DEBUG
export EURONCAP_RATING_2026_ENABLE_DEBUG_GUI=1
```

**On Windows (Command Prompt):**

```cmd
set EURONCAP_RATING_2026_LOG_LEVEL=DEBUG
set EURONCAP_RATING_2026_ENABLE_DEBUG_GUI=1
```

**On Windows (PowerShell):**

```powershell
$env:EURONCAP_RATING_2026_LOG_LEVEL="DEBUG"
$env:EURONCAP_RATING_2026_ENABLE_DEBUG_GUI="1"
```


### Installation from source

To run tests and develop the project, you need to install it from source.

After cloning the repository, install the project using [Poetry](https://python-poetry.org/).

```bash
poetry install
```

After installing from source, the usage is similar to above.

```bash
euroncap_rating_2026 --help
```

```bash
euroncap_rating_2026 --input_file ~/Documents/test_file.xlsx
 Computing NCAP scores...
   Processing CP - Side Farside..
   Processing CP - Frontal FW..
   Processing CP - Frontal Offset..
   Processing CP - Frontal Sled & VT..
   Processing CP - Side MDB..
   Processing CP - Side Pole..
   Processing CP - Rear Whiplash..
Score:
Test                Score     Max Score
----------------------------------------
Farside             9.0       10.0
FW                  9.5       10.0
Offset              13.75     20.0
Sled & VT           10.0      10.0
MDB                 0.0       15.0
Pole                0.0       10.0
Rear                0.0       7.5
----------------------------------------

Final score         42.25     82.5

Log available at /home/user/euroncap_rating_2026.log
```

## Tests

### Unit Tests

Unit test can be executed with the command:

```bash
python -m unittest discover -s tests
```


It should output something similar to:

```
....................................................................
----------------------------------------------------------------------
Ran 68 tests in 0.029s

OK
```

You can check more options for unittest at its [own documentation](https://docs.python.org/3/library/unittest.html).

### Smoke Test

A Docker-based smoke test suite is included to verify that the application and its dependencies work correctly in a containerized environment. The smoke test automatically generates test input files, runs the main application, and checks for successful execution and output generation.

For details on how to build and run the smoke test, see the [smoke_test/README.md](smoke_test/README.md).

## Python Library Licenses

Below is a list of the Python libraries used in this project along with their respective licenses and PyPI links.

| Library              | Version     | License       | PyPI Link                                      |
|----------------------|-------------|---------------|------------------------------------------------|
| pandas               | ^2.2.3      | BSD-3-Clause  | [pandas](https://pypi.org/project/pandas/)     |
| pydantic             | ^2.11.1     | MIT           | [pydantic](https://pypi.org/project/pydantic/) |
| pydantic-settings    | ^2.8.1      | MIT           | [pydantic-settings](https://pypi.org/project/pydantic-settings/) |
| openpyxl             | ^3.1.5      | MIT           | [openpyxl](https://pypi.org/project/openpyxl/) |
| pdoc                 | ^15.0.1     | MIT           | [pdoc](https://pypi.org/project/pdoc/15.0.1/)  |
