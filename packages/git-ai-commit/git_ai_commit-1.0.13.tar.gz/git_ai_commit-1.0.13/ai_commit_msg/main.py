from __future__ import annotations
import argparse
import sys
import os
from typing import Sequence

from ai_commit_msg.cli.help_ai_handler import help_ai_handler
from ai_commit_msg.cli.summary_handler import summary_handler
from ai_commit_msg.cli.config_handler import config_handler, handle_config_setup
from ai_commit_msg.cli.gen_ai_commit_message_handler import (
    gen_ai_commit_message_handler,
)
from ai_commit_msg.cli.hook_handler import hook_handler
from ai_commit_msg.prepare_commit_msg_hook import prepare_commit_msg_hook
from ai_commit_msg.services.config_service import ConfigService
from ai_commit_msg.services.pip_service import PipService
from ai_commit_msg.utils.logger import Logger
from ai_commit_msg.cli.conventional_commit_handler import conventional_commit_handler


def called_from_git_hook():
    return os.environ.get("PRE_COMMIT") == "1"


def main(argv: Sequence[str] = sys.argv[1:]) -> int:
    if called_from_git_hook():
        return prepare_commit_msg_hook()

    if len(argv) == 0:
        if ConfigService().last_updated_at == "":
            handle_config_setup()
            return 0

        return gen_ai_commit_message_handler()

    parser = argparse.ArgumentParser(
        description="🚀 AI-powered CLI tool that revolutionizes your Git workflow by automatically generating commit messages!"
    )
    parser.add_argument(
        "-v", "--version", action="version", version=PipService.get_version()
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Config command
    config_parser = subparsers.add_parser(
        "config", help="🛠️ Configure the tool settings"
    )
    config_parser.add_argument(
        "-k",
        "--openai-key",
        dest="openai_key",
        help="🔑 Set your OpenAI API key for AI-powered commit messages",
    )
    config_parser.add_argument(
        "-r",
        "--reset",
        action="store_true",
        help="🔄 Reset the OpenAI API key to default",
    )
    config_parser.add_argument(
        "-l",
        "--logger",
        type=lambda x: (str(x).lower() == "true"),
        help="📝 Enable or disable logging (true/false) for debugging",
    )
    config_parser.add_argument(
        "-m",
        "--model",
        help="🧠 Set the OpenAI model to use for generating commit messages",
    )
    config_parser.add_argument(
        "-ou", "--ollama-url", help="🌐 Set the Ollama URL for local LLM models"
    )
    config_parser.add_argument(
        "-a",
        "--anthropic-key",
        dest="anthropic_key",
        help="🔑 Set your Anthropic API key for AI-powered commit messages",
    )
    config_parser.add_argument(
        "-s", "--setup", action="store_true", help="🔧 Setup the tool"
    )
    config_parser.add_argument(
        "-p", "--prefix", help="🏷️ Set a prefix for the commit message"
    )
    config_parser.add_argument(
        "-ml", "--max-length", help="🏷️ Set a prefix for the commit message"
    )

    # Help command
    subparsers.add_parser("help", help="Display this help message")

    help_ai_parser = subparsers.add_parser(
        "help-ai", help="🤖 Get help from AI to find the right command for you"
    )
    help_ai_parser.add_argument(
        "message", nargs=argparse.REMAINDER, help="Additional message for help"
    )

    # Hook command
    hook_parser = subparsers.add_parser(
        "hook", help="🪝 Run the prepare-commit-msg hook to generate commit messages"
    )
    hook_parser.add_argument(
        "-s", "--setup", action="store_true", help="Setup the prepare-commit-msg hook"
    )
    hook_parser.add_argument(
        "-sh",
        "--setup-husky",
        action="store_true",
        help="Setup the prepare-commit-msg hook",
    )
    hook_parser.add_argument(
        "-r", "--remove", action="store_true", help="Remove the prepare-commit-msg hook"
    )
    hook_parser.add_argument(
        "-x", "--run", action="store_true", help="Run the prepare-commit-msg hook"
    )

    summarize_cmd_parser = subparsers.add_parser(
        "summarize", help="🚀 Generate an AI commit message"
    )
    summary_cmd_parser = subparsers.add_parser(
        "summary", help="🚀 Generate an AI commit message"
    )
    summarize_cmd_parser.add_argument(
        "-u",
        "--unstaged",
        action="store_true",
        help="Setup the prepare-commit-msg hook",
    )
    summary_cmd_parser.add_argument(
        "-u",
        "--unstaged",
        action="store_true",
        help="Setup the prepare-commit-msg hook",
    )
    summary_cmd_parser.add_argument(
        "-d",
        "--diff",
        default=None,
        help="🔍 Provide a diff to generate a commit message",
    )

    conventional_commit_parser = subparsers.add_parser(
        "conventional", help="🏷️ Generate a conventional commit message"
    )

    args = parser.parse_args(argv)

    def get_full_help_menu():
        full_help_menu = "\nAvailable commands:\n"
        for name, subparser in subparsers.choices.items():
            full_help_menu += f"\n{name}:\n"
            full_help_menu += subparser.format_help()

        return full_help_menu

    if args.command == "config":
        config_handler(args)
    elif args.command == "help":
        print(get_full_help_menu())
    elif args.command == "help-ai":
        help_ai_handler(args, help_menu=get_full_help_menu())
    elif args.command == "hook":
        hook_handler(args)
    elif args.command == "summarize" or args.command == "summary":
        summary_handler(args)
    elif args.command == "conventional":
        conventional_commit_handler(args)

    ## Only in main script, we return zero instead of None when the return value is unused
    return 0


if __name__ == "__main__":
    Logger().log("sys.argv: " + str(sys.argv))
    raise SystemExit(main())
