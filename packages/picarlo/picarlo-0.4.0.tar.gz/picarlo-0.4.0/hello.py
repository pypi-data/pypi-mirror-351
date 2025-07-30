import typer

from picarlo.sim import (
    Config,
    monte_carlo_pi,
    monte_carlo_pi_parallel,
    stringify_the_float,
)


def main(num_samples: int, cores: int = 1) -> None:
    config = Config()

    if num_samples:
        config.num_samples = num_samples

    stringify_the_float(config.num_samples)

    print(f"starting pi carlo with {config.num_samples} samples!")

    if cores > 1:
        pi = monte_carlo_pi_parallel(config.num_samples, cores)
        # print("parallel not implemented yet")
    else:
        pi = monte_carlo_pi(config.num_samples)

    print(f"pi is approximately {pi}")


if __name__ == "__main__":
    typer.run(main)
