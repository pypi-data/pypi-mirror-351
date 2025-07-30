[String] $VEnvPythonPath = [IO.Path]::Combine([IO.Path]::GetDirectoryName($PSCommandPath), ".venv", "Scripts/python.exe")
#& $VEnvPythonPath -m pip install --upgrade pkginfo
#& $VEnvPythonPath -m pip install --upgrade twine
#& $VEnvPythonPath -m pip install --upgrade hatchling
& $VEnvPythonPath -m build
& $VEnvPythonPath -m twine upload --skip-existing --repository pypi dist/*


#& "C:/Program Files/Python312/python.exe" -m pip install --upgrade pkginfo
#& "C:/Program Files/Python312/python.exe" -m pip install --upgrade twine
#& "C:/Program Files/Python312/python.exe" -m pip install --upgrade hatchling
#& "C:/Program Files/Python312/python.exe" -m build
#& "C:/Program Files/Python312/python.exe" -m twine upload --skip-existing --repository pypi dist/*