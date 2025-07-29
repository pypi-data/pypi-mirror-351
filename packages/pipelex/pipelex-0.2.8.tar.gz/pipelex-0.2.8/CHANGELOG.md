# Changelog

## [v0.2.6] - 2025-05-26

- Refactor: use ActivityManagerProtocol, rename BaseModelTypeVar

## [v0.2.5] - 2025-05-25

- Add custom LLM integration via OpenAI sdk with custom base_url

## [v0.2.4] - 2025-05-25

- Tidy tools
- Tidy inference API plugins
- Tidy WIP feature ActivityManager
- Replace license ELv2 by MIT and remove Reuse dependency

## [v0.2.2] - 2025-05-22

- Simplify the use of native concepts
- Include "page views" in the outputs of Ocr features

## [v0.2.1] - 2025-05-22

- Added OcrWorkerAbstract and MistralOcrWorker, along with PipeOcr for OCR processing of images and PDFs.
- Introduced MissionManager for managing missions, cost reports, and activity tracking.
- Added detection and handling for pipe stack overflow, configurable with pipe_stack_limit.
- More possibilities for dependency injection and better class structure.
- Misc updates including simplified PR template, LLM deck overrides, removal of unused config vars, and disabling of an LLM platform id.

## [v0.2.0] - 2025-05-19

- Added OCR, thanks to Mistral
- Refactoring and cleanup

## [v0.1.14] - 2025-05-13

- Initial release 🎉
