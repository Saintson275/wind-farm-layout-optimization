# Wind farm layout optimization based on GA and PSO
 Implementations for the Wind Farm Layout Optimization competition
 
## Info
This project is a competion solution of wind farm layout optimization by using Nature-Inspired algorithms.
We provided 2 folders GA_WFLO and PSO_WFLO for Genetic Algorithm and PSO Algorithm sperately.
And we will these algorithnm to optimize the layout of wind farm

## Variables
The solution will assume the wind speed is a fixed number(16/ms), and the turbine has a diameter of 63.6, a height of 60, and a power rate of 2.
in order to get comopare the results of 2 different models, we will the same objective function for both approaches, the related variables include:
 -  Cost: the cost of wind farm in the layout will depend on the number of turbine, here we use 𝐶𝑜𝑠𝑡𝑡𝑜𝑡𝑎𝑙=𝑁(2/3+1/3𝑒^0.00174𝑁^2) to calculate the annual cost.
 -  Energy: the total power of wind farm that produced by turbines, will be calculated by P_total=∑ P_matrix *0.001.
 -  Objective Function: the fitness value of turbine will be presented as F=Cost/P_total.
 
## Genetic Algorithm
The Genetic Algorithm implementation is displayed in GA.py
## PSO Algorithm
The PSO Algorithm implementation is displayed in PSO.py

## install
  pip install numpy&pandas

### run
  -  python GA.py for Genetic Algorithm
  
  -  python PSO.py for PSO Algorithm
## result
  -  After running the GA.py or PSO.py, you can get the results in the current Directory.
  
  -  The jupyter notebook file has recorded the results of experiments

