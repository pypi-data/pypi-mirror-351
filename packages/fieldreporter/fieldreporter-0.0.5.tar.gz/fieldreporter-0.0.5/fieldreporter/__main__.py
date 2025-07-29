from .reporter import FieldReporter
import argparse

def main():
    parser = argparse.ArgumentParser(description="Field Reporter CLI")
    parser.add_argument("config_path", type=str, help="Path to the configuration file")
    parser.add_argument("--now", action="store_true", help="Run the reporter immediately")
    args = parser.parse_args()

    reporter = FieldReporter(config_path=args.config_path)
    if args.now:
        reporter.check_all()
    
    reporter.run()

main()