"""Class for printing reports on profiled python code."""

# Class for printing reports on profiled python code. rev 1.0  4/1/94
#
# Based on prior profile module by Sjoerd Mullender...
#   which was hacked somewhat by: Guido van Rossum
#
# see profile.doc and profile.py for more info.

# Copyright 1994, by InfoSeek Corporation, all rights reserved.
# Written by James Roskind
#
# Permission to use, copy, modify, and distribute this Python software
# and its associated documentation for any purpose (subject to the
# restriction in the following sentence) without fee is hereby granted,
# provided that the above copyright notice appears in all copies, and
# that both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of InfoSeek not be used in
# advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.  This permission is
# explicitly restricted to the copying and modification of the software
# to remain in Python, compiled Python, or other languages (such as C)
# wherein the modified or derived code is exclusively imported into a
# Python module.
#
# INFOSEEK CORPORATION DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL INFOSEEK CORPORATION BE LIABLE FOR ANY
# SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER
# RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF
# CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import sys
import os
import time
import marshal
import re

__all__ = ["Stats"]

class Stats:
    """This class is used for creating reports from data generated by the
    Profile class.  It is a "friend" of that class, and imports data either
    by direct access to members of Profile class, or by reading in a dictionary
    that was emitted (via marshal) from the Profile class.

    The big change from the previous Profiler (in terms of raw functionality)
    is that an "add()" method has been provided to combine Stats from
    several distinct profile runs.  Both the constructor and the add()
    method now take arbitrarily many file names as arguments.

    All the print methods now take an argument that indicates how many lines
    to print.  If the arg is a floating point number between 0 and 1.0, then
    it is taken as a decimal percentage of the available lines to be printed
    (e.g., .1 means print 10% of all available lines).  If it is an integer,
    it is taken to mean the number of lines of data that you wish to have
    printed.

    The sort_stats() method now processes some additional options (i.e., in
    addition to the old -1, 0, 1, or 2).  It takes an arbitrary number of
    quoted strings to select the sort order.  For example sort_stats('time',
    'name') sorts on the major key of 'internal function time', and on the
    minor key of 'the name of the function'.  Look at the two tables in
    sort_stats() and get_sort_arg_defs(self) for more examples.

    All methods return self,  so you can string together commands like:
        Stats('foo', 'goo').strip_dirs().sort_stats('calls').\
                            print_stats(5).print_callers(5)
    """

    def __init__(self, *args, **kwds):
        # I can't figure out how to explictly specify a stream keyword arg
        # with *args:
        #   def __init__(self, *args, stream=sys.stdout): ...
        # so I use **kwds and sqauwk if something unexpected is passed in.
        self.stream = sys.stdout
        if "stream" in kwds:
            self.stream = kwds["stream"]
            del kwds["stream"]
        if kwds:
            keys = kwds.keys()
            keys.sort()
            extras = ", ".join(["%s=%s" % (k, kwds[k]) for k in keys])
            raise ValueError("unrecognized keyword args: %s" % extras)
        if not len(args):
            arg = None
        else:
            arg = args[0]
            args = args[1:]
        self.init(arg)
        self.add(*args)

    def init(self, arg):
        self.all_callees = None  # calc only if needed
        self.files = []
        self.fcn_list = None
        self.total_tt = 0
        self.total_calls = 0
        self.prim_calls = 0
        self.max_name_len = 0
        self.top_level = {}
        self.stats = {}
        self.sort_arg_dict = {}
        self.load_stats(arg)
        trouble = 1
        try:
            self.get_top_level_stats()
            trouble = 0
        finally:
            if trouble:
                print("Invalid timing data", end=' ', file=self.stream)
                if self.files: print(self.files[-1], end=' ', file=self.stream)
                print(file=self.stream)

    def load_stats(self, arg):
        if not arg:  self.stats = {}
        elif isinstance(arg, str):
            f = open(arg, 'rb')
            self.stats = marshal.load(f)
            f.close()
            try:
                file_stats = os.stat(arg)
                arg = time.ctime(file_stats.st_mtime) + "    " + arg
            except:  # in case this is not unix
                pass
            self.files = [ arg ]
        elif hasattr(arg, 'create_stats'):
            arg.create_stats()
            self.stats = arg.stats
            arg.stats = {}
        if not self.stats:
            raise TypeError("Cannot create or construct a %r object from '%r''"
                            % (self.__class__, arg))
        return

    def get_top_level_stats(self):
        for func, (cc, nc, tt, ct, callers) in self.stats.items():
            self.total_calls += nc
            self.prim_calls  += cc
            self.total_tt    += tt
            if ("jprofile", 0, "profiler") in callers:
                self.top_level[func] = None
            if len(func_std_string(func)) > self.max_name_len:
                self.max_name_len = len(func_std_string(func))

    def add(self, *arg_list):
        if not arg_list: return self
        if len(arg_list) > 1: self.add(*arg_list[1:])
        other = arg_list[0]
        if type(self) != type(other) or self.__class__ != other.__class__:
            other = Stats(other)
        self.files += other.files
        self.total_calls += other.total_calls
        self.prim_calls += other.prim_calls
        self.total_tt += other.total_tt
        for func in other.top_level:
            self.top_level[func] = None

        if self.max_name_len < other.max_name_len:
            self.max_name_len = other.max_name_len

        self.fcn_list = None

        for func, stat in other.stats.items():
            if func in self.stats:
                old_func_stat = self.stats[func]
            else:
                old_func_stat = (0, 0, 0, 0, {},)
            self.stats[func] = add_func_stats(old_func_stat, stat)
        return self

    def dump_stats(self, filename):
        """Write the profile data to a file we know how to load back."""
        f = open(filename, 'wb')
        try:
            marshal.dump(self.stats, f)
        finally:
            f.close()

    # list the tuple indices and directions for sorting,
    # along with some printable description
    sort_arg_dict_default = {
              "calls"     : (((1,-1),              ), "call count"),
              "cumulative": (((3,-1),              ), "cumulative time"),
              "file"      : (((4, 1),              ), "file name"),
              "line"      : (((5, 1),              ), "line number"),
              "module"    : (((4, 1),              ), "file name"),
              "name"      : (((6, 1),              ), "function name"),
              "nfl"       : (((6, 1),(4, 1),(5, 1),), "name/file/line"),
              "pcalls"    : (((0,-1),              ), "call count"),
              "stdname"   : (((7, 1),              ), "standard name"),
              "time"      : (((2,-1),              ), "internal time"),
              }

    def get_sort_arg_defs(self):
        """Expand all abbreviations that are unique."""
        if not self.sort_arg_dict:
            self.sort_arg_dict = dict = {}
            bad_list = {}
            for word, tup in self.sort_arg_dict_default.items():
                fragment = word
                while fragment:
                    if not fragment:
                        break
                    if fragment in dict:
                        bad_list[fragment] = 0
                        break
                    dict[fragment] = tup
                    fragment = fragment[:-1]
            for word in bad_list:
                del dict[word]
        return self.sort_arg_dict

    def sort_stats(self, *field):
        if not field:
            self.fcn_list = 0
            return self
        if len(field) == 1 and type(field[0]) == type(1):
            # Be compatible with old profiler
            field = [ {-1: "stdname",
                      0:"calls",
                      1:"time",
                      2: "cumulative" }  [ field[0] ] ]

        sort_arg_defs = self.get_sort_arg_defs()
        sort_tuple = ()
        self.sort_type = ""
        connector = ""
        for word in field:
            sort_tuple = sort_tuple + sort_arg_defs[word][0]
            self.sort_type += connector + sort_arg_defs[word][1]
            connector = ", "

        stats_list = []
        for func, (cc, nc, tt, ct, callers) in self.stats.items():
            stats_list.append((cc, nc, tt, ct) + func +
                              (func_std_string(func), func))

        stats_list.sort(TupleComp(sort_tuple).compare)

        self.fcn_list = fcn_list = []
        for tuple in stats_list:
            fcn_list.append(tuple[-1])
        return self

    def reverse_order(self):
        if self.fcn_list:
            self.fcn_list.reverse()
        return self

    def strip_dirs(self):
        oldstats = self.stats
        self.stats = newstats = {}
        max_name_len = 0
        for func, (cc, nc, tt, ct, callers) in oldstats.items():
            newfunc = func_strip_path(func)
            if len(func_std_string(newfunc)) > max_name_len:
                max_name_len = len(func_std_string(newfunc))
            newcallers = {}
            for func2, caller in callers.items():
                newcallers[func_strip_path(func2)] = caller

            if newfunc in newstats:
                newstats[newfunc] = add_func_stats(
                                        newstats[newfunc],
                                        (cc, nc, tt, ct, newcallers))
            else:
                newstats[newfunc] = (cc, nc, tt, ct, newcallers)
        old_top = self.top_level
        self.top_level = new_top = {}
        for func in old_top:
            new_top[func_strip_path(func)] = None

        self.max_name_len = max_name_len

        self.fcn_list = None
        self.all_callees = None
        return self

    def calc_callees(self):
        if self.all_callees: return
        self.all_callees = all_callees = {}
        for func, (cc, nc, tt, ct, callers) in self.stats.items():
            if not func in all_callees:
                all_callees[func] = {}
            for func2, caller in callers.items():
                if not func2 in all_callees:
                    all_callees[func2] = {}
                all_callees[func2][func]  = caller
        return

    #******************************************************************
    # The following functions support actual printing of reports
    #******************************************************************

    # Optional "amount" is either a line count, or a percentage of lines.

    def eval_print_amount(self, sel, list, msg):
        new_list = list
        if type(sel) == type(""):
            new_list = []
            for func in list:
                if re.search(sel, func_std_string(func)):
                    new_list.append(func)
        else:
            count = len(list)
            if type(sel) == type(1.0) and 0.0 <= sel < 1.0:
                count = int(count * sel + .5)
                new_list = list[:count]
            elif type(sel) == type(1) and 0 <= sel < count:
                count = sel
                new_list = list[:count]
        if len(list) != len(new_list):
            msg = msg + "   List reduced from %r to %r due to restriction <%r>\n" % (
                         len(list), len(new_list), sel)

        return new_list, msg

    def get_print_list(self, sel_list):
        width = self.max_name_len
        if self.fcn_list:
            list = self.fcn_list[:]
            msg = "   Ordered by: " + self.sort_type + '\n'
        else:
            list = self.stats.keys()
            msg = "   Random listing order was used\n"

        for selection in sel_list:
            list, msg = self.eval_print_amount(selection, list, msg)

        count = len(list)

        if not list:
            return 0, list
        print(msg, file=self.stream)
        if count < len(self.stats):
            width = 0
            for func in list:
                if  len(func_std_string(func)) > width:
                    width = len(func_std_string(func))
        return width+2, list

    def print_stats(self, *amount):
        for filename in self.files:
            print(filename, file=self.stream)
        if self.files: print(file=self.stream)
        indent = ' ' * 8
        for func in self.top_level:
            print(indent, func_get_function_name(func), file=self.stream)

        print(indent, self.total_calls, "function calls", end=' ', file=self.stream)
        if self.total_calls != self.prim_calls:
            print("(%d primitive calls)" % self.prim_calls, end=' ', file=self.stream)
        print("in %.3f CPU seconds" % self.total_tt, file=self.stream)
        print(file=self.stream)
        width, list = self.get_print_list(amount)
        if list:
            self.print_title()
            for func in list:
                self.print_line(func)
            print(file=self.stream)
            print(file=self.stream)
        return self

    def print_callees(self, *amount):
        width, list = self.get_print_list(amount)
        if list:
            self.calc_callees()

            self.print_call_heading(width, "called...")
            for func in list:
                if func in self.all_callees:
                    self.print_call_line(width, func, self.all_callees[func])
                else:
                    self.print_call_line(width, func, {})
            print(file=self.stream)
            print(file=self.stream)
        return self

    def print_callers(self, *amount):
        width, list = self.get_print_list(amount)
        if list:
            self.print_call_heading(width, "was called by...")
            for func in list:
                cc, nc, tt, ct, callers = self.stats[func]
                self.print_call_line(width, func, callers, "<-")
            print(file=self.stream)
            print(file=self.stream)
        return self

    def print_call_heading(self, name_size, column_title):
        print("Function ".ljust(name_size) + column_title, file=self.stream)
        # print sub-header only if we have new-style callers
        subheader = False
        for cc, nc, tt, ct, callers in self.stats.values():
            if callers:
                value = next(iter(callers.values()))
                subheader = isinstance(value, tuple)
                break
        if subheader:
            print(" "*name_size + "    ncalls  tottime  cumtime", file=self.stream)

    def print_call_line(self, name_size, source, call_dict, arrow="->"):
        print(func_std_string(source).ljust(name_size) + arrow, end=' ', file=self.stream)
        if not call_dict:
            print(file=self.stream)
            return
        clist = sorted(call_dict.keys())
        indent = ""
        for func in clist:
            name = func_std_string(func)
            value = call_dict[func]
            if isinstance(value, tuple):
                nc, cc, tt, ct = value
                if nc != cc:
                    substats = '%d/%d' % (nc, cc)
                else:
                    substats = '%d' % (nc,)
                substats = '%s %s %s  %s' % (substats.rjust(7+2*len(indent)),
                                             f8(tt), f8(ct), name)
                left_width = name_size + 1
            else:
                substats = '%s(%r) %s' % (name, value, f8(self.stats[func][3]))
                left_width = name_size + 3
            print(indent*left_width + substats, file=self.stream)
            indent = " "

    def print_title(self):
        print('   ncalls  tottime  percall  cumtime  percall', end=' ', file=self.stream)
        print('filename:lineno(function)', file=self.stream)

    def print_line(self, func):  # hack : should print percentages
        cc, nc, tt, ct, callers = self.stats[func]
        c = str(nc)
        if nc != cc:
            c = c + '/' + str(cc)
        print(c.rjust(9), end=' ', file=self.stream)
        print(f8(tt), end=' ', file=self.stream)
        if nc == 0:
            print(' '*8, end=' ', file=self.stream)
        else:
            print(f8(tt/nc), end=' ', file=self.stream)
        print(f8(ct), end=' ', file=self.stream)
        if cc == 0:
            print(' '*8, end=' ', file=self.stream)
        else:
            print(f8(ct/cc), end=' ', file=self.stream)
        print(func_std_string(func), file=self.stream)

