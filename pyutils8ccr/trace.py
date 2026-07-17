from logging import Logger
from enum import Flag, auto
from collections.abc import Callable
from inspect import signature


class TraceOpts(Flag):
    NONE = 0
    ARGS = auto()
    RETURN = auto()


def _func(
    logger: Logger,
    func: Callable,
):
    def wrapped(*f_args, **f_kwargs):
        logger.debug({'function': func.__name__})
        result = func(*f_args, **f_kwargs)
        return result
    return wrapped


def _args(
    logger: Logger,
    func: Callable,
    arg_names: list[str] | None = None,
):
    def wrapped(*f_args, **f_kwargs):
        f_signature = signature(func)
        bound_args = f_signature.bind(*f_args, **f_kwargs)
        bound_args.apply_defaults()
        if arg_names is not None:
            filtered_args = {
                k: v
                for k, v in bound_args.arguments.items()
                if k in arg_names
            }
        else:
            filtered_args = bound_args.arguments
        logger.debug({
            'function': func.__name__,
            'args': filtered_args
        })
        return func(*f_args, **f_kwargs)
    return wrapped


def _return(
    logger: Logger,
    func: Callable,
):
    def wrapped(*f_args, **f_kwargs):
        result = func(*f_args, **f_kwargs)
        logger.debug({
            'function': func.__name__,
            'return': result
        })
        return result
    return wrapped


def _trace(
    logger: Logger,
    func: Callable,
    opts: TraceOpts,
    arg_names: list[str] | None = None,
):
    if TraceOpts.ARGS in opts:
        func = _args(logger, func, arg_names=arg_names)
    else:
        func = _func(logger, func)
    if TraceOpts.RETURN in opts:
        func = _return(logger, func)
    return func


def trace(
    logger: Logger,
    opts: TraceOpts = TraceOpts.NONE,
    arg_names: list[str] | None = None,
):
    def factory(func: Callable):
        return _trace(
            logger,
            func,
            opts,
            arg_names=arg_names
        )
    return factory
