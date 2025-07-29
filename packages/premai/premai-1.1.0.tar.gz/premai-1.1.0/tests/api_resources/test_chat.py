# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from premai import PremAI, AsyncPremAI
from tests.utils import assert_matches_type
from premai.types import ChatListModelsResponse, ChatCompletionsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChat:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_completions(self, client: PremAI) -> None:
        chat = client.chat.completions(
            messages=[{"role": "system"}],
            model="model",
        )
        assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_completions_with_all_params(self, client: PremAI) -> None:
        chat = client.chat.completions(
            messages=[
                {
                    "role": "system",
                    "content": None,
                }
            ],
            model="model",
            frequency_penalty=-2,
            max_completion_tokens=1,
            presence_penalty=-2,
            response_format={
                "json_schema": {"foo": "bar"},
                "type": "text",
            },
            seed=0,
            stop="string",
            stream=True,
            temperature=0,
            top_p=0,
        )
        assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_completions(self, client: PremAI) -> None:
        response = client.chat.with_raw_response.completions(
            messages=[{"role": "system"}],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = response.parse()
        assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_completions(self, client: PremAI) -> None:
        with client.chat.with_streaming_response.completions(
            messages=[{"role": "system"}],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = response.parse()
            assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_models(self, client: PremAI) -> None:
        chat = client.chat.list_models()
        assert_matches_type(ChatListModelsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_models(self, client: PremAI) -> None:
        response = client.chat.with_raw_response.list_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = response.parse()
        assert_matches_type(ChatListModelsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_models(self, client: PremAI) -> None:
        with client.chat.with_streaming_response.list_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = response.parse()
            assert_matches_type(ChatListModelsResponse, chat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_list_models_internal(self, client: PremAI) -> None:
        chat = client.chat.list_models_internal()
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list_models_internal(self, client: PremAI) -> None:
        response = client.chat.with_raw_response.list_models_internal()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = response.parse()
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list_models_internal(self, client: PremAI) -> None:
        with client.chat.with_streaming_response.list_models_internal() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = response.parse()
            assert_matches_type(object, chat, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncChat:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_completions(self, async_client: AsyncPremAI) -> None:
        chat = await async_client.chat.completions(
            messages=[{"role": "system"}],
            model="model",
        )
        assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_completions_with_all_params(self, async_client: AsyncPremAI) -> None:
        chat = await async_client.chat.completions(
            messages=[
                {
                    "role": "system",
                    "content": None,
                }
            ],
            model="model",
            frequency_penalty=-2,
            max_completion_tokens=1,
            presence_penalty=-2,
            response_format={
                "json_schema": {"foo": "bar"},
                "type": "text",
            },
            seed=0,
            stop="string",
            stream=True,
            temperature=0,
            top_p=0,
        )
        assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_completions(self, async_client: AsyncPremAI) -> None:
        response = await async_client.chat.with_raw_response.completions(
            messages=[{"role": "system"}],
            model="model",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = await response.parse()
        assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_completions(self, async_client: AsyncPremAI) -> None:
        async with async_client.chat.with_streaming_response.completions(
            messages=[{"role": "system"}],
            model="model",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = await response.parse()
            assert_matches_type(ChatCompletionsResponse, chat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_models(self, async_client: AsyncPremAI) -> None:
        chat = await async_client.chat.list_models()
        assert_matches_type(ChatListModelsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_models(self, async_client: AsyncPremAI) -> None:
        response = await async_client.chat.with_raw_response.list_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = await response.parse()
        assert_matches_type(ChatListModelsResponse, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_models(self, async_client: AsyncPremAI) -> None:
        async with async_client.chat.with_streaming_response.list_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = await response.parse()
            assert_matches_type(ChatListModelsResponse, chat, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_models_internal(self, async_client: AsyncPremAI) -> None:
        chat = await async_client.chat.list_models_internal()
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list_models_internal(self, async_client: AsyncPremAI) -> None:
        response = await async_client.chat.with_raw_response.list_models_internal()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        chat = await response.parse()
        assert_matches_type(object, chat, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list_models_internal(self, async_client: AsyncPremAI) -> None:
        async with async_client.chat.with_streaming_response.list_models_internal() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            chat = await response.parse()
            assert_matches_type(object, chat, path=["response"])

        assert cast(Any, response.is_closed) is True