class TupleComp:
    """This class provides a generic function for comparing any two tuples.
    Each instance records a list of tuple-indices (from most significant
    to least significant), and sort direction (ascending or decending) for
    each tuple-index.  The compare functions can then be used as the function
    argument to the system sort() function when a list of tuples need to be
    sorted in the instances order."""

    def __init__(self, comp_select_list):
        self.comp_select_list = comp_select_list

    def compare (self, left, right):
        for index, direction in self.comp_select_list:
            l = left[index]
            r = right[index]
            if l < r:
                return -direction
            if l > r:
                return direction
        return 0

#**************************************************************************
# func_name is a triple (file:string, line:int, name:string)

def func_strip_path(func_name):
    filename, line, name = func_name
    return os.path.basename(filename), line, name

def func_get_function_name(func):
    return func[2]

def func_std_string(func_name): # match what old profile produced
    if func_name[:2] == ('~', 0):
        # special case for built-in functions
        name = func_name[2]
        if name.startswith('<') and name.endswith('>'):
            return '{%s}' % name[1:-1]
        else:
            return name
    else:
        return "%s:%d(%s)" % func_name

#**************************************************************************
# The following functions combine statists for pairs functions.
# The bulk of the processing involves correctly handling "call" lists,
# such as callers and callees.
#**************************************************************************

