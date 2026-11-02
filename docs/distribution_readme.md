# Probability of Us 0.1.0

This is a Windows x64 one-folder application. Run `ProbabilityOfUs.exe` from this directory and keep the `_internal` directory beside it. No installer or administrator access is required.

The bundled birth-count data is synthetic teaching data, not a demographic estimate. Import a documented CSV before interpreting a real-world demographic probability. Meeting and relationship probabilities stay unknown unless you enter explicit assumptions.

The application works offline. It stores scenarios and imported datasets under `%LOCALAPPDATA%\ProbabilityOfUs`. Read `docs/user_guide.md`, `docs/mathematical_model.md`, `docs/privacy.md`, and `docs/limitations.md` before using or sharing results.

This build was smoke-tested on Windows 11 using Qt's offscreen platform. It is unsigned and has not been tested on a clean Windows VM.
