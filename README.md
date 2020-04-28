# Betfairstreamer

What this library provides

* Run single or multiple streams simultaneously.
* Market cache and order cache, these provide abstractions over the betfairstream.
* Using numpy arrays to slicing markets selections.
* Async streaming (Optional).
* Parse historical data.

## Installation

```
pip install betfairstreamer==0.6.0
```

## Example

Jupyter Notebook available in examples folder

## Demo
![](stream.gif)


## Benchmark
```Benchmark
Setup: Two processes, one sending betfair stream messages , one receiving.

Hardware: I7 8550U, 16GB ram

Results: 
 * Using a market cache it can read around ~90k messages/second (no decoding bytes -> dict), with decoding ~25k
 * Without market cache (reading and splitting byte messages. >> 100 Mb/s

```

       
