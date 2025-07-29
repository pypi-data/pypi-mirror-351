from typing import Union, Callable, Dict, List, Any
from sympy import symbols, latex
import matplotlib.pyplot as plt
import math
import numpy as np
from itertools import product


def _get_parameter_combinations(parameters: Dict[str, Any]):
    """Convert parameters dict to a list of parameter combinations."""
    param_values = {k: v if isinstance(v, list) else [v] for k, v in parameters.items()}
    combinations = list(product(*param_values.values()))
    return [dict(zip(param_values.keys(), combo)) for combo in combinations]


def _get_support_bernulli(distribution, params_list):
    """Calculate support for Bernulli distribution."""
    if any(isinstance(params.get("p"), list) for params in params_list):
        return [np.arange(0, 2) for _ in params_list]
    return np.arange(0, 2)


def _get_support_binomial(distribution, params_list):
    """Calculate support for Binomial distribution."""
    supports = [np.arange(0, elem["n"] + 1) for elem in params_list]
    return supports[0] if len(supports) == 1 else supports


def _get_support_hypergeometric(distribution, params_list):
    """Calculate support for HyperGeometric distribution."""
    supports = [np.arange(0, elem["N"] + 1) for elem in params_list]
    return supports[0] if len(supports) == 1 else supports


def _get_support_uniform(distribution, params_list):
    """Calculate support for Uniform distribution."""
    supports = [np.arange(elemt["a"], elemt["b"] + 1) for elemt in params_list]
    return supports[0] if len(supports) == 1 else supports


def _get_support_normal(distribution, params_list):
    """Calculate support for Normal distribution."""
    supports = [
        np.linspace(
            elemt["m"] - math.sqrt(elemt["v"]) * 3,
            elemt["m"] + math.sqrt(elemt["v"]) * 3,
            70,
        )
        for elemt in params_list
    ]
    return supports[0] if len(supports) == 1 else supports


def _get_support_probability_threshold(distribution, params_list, threshold=0.001):
    """Calculate support based on probability threshold."""
    support_max = []
    for param in params_list:
        support = []
        i = 0 if distribution.get_name == "Poisson" else 1
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < threshold:
                break
            support.append(i)
            i += 1
        support_max.append(support)

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_continuous_threshold(
    distribution, params_list, threshold=0.001, start=0.01
):
    """Calculate support for continuous distributions based on threshold."""
    support_max = []
    for param in params_list:
        i = 1
        max_num = 0
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < threshold:
                max_num = i
                break
            i *= 2
        support_max.append(np.linspace(start, max_num, 80))

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_exponential(distribution, params_list):
    """Calculate support for Exponential distribution."""
    support_max = []
    for param in params_list:
        i = 0
        max_num = 0
        while True:
            prob = distribution.replace(param).subs(distribution.x, i).evalf()
            if prob < 0.001:
                max_num = i
                break
            i += 1
        support_max.append(np.linspace(0, max_num, 60))

    if len(support_max) == 1:
        return support_max[0]
    else:
        max_index = max(range(len(support_max)), key=lambda i: len(support_max[i]))
        longest_list = support_max[max_index]
        return [longest_list[:] for _ in support_max]


def _get_support_for_distribution(distribution, params_list):
    """Determine appropriate support based on distribution type."""
    dist_name = distribution.get_name

    if dist_name == "Bernulli":
        return _get_support_bernulli(distribution, params_list)
    elif dist_name == "Binomial":
        return _get_support_binomial(distribution, params_list)
    elif dist_name == "HyperGeometric":
        return _get_support_hypergeometric(distribution, params_list)
    elif dist_name == "Uniform":
        return _get_support_uniform(distribution, params_list)
    elif dist_name == "Normal":
        return _get_support_normal(distribution, params_list)
    elif dist_name == "Exponential":
        return _get_support_exponential(distribution, params_list)
    elif dist_name == "Geometric" or dist_name == "Poisson":
        return _get_support_probability_threshold(distribution, params_list)
    elif dist_name in ["Weibull", "Gamma", "Beta", "LogNormal", "Lindley"]:
        return _get_support_continuous_threshold(distribution, params_list)

    # Default case: return a reasonable range
    return np.linspace(0, 10, 50)


