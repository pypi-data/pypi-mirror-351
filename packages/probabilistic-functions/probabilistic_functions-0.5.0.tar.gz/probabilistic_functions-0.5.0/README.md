# Probabilistic Functions

A comprehensive Python library for working with probability distributions and statistical functions. This library provides tools for symbolic and numeric manipulation of probability distributions, along with visualization capabilities.

## ⚠️ Requirements
> **Warning**  
> This library is designed to work primarily in Jupyter environments with LaTeX support. Some functionality may not work correctly outside of this environment.

- Python 3.13+
- Jupyter Notebook/Lab
- LaTeX installation for proper equation rendering

## Installation

Install the library using pip:

```bash
pip install probabilistic-functions
```

## Features

- Symbolic representation of probability distributions
- Calculation of probability mass/density functions (PMF/PDF)
- Calculation of cumulative distribution functions (CDF)
- Statistical properties (mean, variance, etc.)
- Visualization of distributions with customizable parameters
- Support for both discrete and continuous distributions

## Supported Distributions

### Discrete Distributions
- Bernoulli
- Binomial
- Geometric
- Hypergeometric
- Poisson

### Continuous Distributions
- Normal (Gaussian)
- Exponential
- Uniform
- Weibull
- Gamma
- Beta
- LogNormal
- Lindley

## Experimental Distributions (Limited Support)

The following distributions are included in the library, but their functionality may be limited or unstable:

- Burr
- Pareto
- Cauchy
- Laplace
- Gumbel

> **Note:** Support for these distributions is under development. Some functions may not be fully implemented or may produce unexpected results.

## Usage Examples

```python
from probabilistic_functions.core import Binomial, Normal
from probabilistic_functions.plots import plot_function

# Plot a binomial distribution
binomial = Binomial()
plot_function(binomial, "pmf", {"n": 10, "p": 0.5})

# Plot multiple normal distributions
normal = Normal()
plot_function(normal, "pdf", {"m": [0, 1], "v": [1, 2]})
```

## Working with Multiple Parameters

You can plot multiple parameter combinations by passing lists:

```python
# Plot multiple Poisson distributions with different lambda values
from probabilistic_functions.core import Poisson
poisson = Poisson()
plot_function(poisson, "pmf", {"lambda": [1, 5, 10]})
```

## Changelog

For a detailed list of changes between versions, please see the [Changelog](https://github.com/WilhelmBuitrago/probabilistic-functions/blob/main/CHANGELOG.md).

## License

Apache License 2.0

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
