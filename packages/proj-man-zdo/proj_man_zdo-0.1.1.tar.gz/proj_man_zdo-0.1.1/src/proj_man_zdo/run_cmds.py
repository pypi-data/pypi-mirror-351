import os
import sys


# -------------------
## holds functions for running a command in a set of repos
class RunCmds:
    # -------------------
    ## constructor
    # @param cmn   reference to cmn attributes/values
    def __init__(self, cmn):
        ## holds reference to the cmn object
        self.cmn = cmn

    # -------------------
    ## runs a cmd in the given group of repos
    #
    # @return errs
    def run_cmds(self):
        if len(sys.argv) < 4:
            self.cmn.log.err('missing group and command to run')
            return 1

        group = sys.argv[2]
        self.cmn.log.line(f'group: "{group}"')
        projs_todo = self.cmn.repos.get_projs_todo(group)

        cmd = ' '.join(sys.argv[3:])

        total_run = 0
        total_fail = 0
        for proj_dir in projs_todo:
            total_run += 1
            proj_dir = os.path.expanduser(proj_dir)
            self.cmn.log.highlight(f'running cmd: {cmd} in project: {proj_dir}')
            rc, _ = self.cmn.os_spec.run_cmd(cmd, working_dir=proj_dir, print_cb=self._print_line_cb)
            self.cmn.log.check(rc == 0, f'cmd rc={rc}')
            self.cmn.log.line('')
            if rc != 0:
                total_fail += 1

        self.cmn.log.highlight(f'total run : {total_run: >3}')
        self.cmn.log.check(total_fail == 0, f'total fail: {total_fail: >3}')
        return 0

    # -------------------
    ## callback for run_cmd
    #
    # @param lineno  the current lineno
    # @param line    the line to print
    def _print_line_cb(self, lineno, line):
        self.cmn.log.output(lineno, line)

    # -------------------
    ## based on the given group name, gather the list of projects/repos to visit
    #
    # @param req_group   the requested group
    # @return the list of projects to visit
    def _get_projs_todo(self, req_group):
        groups = self._get_groups(req_group)
        if not groups:
            self.cmn.log.err(f'unknown group: {req_group}')
            return []

        groups = sorted(groups)

        projs_todo = []
        # doing this as the outer loop should ensure that projs that belong to the same group
        # with the same sort field value, will be done together e.g. all rb-apps
        for grp in groups:
            # sort by the sort field and by the repo directory (the key)
            for repo, info in sorted(self.cmn.repos.repos.items(), key=lambda k_v: (k_v[1]['sort'], k_v[0])):
                # this repo belongs to one of the groups the user asked for
                if grp == info['group']:
                    # ensure there are no duplicates
                    if repo not in projs_todo:
                        projs_todo.append(repo)

        return projs_todo

    # -------------------
    ## get all subgroups for the given group name
    #
    # @param req_group   the requested group
    # @return the list of subgroups
    def _get_groups(self, req_group):
        # all2: all + non-project + wip
        # all1: all + wip
        # all : all groups

        top_groups = self.cmn.repos.proj_top_groups

        groups = []
        sub_group_added = False
        for proj_group in self.cmn.repos.proj_groups:
            if req_group == 'all2':
                groups.append(proj_group)
            elif req_group == 'all1' and proj_group not in ['non-project']:
                groups.append(proj_group)
            elif req_group == 'all' and proj_group not in ['non-project', 'wip', 'ard-wip', 'cpp-wip']:
                groups.append(proj_group)
            elif proj_group == req_group:
                groups.append(proj_group)
            elif req_group in top_groups and proj_group in top_groups[req_group]:
                if not sub_group_added:
                    sub_group_added = True
                    for sub_group in self.cmn.repos.proj_top_groups[req_group]:
                        groups.append(sub_group)

        return groups
