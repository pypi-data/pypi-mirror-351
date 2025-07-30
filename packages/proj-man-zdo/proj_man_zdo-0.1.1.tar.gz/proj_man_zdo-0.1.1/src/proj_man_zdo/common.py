import os


# -------------------
## holds common values and attributes.
# use the cmn global instance below
class Common:  # pylint: disable=too-few-public-methods
    ## holds the name of the current repo/project
    repo = os.path.basename(os.path.normpath(os.getcwd()))

    ## reference to the logger
    log = None
    ## reference to the OsSpecific class
    os_spec = None
    ## reference to the Repos class
    repos = None

    ## function to get the git url for cloning
    get_git_url = None
    ## default git branch
    default_branch = 'master'
    ## submodule info expected in each repo
    # this should be a list of 2-tuples of (subm_dir, subm_branch)
    subm_info = None
    ## list of repos that do not have submodules
    subm_excludes = None
    ## list of paths for base-level requirement files
    reqmts_base_paths = None
    ## path to top level requirement file
    reqmts_top_path = None
    ## skip projects that don't use requirements or gemfile
    reqmts_skip = []


cmn = Common()
