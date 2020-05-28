# Betfairstreamer

What this library provides

* Run single or multiple streams simultaneously.
* Market cache and order cache, these provide abstractions over the betfairstream.
* Using numpy arrays to slicing markets selections.
* Async streaming (Optional).
* Parse historical data.

## Installation

```
pip install betfairstreamer==0.7.0
```

## Examples

```python
session_token = api_client.get_session_token()

soccer_subscription = create_market_subscription(
    event_type_ids=["1"],
    country_codes=["DE"],
    market_types=["MATCH_ODDS"],
    fields=["EX_MARKET_DEF", "EX_LTP", "EX_BEST_OFFERS_DISP"],
    ladder_levels=2,
)

order_subscription = create_order_subscription()

connection_pool = BetfairConnectionPool.create_connection_pool(
    subscription_messages=[
        soccer_subscription_message, 
        order_subscription_message
    ],
    app_key=APP_KEY,
    session_token=session_token
)

for stream_update in connection_pool.read():
    print(stream_update)
```
#### Jupyter notebooks available in ./examples


## Benchmark
```Benchmark
Setup: Two processes, one sending betfair stream messages , one receiving.

Hardware: I7 8550U, 16GB ram

Results: 
 * Using a market cache it can read around ~90k decoded messages/second
```

       
