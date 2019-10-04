# snake-oil-crypto

[Snake-oil](https://philzimmermann.com/EN/essays/SnakeOil.html) crypto is a term
coined by Phil Zimmermann in 1991 original PGP user guide that designates bad
security products that are hardly distinguishable from good ones:

>  like [...] automotive seat belts that look good and feel good, but snap open in the slowest crash test

The main aim of this project is therefore to provide slow speed crash tests for
crypto materials: trying the easiest cracking techniques against the crypto
items found in the wild.

Broadly speaking this project generates a feed of crypto materials identified as
borked, or being low hanging fruits for an attacker.

# Subjects

We are interested in the use of RSA and ECDSA in TLS, GPG, SSH, and OpenVPN.

# Ingestion

The project will acquire crypto materials from:

* [AIL](https://github.com/CIRCL/AIL-framework) clearnet/darknet crawlings,
* D4 through [sensor-d4-tls-fingerprinting](https://github.com/D4-project/sensor-d4-tls-fingerprinting) collections,
* a ReST API.
* existing databases of broken keys (eg. CVE-2008-0166)

# Analysis

A good starting point is all Nadia Heninger et al.'s work:

* [latticehacks](http://latticehacks.cr.yp.to/) 
* [facthacks](http://facthacks.cr.yp.to/) 

Some of these techniques and others are already implemented in
[RsaCtfTool](https://github.com/Ganapati/RsaCtfTool).

# Dissemination

Outputs (means of identifying cracked keys and along with their solutions) will
be exposed through a ReST API, and [MISP](https://www.misp-project.org/) feeds.

# Requirements

* Debian derivative, tested under Ubuntu 18.04
* python 3.7 (Use virtualenv!)
* SageMath 8.8 compiled for python 3

# Install and config

* Use ./install.sh to install in a virtualenv
* Modify config.conf for configuration

# Use

```shell
$ sage --python ./sage-8.8/local/bin/rq worker
$ sage --python ./snake-oil-crypto.py
```
