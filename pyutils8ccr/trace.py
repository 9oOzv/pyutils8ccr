from logging import Logger
from enum import Flag, auto
from collections.abc import (
    Callable,
    Container,
    Collection,
)
from inspect import signature
from functools import wraps


class TraceOpts(Flag):
    NONE = 0
    ARGS = auto()
    RETURN = auto()


def _func(
    logger: Logger,
    func: Callable,
):
    @wraps(func)
    def wrapped(*f_args, **f_kwargs):
        logger.debug({'function': func.__name__})
        result = func(*f_args, **f_kwargs)
        return result
    return wrapped


def _args(
    logger: Logger,
    func: Callable,
    arg_names: Collection[str] | None = None,
    exclude: Collection[str] = []
):
    @wraps(func)
    def wrapped(*f_args, **f_kwargs):
        f_signature = signature(func)
        bound_args = f_signature.bind(*f_args, **f_kwargs)
        bound_args.apply_defaults()
        filtered_args = {
            k: v
            for k, v in bound_args.arguments.items()
            if k not in exclude
            and (arg_names is None or k in arg_names)
        }
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
    @wraps(func)
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
    arg_names: Collection[str] | None = None,
    exclude: Collection[str] = [],
):
    if TraceOpts.ARGS in opts:
        func = _args(
            logger,
            func,
            arg_names=arg_names,
            exclude=exclude
        )
    else:
        func = _func(logger, func)
    if TraceOpts.RETURN in opts:
        func = _return(logger, func)
    return func


def _trace_class(
    logger: Logger,
    cls: type,
    opts: TraceOpts,
    exclude: Container[str] = [],
):
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if not callable(attr):
            continue
        if attr_name.startswith("__") and attr_name != "__init__":
            continue
        if attr_name in exclude:
            continue
        if callable(attr) and not attr_name.startswith("__"):
            traced_attr = _trace(logger, attr, opts)
            setattr(cls, attr_name, traced_attr)
    return cls


def trace(
    logger: Logger,
    opts: TraceOpts = TraceOpts.NONE,
    arg_names: Collection[str] | None = None,
    exclude: Collection[str] = [],
):
    def factory(target: Callable | type):
        if isinstance(target, type):
            return _trace_class(
                logger=logger,
                cls=target,
                opts=opts,
                exclude=exclude
            )
        elif callable(target):
            return _trace(
                logger=logger,
                func=target,
                opts=opts,
                arg_names=arg_names,
                exclude=exclude
            )
        else:
            return target
    return factory
