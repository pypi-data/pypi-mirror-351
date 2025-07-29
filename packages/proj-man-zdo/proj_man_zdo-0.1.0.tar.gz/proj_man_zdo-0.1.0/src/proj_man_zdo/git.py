import sys


# -------------------
## holds git related commands and functions
class Git:
    # -------------------
    ## constructor
    #
    # @param cmn   reference to cmn attributes/values
    def __init__(self, cmn):
        ## holds reference to the cmn object
        self.cmn = cmn

    # -------------------
    ## check the repo state, committed, unpushed, etc.
    #
    # @return errs found
    def git_check_repo(self):
        tag = 'check-repo'
        errs = 0
        if len(sys.argv) == 2 or sys.argv[2] == '':
            branch = self.cmn.default_branch
        else:
            branch = sys.argv[2]

        errs += self._check_repo_state(tag, '.', branch)
        return errs

    # -------------------
    ## check submodule states, committed, unpushed, etc.
    #
    # @return errs found
    def check_subm(self):
        tag = 'check-subm'
        errs = 0

        if self.cmn.subm_excludes is not None and self.cmn.repo in self.cmn.subm_excludes:
            # skip repos without submodules
            self.cmn.log.ok(f'{tag}: does not have submodules: {self.cmn.repo}')
            return errs

        if self.cmn.subm_info is not None:
            for subm in self.cmn.subm_info:
                errs += self._check_repo_state(tag, subm[0], subm[1])
        return errs

    # -------------------
    ## check the submodule state, committed, unpushed, etc.
    #
    # @param tag           logging tag
    # @param subm_dir      submodule directory
    # @param subm_branch   expected submodule branch name
    # @return errs found
    def _check_repo_state(self, tag, subm_dir, subm_branch):
        errs = 0
        rc, lines = self.cmn.os_spec.run_cmd('git status', working_dir=subm_dir)
        if rc != 0:
            errs += rc
            self.cmn.log.bug(f'{tag}: git command failed: rc={rc} ({subm_dir})')
        elif not lines:
            errs += 1
            self.cmn.log.bug(f'{tag}: lines are empty ({subm_dir})')
        elif lines[0] != f'On branch {subm_branch}':
            errs += 1
            self.cmn.log.warn(f'{tag}: not on {subm_branch} ({subm_dir})')
            self.cmn.log.warn(f'{tag}: actual {lines[1]}')
        elif lines[1].startswith('Your branch is up to date'):
            if len(lines) < 4:
                errs += 1
                self.cmn.log.bug(f'{tag}: huh? unknown output ({subm_dir})')
                self.cmn.log.num_output(lines)
            elif lines[3].startswith('Changes not staged for commit') or lines[3].startswith('Changes to be committed'):
                errs += 1
                self.cmn.log.warn(f'{tag}: has uncommitted changes ({subm_dir})')
                if lines[3].startswith('Changes not staged for commit'):
                    self.cmn.log.num_output(lines[6:])
                else:
                    self.cmn.log.num_output(lines[3:])
            elif lines[3].startswith('nothing to commit, working tree clean'):
                self.cmn.log.ok(f'{tag}: all changes are committed ({subm_dir})')
            elif lines[3].startswith('Untracked files'):
                errs += 1
                self.cmn.log.warn(f'{tag}: untracked files found ({subm_dir})')
                self.cmn.log.num_output(lines[3:])
            else:
                errs += 1
                self.cmn.log.bug(f'{tag}: unknown commit format')
                self.cmn.log.num_output(lines)
        elif lines[1].startswith('Your branch is ahead of'):
            errs += 1
            self.cmn.log.warn(f'{tag}: has unpushed changes ({subm_dir})')
            self.cmn.log.num_output(lines)
        else:
            errs += 1
            self.cmn.log.bug(f'{tag}: unknown output ({subm_dir})')
            self.cmn.log.num_output(lines)
        return errs

    # -------------------
    ## check main and submodule are the expected branches.
    #
    # @return errs found
    def git_check_branch(self):
        tag = 'check_branch'
        errs = 0
        if len(sys.argv) == 2 or sys.argv[2] == '':
            exp_branch = self.cmn.default_branch
        else:
            exp_branch = sys.argv[2]

        errs += self._check_main_branch(tag, exp_branch)

        if self.cmn.subm_excludes is not None and self.cmn.repo in self.cmn.subm_excludes:
            # skip repos without submodules
            self.cmn.log.ok(f'{tag}: repo: does not have submodules: {self.cmn.repo}')
            return errs

        if self.cmn.subm_info is not None:
            for subm in self.cmn.subm_info:
                errs += self._check_submodule_branch(tag, subm[0], subm[1])

        return errs

    # -------------------
    ## check the main repo is on the expected branch.
    #
    # @param tag           logging tag
    # @param exp_branch    expected branch name
    # @return errs found
    def _check_main_branch(self, tag, exp_branch):
        errs = 0
        rc, lines = self.cmn.os_spec.run_cmd('git rev-parse --abbrev-ref HEAD')
        errs += rc
        if rc != 0:
            self.cmn.log.err(f'{tag}: repo: git command failed: rc={rc}')
        elif not lines:
            errs += 1
            self.cmn.log.err(f'{tag}: repo: no output from git command')
        elif len(lines) == 1:
            act_branch = lines[0]
            if exp_branch and act_branch == exp_branch:
                self.cmn.log.ok(f'{tag}: repo: branch matches: {act_branch}')
            elif exp_branch and act_branch != exp_branch:
                errs += 1
                self.cmn.log.err(f'{tag}: repo: branch does not match: {act_branch}')
            elif exp_branch is None:
                self.cmn.log.ok(f'{tag}: repo: branch is {act_branch}')
        else:
            errs += 1
            self.cmn.log.warn(f'{tag}: repo: unknown output')
            self.cmn.log.num_output(lines)
        return errs

    # -------------------
    ## check the submodule branch in use
    #
    # @param tag           logging tag
    # @param subm_dir      submodule directory
    # @param subm_branch   expected submodule branch name
    # @return errs found
    def _check_submodule_branch(self, tag, subm_dir, subm_branch):
        rc, lines = self.cmn.os_spec.run_cmd('git rev-parse --abbrev-ref HEAD', working_dir=subm_dir)
        errs = rc
        if rc != 0:
            self.cmn.log.bug(f'{tag}: subm: git command failed rc={rc} ({subm_dir})')
        elif not lines:
            errs += 1
            self.cmn.log.err(f'{tag}: subm: missing output from git ({subm_dir})')
        elif len(lines) == 1:
            act_branch = lines[0]
            if subm_branch and act_branch == subm_branch:
                self.cmn.log.ok(f'{tag}: subm: branch matches: {act_branch} ({subm_dir})')
            elif subm_branch and act_branch != subm_branch:
                errs += 1
                self.cmn.log.err(f'{tag}: subm: branch does not match: {act_branch} ({subm_dir})')
            elif subm_branch is None:
                self.cmn.log.ok(f'{tag}: subm: branch is {act_branch} ({subm_dir})')
        else:
            errs += 1
            self.cmn.log.bug(f'{tag}: subm: unknown output ({subm_dir})')
            self.cmn.log.num_output(lines)
        return errs

    # -------------------
    ## show the local and remote branches for the main and any submodules.
    #
    # @return errs found
    def show_branches(self):
        tag = 'show_branches'
        errs = 0

        # assumes branch name is not one of: both, subm or base
        check_branch_name = None
        check_branch_loc = 'both'
        if len(sys.argv) < 4 or sys.argv[3] == '':
            pass
        elif sys.argv[3] in ['both', 'subm', 'base']:
            check_branch_loc = sys.argv[3]
        else:
            check_branch_name = sys.argv[3]

        if len(sys.argv) < 3 or sys.argv[2] == '':
            pass
        elif sys.argv[2] in ['both', 'subm', 'base']:
            check_branch_loc = sys.argv[2]
        else:
            check_branch_name = sys.argv[2]

        # self.cmn.log.dbg(f'{tag}: branch:{check_branch_name} loc:{check_branch_loc}')
        self.cmn.log.line(f'{tag}: branches found:')

        check_branch = None
        if check_branch_loc in ['both', 'base']:
            check_branch = check_branch_name

        errs += self._check_branch_exists('.', check_branch, remote=False)
        errs += self._check_branch_exists('.', check_branch, remote=True)
        if self.cmn.subm_excludes is not None and self.cmn.repo in self.cmn.subm_excludes:
            # skip repos without submodules
            self.cmn.log.ok(f'{tag}: does not have submodules: {self.cmn.repo}')
            return errs

        if self.cmn.subm_info is not None:
            check_branch = None
            if check_branch_loc in ['both', 'subm']:
                check_branch = check_branch_name

            for subm in self.cmn.subm_info:
                errs += self._check_branch_exists(subm[0], check_branch, remote=False)
                errs += self._check_branch_exists(subm[0], check_branch, remote=True)
        return errs

    # -------------------
    ## show branches for local/remote repo
    #
    # @param path           the '.' for main branch, or the submodule directory
    # @param check_branch   the expected branch; None to skip the check
    # @param remote         True to list the remote, False to list the local
    # @return errs found
    def _check_branch_exists(self, path, check_branch, remote=True):
        errs = 0

        # do a fetch just in case
        if remote:
            prefix = '   remote'
            arg = ' -r'
            self.cmn.os_spec.run_cmd('git remote update origin --prune', working_dir=path)
        else:
            prefix = '   local'
            arg = ''

        # show local branches
        rc, lines = self.cmn.os_spec.run_cmd(f'git branch --no-color{arg}', working_dir=path)
        if rc != 0:
            errs += 1
            self.cmn.log.warn(f'{prefix} bad rc: {rc} on git branch cmd')
            return errs

        for line in lines:
            self.cmn.log.line(f'{prefix: <9}: {line: <20} {path}')

        if check_branch is not None:
            found_branch = False
            for line in lines:
                if line.find(check_branch) != -1:
                    found_branch = True

            if found_branch:
                self.cmn.log.line(f'{prefix: <9}:   branch found: {check_branch}')
            else:
                errs += 1
                self.cmn.log.err(f'{prefix: <9}:   branch not found: {check_branch}')

        return errs
