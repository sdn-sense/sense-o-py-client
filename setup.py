import setuptools

from sense import __VERSION__

with open("requirements.txt", "r", encoding="utf-8") as fh:
  requirements = fh.read()

setuptools.setup(
  name="sense_o_api",
  version=__VERSION__,
  author="Xi Yang",
  description="SENSE-Orchestrator Northbound API Client",
  url="https://github.com/esnet/StackV",
  long_description="SENSE-Orchestrator Northbound API Client Library",
  long_description_content_type="text/plain",
  packages=setuptools.find_packages(),
  include_package_data=True,
  scripts=['util/sense_util.py', 'sense/workflow/sense_workflow.py'],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
  ],
  python_requires=">=3.6",
  install_requires=requirements,
  setup_requires=requirements,
)
