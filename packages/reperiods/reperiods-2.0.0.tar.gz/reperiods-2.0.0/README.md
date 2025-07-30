<div align="center">
  <img src="https://raw.githubusercontent.com/RobinsonBeaucour/reperiods-beta/beta/docs/images/logo.svg"><br>
</div>


-----------------

# RePeriods : a tool to find Representatives Periods

## What is it?

**RePeriods** is a Python package that provides multiple methods to process time series in order to find *Representative Periods*. <br>
**Representative Periods (RPs)** are a concept often used in the context of energy systems and optimization. They are particularly useful in situations where you want to model and analyze the behavior of a system over time, but it's computationally or practically infeasible to consider every individual time step. RPs are used to capture the essential characteristics of a time series in a more manageable way. Here are some specific applications where RPs can be useful:

1. **Energy System Modeling:** RPs can be used in the modeling of energy systems, such as power grids or renewable energy generation, to represent the variability and uncertainty of energy sources over time. They provide a way to simplify complex time series data while preserving key features.

2. **Energy Management:** In energy management systems, RPs can help make decisions about how to allocate energy resources optimally. By using RPs, you can make informed decisions about when to generate, store, or use energy based on representative patterns.

3. **Optimization:** RPs are commonly used in optimization problems, where they can significantly reduce computational complexity. Instead of considering every time step, you can optimize over a set of RPs, which captures the essential behavior of the system.

4. **Long-Term Planning:** When planning for the long term, RPs can help in scenarios like capacity expansion of power plants, designing energy storage systems, or making investment decisions in renewable energy projects. They allow you to consider long-term trends without needing high-resolution data.

5. **Risk Assessment:** RPs can be used in risk assessment and scenario analysis. By considering a range of representative scenarios, you can evaluate the potential impacts of various uncertainties on your system.

6. **Control Strategies:** In control systems, RPs can inform control strategies by providing a simplified representation of system dynamics. This can be especially useful in real-time control applications.

7. **Forecasting:** RPs can be used as a basis for forecasting future energy generation or consumption. Forecasting based on representative patterns is often more computationally efficient than forecasting every time step.

8. **Research and Analysis:** Researchers and analysts may use RPs to study the behavior of energy systems, identify trends, and gain insights into system performance without the computational burden of analyzing every data point.

In summary, RPs are a valuable tool in various aspects of energy system analysis, optimization, and decision-making. They allow you to strike a balance between capturing important temporal dynamics and managing computational complexity. The choice of RPs and how they are defined can have a significant impact on the accuracy and efficiency of models and systems in the field of energy management and beyond.


## Table of Contents

- [Install](#Install)
- [Dependencies](#dependencies)
- [License](#license)
- [Documentation](#documentation)

## Install
Can be installed with Pypi :

`pip install reperiods-beta`

## Dependencies

reperiods requires,

* Python >= 3.10
* pandas>=2.0.3, for time series management
* plotly>=5.15.0, for embedded visualisation
* PuLP>=2.7.0, for optimization process
* scikit-learn-extra>=0.3.0, for k-medoids process

## License


## Documentation
