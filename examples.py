import run


def examples():
    # python run.py -s rdfxml examples/templates.rdfsh -o <output-file>
    run.parse_from_file("examples/templates.rdfsh","rdfxml",[],"test.xml",[],1 )


if __name__ == "__main__": examples()