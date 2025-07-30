# -------------------
## Services - holds all singletons and global variables needed across all classes
class svc:  # pylint: disable=invalid-name
    ## holds reference to Cfg
    cfg = None

    ## holds reference to logger
    log = None

    ## overall return code
    rc = 0

    # -------------------
    ## aborts the process with a default msg
    #
    # @param msg  (optional) the reason for the abort
    # @return None
    @classmethod
    def abort(cls, msg=None):
        cls.rc += 1

        if msg is None:
            line = 'ABRT: session aborted'
        else:
            line = f'ABRT: {msg}'

        # logger may or may not be defined
        print(line)

        ## see description above
        import sys
        sys.exit(cls.rc)
