# Benchmark for Server-Side Rendering (SSR) on the Edge

## Usage

This repository contains a Cloudflare Worker. `wrangler` is used to develop, deploy, and configure the Worker via CLI (see example commands below). Read the latest `worker` crate documentation here: https://docs.rs/worker

```sh
# Run in an ideal development workflow (with a local server, file watcher & more).
$ npx wrangler dev

# Deploy to Cloudflare network.
$ npx wrangler deploy
```

This Worker is deployed here: https://ssr-bench.sns-radical.workers.dev

## Description

The benchmark uses a simple blog-style website to estimate the time it takes to request, generate, and return a server-side rendered HTML template using data from Workers KV. `benchmark/benchmark.py` does so by:
1. Clearing the KV store
2. Populating the KV store with some `N` number of posts where each post is the content stored in `benchmark/post.json`: a 1500-word copypasta, precisely the length of an average real-world blog post
3. Measuring how long it takes to load the index page on the first request (`first_load`) in milliseconds
4. Measuring how long it takes to laod the index page on subsequent loads (`cached_load`) in milliseconds

The results are stored in the file `output_con_edge.txt` where each line is in the format `{N}: {first_load}, {cached_load}`.
