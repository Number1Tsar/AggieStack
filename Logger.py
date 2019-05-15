"""Logger Decorator. Wraps the methods and output the execution result in Log file 'AggiestackLogs.log.
Example:
    <2018 13:25:53> <SUCCESS> <aggiestack.py aggiestack show hardware>
    <2018 13:43:56> <ERROR> <aggiestack.py aggiestack can_host dora small> <Exception:: Machine "dora" not found>
    """


def logger(method):
    import logging
    import sys

    LOG_FILE_NAME = 'AggiestackLogs.log'

    logging.basicConfig(level=logging.INFO,
                        format='<%(asctime)s> %(message)s',
                        datefmt='%Y %H:%M:%S',
                        filename=LOG_FILE_NAME)

    def wrapper(*args):
        command = ' '.join(sys.argv)
        try:
            result = method(*args)
            logging.info("<SUCCESS> <{}>".format(command))
            return result
        except Exception as e:
            logging.error("<ERROR> <{}> <Exception:: {}>".format(command, e))
            print(str(e))

    return wrapper
