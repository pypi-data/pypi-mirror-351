# --------------------
## base class for all targets
class TargetBaseMin:  # pylint: disable=too-many-instance-attributes
    # --------------------
    ## constructor
    #
    # @param target_name  the target name
    def __init__(self, target_name):
        ## target name
        self._target = target_name

        ## info for the clean rule for this target
        self._clean = {}
        ## help for this target
        self._help = {}
        ## list of rules for this target
        self._rules = []
        ## list of lines in the makefile for all aspects of this target
        self._lines = []

    # --------------------
    ## return the name of this target
    # @return the name of this target
    @property
    def target(self):
        return self._target

    # === target rules

    # --------------------
    ## add a new rule for this target
    #
    # @param rule  the name of the rule
    def add_rule(self, rule):
        self._rules.append(rule)

    # --------------------
    ## return the list of rules for this target
    # @return list of rules
    @property
    def rules(self):
        return self._rules

    # === clean rules

    # --------------------
    ## add clean target to list of patterns to clean
    #
    # @param pattern   the pattern to add
    # @return None
    def add_clean(self, pattern):
        if pattern not in self._clean:
            self._clean[pattern] = 1

    # --------------------
    ## return list of clean patterns for this target
    # @return return list of clean patterns
    @property
    def clean(self):
        return self._clean

    # === help text

    # --------------------
    ## add halp line for the given rule
    #
    # @param rule   the rule this help applies to
    # @param desc   the description for this help
    # @return None
    def _add_help(self, rule, desc):
        # note: replaces the help text if it already exists
        self._help[rule] = desc

    # --------------------
    ## return current help lines
    # @return list of help lines
    @property
    def help(self):
        return self._help

    # === gen functions

    # --------------------
    ## generate a rule
    #
    # @param rule   the rule's name
    # @param deps   the dependencies on this rule
    # @param desc   the description for this rule (comment in the makefile)
    def _gen_rule(self, rule, deps, desc):
        self._writeln(f'#-- {desc}')
        self._add_help(rule, desc)
        if deps:
            self._writeln(f'{rule}: {deps}')
        else:
            self._writeln(f'{rule}:')

    # --------------------
    ## generate lines to clean and generated directories and files given
    #
    # @return None
    def gen_clean(self):
        pass

    # === for writing to Makefile

    # --------------------
    ## return the list of lines for this target
    #
    # @return the list of lines
    @property
    def lines(self):
        return self._lines

    # --------------------
    ## save the given line to be generated later
    #
    # @param line  the line to write
    # @return None
    def _writeln(self, line):
        self._lines.append(line)