def _plot_discrete_distribution(
    plt, support, probs, color=None, params=None, distribution=None, mode=None
):
    """Plot a discrete distribution."""
    if mode.lower() in ["cdf", "sf", "hf"]:
        for i in range(len(list(support)) - 1):
            plt.hlines(
                y=probs[i],
                xmin=list(support)[i],
                xmax=list(support)[i + 1],
                color=color if color else "r",
                linestyle="-",
            )

    markerline, _, _ = plt.stem(
        list(support),
        probs,
        linefmt="none",
        markerfmt="o",
        basefmt=" ",
        label=r"$" + latex(distribution) + (f", {params}" if params else "") + r"$",
    )
    if color:
        markerline.set_color(color)


def _plot_continuous_distribution(
    plt, support, probs, color=None, params=None, distribution=None
):
    """Plot a continuous distribution."""
    plt.plot(
        support,
        probs,
        color=color,
        label=r"$" + latex(distribution) + (f", {params}" if params else "") + r"$",
    )


def plot_function(
    function: Union[str, Callable], mode: str, parameters, *args, **kwargs
):
    """
    Plot a probabilistic function with given parameters.

    Args:
        function: The probabilistic function to plot
        mode: Mode of the function
        parameters: Dictionary of parameters for the function
        *args, **kwargs: Additional arguments for the plot
    """
    size = kwargs.get("size", (5, 5))
    legend = kwargs.get("legend", True)
    distribution = function

    # Get all parameter combinations
    param_combinations = _get_parameter_combinations(parameters)

    # Get appropriate supports for this distribution
    distribution._support = _get_support_for_distribution(
        distribution, param_combinations
    )

    plt.figure(figsize=size)
    colors = plt.cm.tab10.colors

    # Handle multiple parameter sets
    if len(param_combinations) > 1:
        for i, (params, color, support) in enumerate(
            zip(
                param_combinations,
                colors[: len(param_combinations)],
                (
                    distribution._support
                    if isinstance(distribution._support, list)
                    else [distribution._support] * len(param_combinations)
                ),
            )
        ):
            dis = distribution.replace(params, mode)
            probs = [dis.subs(distribution.x, i).evalf() for i in support]

            if distribution.get_mode == "Discrete":
                _plot_discrete_distribution(
                    plt,
                    support,
                    probs,
                    color=color,
                    params=params,
                    distribution=dis,
                    mode=mode,
                )
            elif distribution.get_mode == "Continuous":
                _plot_continuous_distribution(
                    plt, support, probs, color=color, params=params, distribution=dis
                )
    else:
        # Single parameter set
        dis = distribution.replace(param_combinations[0], mode)
        support = distribution._support
        probs = [dis.subs(distribution.x, i).evalf() for i in support]

        if distribution.get_mode == "Discrete":
            _plot_discrete_distribution(
                plt, support, probs, params=parameters, distribution=dis, mode=mode
            )
        elif distribution.get_mode == "Continuous":
            _plot_continuous_distribution(
                plt, support, probs, color="b", params=parameters, distribution=dis
            )
    if legend:
        plt.legend()
    plt.show()


# Import distributions based on context
if __name__ == "__main__":
    from probabilistic_functions.core import (
        Bernulli,
        Binomial,
        Geometric,
        HyperGeometric,
        Poisson,
        Uniform,
        Exponential,
        Normal,
        Weibull,
    )
else:
    from .core import (
        Bernulli,
        Binomial,
        Geometric,
        HyperGeometric,
        Poisson,
        Uniform,
        Exponential,
        Normal,
        Weibull,
    )
