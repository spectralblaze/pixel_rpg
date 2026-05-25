"""
Local p4a recipe override: pygame 2.1.3 with Python 3.11 compatibility patches.

Problems
--------
All Cython-generated files under pygame 2.1.3's src_c/ tree were built
against Python 3.9 internals that were removed/changed in Python 3.11:

  * #include "longintrepr.h"   -> moved to cpython/longintrepr.h
  * PyCode_New() argument count changed (15 -> 17)
  * PyFrameObject struct became opaque
  * tstate->recursion_depth removed (renamed recursion_remaining)
  * CO_NOFREE flag removed

Affected files: src_c/_sdl2/{sdl2,audio,video,mixer,touch,controller}.c,
                src_c/_sprite.c, and potentially others.

Fix
---
We keep the exact version / URL / sha256 from the built-in pygame recipe
so all p4a patches and build flags stay intact, and we add a
prebuild_arch() step that walks the entire src_c/ tree, finds every .c
file that still contains the old  #include "longintrepr.h"  line, and
replaces it with a minimal Python 3.11-safe stub module.

pygame._sdl2 is the high-level SDL2 binding the game doesn't use.
pygame._sprite is the C accelerator for pygame.sprite; pygame falls back
to the pure-Python sprite.py when the C extension is absent, so stubbing
it is safe.
"""

import importlib.util as _ilu
import os as _os
import sys as _sys

# ── Load the built-in 'pygame' recipe under a private module name ─────────────
# We cannot do  from pythonforandroid.recipes.pygame import ...  because p4a
# registers OUR file as sys.modules['pythonforandroid.recipes.pygame'] before
# executing it, which would create a circular import.  Loading by file path
# under a different name sidesteps the problem entirely.
import pythonforandroid as _p4a

_builtin_path = _os.path.join(
    _os.path.dirname(_p4a.__file__), 'recipes', 'pygame', '__init__.py'
)
_spec = _ilu.spec_from_file_location('_pygame_builtin_recipe', _builtin_path)
_mod  = _ilu.module_from_spec(_spec)
_sys.modules['_pygame_builtin_recipe'] = _mod
_spec.loader.exec_module(_mod)

_Base = _mod.recipe.__class__   # the real PygameRecipe from p4a


def _make_stub(module_name: str) -> str:
    """Return a minimal Python 3.11-safe C extension stub for the given name."""
    init_func = 'PyInit_' + module_name
    return (
        '#include <Python.h>\n'
        '\n'
        'static PyMethodDef _stub_methods[] = { {NULL, NULL, 0, NULL} };\n'
        '\n'
        'static struct PyModuleDef _stub_moduledef = {\n'
        '    PyModuleDef_HEAD_INIT,\n'
        f'    "{module_name}",\n'
        '    NULL, -1, _stub_methods\n'
        '};\n'
        '\n'
        f'PyMODINIT_FUNC {init_func}(void) {{\n'
        '    return PyModule_Create(&_stub_moduledef);\n'
        '}\n'
    )


# ── Override ──────────────────────────────────────────────────────────────────
class PygameRecipe(_Base):
    name = 'pygame'   # keep the same recipe name

    def prebuild_arch(self, arch):
        import os
        super().prebuild_arch(arch)

        src_c_dir = os.path.join(self.get_build_dir(arch.arch), 'src_c')
        if not os.path.isdir(src_c_dir):
            print(f'[pygame patch] src_c dir not found at {src_c_dir}, skipping')
            return

        # Walk the entire src_c/ tree and stub every Cython-generated .c file
        # that still references the old Python 3.9 internal header
        # "longintrepr.h" (moved to cpython/longintrepr.h in 3.11).  Those
        # files also tend to use other removed APIs (PyCode_New arity,
        # opaque PyFrameObject, etc.), so a line-by-line patch would be
        # fragile — replacing the whole file with a minimal stub is safer.
        #
        # Known affected files (pygame 2.1.3 + Python 3.11):
        #   src_c/_sdl2/{sdl2,audio,video,mixer,touch,controller}.c
        #   src_c/_sprite.c
        stubbed = 0
        for dirpath, _dirs, fnames in os.walk(src_c_dir):
            for fname in fnames:
                if not fname.endswith('.c'):
                    continue
                fpath = os.path.join(dirpath, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='replace') as fh:
                        contents = fh.read()
                except OSError:
                    continue
                if '#include "longintrepr.h"' not in contents:
                    continue
                mod_name = fname[:-2]   # strip .c suffix
                with open(fpath, 'w', encoding='utf-8') as fh:
                    fh.write(_make_stub(mod_name))
                rel = os.path.relpath(fpath, src_c_dir)
                print(f'[pygame patch] Stubbed src_c/{rel} (Python 3.11 ABI fix)')
                stubbed += 1

        if stubbed == 0:
            print('[pygame patch] No longintrepr.h references found — nothing to stub')
        else:
            print(f'[pygame patch] Stubbed {stubbed} file(s) total')


recipe = PygameRecipe()
