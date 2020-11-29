import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import challenge_manager as cm
import pytest


@pytest.mark.asyncio
async def test_update(tmp_path):
    await cm.update_challenges(tmp_path, 'https://github.com/Insper/design-de-software-exercicios.git')
    # assert len(list(tmp_path.iterdir())) > 0


