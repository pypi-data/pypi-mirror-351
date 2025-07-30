# BandGraph

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

Given a list of bands and artists belonging to a musical movement, create a graph of memberships and collaborations using [networkx](https://networkx.org/) and render interactively with [ipysigma](https://github.com/medialab/ipysigma).

Data is stored in folder `data` and are text files with several rows, wach of them with the following format: `band;members;collaborations`. `members` and `collaborations` are lists of musicians or bands separated by commas `,`. `collaborations` includes collaborations between bands and musicians from other projects, and also between bands in songs or split albums. Most of info has been extracted from [Wikipedia](https://en.wikipedia.org), [Discogs](https://www.discogs.com/), [Rate Your Music](https://rateyourmusic.com/), [Spotify](https://spotify.com/) and other sources.

## Examples

**See a web application with examples [here](https://pablovd.github.io/misc/musicgraph.html).**

Example graph, showing the [Jazz](https://en.wikipedia.org/wiki/Jazz) scene

![Jazz](images/jazz.png "Jazz")

## To do

- [x] Improve graph visualization, using `ipysigma`
- [x] Create web application
- [x] Fix visualization of webpage in mobile phone
- [ ] Improve colors and visualization
- [ ] Write web scrapping tool to parse data from Rate Your Music and/or Wikipedia.

## Contact

If you want to include new data or have comments or suggestions, feel free to create a pull request or contact me at <pablo.villanueva.domingo@gmail.com>.