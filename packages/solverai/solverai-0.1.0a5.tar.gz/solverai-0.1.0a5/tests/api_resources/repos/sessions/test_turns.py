# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from solverai import Solver, AsyncSolver
from tests.utils import assert_matches_type
from solverai.types.repos import Turn
from solverai.types.repos.sessions import TurnListResponse, TurnGetPatchResponse, TurnGetChangeLocalizationsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTurns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Solver) -> None:
        turn = client.repos.sessions.turns.list(
            session_id="sessionId",
            provider="github",
            org="org",
            repo="repo",
        )
        assert_matches_type(TurnListResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Solver) -> None:
        response = client.repos.sessions.turns.with_raw_response.list(
            session_id="sessionId",
            provider="github",
            org="org",
            repo="repo",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(TurnListResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Solver) -> None:
        with client.repos.sessions.turns.with_streaming_response.list(
            session_id="sessionId",
            provider="github",
            org="org",
            repo="repo",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(TurnListResponse, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_list(self, client: Solver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            client.repos.sessions.turns.with_raw_response.list(
                session_id="sessionId",
                provider="github",
                org="",
                repo="repo",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            client.repos.sessions.turns.with_raw_response.list(
                session_id="sessionId",
                provider="github",
                org="org",
                repo="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.list(
                session_id="",
                provider="github",
                org="org",
                repo="repo",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_cancel(self, client: Solver) -> None:
        turn = client.repos.sessions.turns.cancel(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_cancel(self, client: Solver) -> None:
        response = client.repos.sessions.turns.with_raw_response.cancel(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_cancel(self, client: Solver) -> None:
        with client.repos.sessions.turns.with_streaming_response.cancel(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(Turn, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_cancel(self, client: Solver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Solver) -> None:
        turn = client.repos.sessions.turns.get(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Solver) -> None:
        response = client.repos.sessions.turns.with_raw_response.get(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Solver) -> None:
        with client.repos.sessions.turns.with_streaming_response.get(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(Turn, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Solver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            client.repos.sessions.turns.with_raw_response.get(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            client.repos.sessions.turns.with_raw_response.get(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.get(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.get(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_change_localizations(self, client: Solver) -> None:
        turn = client.repos.sessions.turns.get_change_localizations(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(TurnGetChangeLocalizationsResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_change_localizations(self, client: Solver) -> None:
        response = client.repos.sessions.turns.with_raw_response.get_change_localizations(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(TurnGetChangeLocalizationsResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_change_localizations(self, client: Solver) -> None:
        with client.repos.sessions.turns.with_streaming_response.get_change_localizations(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(TurnGetChangeLocalizationsResponse, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_change_localizations(self, client: Solver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get_patch(self, client: Solver) -> None:
        turn = client.repos.sessions.turns.get_patch(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(TurnGetPatchResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_patch(self, client: Solver) -> None:
        response = client.repos.sessions.turns.with_raw_response.get_patch(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = response.parse()
        assert_matches_type(TurnGetPatchResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_patch(self, client: Solver) -> None:
        with client.repos.sessions.turns.with_streaming_response.get_patch(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = response.parse()
            assert_matches_type(TurnGetPatchResponse, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get_patch(self, client: Solver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )


class TestAsyncTurns:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncSolver) -> None:
        turn = await async_client.repos.sessions.turns.list(
            session_id="sessionId",
            provider="github",
            org="org",
            repo="repo",
        )
        assert_matches_type(TurnListResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncSolver) -> None:
        response = await async_client.repos.sessions.turns.with_raw_response.list(
            session_id="sessionId",
            provider="github",
            org="org",
            repo="repo",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = await response.parse()
        assert_matches_type(TurnListResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncSolver) -> None:
        async with async_client.repos.sessions.turns.with_streaming_response.list(
            session_id="sessionId",
            provider="github",
            org="org",
            repo="repo",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(TurnListResponse, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_list(self, async_client: AsyncSolver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.list(
                session_id="sessionId",
                provider="github",
                org="",
                repo="repo",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.list(
                session_id="sessionId",
                provider="github",
                org="org",
                repo="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.list(
                session_id="",
                provider="github",
                org="org",
                repo="repo",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_cancel(self, async_client: AsyncSolver) -> None:
        turn = await async_client.repos.sessions.turns.cancel(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncSolver) -> None:
        response = await async_client.repos.sessions.turns.with_raw_response.cancel(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = await response.parse()
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncSolver) -> None:
        async with async_client.repos.sessions.turns.with_streaming_response.cancel(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(Turn, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncSolver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.cancel(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncSolver) -> None:
        turn = await async_client.repos.sessions.turns.get(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncSolver) -> None:
        response = await async_client.repos.sessions.turns.with_raw_response.get(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = await response.parse()
        assert_matches_type(Turn, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncSolver) -> None:
        async with async_client.repos.sessions.turns.with_streaming_response.get(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(Turn, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncSolver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_change_localizations(self, async_client: AsyncSolver) -> None:
        turn = await async_client.repos.sessions.turns.get_change_localizations(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(TurnGetChangeLocalizationsResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_change_localizations(self, async_client: AsyncSolver) -> None:
        response = await async_client.repos.sessions.turns.with_raw_response.get_change_localizations(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = await response.parse()
        assert_matches_type(TurnGetChangeLocalizationsResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_change_localizations(self, async_client: AsyncSolver) -> None:
        async with async_client.repos.sessions.turns.with_streaming_response.get_change_localizations(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(TurnGetChangeLocalizationsResponse, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_change_localizations(self, async_client: AsyncSolver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_change_localizations(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_patch(self, async_client: AsyncSolver) -> None:
        turn = await async_client.repos.sessions.turns.get_patch(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )
        assert_matches_type(TurnGetPatchResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_patch(self, async_client: AsyncSolver) -> None:
        response = await async_client.repos.sessions.turns.with_raw_response.get_patch(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        turn = await response.parse()
        assert_matches_type(TurnGetPatchResponse, turn, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_patch(self, async_client: AsyncSolver) -> None:
        async with async_client.repos.sessions.turns.with_streaming_response.get_patch(
            turn_id="turnId",
            provider="github",
            org="org",
            repo="repo",
            session_id="sessionId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            turn = await response.parse()
            assert_matches_type(TurnGetPatchResponse, turn, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get_patch(self, async_client: AsyncSolver) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `org` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="turnId",
                provider="github",
                org="",
                repo="repo",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `repo` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="",
                session_id="sessionId",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `session_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="turnId",
                provider="github",
                org="org",
                repo="repo",
                session_id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `turn_id` but received ''"):
            await async_client.repos.sessions.turns.with_raw_response.get_patch(
                turn_id="",
                provider="github",
                org="org",
                repo="repo",
                session_id="sessionId",
            )
