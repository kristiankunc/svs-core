# Changelog

## [0.10.1](https://github.com/kristiankunc/svs-core/compare/v0.10.0...v0.10.1) (2025-12-30)


### Bug Fixes

* Call verbose setup earlier in CLI bootstrap ([c65b94e](https://github.com/kristiankunc/svs-core/commit/c65b94ea0db6a551dc40b08495592b946995f0e6))

## [0.10.0](https://github.com/kristiankunc/svs-core/compare/v0.9.1...v0.10.0) (2025-12-30)


### Features

* Add reverse proxy configuration ([#157](https://github.com/kristiankunc/svs-core/issues/157)) ([4c45355](https://github.com/kristiankunc/svs-core/commit/4c453552bcc8a04c18ba542edcd34b6b1a5583f5))
* Add service rebuilding support ([#176](https://github.com/kristiankunc/svs-core/issues/176)) ([9d1b672](https://github.com/kristiankunc/svs-core/commit/9d1b6722a7794d9f8e6276baa7083ac7ac1a3fcb))
* Migrate documentation build from MkDocs to Zensical ([#190](https://github.com/kristiankunc/svs-core/issues/190)) ([8906e0c](https://github.com/kristiankunc/svs-core/commit/8906e0c1dcf98c9225f8bd89152a9e350c695f9f))


### Bug Fixes

* Add adminer template ([#151](https://github.com/kristiankunc/svs-core/issues/151)) ([7fd3b7d](https://github.com/kristiankunc/svs-core/commit/7fd3b7d047f7f3f02d6b02b5fab149feb977593b))
* Add CLI logs command ([#174](https://github.com/kristiankunc/svs-core/issues/174)) ([1f300ff](https://github.com/kristiankunc/svs-core/commit/1f300ff8e03c6a3edd066664aa2812bb7ca4b603))
* Add tables to CLI output ([#155](https://github.com/kristiankunc/svs-core/issues/155)) ([49fe7f3](https://github.com/kristiankunc/svs-core/commit/49fe7f35963f6759a4c9ddc2abf7805c037d6ccf))
* Ensure docker images are deleted when BUILD service is deleted ([520da75](https://github.com/kristiankunc/svs-core/commit/520da7586eabbd1513a3fdf3f0360f07392c6c9b))
* Fix django template ([#169](https://github.com/kristiankunc/svs-core/issues/169)) ([bb0d850](https://github.com/kristiankunc/svs-core/commit/bb0d85056b254f67d1ea0f7c1882af80ebd8b196))
* Fix system username getter if svs ran via sudo/su ([#159](https://github.com/kristiankunc/svs-core/issues/159)) ([3746d3a](https://github.com/kristiankunc/svs-core/commit/3746d3af39445ca815028de68c369496bef264fe))
* Force set caddy network name in install script ([#161](https://github.com/kristiankunc/svs-core/issues/161)) ([d7e0b92](https://github.com/kristiankunc/svs-core/commit/d7e0b9238d0c56b11ce53d347a8495c8c452d049))

## [0.9.1](https://github.com/kristiankunc/svs-core/compare/v0.9.0...v0.9.1) (2025-12-08)


### Bug Fixes

* Add comprehensive logging throughout Docker operations, user management, and templates ([#144](https://github.com/kristiankunc/svs-core/issues/144)) ([6627e53](https://github.com/kristiankunc/svs-core/commit/6627e534f44d92e6732f991532f84762111ec7e8))
* Ensure unique docker container names ([#145](https://github.com/kristiankunc/svs-core/issues/145)) ([ff4f3e5](https://github.com/kristiankunc/svs-core/commit/ff4f3e57be9228d1d012fd4b57bf1b11aebf01b2))

## [0.9.0](https://github.com/kristiankunc/svs-core/compare/v0.8.1...v0.9.0) (2025-12-07)


### Features

* Add default volume contents ([#126](https://github.com/kristiankunc/svs-core/issues/126)) ([920d176](https://github.com/kristiankunc/svs-core/commit/920d176d8357f665a6930bfaed86ead267363033))


### Bug Fixes

* Add spinning loaders to long commands ([#127](https://github.com/kristiankunc/svs-core/issues/127)) ([148f330](https://github.com/kristiankunc/svs-core/commit/148f330a99b812efa249bbc2e3384d870a3c020b))
* Fix volume permission errors ([#134](https://github.com/kristiankunc/svs-core/issues/134)) ([2479751](https://github.com/kristiankunc/svs-core/commit/247975196b849c8d69275c5ceb33ef0e9c5ac82e))
* Use null handler if logfile not found ([4abfaa5](https://github.com/kristiankunc/svs-core/commit/4abfaa5bf97fc82c1e6299f16684a697b35bf554))

## [0.8.1](https://github.com/kristiankunc/svs-core/compare/v0.8.0...v0.8.1) (2025-11-29)


### Bug Fixes

* update service create command for 0.8 ([f3d4f29](https://github.com/kristiankunc/svs-core/commit/f3d4f2972a3d494c5bf01f72ccfbbe878bfd5ece))

## [0.8.0](https://github.com/kristiankunc/svs-core/compare/v0.7.1...v0.8.0) (2025-11-29)


### Features

* Add cli version ([#115](https://github.com/kristiankunc/svs-core/issues/115)) ([bd14d74](https://github.com/kristiankunc/svs-core/commit/bd14d7425e68a9d0bb711ffb687c2c13bea288a2))
* Add mysql template ([#113](https://github.com/kristiankunc/svs-core/issues/113)) ([1cd0d48](https://github.com/kristiankunc/svs-core/commit/1cd0d48b78da890edb68bb63f77a09c361c97c7c))
* Add SSH key management ([#111](https://github.com/kristiankunc/svs-core/issues/111)) ([ff20953](https://github.com/kristiankunc/svs-core/commit/ff2095388325eb8dfc5ff62a23b11e27cc443b60))
* Add verbose cli option ([#116](https://github.com/kristiankunc/svs-core/issues/116)) ([0c2c617](https://github.com/kristiankunc/svs-core/commit/0c2c617b9829b427c5ef4d0da71b417eab7e4b58))
* Remove user args from commands, allow admin override ([#120](https://github.com/kristiankunc/svs-core/issues/120)) ([d1f83d7](https://github.com/kristiankunc/svs-core/commit/d1f83d7b97283d16d3219695f1f0c5eb68a986f1))


### Bug Fixes

* Add full internal docs ([2db2398](https://github.com/kristiankunc/svs-core/commit/2db2398f4feb9df06a0554123184e9ad3312fac4))
* create default user with bash shell ([#110](https://github.com/kristiankunc/svs-core/issues/110)) ([aab42b6](https://github.com/kristiankunc/svs-core/commit/aab42b675df56ee70ac22a94bbe57c7d0f43c6b5))
* Fix system username detection to use effective user instead of SUDO_USER ([#122](https://github.com/kristiankunc/svs-core/issues/122)) ([e96cff9](https://github.com/kristiankunc/svs-core/commit/e96cff99f54f978d574e7c5f81d62e1d85a744b7))
* Remove emojis from CLI ([#117](https://github.com/kristiankunc/svs-core/issues/117)) ([07b21e4](https://github.com/kristiankunc/svs-core/commit/07b21e4aa336889fa80a1e0b68e94d5a90551b64))
* Stop loading .env file in dev ([d3afa1f](https://github.com/kristiankunc/svs-core/commit/d3afa1fe01e70dfa34b0d7d90aa3a37dfea8c14f))
* Use -v for verbose instead of version ([19b6711](https://github.com/kristiankunc/svs-core/commit/19b6711bc3b40c555552492d247460d5f6479fa2))
* Use adduser for system user creation ([b6bd7c4](https://github.com/kristiankunc/svs-core/commit/b6bd7c49198926c7addd8175dadbdada2b9a0a77))

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
