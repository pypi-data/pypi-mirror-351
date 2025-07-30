## Setuptools
https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-setup-py
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-setup-cfg
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-a-source-distribution
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-a-wheel
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-a-binary-distribution
[]: # https://packaging.python.org/en/latest/tutorials/packaging-projects/#creating-a-wheels
test tst









Packaging terms:

- module: A module is a single file (with a .py extension) that contains Python code. It can define functions, classes, and variables that can be reused in other Python programs. Modules are the smallest unit of code organization in Python.
- package: A package is a collection of related modules organized in a directory hierarchy. It allows for better organization and management of code, especially in larger projects. A package must contain an __init__.py file to be recognized as a package by Python.
- regular package: A regular package is a standard package that contains an __init__.py file and can include sub-packages and modules. It is the most common type of package used in Python projects.
- namespace package: A namespace package is a special type of package that allows for the distribution of modules across multiple directories or distributions. It does not require an __init__.py file and enables different packages to share the same namespace.
- sub-package: A sub-package is a package that is contained within another package. It allows for further organization of code and can include its own modules and sub-packages. Sub-packages are typically used to group related functionality within a larger package.
- __init__.py: The __init__.py file is a special file that indicates that a directory should be treated as a package. It can be empty or contain initialization code for the package. This file is executed when the package is imported, allowing for package-level variables and functions to be defined.
- __all__: The __all__ variable is a list that defines the public interface of a module or package. It specifies which names should be exported when the module is imported using the from module import * syntax. This helps control what is accessible to users and prevents accidental access to internal functions or variables.
- __main__: The __main__ module is the entry point of a Python program. It is the module that is executed when a Python script is run directly. The __name__ variable is set to "__main__" in this context, allowing for conditional execution of code based on whether the module is being run as the main program or imported as a module.
- __name__: The __name__ variable is a built-in variable in Python that represents the name of the current module. When a module is run directly, __name__ is set to "__main__". When it is imported as a module, __name__ is set to the module's name. This allows for conditional execution of code based on how the module is being used.
- __package__: The __package__ variable is a built-in variable in Python that represents the name of the package that a module belongs to. It is used to determine the package hierarchy and can be useful for relative imports within packages.
- __file__: The __file__ variable is a built-in variable in Python that represents the path to the current module's file. It can be used to determine the location of the module and is often used for loading resources or data files relative to the module's location.
- __path__: The __path__ variable is a built-in variable in Python that represents the search path for modules in a package. It is a list of directories that Python searches when importing modules. This variable can be modified to include additional directories for module searching.
- __cached__: The __cached__ variable is a built-in variable in Python that represents the path to the compiled bytecode file for a module. It is used to store the compiled version of the module to improve import performance. The __cached__ variable is typically used in conjunction with the __file__ variable to determine the location of the bytecode file.
- library: A library is a collection of related modules and packages that provide specific functionality. Libraries can be installed and used in Python programs to extend the capabilities of the language. Examples include NumPy, Pandas, and Matplotlib.
- framework: A framework is a larger, more comprehensive collection of libraries and tools that provide a foundation for building applications. Frameworks often dictate the structure and flow of the application, providing a set of conventions and best practices. Examples include Django, Flask, and React.
- distribution: A distribution is a packaged version of a library or application that can be easily installed and managed. Distributions are typically created using tools like setuptools or distutils and can be shared via package repositories like PyPI (Python Package Index).
- dependency: A dependency is a library or package that a project relies on to function correctly. Dependencies can be managed using tools like pip, which allows for easy installation and version management.
- versioning: Versioning is the practice of assigning unique version numbers to software releases. This helps developers track changes, manage dependencies, and ensure compatibility between different versions of libraries and applications. Semantic versioning (e.g., MAJOR.MINOR.PATCH) is a common convention used in versioning.
- virtual environment: A virtual environment is an isolated Python environment that allows developers to manage dependencies and packages for a specific project without affecting the global Python installation. This is useful for avoiding version conflicts and ensuring that projects have the necessary dependencies.
- requirements file: A requirements file is a text file that lists the dependencies required for a Python project. It typically includes the package names and their versions. This file can be used with pip to install all the required packages in a virtual environment.
- setup.py: A setup.py file is a Python script used to package and distribute a library or application. It contains metadata about the project, such as its name, version, author, and dependencies. This file is typically used with setuptools to create a distribution package.
- entry point: An entry point is a specific function or method in a library or application that serves as the starting point for execution. It allows users to run the code without needing to know the internal structure of the package. Entry points are often defined in the setup.py file and can be used to create command-line interfaces or plugins.
- namespace package: A namespace package is a type of package that allows for the distribution of modules across multiple directories or distributions. This enables different packages to share the same namespace, making it easier to organize and manage large codebases. Namespace packages are defined using the __init__.py file and can be created using tools like setuptools.
- egg: An egg is a distribution format for Python packages that allows for easy installation and management of dependencies. Eggs can contain both code and metadata about the package, including its dependencies and entry points. The egg format has been largely replaced by the wheel format but is still used in some projects.
- wheel: A wheel is a distribution format for Python packages that provides a faster and more efficient way to install and manage dependencies. Wheels are binary distributions that can be installed using pip, making them easier to work with than source distributions. The wheel format is now the preferred distribution format for Python packages.
- source distribution: A source distribution is a distribution format for Python packages that contains the source code and metadata required to build and install the package. Source distributions are typically used when a package cannot be installed as a binary wheel or when users want to modify the source code before installation.
- build: The process of creating a distribution package from source code. This typically involves compiling the code, generating metadata, and creating the necessary files for installation. The build process can be automated using tools like setuptools or distutils.
- install: The process of copying a distribution package to the appropriate location in the Python environment, making it available for use in Python programs. This can be done using tools like pip or by running the setup.py script directly.
- uninstall: The process of removing a distribution package from the Python environment. This can be done using tools like pip or by manually deleting the package files.
- upgrade: The process of updating a distribution package to a newer version. This can be done using tools like pip, which can automatically handle dependencies and ensure that the latest version is installed.
- downgrade: The process of reverting a distribution package to an older version. This can be done using tools like pip, which allows users to specify the desired version of the package to install.
- pip: Pip is the package manager for Python that allows users to install, upgrade, and manage Python packages and dependencies. It is the most widely used tool for managing Python packages and is included with most Python installations.
test45
