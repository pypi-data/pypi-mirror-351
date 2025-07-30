# BandGraph

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

Given a list of bands and artists belonging to a musical movement, create a graph of memberships and collaborations using [networkx](https://networkx.org/) and render interactively with [ipysigma](https://github.com/medialab/ipysigma).

Data is is stored as text files with several rows, each of them with the following format: `band;members;collaborations`. `members` and `collaborations` are lists of musicians or bands separated by commas `,`. `collaborations` includes collaborations between bands and musicians from other projects, and also between bands in songs or split albums. Most of info has been extracted from [Wikipedia](https://en.wikipedia.org), [Discogs](https://www.discogs.com/), [Rate Your Music](https://rateyourmusic.com/), [Spotify](https://spotify.com/) and other sources.

**See a web application with examples [here](https://pablovd.github.io/misc/musicgraph.html).**

## Installation

To install the library, run:

```sh
pip install bandgraph
```

## Get started

Load the data

```py
from bandgraph import load_data

filename = "jazz.txt"
dataframe = load_data(filename)
```

Generate the graph

```py
from bandgraph import create_graph

graph = create_graph(dataframe)
```

Render the graph with [ipysigma](https://github.com/medialab/ipysigma)

```py
from ipysigma import Sigma

args = {"node_size":0,
        "node_color":"type",
        "edge_color":"type",
        "label_density":10,
        "node_border_color_from":"node",
        "start_layout":2,
        "hide_info_panel":True,
        "background_color":"rgb(255, 255, 255)"}

sig = Sigma(graph, **args)
```

## Examples

**See a web application with examples [here](https://pablovd.github.io/misc/musicgraph.html).**

Example graph, showing the [Jazz](https://en.wikipedia.org/wiki/Jazz) scene

![Jazz](https://github.com/PabloVD/BandGraph/blob/master/images/jazz.png?raw=true "Jazz")

## To do

- [x] Improve graph visualization, using `ipysigma`
- [x] Create web application
- [x] Fix visualization of webpage in mobile phone
- [x] Create library and publish in pypi
- [ ] Improve colors and visualization
- [ ] Write web scrapping tool to parse data from Rate Your Music and/or Wikipedia.

## Contributing

If you want to include new data or have comments or suggestions, feel free to create a pull request or contact me at <pablo.villanueva.domingo@gmail.com>.

## License

MIT
