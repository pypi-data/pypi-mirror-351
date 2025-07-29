from argparse import ArgumentParser, Namespace
from .constants import DEFAULT_PROFILE, DEFAULT_TEMPLATE
from .render import compile_pdf


def build_parser(subparser):
    build = subparser.add_parser(name="build", help="Generate latex resumes from a yaml profile.")
    build.add_argument("-p", "--profile", default=DEFAULT_PROFILE)
    build.add_argument("-t", "--template", default=DEFAULT_TEMPLATE)
    build.add_argument("-o", "--output")

def git_parser(subparser):
    git = subparser.add_parser(name="git", help="Sync profiles and templates with git.")
    git.add_argument("--init", action="store_true", help="Initializes profile git repository.")
    git.add_argument("--sync", action="store_true", help="Syncs profile with git remote.")

def get_args() -> Namespace:
    parser = ArgumentParser(prog="resume", description="Command-line tool to generate resumes from YAML and LaTeX templates")
    subparser = parser.add_subparsers(dest="command", required=True)

    build_parser(subparser)
    git_parser(subparser)
    
    return parser.parse_args()

def main():
    args = get_args()

    if args.command == "build":
        compile_pdf(
            profile=args.profile,
            template=args.template,
            output_name=args.output or args.profile
        )
    elif args.command == "git":
        print("Git functionality is currently unavailable.")