from typing import Generator

import pytest


class TestTemplate:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_test(self, docker_cleanup: Generator[None, None, None]) -> None:
        print("Running a test")
        assert True
