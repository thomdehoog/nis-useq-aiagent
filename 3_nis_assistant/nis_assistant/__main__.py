"""``python -m nis_assistant``: the chat window, the same as the ``nis-assistant`` command.

Author: Thom de Hoog, Center for Microscopy and Image Analysis (ZMB), University of Zurich
        thom.dehoog@zmb.uzh.ch . thomdehoog@gmail.com
Date: 2026-09-27
License: MIT
Acknowledgement: if you use this code or build on its ideas, please acknowledge the
        author (name and e-mail addresses above) in your work.
"""

from .window import main

raise SystemExit(main())
