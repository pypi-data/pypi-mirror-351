import sys
import pytest
from argparse import ArgumentParser
from builder.cli import get_args, build_parser, git_parser

@pytest.mark.parametrize("argv, expected", [
    (["resume", "build", "-p", "profile.yaml", "-t", "template"], {"command": "build", "profile": "profile.yaml", "template": "template"}),
    (["resume", "git", "--init"], {"command": "git", "init": True}),
    (["resume", "git", "--sync"], {"command": "git", "sync": True}),
])
def test_get_args(monkeypatch, argv, expected):
    monkeypatch.setattr(sys, "argv", argv)
    args = get_args()

    for key, val in expected.items():
        assert getattr(args, key) == val

# def test_build_parser(monkeypatch):
#     TEST_ARGS = ("build", "-p", "default", "-t", "sheets")
#     monkeypatch.setattr(sys, [*TEST_ARGS])

#     args = get_args()

#     assert args.profile == "default"
#     assert args.template == "sheets"

# @pytest.mark.parametrize("argv", "expected", [
#     (["resume", "git", "--init"], {"command": "git", "init": True, "sync": False}),
#     (["resume", "git", "--sync"], {"command": "git", "init`": False, "sync": True}),
# ])
# def test_git_parser(monkeypatch, argv, expected):
#     monkeypatch.setattr(sys, "argv", argv)
#     args = get_args()

#     for key, val in expected.items():
#         assert getattr(args, key) == val