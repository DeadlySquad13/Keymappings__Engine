ENV = 'debug'

def debug_arguments(func):
    def wrapper(*args, **kwargs):
        print(*args, **kwargs)
        func(*args, **kwargs)

    return wrapper

def debug_print(*args, **kwargs):
    if ENV == 'debug':
        print(*args, **kwargs)


def with_decoration(func):
    def wrapper(*args, **kwargs):
        print('-----------')
        func(*args, **kwargs)
        print('-----------')

    return wrapper


def P(args):
    print(args)

    return args

