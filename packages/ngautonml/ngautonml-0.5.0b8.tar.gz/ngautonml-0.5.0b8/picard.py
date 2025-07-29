#!/bin/env python
"""Main for AutonML."""

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import argparse
import logging
import sys
import warnings
from typing import Callable, Optional

from ngautonml.algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ngautonml.executor.simple.simple_executor import SimpleExecutor
from ngautonml.generator.generator import GeneratorImpl
from ngautonml.instantiator.instantiator_factory import InstantiatorFactory
from ngautonml.metrics.impl.metric_auto import MetricCatalogAuto
from ngautonml.problem_def.problem_def import ProblemDefinition
from ngautonml.ranker.ranker_impl import RankerImpl
from ngautonml.tables.impl.table_auto import TableCatalogAuto
from ngautonml.templates.impl.template_auto import TemplateCatalogAuto
from ngautonml.wrangler.logger import Level, Logger
from ngautonml.wrangler.wrangler import Wrangler
from ngautonml.wrangler.distributed_wrangler import DistributedWrangler

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
_ = TableCatalogAuto()


def set_global_log_level(args: argparse.Namespace) -> logging.Logger:
    '''Set log level for all of ngautonml, overridding levels set in each file.'''
    level: Optional[str] = args.log_level
    level_int: Optional[int] = None
    if level is not None:
        try:
            level_int = int(level)
        except ValueError:
            try:
                level_int = int(getattr(Level, level.upper()))
            except (ValueError, AttributeError) as exc:
                raise ValueError(
                    f'Log level {level} is not a valid level name and cannot be casted to int.  '
                    'Try one of: VERBOSE, DEBUG, INFO, WARN, ERROR.') from exc

    if level_int is not None:
        Logger.set_global_level(level=level_int)
    return Logger(__file__,
                  to_stdout=True,
                  level=level_int or Level.WARN).logger()


def wrangle(args: argparse.Namespace):
    """Do full autoML."""
    # TODO(piggy): Set up non-trivial architectural componenents
    # here based on command-line arguments.
    with open(args.problem_definition, 'r', encoding='utf8') as _f:
        problem_definition = ProblemDefinition(_f.read())
    log = set_global_log_level(args)
    log.info('%s', problem_definition)
    wrangler = Wrangler(
        problem_definition=problem_definition,
        metric_catalog=MetricCatalogAuto,
        algorithm_catalog=AlgorithmCatalogAuto,
        ranker=RankerImpl,
        template_catalog=TemplateCatalogAuto,
        generator=GeneratorImpl,
        executor=SimpleExecutor,
        instantiator_factory=InstantiatorFactory,
    )
    got = wrangler.fit_predict_rank()
    print(got.rankings)


def instantiate(args: argparse.Namespace):
    """Instantiate one or more pipelines.

    Optionally includes a trained model in the instantiated pipeline.
    """
    print(f'Instantiate: {args!r}')


def distributed(args: argparse.Namespace):
    """Stand up a distributed node."""
    with open(args.problem_definition, 'r', encoding='utf8') as _f:
        problem_definition = ProblemDefinition(_f.read())
    log = set_global_log_level(args)
    log.info('%s', problem_definition)
    wrangler = DistributedWrangler(
        problem_definition=problem_definition,
        my_id=args.my_id)
    wrangler.server(host=args.host, port=args.port)()


def usage(parser: argparse.ArgumentParser) -> Callable[
        [argparse.Namespace], None]:
    """Returns a function that prints the usage message."""
    def _f(_args: argparse.Namespace):
        parser.print_usage(sys.stderr)
    return _f


def main():
    """
    Just do something
    """
    # Create the top-level parser.
    parser_global = argparse.ArgumentParser(prog='picard')
    parser_global.set_defaults(func=usage(parser_global))
    parser_global.add_argument(
        '-l', '--log_level',
        type=str,
        help='Log level.  int or one of "VERBOSE", "DEBUG", "INFO", "WARN", "ERROR".',
        required=False
    )

    # Create sub-parser.
    sub_parsers = parser_global.add_subparsers(help='sub-command help')

    # Create the parser for the "wrangle" sub-command.
    parser_wrangle = sub_parsers.add_parser('wrangle',
                                            help='Run full autoML on a '
                                            'dataset.')
    parser_wrangle.set_defaults(func=wrangle)
    parser_wrangle.add_argument(
        '-d', '--problem_definition',
        type=str,
        help='path to problem definition JSON file',
        required=True)

    # Create the parser for the "instantiate" sub-command.
    parser_instantiate = sub_parsers.add_parser('instantiate',
                                                help='Generate an '
                                                'executable algorithm.')
    parser_instantiate.set_defaults(func=instantiate)
    parser_instantiate.add_argument(
        '-k', '--kind',
        action='append', choices=['d3m_json', 'python_script',
                                  'jupyter_notebook', 'airflow_class'],
        help='Indicate the kind of executable algorithm to generate. '
        'May be repeated. Defaults to all choices.')
    parser_instantiate.add_argument(
        '-p', '--pipeline',
        type=str,
        help='name or path to a pipeline to instantiate',
        required=True
    )
    parser_instantiate.add_argument(
        '-m', '--trained_model',
        action='append',
        help='optional path to the trained model to instantiate. '
        'May be repeated.'
    )

    parser_distributed = sub_parsers.add_parser('distributed',
                                                help='Start up a server running '
                                                'a set of distributed algorithms.')
    parser_distributed.set_defaults(func=distributed)
    parser_distributed.add_argument(
        '-d', '--problem_definition',
        type=str,
        help='path to problem definition JSON file',
        required=True)
    parser_distributed.add_argument(
        '-i', '--my_id',
        type=int,
        help='Node number of the server',
        required=False,
        default=1
    )
    parser_distributed.add_argument(
        '-H', '--host',
        type=str,
        help='Host name or IP address of web API',
        default='localhost',
    )
    parser_distributed.add_argument(
        '-P', '--port',
        type=int,
        help='Port number of web API',
        default=60080,
    )

    a = parser_global.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
