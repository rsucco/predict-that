# predict-that
Automated analysis of PredictIt markets to calculate and present all possible market positions that lead to a mathematically guaranteed positive return. Right now, the UI is very rudimentary. This runs as a commandline Python program. I developed and tested it with Python 3.8 on Manjaro Linux, but it should work with Windows, macOS, and other versions of Python 3 as well. 

## Instructions
To run, navigate to the directory containing the repo, and run ```python3 predict.py```. Monitor mode refreshes every 60 seconds for the most up-to-date PredictIt data. One-time mode just shows you the current top markets.
