import json
import os
import re


# -------------------
## holds other miscellaneous commands
class Various:
    # -------------------
    ## constructor
    # @param cmn   reference to cmn attributes/values
    def __init__(self, cmn):
        ## holds reference to the cmn object
        self.cmn = cmn

    # -------------------
    ## check the size of the proj and .git directory
    #
    # @return number of errors found
    def check_size(self):
        errs = 0

        cmd = 'du -hs .git .'
        rc, lines = self.cmn.os_spec.run_cmd(cmd)
        self.cmn.log.check(rc == 0, f'cmd rc={rc}')
        # self.cmn.log.num_output(lines)

        count_data = {}
        for line in lines:
            line = line.strip()
            m = re.match(r'^([0123456789.]+.)\s+(.*)$', line)
            if m:
                count_data[m.group(2)] = m.group(1)
        self.cmn.log.line(count_data)

        # get current project
        cwd = os.getcwd()
        proj_dir = cwd.replace(os.path.expanduser('~'), '~')

        all_count_data = {}
        path = os.path.join(self.cmn.proj_man_dir, 'proj_sizes.json')
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as fp:
                all_count_data = json.load(fp)

        all_count_data[proj_dir] = count_data
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(all_count_data, fp, indent=4)

        return errs
