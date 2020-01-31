# Table of Contents

1.  [Service Discovery](#orgfab5874)
    1.  [Why](#org1de82a0)
    2.  [Strategy](#orgc5cb5a1)
    3.  [Implementation](#orge884fc4)
        1.  [Interface](#orgf03e755)
    4.  [How is this actually tested](#orgcc3eccb)
    5.  [Using this library](#orgea55323)


<a id="orgfab5874"></a>

# Service Discovery


<a id="org1de82a0"></a>

## Why

In any distributed system, passing messages between nodes is a common pattern. In order to pass these messages around there must exist some view indicating the availability of existing nodes. This will likely be managed in one of two ways: either centralized or decentralized. In either case, there are pros and cons. In any case, in a massive system, a decentralized view will provide better performance. While this will probably never see the light of day outside of my computer, for the purposes of education this project will implement a decetralized algorithm.


<a id="orgc5cb5a1"></a>

## Strategy

The strategy follows that of a gossip protocol. Per the wiki on gossip, "a gossip protocol is a procedure or process of computer peer-to-peer communication that is based on the way epidemics spread. Some distributed systems use peer-to-peer gossip to ensure that data is disseminated to all members of a group." 

Effectively, if we consider the union of data across all nodes, the most up to date view of the world can be generated. In order to spread that information effetively, each node will-at some frequency-gossip to some K local neighbors. Suppose each node gossips to 2 nodes, its information will reach all nodes in some logarithmic time complexity. Meaning, this is an eventually consistent view of the world.

In order to begin discovering eachothere, there exists a set of seed nodes describing which servers are initial neighbors to all nodes. 


<a id="orge884fc4"></a>

## Implementation

A simple flask (python3) application with a few exposed endpoints allowing clients to either list all active services or perform some conditional put on the list of active services. The data is managed entirely by sqlite.


<a id="orgf03e755"></a>

### Interface

From the client perspective, the only endpoints are in `registry.py`.

The first endpoint is list: 

    GET /registry/list

List returns a json blob such that each key gives an address and the associated value desribes the services and its health.

    {
      "address" : { // I'm using the ip addresses  themselves
        "app_name" : "string", 
        "last_update" : "integer" // unix time stamp
      },
    }

The last endpoint will generally be used by client applications running along side the `service_discovery` service.

    POST /register/register_instance 
    {
      "address": "string",
      "app_name": "string",
      "last_update": integer 
    }

    GET /registry/perform_update

Perform performs a single step of gossip. Simply put, choose a neighbor and tell him about yourself and your friends. 


<a id="orgcc3eccb"></a>

## How is this actually tested

Unfortunately, I do not have enough money to spin instances in ec2 or run a datacenter, but I can simulate a distributed network using docker. This package itself supplies the docker file needed and is in fact the best way to run and test this. 

In addition to the api itself, a small application must run and actually hit the `/perform_udpate` endpoint. Currently, this is a simple bash script that performs a `curl` request against the local host and sleeps for 5 seconds before updating again. 

In a real world situtation, this service would run on any node that must be discoverable in nature. We can test this in docker as well, but from what I can tell docker considers this to be somewhat of an anti-pattern.


<a id="orgea55323"></a>

## Using this library

For all intents and purposes, this service can on any host, but should run side by side with another application that requires service discovery. In order for that service to register itself, it simply needs to hit the `/registry/register_instance` endpoint with whatever relevant data it has.
