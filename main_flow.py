
from wikidata_filter import run_flow


if __name__ == '__main__':
    import sys

    flow_file = sys.argv[1]
    run_flow(flow_file, *sys.argv[2:], finish_signal=True)
