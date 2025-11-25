# Changelog

## [0.7.1](https://github.com/kristiankunc/svs-core/compare/v0.7.0...v0.7.1) (2025-11-25)


### Bug Fixes

* Properly load ENV variables, add override options for ENV variables ([#108](https://github.com/kristiankunc/svs-core/issues/108)) ([9906cc4](https://github.com/kristiankunc/svs-core/commit/9906cc47c97aba3e9b4d376faa6bfa79dbdf90e7))

## [0.7.0](https://github.com/kristiankunc/svs-core/compare/v0.6.2...v0.7.0) (2025-11-25)


### Features

* Add service building ([#100](https://github.com/kristiankunc/svs-core/issues/100)) ([2483706](https://github.com/kristiankunc/svs-core/commit/24837066c05233ce9b1d049e4369ebf79fddcb10))


### Bug Fixes

* Improve install script ([03f381e](https://github.com/kristiankunc/svs-core/commit/03f381eeef517e42cf56eea3715590b060c3f8b5))
* Test install script ([#107](https://github.com/kristiankunc/svs-core/issues/107)) ([fb3ab9a](https://github.com/kristiankunc/svs-core/commit/fb3ab9a6869f752cd7d6aedea33a665bfede10da))

## [0.6.2](https://github.com/kristiankunc/svs-core/compare/v0.6.1...v0.6.2) (2025-11-13)


### Bug Fixes

* Add override params for CLI service creation ([#97](https://github.com/kristiankunc/svs-core/issues/97)) ([05a95cf](https://github.com/kristiankunc/svs-core/commit/05a95cf56b13a027c1af77586a5a39f42e28aa86))
* Silently pull/remove Docker images ([#99](https://github.com/kristiankunc/svs-core/issues/99)) ([a2bd4c8](https://github.com/kristiankunc/svs-core/commit/a2bd4c893d22634b3ea27e9c8f869d2259329daf))

## [0.6.1](https://github.com/kristiankunc/svs-core/compare/v0.6.0...v0.6.1) (2025-11-12)


### Bug Fixes

* Load .env file manually ([9389108](https://github.com/kristiankunc/svs-core/commit/9389108acbf6c45bd3a8678458662315ab45040d))

## [0.6.0](https://github.com/kristiankunc/svs-core/compare/v0.5.0...v0.6.0) (2025-11-10)


### Features

* Rework json props once again ([#83](https://github.com/kristiankunc/svs-core/issues/83)) ([f0e5a1c](https://github.com/kristiankunc/svs-core/commit/f0e5a1cc409080e7ddea479c43ed46008d1b8cd4))


### Bug Fixes

* Fix volume creation permissions ([#84](https://github.com/kristiankunc/svs-core/issues/84)) ([d8bd47d](https://github.com/kristiankunc/svs-core/commit/d8bd47d9c7449f856caad8025572e10e4a60f920))
* Properly mount service volumes ([93d8127](https://github.com/kristiankunc/svs-core/commit/93d8127e6635feb09b0d83a5316286048a786ca4))
* Use host volume as key in json props ([81a1a02](https://github.com/kristiankunc/svs-core/commit/81a1a02fb9f407c65ddbd26f642f6f2d457e67e2))
* Use template id to identify templates in cli ([040eccb](https://github.com/kristiankunc/svs-core/commit/040eccbeccf0211323c4e03b4b9fe56e899424b7))

## [0.5.0](https://github.com/kristiankunc/svs-core/compare/v0.4.1...v0.5.0) (2025-11-01)


### Features

* Consolidate Docker image name and tags into a single param ([3b56629](https://github.com/kristiankunc/svs-core/commit/3b566295ec432d10dcb4899a9fbb8c28614dcd4f))


### Bug Fixes

* Add service log obtaining ([50868d5](https://github.com/kristiankunc/svs-core/commit/50868d5837116ff4b88cbdffdbc8d64e2705f8cb))

## [0.4.1](https://github.com/kristiankunc/svs-core/compare/v0.4.0...v0.4.1) (2025-10-31)


### Bug Fixes

* Allow custom python path passing in install script ([d247093](https://github.com/kristiankunc/svs-core/commit/d24709375a7ba4cfdc00c3c20d2a858e860bb562))

## [0.4.0](https://github.com/kristiankunc/svs-core/compare/v0.3.2...v0.4.0) (2025-10-30)


### Features

* Implement service parameter overrides ([#68](https://github.com/kristiankunc/svs-core/issues/68)) ([9ad0f8e](https://github.com/kristiankunc/svs-core/commit/9ad0f8e283516238c8caf2c66f5563eee5e42bd6))
* Refactor JSON db fields handling ([#58](https://github.com/kristiankunc/svs-core/issues/58)) ([ff99cc3](https://github.com/kristiankunc/svs-core/commit/ff99cc33184f5b9a2d1ffbdbba431cf846eb1924))


### Bug Fixes

* Overhaul json props ([#55](https://github.com/kristiankunc/svs-core/issues/55)) ([66f1706](https://github.com/kristiankunc/svs-core/commit/66f1706458016ab4ebf74e1de6abe97cfca6d87a))
* Remove internal Docker APIs from docs ([6e845d0](https://github.com/kristiankunc/svs-core/commit/6e845d028edd1a0081019a9eda7f004055a15080))
* Use proper permissions for volume management ([#57](https://github.com/kristiankunc/svs-core/issues/57)) ([33855d5](https://github.com/kristiankunc/svs-core/commit/33855d5c3481a546809917e08904a0a08e52dbe8))

## [0.3.2](https://github.com/kristiankunc/svs-core/compare/v0.3.1...v0.3.2) (2025-10-29)


### Bug Fixes

* fix typo in install script ([e92945b](https://github.com/kristiankunc/svs-core/commit/e92945babf107d3bfaa20629cdba7c2d7b496e12))

## [0.3.1](https://github.com/kristiankunc/svs-core/compare/v0.3.0...v0.3.1) (2025-10-27)


### Bug Fixes

* Add system user testing ([#46](https://github.com/kristiankunc/svs-core/issues/46)) ([608d527](https://github.com/kristiankunc/svs-core/commit/608d527b91943cdf395a14647b7fda0bea87f224))
* Add template delete functionality ([#52](https://github.com/kristiankunc/svs-core/issues/52)) ([c7cdaed](https://github.com/kristiankunc/svs-core/commit/c7cdaed51c744028580596e8e9245d9f2311282b))

## [0.3.0](https://github.com/kristiankunc/svs-core/compare/v0.2.0...v0.3.0) (2025-10-24)


### Features

* Env Manager overhaul, install script ([#41](https://github.com/kristiankunc/svs-core/issues/41)) ([735dab2](https://github.com/kristiankunc/svs-core/commit/735dab2b76e872e6384cb4db2281d632ecfdccf6))


### Bug Fixes

* Deprecate db-based service status ([#45](https://github.com/kristiankunc/svs-core/issues/45)) ([2f0b81e](https://github.com/kristiankunc/svs-core/commit/2f0b81e8fc9986f56a94a88b3f1e3a83a78e6903))
* improve docstring formatting ([#44](https://github.com/kristiankunc/svs-core/issues/44)) ([a2fd0f1](https://github.com/kristiankunc/svs-core/commit/a2fd0f1b014a42fab0eaff5b35ee35ff3bea90b6))

## [0.2.0](https://github.com/kristiankunc/svs-core/compare/v0.1.0...v0.2.0) (2025-10-22)


### Features

* add user CLI ([2314121](https://github.com/kristiankunc/svs-core/commit/2314121eeecbfa8ce4387f10b372493f683d4911))

## 0.1.0 (2025-10-22)


### Features

* add ci workflows for release-please and publishing ([#38](https://github.com/kristiankunc/svs-core/issues/38)) ([6c612a0](https://github.com/kristiankunc/svs-core/commit/6c612a0de664d6753e4133392d979599682745ff))


### Bug Fixes

* delete invalid arg for release-please ([960cfdc](https://github.com/kristiankunc/svs-core/commit/960cfdc352c66d1217f43f70c5085ca6394f2409))
