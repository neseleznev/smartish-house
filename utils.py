import datetime
import logging
import os


def setup_logging(log_directory, file_level, console_level):
    filename = datetime.datetime.now().strftime('%Y-%m-%d %H:%M.log')
    os.makedirs(os.path.dirname('./' + log_directory), exist_ok=True)

    # set up logging to file
    logging.basicConfig(level=file_level,
                        format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=os.path.join(log_directory, filename),
                        filemode='w')
    # define a Handler which writes messages to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(console_level)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-16s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
