def main():
    benchmarks = [...]  # List of benchmark configurations

    for config in benchmarks:
        if config["type"] == "client":
            benchmark = ClientBenchmark(config)
        elif config["type"] == "server":
            benchmark = ServerBenchmark(config)
        else:
            raise ValueError("Invalid benchmark type")

        benchmark.run()


if __name__ == "__main__":
    main()
