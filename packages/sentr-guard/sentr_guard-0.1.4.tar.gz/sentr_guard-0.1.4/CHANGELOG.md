# Changelog

All notable changes to sentr-guard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2024-12-19

### Changed
- Updated README.md with improved project description
- Enhanced documentation and changelog

## [0.1.3] - 2025-5-28

### Changed
- Package renamed from "sentr-fraud" to "sentr-guard" for PyPI publication
- Updated all documentation and CLI references
- Infrastructure optimizations completed with Unix domain socket support

### Added
- Complete infrastructure optimization guide (INFRASTRUCTURE_OPTIMIZATIONS.md)
- Unix domain socket support for 80-120µs performance improvement
- Production deployment configurations for Docker/Kubernetes/Helm

## [0.1.2] - 2025-5-25

### Added
- Lightweight rules engine with sub-millisecond evaluation
- CLI commands: `sentr version`, `sentr status`, `sentr rules`
- Component availability checking with graceful fallbacks
- Minimal dependencies (PyYAML, Typer) for core functionality

### Changed
- Simplified package to rules engine only (removed heavy dependencies)
- Package renamed from "sentr" to "sentr-fraud" for PyPI compatibility
- Optimized for 4-5µs evaluation time (225x better than 1ms SLA)

### Fixed
- Performance test thresholds adjusted for development environment
- Import handling for optional components

## [0.1.1] - 2024-5-22

### Fixed
- Pydantic-settings dependency conflicts
- Import issues with prometheus components

## [0.1.0] - 2025-5-18

### Added
- Initial release with full fraud detection system
- FastAPI middleware integration
- Redis-based feature store with sliding windows
- Comprehensive monitoring and metrics
- Docker/Kubernetes deployment support

### Performance
- Rules evaluation: 4.4µs P95 latency
- Total system latency: ~1ms including infrastructure
- Throughput: 1k+ TPS with scaling potential 