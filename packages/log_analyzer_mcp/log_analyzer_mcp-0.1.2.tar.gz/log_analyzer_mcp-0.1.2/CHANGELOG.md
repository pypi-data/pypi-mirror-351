# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-05-28

**Changed**:

- Refactored `AnalysisEngine` to improve log file discovery, filtering logic (time, positional, content), and context extraction.
- Updated `ConfigLoader` for robust handling of `.env` configurations and environment variables, including list parsing and type conversions.
- Enhanced `test_log_parser.py` with refined regexes for `pytest` log analysis.
- Implemented new MCP search tools (`search_log_all_records`, `search_log_time_based`, `search_log_first_n_records`, `search_log_last_n_records`) in `log_analyzer_mcp_server.py` using `AnalysisEngine`.
- Updated Pydantic models for MCP tools to use default values instead of `Optional`/`Union`.
- Developed `log_analyzer_client/cli.py` with `click` for command-line access to log search functionalities, mirroring MCP tools.
- Added comprehensive tests for `AnalysisEngine` in `tests/log_analyzer_mcp/test_analysis_engine.py`, achieving high coverage for core logic.
- Refactored `_run_tests` in `log_analyzer_mcp_server.py` to use `hatch test` directly, save full log output, and manage server integration test recursion.
- Improved `create_coverage_report` MCP tool to correctly invoke `hatch` coverage scripts and resolve environment/path issues, ensuring reliable report generation.
- Updated `pyproject.toml` to correctly define dependencies for `hatch` environments and scripts, including `coverage[toml]`.
- Streamlined build and release scripts (`scripts/build.sh`, `scripts/publish.sh`, `scripts/release.sh`) for better version management and consistency.

**Fixed**:

- Numerous test failures in `test_analysis_engine.py` related to path handling, filter logic, timestamp parsing, and assertion correctness.
- Issues with `create_coverage_report` MCP tool in `log_analyzer_mcp_server.py` failing due to `hatch` script command errors (e.g., 'command not found', `HATCH_PYTHON_PATH` issues).
- Corrected `anyio` related errors and `xfail` markers for unstable server session tests in `test_log_analyzer_mcp_server.py`.
- Addressed various Pylint warnings (e.g., `W0707`, `W1203`, `R1732`, `C0415`) across multiple files.
- Resolved `TypeError` in `_apply_positional_filters` due to `None` timestamps during sorting.

## [0.1.1] - 2025-05-27

**Changed**:

- Integrated `hatch` for project management, build, testing, and publishing.
- Refactored `pyproject.toml` with updated metadata, dependencies, and `hatch` configurations.
- Corrected internal import paths after moving from monorepo.
- Added `src/log_analyzer_mcp/common/logger_setup.py`.
- Replaced `run_all_tests.py` and `create_coverage_report.sh` with `hatch` commands.
- Refactored `log_analyzer_mcp_server.py` to use `hatch test` for its internal test execution tools.
- Updated test suite (`test_analyze_runtime_errors.py`, `test_log_analyzer_mcp_server.py`) for `pytest-asyncio` strict mode and improved assertions.
- Implemented subprocess coverage collection using `COVERAGE_PROCESS_START`, `coverage.process_startup()`, and `SIGTERM` handling, achieving >80% on server and improved coverage on other scripts.
- Added tests for `parse_coverage.py` (`test_parse_coverage_script.py`) and created `sample_coverage.xml`.
- Updated `log_analyzer.py` with more robust `pytest` summary parsing.
- Updated documentation: `docs/refactoring/log_analyzer_refactoring_v1.md`, `docs/refactoring/README.md`, main `README.md`, `docs/README.md`.
- Refactored scripts in `scripts/` folder (`build.sh`, `cleanup.sh`, `run_log_analyzer_mcp_dev.sh`, `publish.sh`, `release.sh`) to use `hatch` and modern practices.

**Fixed**:

- Numerous test failures related to timeouts, `anyio` task scope errors, `ImportError` for `TextContent`, and `pytest`/`coverage` argument conflicts.
- Code coverage issues for subprocesses.
- `TypeError` in `test_parse_coverage_xml_no_line_rate`.

## [0.1.0] - 2025-05-26

**Added**:

- Initial project structure for `log_analyzer_mcp`.
- Basic MCP server setup.
- Core log analysis functionalities.
