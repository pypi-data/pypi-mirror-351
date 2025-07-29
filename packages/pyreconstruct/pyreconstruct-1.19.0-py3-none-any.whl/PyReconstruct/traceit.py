"""traceit.py

Traces the call stack.

Usage:

import sys
import traceit

sys.setprofile(traceit.tracefunc)
"""

from pathlib import Path

## Look for these words in the file path.
INCLUSIONS = {"main", "table"}

## Ignore <listcomp>, etc. in the function name.
EXCLUSIONS = {"<", "markTime", "resizeEvent", "addLine"}


def tracefunc(frame, event, arg):

    if event == "call":

        tracefunc.stack_level += 1

        unique_id = frame.f_code.co_filename + str(frame.f_lineno)

        if unique_id in tracefunc.memorized:  # already run?
            return

        include = any(x in frame.f_code.co_filename for x in INCLUSIONS)
        exclude = any(x in frame.f_code.co_name for x in EXCLUSIONS)

        # Part of filename MUST be in white list.
        if include and not exclude:

            if 'self' in frame.f_locals:
                
                class_name = frame.f_locals['self'].__class__.__name__
                func_name = class_name + '.' + frame.f_code.co_name
                
            else:
                
                func_name = frame.f_code.co_name

            func_name = '{name:->{indent}s}()'.format(
                    indent=tracefunc.stack_level*2, name=func_name
            )

            filename = Path(frame.f_code.co_filename).name
            
            txt = '{: <40} # {}, {}'.format(
                    func_name, filename, frame.f_lineno
            )
            
            print(txt)

            tracefunc.memorized.add(unique_id)

    elif event == "return":
        tracefunc.stack_level -= 1


tracefunc.memorized = set()
tracefunc.stack_level = 0