def add_func_stats(target, source):
    """Add together all the stats for two profile entries."""
    cc, nc, tt, ct, callers = source
    t_cc, t_nc, t_tt, t_ct, t_callers = target
    return (cc+t_cc, nc+t_nc, tt+t_tt, ct+t_ct,
              add_callers(t_callers, callers))

def add_callers(target, source):
    """Combine two caller lists in a single list."""
    new_callers = {}
    for func, caller in target.items():
        new_callers[func] = caller
    for func, caller in source.items():
        if func in new_callers:
            new_callers[func] = caller + new_callers[func]
        else:
            new_callers[func] = caller
    return new_callers

def count_calls(callers):
    """Sum the caller statistics to get total number of calls received."""
    nc = 0
    for calls in callers.values():
        nc += calls
    return nc

#**************************************************************************
# The following functions support printing of reports
#**************************************************************************

def f8(x):
    return "%8.3f" % x

#**************************************************************************
# Statistics browser added by ESR, April 2001
#**************************************************************************

if __name__ == '__main__':
    import cmd
    try:
        import readline
    except ImportError:
        pass

    class ProfileBrowser(cmd.Cmd):
        def __init__(self, profile=None):
            cmd.Cmd.__init__(self)
            self.prompt = "% "
            if profile is not None:
                self.stats = Stats(profile)
                self.stream = self.stats.stream
            else:
                self.stats = None
                self.stream = sys.stdout

        def generic(self, fn, line):
            args = line.split()
            processed = []
            for term in args:
                try:
                    processed.append(int(term))
                    continue
                except ValueError:
                    pass
                try:
                    frac = float(term)
                    if frac > 1 or frac < 0:
                        print("Fraction argument must be in [0, 1]", file=self.stream)
                        continue
                    processed.append(frac)
                    continue
                except ValueError:
                    pass
                processed.append(term)
            if self.stats:
                getattr(self.stats, fn)(*processed)
            else:
                print("No statistics object is loaded.", file=self.stream)
            return 0
        def generic_help(self):
            print("Arguments may be:", file=self.stream)
            print("* An integer maximum number of entries to print.", file=self.stream)
            print("* A decimal fractional number between 0 and 1, controlling", file=self.stream)
            print("  what fraction of selected entries to print.", file=self.stream)
            print("* A regular expression; only entries with function names", file=self.stream)
            print("  that match it are printed.", file=self.stream)

        def do_add(self, line):
            self.stats.add(line)
            return 0
        def help_add(self):
            print("Add profile info from given file to current statistics object.", file=self.stream)

        def do_callees(self, line):
            return self.generic('print_callees', line)
        def help_callees(self):
            print("Print callees statistics from the current stat object.", file=self.stream)
            self.generic_help()

        def do_callers(self, line):
            return self.generic('print_callers', line)
        def help_callers(self):
            print("Print callers statistics from the current stat object.", file=self.stream)
            self.generic_help()

        def do_EOF(self, line):
            print("", file=self.stream)
            return 1
        def help_EOF(self):
            print("Leave the profile brower.", file=self.stream)

        def do_quit(self, line):
            return 1
        def help_quit(self):
            print("Leave the profile brower.", file=self.stream)

        def do_read(self, line):
            if line:
                try:
                    self.stats = Stats(line)
                except IOError as args:
                    print(args[1], file=self.stream)
                    return
                self.prompt = line + "% "
            elif len(self.prompt) > 2:
                line = self.prompt[-2:]
            else:
                print("No statistics object is current -- cannot reload.", file=self.stream)
            return 0
        def help_read(self):
            print("Read in profile data from a specified file.", file=self.stream)

        def do_reverse(self, line):
            self.stats.reverse_order()
            return 0
        def help_reverse(self):
            print("Reverse the sort order of the profiling report.", file=self.stream)

        def do_sort(self, line):
            abbrevs = self.stats.get_sort_arg_defs()
            if line and not filter(lambda x,a=abbrevs: x not in a,line.split()):
                self.stats.sort_stats(*line.split())
            else:
                print("Valid sort keys (unique prefixes are accepted):", file=self.stream)
                for (key, value) in Stats.sort_arg_dict_default.items():
                    print("%s -- %s" % (key, value[1]), file=self.stream)
            return 0
        def help_sort(self):
            print("Sort profile data according to specified keys.", file=self.stream)
            print("(Typing `sort' without arguments lists valid keys.)", file=self.stream)
        def complete_sort(self, text, *args):
            return [a for a in Stats.sort_arg_dict_default if a.startswith(text)]

        def do_stats(self, line):
            return self.generic('print_stats', line)
        def help_stats(self):
            print("Print statistics from the current stat object.", file=self.stream)
            self.generic_help()

        def do_strip(self, line):
            self.stats.strip_dirs()
            return 0
        def help_strip(self):
            print("Strip leading path information from filenames in the report.", file=self.stream)

        def postcmd(self, stop, line):
            if stop:
                return stop
            return None

    import sys
    if len(sys.argv) > 1:
        initprofile = sys.argv[1]
    else:
        initprofile = None
    try:
        browser = ProfileBrowser(initprofile)
        print("Welcome to the profile statistics browser.", file=browser.stream)
        browser.cmdloop()
        print("Goodbye.", file=browser.stream)
    except KeyboardInterrupt:
        pass

# That's all, folks.
