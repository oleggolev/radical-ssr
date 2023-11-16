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

A short paragraph about what this Worker does.
