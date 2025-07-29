import json
import os
import re
import urllib.error
import urllib.request


# -------------------
## holds functions related to getting python/ruby requirements for modules/gems
class Requirements:
    # -------------------
    ## constructor
    # @param cmn   reference to cmn attributes/values
    def __init__(self, cmn):
        ## holds reference to the cmn object
        self.cmn = cmn

    # -------------------
    ## check requirements are up to date and have no conflict
    #
    # @return errs
    def check_reqmts(self):
        tag = 'check-reqmts'
        errs = 0

        if self.cmn.repo in self.cmn.reqmts_skip:
            self.cmn.log.line(f'skipping, does not use reqmts: {self.cmn.repo}')
        elif os.path.isfile(os.path.join('tools', 'requirements.txt')):
            errs += self._check_py_reqmts(tag)
        elif os.path.isfile('Gemfile'):
            errs += self._check_rb_reqmts(tag)
        else:
            errs += 1
            self.cmn.log.err(f'missing requirements.txt file or Gemfile: {self.cmn.repo}')
        self.cmn.log.check(errs == 0, f'{tag}: number errs found: {errs}')
        return errs

    # === ruby related

    # -------------------
    ## check ruby requirements using bundle outdated
    #
    # @param tag   logging tag
    # @return errs
    def _check_rb_reqmts(self, tag):
        errs = 0
        _, lines = self.cmn.os_spec.run_cmd('bundle outdated')
        count_it = False
        for line in lines:
            if 'Bundle up to date!' in line:
                break
            if line.startswith('Gem '):
                count_it = True
                continue
            if count_it:
                errs += 1
                self.cmn.log.err(f'{tag}: {line}')
        return errs

    # === python related

    # -------------------
    ## check python requirements using pypi info
    #
    # @param tag   logging tag
    # @return errs
    def _check_py_reqmts(self, tag):
        errs = 0

        # get the base, common requirement packages first
        packages = {}
        errs += self._check_base_reqmts(tag, packages)

        if self.cmn.reqmts_top_path is not None:
            # get top level requirements, should not be any duplicates
            errs += self._get_packages(tag, self.cmn.reqmts_top_path, packages, allow_dup=False)

        # check if the packages are at the latest pypi version
        for pkg, pkg_info in packages.items():
            # self.cmn.log.dbg(f'{tag}: {pkg: <25}: {pkg_info}')
            errs += self._check_package(tag, pkg, pkg_info)

        return errs

    # -------------------
    ## get requirements in base level files
    #
    # @param tag       logging tag
    # @param packages  holds list of packages found so far
    # @return errs
    def _check_base_reqmts(self, tag, packages):
        errs = 0

        if self.cmn.reqmts_base_paths is None:
            return errs

        for path in self.cmn.reqmts_base_paths:
            errs += self._get_packages(tag, path, packages)
        return errs

    # -------------------
    ## get requirements from the given file path
    #
    # @param tag        logging tag
    # @param path       the path to the requirements file
    # @param packages   holds list of packages found so far
    # @param allow_dup  if True, check for duplicate requirements
    # @return errs
    def _get_packages(self, tag, path, packages, allow_dup=True):
        errs = 0
        if not os.path.isfile(path):
            self.cmn.log.warn(f'{tag}: path does not exist: {path}')
            return errs

        with open(path, 'r', encoding='utf-8') as fp:
            lines = fp.readlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                m = re.search(r'(.*)(==|>=)([0123456789.\[\]]+)', line)
                if not m:
                    errs += 1
                    self.cmn.log.err(f'{tag}: huh? unknown format1: {line}')
                    continue
                pkg_name = m.group(1)
                pkg_version = m.group(3)
                if pkg_name not in packages:
                    # new one, save it
                    packages[pkg_name] = {'path': path, 'version': pkg_version}
                    continue

                # pkg is already in the list
                if not allow_dup:
                    self.cmn.log.warn(f'{tag}: package "{pkg_name}" already in:')
                    self.cmn.log.warn(f'   {packages[pkg_name]["path"]}')
                    self.cmn.log.warn(f'   {path}')

                if pkg_version != packages[pkg_name]["version"]:
                    self.cmn.log.warn(f'{tag}: package "{pkg_name}" version:')
                    self.cmn.log.warn(f'   {packages[pkg_name]["version"]: <8} {packages[pkg_name]["path"]}')
                    self.cmn.log.warn(f'   {pkg_version: <8} {path}')
        return errs

    # -------------------
    ## check the current package in pypi is at the latest version
    #
    # @param tag       logging tag
    # @param pkg_name  the package to check
    # @param pkg_info  info about the package (path and version)
    # @return errs
    def _check_package(self, tag, pkg_name, pkg_info):
        clean_name = pkg_name.split('[')[0]
        exp_version = pkg_info['version']
        # self.cmn.log.dbg(f'checking: {clean_name}')
        try:
            with urllib.request.urlopen(f'https://pypi.org/pypi/{clean_name}/json') as rsp:
                response = rsp.read().decode('utf-8')
                data = json.loads(response)
                latest_version = data['info']['version']
                if latest_version == exp_version:
                    return 0
        except urllib.error.HTTPError:
            self.cmn.log.warn(f'{tag}: {pkg_name: <17} not found in pypi, see {pkg_info["path"]}')
            return 1

        self.cmn.log.warn(f'{tag}: {pkg_name: <17} in use: {exp_version: >7}  latest: {latest_version: >7}, '
                          f'see {pkg_info["path"]}')
        return 1
