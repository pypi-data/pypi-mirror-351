# Simple parser of data from DDNet Master Servers and DDStats

This parser makes it easy to get data from [ddnet master servers](https://master1.ddnet.org/ddnet/15/servers.json) and various statistics from [ddstats.tw](https://ddstats.tw/).

## Installation:
Installing the library:
```
pip install requests
```
Installing the latest stable version of the parser:
```
pip install ddnet-parser
```
Installing test and unstable version of the parser:
```
pip install git+https://github.com/neyxezz/ddnet-parser@tests
```

## GetClients(address=None, data=None)
* Gets an object for parsing client information
* Documentation: [🙂](https://github.com/neyxezz/ddnet-parser/blob/main/docs/docs.md#clientsparser-class)
* Args: address(bool, optional): address of the server for which to get client information; data(dict or str, optional): data from which the information will be parsed

Example:
```python
from ddnet_parser import GetClients

clients = GetClients()
print(clients.get_clients(count=True))
```
## GetServers(address=None, data=None)
* Gets an object for parsing server information
* Documentation: [🙂](https://github.com/neyxezz/ddnet-parser/blob/main/docs/docs.md#serversparser-class)
* Args: address(bool, optional): address of the server to get information for; data(dict or str, optional): data from which the information will be parsed

Example:
```python
from ddnet_parser import GetServers

servers = GetServers()
print(servers.get_count())
```
## GetPlayerStats(name)
* Gets an object for parsing player stats
* Documentation: [🙂](https://github.com/neyxezz/ddnet-parser/blob/main/docs/docs.md#playerstatsparser-class)
* Args: name(str): the nickname for which you want to get stats

Example:
```python
from ddnet_parser import GetPlayerStats

player = GetPlayerStats("neyxezz")
print(player.get_total_seconds_played())
```
## GetMap(_map)
* Gets an object for parsing map data
* Documentation: [🙂](https://github.com/neyxezz/ddnet-parser/blob/main/docs/docs.md#mapsparser-class)
* Args: address(str): the map to get data for

Example:
```python
from ddnet_parser import GetMap

map = GetMap("Linear")
print(map.get_mapper())
```
## GetProfile(name)
* Gets an object for parsing a player's profile
* Documentation: [🙂](https://github.com/neyxezz/ddnet-parser/blob/main/docs/docs.md#profileparser-class)
* Args: name(str): the nickname to get the profile for

Example:
```python
from ddnet_parser import GetProfile

profile = GetProfile()
print(profile.get_points())
```
## Detailed documentation with examples:
* Detailed documentation: [🙂](docs/docs.md)
* Examples: [🙂](examples/examples.py)

## Contact me
tg main: @neyxezz, tg twink: @neyxezz_twink
