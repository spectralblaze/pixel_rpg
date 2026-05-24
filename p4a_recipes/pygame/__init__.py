"""
Local p4a recipe override: pygame 2.1.3 with a one-line C patch.

Problem
-------
pygame 2.1.3's  src_c/_sdl2/sdl2.c  does:
    #include <longintrepr.h>
The Python 3.11 Android cross-compile headers don't ship the legacy
top-level longintrepr.h (it lived there as a deprecated shim); the
real file is at  cpython/longintrepr.h.

Fix
---
We keep the exact version / URL / sha256 from the built-in pygame recipe
so all p4a patches and build flags stay intact, and we add a
prebuild_arch() step that rewrites the one bad include path in-place.
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


# ── Override ──────────────────────────────────────────────────────────────────
class PygameRecipe(_Base):
    name = 'pygame'   # keep the same recipe name

    def prebuild_arch(self, arch):
        import os
        super().prebuild_arch(arch)
        # Patch the one broken include in sdl2.c.
        # Python 3.11 Android cross-compile headers have cpython/longintrepr.h
        # but NOT the legacy top-level longintrepr.h shim.
        sdl2_c = os.path.join(
            self.get_build_dir(arch.arch), 'src_c', '_sdl2', 'sdl2.c'
        )
        if not os.path.exists(sdl2_c):
            print(f'[pygame patch] sdl2.c not found at {sdl2_c}, skipping')
            return
        with open(sdl2_c, 'r', encoding='utf-8') as fh:
            code = fh.read()
        patched = code.replace(
            '#include <longintrepr.h>',
            '#include <cpython/longintrepr.h>',
        )
        if patched != code:
            with open(sdl2_c, 'w', encoding='utf-8') as fh:
                fh.write(patched)
            print('[pygame patch] Fixed longintrepr.h -> cpython/longintrepr.h')
        else:
            print('[pygame patch] longintrepr.h include not found, nothing to patch')


recipe = PygameRecipe()
