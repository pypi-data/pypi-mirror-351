from .svc import svc
from .target_base_min import TargetBaseMin


# --------------------
## generate a target with given commands, help etc.
class TargetManual(TargetBaseMin):
    # class TargetManual(TargetBase):
    # --------------------
    ## create a manual target instance
    #
    # @param targets      current list of targets
    # @param target_name  name of new target to add
    @classmethod
    def create(cls, targets, target_name):
        impl = TargetManual(target_name)
        targets.append(impl)
        return impl

    # --------------------
    ## constructor
    #
    # @param target_name  the name of this target
    def __init__(self, target_name):
        super().__init__(target_name)

        ## commands to invoke
        self._cmds = []

        ## dependencies for this target
        self._deps = []

        ## help line to display
        self._help_line = 'run commands'

    # --------------------
    ## return target type
    #
    # @return manual target
    @property
    def target_type(self):
        return 'manual'

    # --------------------
    ## add a command to this target
    #
    # @param line   the command line to add
    # @return None
    def add_command(self, line):
        self._cmds.append(line)

    # --------------------
    ## add a dependency to this target
    #
    # @param dependency   name of another rule to invoke before this target
    # @return None
    def add_dependency(self, dependency):
        self._deps.append(dependency)

    # --------------------
    ## set the description displayed in the help
    #
    # @param line   the help to use
    # @return None
    def set_help(self, line):
        self._help_line = line

    # --------------------
    ## check target for any issues
    #
    # @return None
    def check(self):
        # nothing to check
        pass

    # --------------------
    ## gen Manual target
    #
    # @return None
    def gen_target(self):
        svc.log.highlight(f'{self.target}: gen target, type:{self.target_type}')

        self._gen_run()

    # --------------------
    ## gen target to run the manual command
    #
    # @return None
    def _gen_run(self):
        deps = ''
        if len(self._deps) > 0:
            deps = ' '.join(self._deps)

        self._gen_rule(self.target, deps, f'{self._help_line}')
        for cmd in self._cmds:
            self._writeln(f'\t{cmd}')
        self._writeln('')
