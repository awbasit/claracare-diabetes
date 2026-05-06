"""Minimal CLI for ClaraCare data pipeline."""

from argparse import ArgumentParser

def run_step(step: str) -> None:
    """Execute one pipeline step or all steps."""
    assert step in {
        "collect",
        "clean",
        "synthetic",
        "format",
        "expand",
        "integrate_hf",
        "merge",
        "audit",
        "all",
    }, f"Unknown step: {step}"
    if step == "collect":
        from data.scripts.collect import main as collect_main

        collect_main()
        return
    if step == "clean":
        from data.scripts.clean import main as clean_main

        clean_main()
        return
    if step == "synthetic":
        from data.scripts.generate_synthetic import main as synthetic_main

        synthetic_main()
        return
    if step == "format":
        from data.scripts.format_dataset import main as format_main

        format_main()
        return
    if step == "expand":
        from data.scripts.build_expanded_dataset import main as expand_main

        expand_main()
        return
    if step == "integrate_hf":
        from data.scripts.integrate_hf_diabetes import main as integrate_hf_main

        integrate_hf_main()
        return
    if step == "merge":
        from data.scripts.merge_datasets import main as merge_main

        merge_main()
        return
    if step == "audit":
        from data.scripts.audit_samples import main as audit_main

        audit_main()
        return
    from data.scripts.collect import main as collect_main
    from data.scripts.clean import main as clean_main
    from data.scripts.generate_synthetic import main as synthetic_main
    from data.scripts.format_dataset import main as format_main

    collect_main()
    clean_main()
    synthetic_main()
    format_main()


def main() -> None:
    """Parse command-line args and dispatch pipeline execution."""
    parser = ArgumentParser(prog="claracare", description="Run ClaraCare data pipeline steps.")
    parser.add_argument(
        "step",
        choices=[
            "collect",
            "clean",
            "synthetic",
            "format",
            "expand",
            "integrate_hf",
            "merge",
            "audit",
            "all",
        ],
        help="Pipeline step to run.",
    )
    args = parser.parse_args()
    run_step(args.step)


if __name__ == "__main__":
    main()
