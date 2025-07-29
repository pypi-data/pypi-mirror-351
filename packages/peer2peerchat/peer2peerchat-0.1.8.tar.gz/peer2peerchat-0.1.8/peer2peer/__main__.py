from .peer2peer import Peer
import argparse



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host IP')
    host = parser.parse_args().host
    peer = Peer(host=host)