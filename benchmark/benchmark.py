import json
import requests
import argparse
import time

# Parse in command-line arguments.
parser = argparse.ArgumentParser(
    prog='benchmark',
    description='Clears the KV of the Worker, populates it with N posts, then measures first-load and cached latency.',
)
parser.add_argument('-d', '--dev', action='store_true', help='use the local dev server rather than the Cloudflare deployment')
parser.add_argument('outfile')
args = parser.parse_args()

# Set target depending on dev vs. prod.
if args.dev:
    target = "http://0.0.0.0:8787"
else:
    target = "https://ssr-bench.sns-radical.workers.dev"

# Useful functions.
def clear_kv():
    resp = session.post(target + "/clear_kv")
    assert resp.status_code == 200

def populate_kv(N):
    fs_json = open('./benchmark/post.json')
    post = json.load(fs_json)
    for i in range(N):
        post["id"] = i
        resp = session.post(target + "/post", json=post)
        assert resp.status_code == 200
    fs_json.close()

def time_get_posts():
    start = time.perf_counter()
    session.get(target + "/posts")
    end = time.perf_counter()
    return (end - start) * 1000

def measure_latencies():
    first_load = time_get_posts()
    cached_loads = [0] * 10
    for i in range(10):
        cached_loads[i] = time_get_posts()
    cached_load = sum(cached_loads) / len(cached_loads)
    return first_load, cached_load

# Measure latency with a pre-determined set of N posts.
fs_output = open('benchmark/' + args.outfile, 'w')
num_trials = 10
N_set = [0, 5, 10, 15, 20, 50]
for N in N_set:
    first_load_outputs = [0] * num_trials
    cached_load_outputs = [0] * num_trials
    
    # Cache connection.
    session = requests.Session()
    session.get(target + "/about")
    
    # Run the trials.
    for trial_num in range(num_trials):
        clear_kv()
        time.sleep(1)
        populate_kv(N)
        time.sleep(1)
        first_load, cached_load = measure_latencies()
        first_load_outputs[trial_num] = first_load
        cached_load_outputs[trial_num] = cached_load
    fs_output.write(f"{N}: {sum(first_load_outputs) / len(first_load_outputs)}, {sum(cached_load_outputs) / len(cached_load_outputs)}\n")
    
fs_output.close()   
