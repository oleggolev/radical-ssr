import json
import requests
import argparse
import time

class SSRBenchmark:
    
    SAMPLE_POST_JSON_PATH: str = "./benchmark/post.json"
    
    def __init__(self, target: str):
        self.target = target
        self.session = requests.Session()
        # Add the connection to the cache.
        resp = self.session.get(target + "/posts")
        assert resp.status_code == 200

    # Add N posts to the blog's Cache.
    def add_posts(self, N):
        fs_json = open(self.SAMPLE_POST_JSON_PATH)
        post = json.load(fs_json)
        for i in range(N):
            post["id"] = i
            resp = self.session.post(self.target + "/post", json=post)
            assert resp.status_code == 200
            print(resp.content)
        fs_json.close()

    # Clear the Cache.
    def clear_posts(self):
        resp = self.session.post(target + "/clear_kv")
        assert resp.status_code == 200
        print(resp.content)

    # Get the HTML page with all posts, timing the RTT.
    def time_get_posts(self) -> float:
        start = time.perf_counter()
        resp = self.session.get(target + "/posts")
        end = time.perf_counter()
        assert resp.status_code == 200
        return (end - start) * 1000


if __name__ == "__main__":
    # Parse in command-line arguments.
    parser = argparse.ArgumentParser(
        prog='benchmark',
        description='Clears the Worker Cache populates it with N posts, then measures load latency',
    )
    parser.add_argument('-d', '--dev', action='store_true', help='use the local dev server rather than the Cloudflare deployment')
    parser.add_argument('num_trials', type=int)
    parser.add_argument('outfile', type=str)
    args = parser.parse_args()

    # Set target depending on dev vs. prod.
    if args.dev:
        target = "http://0.0.0.0:8787"
    else:
        target = "https://ssr-bench.radical-serverless.com"

    # Prepare the output CSV file for writing results.
    fs_output = open('./benchmark/' + args.outfile, 'w')
    fs_output.write(f"num_posts, first_load_latency, cached_load_latency\n")

    # Measure latency with a pre-determined set of N posts.
    N_set = [0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    for N in N_set:
        first_load_latencies = [0] * args.num_trials
        cached_load_latencies = [0] * args.num_trials
        
        # Run the trials.
        for trial_num in range(args.num_trials):
            ssr_bench = SSRBenchmark(target)
            ssr_bench.clear_posts()
            ssr_bench.add_posts(N)
            first_load_latency = ssr_bench.time_get_posts()
            cached_load_latency = ssr_bench.time_get_posts()
            print(f"{N}, {first_load_latency}, {cached_load_latency}")
            first_load_latencies[trial_num] = first_load_latency
            cached_load_latencies[trial_num] = cached_load_latency
            
        # Write the average load times for this N.
        fs_output.write(f"{N}, {sum(first_load_latencies) / len(first_load_latencies)}, {sum(cached_load_latencies) / len(cached_load_latencies)}\n")

    # Done.
    fs_output.close()
