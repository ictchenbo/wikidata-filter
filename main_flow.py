
from wikidata_filter import run_flow


if __name__ == '__main__':
    import sys

    flow_file = sys.argv[1]
    run_flow(flow_file, *sys.argv[2:], True)

    # run_flow('flows/p1_idname_simple.yaml', 'data/wikidata.100K.json', 'out_human.json')
    # run_flow('flows/gdelt_test.yaml')
