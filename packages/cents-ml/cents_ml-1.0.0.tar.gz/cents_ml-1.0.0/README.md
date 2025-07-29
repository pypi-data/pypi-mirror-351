<p align="left">
<img width=15% src="https://dai.lids.mit.edu/wp-content/uploads/2018/06/Logo_DAI_highres.png" alt=“DAI-Lab” />
<i>An open source project from Data to AI Lab at MIT.</i>
</p>

[![PyPI Shield](https://img.shields.io/pypi/v/Cents.svg)](https://pypi.python.org/pypi/cents)
[![Downloads](https://pepy.tech/badge/cents)](https://pepy.tech/project/cents)
[![GitHub Actions Build Status](https://github.com/DAI-Lab/Cents/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/DAI-Lab/Cents/actions)


# Cents

A library for generative modeling and evaluation of synthetic household-level electricity load timeseries. This package is still under active development.

- Documentation: (tbd)

# Overview

Cents is a library built for generating *synthetic household-level electric load and generation timeseries*. Cents supports several generative time series models that can be used to train a time series data generator from scratch on a user-defined dataset. Additionally, Cents provides functionality for loading pre-trained model checkpoints that can be used to generate data instantly. Trained models can be evaluated using a series of metrics and visualizations also implemented here.

These currently supported models are:

- [Diffusion-TS](https://github.com/Y-debug-sys/Diffusion-TS/tree/main)
- [ACGAN](https://arxiv.org/abs/1610.09585)

Feel free to look at our [tutorial notebooks]() to get started.

# Install

## Requirements

**Cents** has been developed and tested on [Python 3.9]((https://www.python.org/downloads/)), [Python 3.10]((https://www.python.org/downloads/)) and [Python 3.11]((https://www.python.org/downloads/)).

Also, although it is not strictly required, the usage of a [virtualenv](https://virtualenv.pypa.io/en/latest/)
is highly recommended in order to avoid interfering with other software installed in the system
in which **Cents** is run.

These are the minimum commands needed to create a virtualenv using python3.8 for **Cents**:

```bash
pip install virtualenv
virtualenv -p $(which python3.9) cents-venv
```

Afterwards, you have to execute this command to activate the virtualenv:

```bash
source cents-venv/bin/activate
```

Remember to execute it every time you start a new console to work on **Cents**!

## Install from PyPI

After creating the virtualenv and activating it, we recommend using
[pip](https://pip.pypa.io/en/stable/) in order to install **Cents**:

```bash
pip install cents
```

This will pull and install the latest stable release from [PyPI](https://pypi.org/).
-->

<!-- ## Install from source

With your virtualenv activated, you can clone the repository and install it from
source by running `make install` on the `stable` branch:

```bash
git clone git@github.com:michael-fuest/Cents.git
cd Cents
git checkout stable
make install
``` -->

<!-- ## Install for Development

If you want to contribute to the project, a few more steps are required to make the project ready
for development.

Please head to the [Contributing Guide](https://michael-fuest.github.io/Cents/contributing.html#get-started)
for more details about this process. -->

<!-- # Quickstart

In this short tutorial we will guide you through a series of steps that will help you
getting started with **Cents**.

## Generating Data

To get started, define a DataGenerator and specify the name of the model you would like to use.

```python
generator = DataGenerator(model_name="diffusion_ts")
```

We provide pre-trained model checkpoints that were trained on the [PecanStreet Dataport](https://www.pecanstreet.org/dataport/) dataset. You can use these checkpoints to load a trained model. The first step is to assign the `DataGenerator` a `TimeSeriesDataset`instance. We are using the `PecanStreetDataset` class here, which is an extension of `TimeSeriesDataset`.

```python
dataset = PecanStreetDataset()
generator.set_dataset(dataset)
```

Once a dataset has been assigned, we can load a pre-trained model for that dataset as follows:

```python
generator.load_model()
```

These pre-trained models are conditional models, meaning they require a set of conditioning variables to generate synthetic time series data. If you want to generate data for a random set of conditioning variables, you can do so as follows:

```python
conditioning_variables = generator.sample_random_conditioning_variables()
synthetic_data = generator.generate(conditioning_variables)
```

For a more in-depth tutorial, please refer to the tutorial notebooks in the `tutorials` directory. -->

## Datasets

If you want to reproduce our models from scratch, you will need to download the [PecanStreet DataPort dataset](https://www.pecanstreet.org/dataport/) and place it under the path specified in `pecanstreet.yaml`. Specifically you will require the following files:

- 15minute_data_austin.csv
- 15minute_data_california.csv
- 15minute_data_newyork.csv
- metadata.csv

# What's next?

New models, new evaluation functionality and new datasets coming soon!
