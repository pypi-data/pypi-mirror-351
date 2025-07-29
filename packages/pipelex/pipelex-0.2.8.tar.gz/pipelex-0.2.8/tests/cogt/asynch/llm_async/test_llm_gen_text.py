import asyncio
from typing import List

import pytest

from pipelex import log, pretty_print
from pipelex.cogt.llm.llm_job_components import LLMJobParams
from pipelex.cogt.llm.llm_job_factory import LLMJobFactory
from pipelex.cogt.llm.llm_models.llm_family import LLMFamily
from pipelex.hub import get_llm_deck, get_llm_worker, get_report_delegate
from tests.cogt.test_data import LLMTestCases


def get_async_worker_and_job(llm_preset_id: str, user_text: str):
    llm_setting = get_llm_deck().get_llm_setting(llm_setting_or_preset_id=llm_preset_id)
    pretty_print(llm_setting, title=llm_preset_id)
    pretty_print(user_text)
    llm_worker = get_llm_worker(llm_handle=llm_setting.llm_handle)
    llm_job_params = llm_setting.make_llm_job_params()
    llm_job = LLMJobFactory.make_llm_job_from_prompt_contents(
        user_text=user_text,
        llm_job_params=llm_job_params,
    )
    return llm_worker, llm_job


@pytest.mark.llm
@pytest.mark.inference
@pytest.mark.asyncio(loop_scope="class")
class TestAsyncCogtLLMGenText:
    @pytest.mark.parametrize("topic, prompt_text", LLMTestCases.SINGLE_TEXT)
    async def test_gen_text_async_using_handle(self, llm_job_params: LLMJobParams, llm_handle: str, topic: str, prompt_text: str):
        pretty_print(prompt_text, title=topic)
        llm_worker = get_llm_worker(llm_handle=llm_handle)
        llm_job = LLMJobFactory.make_llm_job_from_prompt_contents(
            user_text=prompt_text,
            llm_job_params=llm_job_params,
        )
        generated_text = await llm_worker.gen_text(llm_job=llm_job)
        assert generated_text
        pretty_print(generated_text)
        get_report_delegate().generate_report()

    @pytest.mark.parametrize("topic, prompt_text", LLMTestCases.SINGLE_TEXT)
    async def test_gen_text_async_using_llm_preset(self, llm_preset_id: str, topic: str, prompt_text: str):
        llm_worker, llm_job = get_async_worker_and_job(llm_preset_id=llm_preset_id, user_text=prompt_text)
        generated_text = await llm_worker.gen_text(llm_job=llm_job)
        assert generated_text
        pretty_print(generated_text)

    @pytest.mark.parametrize("topic, prompt_text", LLMTestCases.SINGLE_TEXT)
    async def test_gen_text_async_multiple_using_llm_preset(self, llm_preset_id: str, topic: str, prompt_text: str):
        llm_worker, llm_job = get_async_worker_and_job(llm_preset_id=llm_preset_id, user_text=prompt_text)
        job_params_base = llm_job.job_params
        max_tokens = 30
        temperature = 0.1
        tasks: List[asyncio.Task[str]] = []
        for _ in range(4):
            max_tokens += 50
            temperature += 0.2
            if temperature > 1:
                break
            if llm_worker.llm_engine.llm_model.llm_family == LLMFamily.O_SERIES:
                log.warning("LLMFamily.O1, forcing temprature to 1, setting minimum tokens to avoid empty output")
                completion_max_tokens = max(max_tokens, 2000)
                llm_job.job_params = job_params_base.model_copy(update={"max_tokens": completion_max_tokens, "temperature": 1})
            else:
                llm_job.job_params = job_params_base.model_copy(update={"max_tokens": max_tokens, "temperature": temperature})
            task: asyncio.Task[str] = asyncio.create_task(llm_worker.gen_text(llm_job=llm_job))
            tasks.append(task)

        generated_texts = await asyncio.gather(*tasks)
        for generated_text in generated_texts:
            assert generated_text
            pretty_print(generated_text)
