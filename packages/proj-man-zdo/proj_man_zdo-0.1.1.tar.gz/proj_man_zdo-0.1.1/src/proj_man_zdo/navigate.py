import os
import sys


# -------------------
## holds functions for navigating through repos/projects
class Navigate:
    # -------------------
    ## constructor
    # @param cmn   reference to cmn attributes/values
    def __init__(self, cmn):
        ## holds reference to the cmn object
        self.cmn = cmn

    # -------------------
    ## navigate to the first repo in the repos.
    # if that directory/repo does not exist, clone it
    #
    # @return errs
    def navigate_first(self):
        self._check_git_url()
        return self._goto_proj('first', self.cmn.repos.proj_list_order[0])

    # -------------------
    ## navigate to the next repo in the repos based on the current repo.
    # if that directory/repo does not exist, clone it
    #
    # @return errs
    def navigate_next(self):
        self._check_git_url()
        return self._next_proj(forward=True)

    # -------------------
    ## navigate to the previous repo in the repos based on the current repo.
    # if that directory/repo does not exist, clone it
    #
    # @return errs
    def navigate_prev(self):
        self._check_git_url()
        return self._next_proj(forward=False)

    # -------------------
    ## goto the the given repo
    #
    # @return errs
    def navigate_goto(self):
        if len(sys.argv) < 3:
            self.cmn.log.err('cd: need location or a hint')
            return 1

        # also "thefuzz" and "rapidfuzz"
        from fuzzywuzzy import fuzz

        matches = []
        for path in self.cmn.repos.repos.keys():
            site = os.path.basename(path)
            rank = fuzz.token_set_ratio(sys.argv[2], site)
            if rank > 30:
                matches.append((path, rank))

        if len(matches) == 0:
            self.cmn.log.err(f'no matches found for "{sys.argv[2]}"')
            return 1

        self.cmn.log.line(f'found matches for {sys.argv[2]}:')
        count = 0
        best = None
        for match in sorted(matches, key=lambda item: item[1], reverse=True):
            if not best:
                best = match
            self.cmn.log.line(f'    rank {match[1]: >3}: {match[0]}')
            count += 1
            if count > 5:
                break

        return self._goto_proj('cd', best[0])

    # -------------------
    ## navigate to the next/prev repo
    #
    # @param forward  navigate forwards if True, else backwards
    # @return errs
    def _next_proj(self, forward=True):
        if forward:
            direction = 'next'
        else:
            direction = 'prev'
        errs = 0
        cwd = os.getcwd()
        self.cmn.log.line(f'curr directory: {cwd}')
        done = False
        for posn, proj_dir in enumerate(self.cmn.repos.proj_list_order):
            proj_dir2 = os.path.expanduser(proj_dir)
            if cwd != proj_dir2:
                # self.cmn.log.dbg(f'no match: proj_dir: {proj_dir2}')
                continue

            # self.cmn.log.dbg(f'posn:{posn} {len(self.cmn.repos.proj_list_order)}')
            if forward:
                next_posn = posn + 1
                done = (posn + 1) >= len(self.cmn.repos.proj_list_order)
            else:
                next_posn = posn - 1
                done = posn <= 0

            if done:
                self.cmn.log.ok(f'no {direction} project, all done!')
                break

            next_proj = self.cmn.repos.proj_list_order[next_posn]
            next_proj = os.path.expanduser(next_proj)
            if not os.path.isdir(next_proj):
                self.cmn.log.highlight(f'repo missing: {next_proj}, creating it...')
                _, info = self._get_info(next_proj)
                if not info:
                    self.cmn.log.bug('_next_proj: info is None')
                    return 1

                errs += self._create_repo(next_proj, info)

            if os.path.isdir(next_proj):
                self._goto_proj(direction, next_proj)
                done = True
                break

        if not done:
            self.cmn.log.warn(f'unknown {direction} project, check repos')

        return errs

    # -------------------
    ## launch a terminal and cd in the given directory
    #
    # @param direction  next or prev for logging
    # @param next_proj  the name of the project to navigate to
    # @return errs
    # see https://askubuntu.com/questions/998813/how-to-get-terminal-to-open-launch-a-program-and-stay-open-at-startup
    def _goto_proj(self, direction, next_proj):
        self.cmn.log.line(f'{direction} directory: {next_proj}')

        key, info = self._get_info(next_proj)
        if not info:
            self.cmn.log.bug('_goto_proj: info is None')
            return 1

        path_to_next = os.path.expanduser(key)
        if not os.path.isdir(path_to_next):
            self.cmn.log.highlight(f'repo missing: {path_to_next}, creating it...')
            self._create_repo(path_to_next, info)

        if not os.path.isdir(path_to_next):
            return 1

        # self.cmn.log.ok(f'dir exists    : {path_to_next}')

        os.system(f'gnome-terminal '
                  '--geometry=125x40 '
                  f'-- bash -c \'cd {next_proj}; exec $SHELL\'')

        return 0

    # -------------------
    ## clone the given repo
    #
    # @param path_to_next  the directory where to create the repo
    # @param info          information about the repo from repos
    # @return errs
    def _create_repo(self, path_to_next, info):
        parent_dir = os.path.dirname(path_to_next)
        if not os.path.isdir(parent_dir):
            self.cmn.log.line(f'creating repo parent dir: {parent_dir}')
            os.makedirs(parent_dir, exist_ok=True)

        url, _, _ = self._get_url_info(info)

        self.cmn.log.line(f'creating repo: {url}')
        rc, _ = self.cmn.os_spec.run_cmd(f'git clone {url}', working_dir=parent_dir, print_cb=self._print)
        if rc == 0:
            self.cmn.log.ok(f'created repo: rc={rc}')
        else:
            self.cmn.log.warn(f'repo clone failed: {path_to_next}')
        return rc

    # -------------------
    ## callback for printing to stdout
    #
    # @param lineno  the current line number
    # @param line    the line to print
    # @return errs
    def _print(self, lineno, line):
        self.cmn.log.output(lineno, line)

    # -------------------
    ## check the git url matches with the info in repos
    #
    # @return errs
    def _check_git_url(self):
        errs = 0
        _, info = self._get_info(os.getcwd())
        if info is None:
            # nothing to warn about
            self.cmn.log.line(f'curr dir is not in repos: {os.getcwd()}, check if this is expected.')
            return errs

        exp_url, bb_repo, git_url = self._get_url_info(info)

        _, lines = self.cmn.os_spec.run_cmd('git remote get-url origin')
        act_url = lines[0]

        if act_url == exp_url:
            self.cmn.log.ok('git urls match')
        else:
            self.cmn.log.err('check repos: url does not match:')
            self.cmn.log.err(f'   act: {act_url}')
            self.cmn.log.err(f'   exp: {exp_url}')
            self.cmn.log.err(f'   check: git_url {git_url}')
            self.cmn.log.err(f'   check: bb_repo:{bb_repo}')
            errs += 1
        return errs

    # -------------------
    ## get the git URL info from repos
    #
    # @param info  information from repos
    # @return expected url, tag for choosing private/public repos, full git url
    def _get_url_info(self, info):
        bb_repo = info['bb-repo']
        git_url = info['giturl']
        if git_url.startswith('git@'):
            # it's already a full git url, just use it
            exp_url = git_url
        elif self.cmn.get_git_url is None:
            exp_url = 'unknown'
        else:
            exp_url = self.cmn.get_git_url(git_url, bb_repo)
        return exp_url, bb_repo, git_url

    # -------------------
    ## get repo info from repos object
    #
    # @param next_proj  the project to get info about
    # @return errs
    def _get_info(self, next_proj):
        key = next_proj
        home = os.path.expanduser('~')
        if key.startswith(home):
            key = key.replace(home, '~')
        info = self.cmn.repos.repos.get(key)
        return key, info
