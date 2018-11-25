# RDFScript

A scripting language for creating RDF graphs.

* Define, extend, and expand parameterisable templates for common patterns of RDF triples.
* Share your RDFScript templates with collaborators, or import their templates for use in your own script.
* Serialise as [turtle](https://www.w3.org/TR/turtle/), [n3](https://www.w3.org/TeamSubmission/n3/), [rdf/xml](https://www.w3.org/TR/rdf-syntax-grammar/), or easily extend RDFScript with a custom serialiser.
* Perform complex manipulations of the graph by hooking into Python code defined as extensions.

## Get Started

### Dependencies

RDFScript requires Python 3.x.

Python package dependencies are listed in `setup.py`.

### Install

1. Download or clone repository. `git clone https://github.com/lgrozinger/rdfscript.git`
2. Navigate to RDFScript directory. `cd rdfscript`
3. As a non-root user. `python setup.py install --user`

## Example usage

Running the example in `examples/templates.rdfsh`

`python run.py -s rdfxml examples/templates.rdfsh -o <output-file>`

Run the REPL

`python run.py -s rdfxml -o <output-file>`

Display command line options, including available serialisations.

`python run.py -h`

The example files in `examples/` are commented with some a explaination of the language.

## Contributing

