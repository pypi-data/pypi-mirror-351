from .pl import TOOLS_DICT as PL_TOOLS_DICT
from .pp import TOOLS_DICT as PP_TOOLS_DICT
from .tl import TOOLS_DICT as TL_TOOLS_DICT
from biochatter.api_agent.base.agent_abc import ROOT

TOOLS_DICT = {}
TOOLS_DICT.update(PL_TOOLS_DICT)
TOOLS_DICT.update(PP_TOOLS_DICT)
TOOLS_DICT.update(TL_TOOLS_DICT)


TOOLS_DICT.update({ROOT._api_name.default: ROOT})

TARGET_TOOLS_DICT = PL_TOOLS_DICT