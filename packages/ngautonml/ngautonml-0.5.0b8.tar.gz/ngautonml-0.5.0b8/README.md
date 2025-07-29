# ngAutonML

## ngAutonML

The **ngAutonML** project is an Automated Machine Learning solution intended to make it much easier to find good solutions to common machine learning problems, or to aid in prototyping a more complex solution. It aims to be simple to use for the bulk of machine learning problems, but maintains a high level of customizability for those situations that require more specific setups by more experiences machine learning professionals.

This project is the result of research performed as part of the [D3M](https://datadrivendiscovery.org) project run by DARPA. It is a reimplementation of many concepts used in that project, and is currently under heavy development.

## Installation

It is recommended to create a virtual environment to run ngautonml.  To do so with conda, run:
```
conda create -n env-name python=3.10
conda activate env-name
```

To install from pypi, use:
```
pip install ngautonml
```
ngAutonML is designed to run on Python 3.10 and above.

To install from this repository, use poetry:
```
pip install poetry
poetry install
```

If you are a developer, install the dev dependency group as well:
```
poetry install --with dev
```
This includes linters that code must be compliant with.

## Usage
To use ngAutonML from the command line, you need to provide a problem definition (see below).  Run:

```
python picard.py wrangle -d <path to problem definition>
```

The problem definition is a JSON file that describes the machine learning problem you wish ngAutonML to tackle. A simple problem definition might look like:

```
{
    "dataset" : {
        "config" : "memory",
        "params" : {
            "train_data": "train",
            "test_data": "test"
        },
        "column_roles": {
            "target": {
                "name": "target"
            }
        }
    },
    "problem_type" : {
        "data_type": "tabular",
        "task": "binary_classification"
    },
    "metrics" : {
        "accuracy_score": {},
        "roc_auc_score": {}
    }
}
```
Examples can be found in the ```examples``` directory, but in brief the important aspects are the following fields:

- dataset: The dataset that the algorithms are being run on.  There are serveral data loaders that can load data from different sources.
- problem_type: This uses the subfields of ```data_type``` to tell the type of dataset, and the ```task``` to determine how the dataset will be handled, such as a classification or forecasting problem.
- metrics: This field defines the scoring metric(s) that ngAutonML will use to evaluate algorithms.

For more information, see [our documentation](https://autonlab.gitlab.io/ngautonml/quickstart.html)

## Support

Currently all issues should be generated via the GitLab Issue Tracker.

## Roadmap

In Development:
- Support for external models such as Docker Containers or LLM services
- Code generation for insertion into your own projects or for low-level customization
- API support

## Contributing

If forking and wanting to contribute, please ensure PEP8 Compliance. The current project uses flake8, mypy, and pylint for code compliance, with the exception of setting the maximum line length to 100 characters.

## Authors and acknowledgment

The CMU AutonML Development Team:

Piggy Yarroll (programmer/architect) \
Andrew Williams (programmer) \
Merritt Kowaleski (programmer) \
Mujing Wang (programmer) \
Carter Weaver (programmer) \
Jeishi Chen (data scientist)

## License

This project is currently licensed under the Apache 2.0 license.
