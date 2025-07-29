# -*- coding: utf-8 -*-
#
# This file is a part of the LinkAhead Project.
#
# Copyright (C) 2024 Henrik tom Wörden <h.tomwoerden@indiscale.com>
# Copyright (C) 2024 IndiScale GmbH <info@indiscale.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

import warnings


def escape_squoted_text(text: str) -> str:
    r"""Return an escaped version of the argument.

    The characters ``\``, ``*`` and ``'`` need to be escaped if used in single quoted
    expressions in the query language.

    This function returns the given string where the characters ``\``, ``'`` and ``*`` are
    escaped by a ``\`` (backslash character).

    Parameters
    ----------
    text : str
        The text to be escaped.

    Returns
    -------
    out : str
        The escaped text.
    """
    return text.replace("\\", r"\\").replace("'", r"\'").replace("*", r"\*")


def escape_dquoted_text(text: str) -> str:
    r"""Return an escaped version of the argument.

    The characters ``\``, ``*`` and ``"`` need to be escaped if used in double quoted
    expressions in the query language.

    This function returns the given string where the characters ``\``, ``"`` and ``*`` are
    escaped by a ``\`` (backslash character).

    Parameters
    ----------
    text : str
        The text to be escaped.

    Returns
    -------
    out : str
        The escaped text.
    """
    return text.replace("\\", r"\\").replace('"', r"\"").replace("*", r"\*")


def escape_quoted_text(text: str) -> str:
    """
    Please use escape_squoted_text or escape_dquoted_text instead of this function.
    """
    warnings.warn("Please use escape_squoted_text or escape_dquoted_text", DeprecationWarning)
    return escape_squoted_text(text)
