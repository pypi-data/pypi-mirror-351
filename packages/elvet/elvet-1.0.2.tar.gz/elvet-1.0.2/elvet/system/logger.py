import logging
import sys


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        if record.levelno >= 50:  # FATAL
            color = "\x1b[31m Elvet - ERROR: "
        elif record.levelno >= 40:  # ERROR
            color = "\x1b[31m Elvet - ERROR: "
        elif record.levelno >= 30:  # WARNING
            color = "\x1b[35m Elvet - WARNING: "
        elif record.levelno >= 20:  # INFO
            color = "\x1b[0m Elvet: "
        elif record.levelno >= 10:  # DEBUG
            color = "\x1b[36m Elvet - DEBUG: "
        else:  # ANYTHING ELSE
            color = "\x1b[0m Elvet: "

        record.msg = color + str(record.msg) + "\x1b[0m"
        return logging.Formatter.format(self, record)


def init(LoggerStream=sys.stdout):
    rootLogger = logging.getLogger()
    hdlr = logging.StreamHandler()
    fmt = ColoredFormatter("%(message)s")
    hdlr.setFormatter(fmt)
    rootLogger.addHandler(hdlr)

    # we need to replace all root loggers by ma5 loggers for a proper
    # interface with madgraph5
    ElvetLogger = logging.getLogger("Elvet")
    for hdlr in ElvetLogger.handlers:
        ElvetLogger.removeHandler(hdlr)
    hdlr = logging.StreamHandler(LoggerStream)
    fmt = ColoredFormatter("%(message)s")
    hdlr.setFormatter(fmt)
    ElvetLogger.addHandler(hdlr)
    ElvetLogger.propagate = False
