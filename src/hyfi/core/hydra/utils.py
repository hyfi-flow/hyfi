# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved
import argparse
import logging.config
import os
import sys
from typing import Optional

from hydra._internal.utils import (
    _run_app,
    create_automatic_config_search_path,
    detect_calling_file_or_module_from_stack_frame,
    detect_calling_file_or_module_from_task_function,
    detect_task_name,
    run_and_report,
)
from hydra.core.config_search_path import SearchPathQuery
from hydra.core.utils import validate_config_path
from hydra.errors import SearchPathException
from hydra.types import TaskFunction

log = logging.getLogger(__name__)


def _run_hydra(
    args: argparse.Namespace,
    args_parser: argparse.ArgumentParser,
    task_function: TaskFunction,
    config_path: Optional[str],
    config_name: Optional[str],
    caller_stack_depth: int = 2,
) -> None:
    from hydra._internal.hydra import Hydra
    from hydra.core.global_hydra import GlobalHydra

    if args.config_name is not None:
        config_name = args.config_name

    if args.config_path is not None:
        config_path = args.config_path

    (
        calling_file,
        calling_module,
    ) = detect_calling_file_or_module_from_task_function(task_function)
    if calling_file is None and calling_module is None:
        (
            calling_file,
            calling_module,
        ) = detect_calling_file_or_module_from_stack_frame(caller_stack_depth + 1)
    task_name = detect_task_name(calling_file, calling_module)

    validate_config_path(config_path)

    search_path = create_automatic_config_search_path(
        calling_file, calling_module, config_path
    )

    def add_conf_dir() -> None:
        if args.config_dir is not None:
            abs_config_dir = os.path.abspath(args.config_dir)
            if not os.path.isdir(abs_config_dir):
                raise SearchPathException(
                    f"Additional config directory '{abs_config_dir}' not found"
                )
            search_path.prepend(
                provider="command-line",
                path=f"file://{abs_config_dir}",
                anchor=SearchPathQuery(provider="schema"),
            )

    run_and_report(add_conf_dir)
    hydra = run_and_report(
        lambda: Hydra.create_main_hydra2(
            task_name=task_name, config_search_path=search_path
        )
    )

    try:
        if args.help:
            hydra.app_help(config_name=config_name, args_parser=args_parser, args=args)
            sys.exit(0)
        has_show_cfg = args.cfg is not None
        if args.resolve and (not has_show_cfg and not args.help):
            raise ValueError(
                "The --resolve flag can only be used in conjunction with --cfg or --help"
            )
        if args.hydra_help:
            hydra.hydra_help(
                config_name=config_name, args_parser=args_parser, args=args
            )
            sys.exit(0)

        num_commands = (
            args.run
            + has_show_cfg
            + args.multirun
            + args.shell_completion
            + (args.info is not None)
        )
        if num_commands > 1:
            raise ValueError(
                "Only one of --run, --multirun, --cfg, --info and --shell_completion can be specified"
            )
        if num_commands == 0:
            args.run = True

        overrides = args.overrides

        if args.run or args.multirun:
            run_mode = hydra.get_mode(config_name=config_name, overrides=overrides)
            _run_app(
                run=args.run,
                multirun=args.multirun,
                mode=run_mode,
                hydra=hydra,
                config_name=config_name,
                task_function=task_function,
                overrides=overrides,
            )
        elif args.cfg:
            run_and_report(
                lambda: hydra.show_cfg(
                    config_name=config_name,
                    overrides=args.overrides,
                    cfg_type=args.cfg,
                    package=args.package,
                    resolve=args.resolve,
                )
            )
        elif args.shell_completion:
            run_and_report(
                lambda: hydra.shell_completion(
                    config_name=config_name, overrides=args.overrides
                )
            )
        elif args.info:
            hydra.show_info(
                args.info, config_name=config_name, overrides=args.overrides
            )
        else:
            sys.stderr.write("Command not specified\n")
            sys.exit(1)
    finally:
        GlobalHydra.instance().clear()
