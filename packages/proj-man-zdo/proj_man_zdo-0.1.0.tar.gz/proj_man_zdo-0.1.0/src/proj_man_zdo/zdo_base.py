from .common import cmn
from .git import Git
from .navigate import Navigate
from .requirements import Requirements
from .run_cmds import RunCmds
from .various import Various


# -------------------
## parent class for zdo, holds all commands and common data
class ZdoBase(Git, Navigate, Requirements, RunCmds, Various):
    # -------------------
    ## constructor
    def __init__(self):
        Git.__init__(self, cmn)
        Navigate.__init__(self, cmn)
        Requirements.__init__(self, cmn)
        RunCmds.__init__(self, cmn)
        Various.__init__(self, cmn)

        ## these must all take 0 params and return errs (int)
        self._fn_map = {
            # in navigate
            'first': self.navigate_first,
            'next': self.navigate_next,
            'prev': self.navigate_prev,
            'cd': self.navigate_goto,
            # in git
            'check-repo': self.git_check_repo,
            'check-branch': self.git_check_branch,
            'check-subm': self.check_subm,
            'show-branches': self.show_branches,
            # in requirements
            'check-reqmts': self.check_reqmts,
            # in run_cmds
            'run': self.run_cmds,
            # in various
            'check-size': self.check_size,
        }

    # -------------------
    ## add a command to fn_map
    #
    # @param name   the cmd name
    # @param fn     the function to invoke
    # @return None
    def add_cmd(self, name, fn):
        self._fn_map[name] = fn

    # -------------------
    ## get the current list of recognized command names
    #
    # @return list of command names
    @property
    def cmd_names(self):
        return self._fn_map.keys()

    # -------------------
    ## run the given command
    #
    # @param name   the cmd name
    # @return errs
    def run_cmd(self, name):
        errs = 0
        if name in self._fn_map:
            fn = self._fn_map[name]
        else:
            errs += 1
            cmn.log.err(f'unknown command: {name}')
            cmds_list = ', '.join(self.cmd_names)
            cmn.log.err(f'use one of: {cmds_list}')
            return errs

        errs += fn()
        return errs

    # -------------------
    ## set an attribute for use by other zdo functions
    #
    # @param name   the attribute name
    # @param val    the attribute value
    # @return None
    def set_cmn_attr(self, name, val):
        setattr(cmn, name, val)

    # -------------------
    ## override the default logger
    #
    # @param logger the logger to use
    # @return None
    def set_cmn_logger(self, logger):
        cmn.log = logger

    # -------------------
    ## set the repos object that holds information about all repos
    #
    # @param repos   the object to use
    # @return None
    def set_cmn_repos(self, repos):
        cmn.repos = repos

    # -------------------
    ## override the default OSSpecific object
    #
    # @param os_spec   the object to use
    # @return None
    def set_cmn_os_spec(self, os_spec):
        cmn.os_spec = os_spec
