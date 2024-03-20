# How to contribute

It is encouraged for users to make contributions to improve the software for themselves and others.

## Getting Started

Join the [Discord](https://discord.gg/3bZuq9QzFk)

### Setup Dev Environment

Fork the repo.

Clone your fork of the repo.

#### Windows & MACOS
It is recomended to use VSCode with the docker dev container extension.<br>
Install docker or docker desktop.<br>
Open the project in a dev container.<br>

##### Core
The dev container will create a python virtual environment for you and upgrade pip and wheel.
```
source env/bin/activate
pip install requirements_dev.txt
```
You should then be able to start core:
```
python -m core
```
When developing you can utilize some of the aditional flags:<br>
```--debug``` will give you more log info.<br>
```--port``` will change the port that the core api runs on. It is recomended not to change this unless you have a specific use case.

From here you should be able to make changes and test them.

If you are making changes that require updates to ```requirements.txt```, you must use ```pip freeze``` and make the appropriate changes. Make sure to update it for ```requirements.txt``` and ```requirements_dev.txt```.

##### Frontend
From your repo cd into frontend.
```
npm install
npm start
```

Using npm start will allow you to make and observe changes quickly. Access via ```localhost:3000```<br>
If you want to test changes from ```localhost:7123``` run:
```
npm run build
```

## Skills

Check out the [documentation](core/skills/README.md) for creating new skills.

## Integrations

Check out the [documentation](core/integrations/README.md) for creating new integrations.

## General Improvements

Documentation coming soon... (Or just read the code)

## Pull Requests

Pull requests should be against the develop branch. If you're unsure about a contribution, feel free to open a discussion, issue, or draft PR to discuss the problem you're trying to solve.

A good pull request has all of the following:
* a clearly stated purpose
* every line changed directly contributes to the stated purpose
* verification, i.e. how did you test your PR?
* justification
  * if you've optimized something, post benchmarks to prove it's better