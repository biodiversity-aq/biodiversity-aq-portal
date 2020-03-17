# Changelog

## [Unreleased]

### Added
- A BooleanField in abstract class BaseMenuPage to indicate if a page should appear as card in parent page if 
parent page type is a OverviewPage or AppLandingPage. 
[#8](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/8)  ([ymgan](https://gitlab.com/ymgan))
- A StreamField with PageChooserBlock for user to indicate which pages should be pinned in OverviewPage or 
AppLandingPage. 
[#10](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/10)  ([ymgan](https://gitlab.com/ymgan))

### Changed
- OverviewPage template only renders child pages which has `show_in_parent` set to `True`. 
[#8](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/8)  ([ymgan](https://gitlab.com/ymgan))
- AppLandingPage template only renders **descendant** pages which has `show_in_parent` set to `True`. 
[#8](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/8)  ([ymgan](https://gitlab.com/ymgan))
- OverviewPage and AppLandingPage template to render pinned pages. 
[#10](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/10)  ([ymgan](https://gitlab.com/ymgan))
- OverviewPage and `AppLandingPage template only render max 6 most recent pages. 
[#6](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/6), 
[#7](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/7) ([ymgan](https://gitlab.com/ymgan))


## [0.1.1](https://gitlab.com/ymgan/biodiversity-aq-dev/-/releases/v0.1.1) - 2020-03-13

### Added
- missing packages in [requirements.txt](requirements.txt). ([ymgan](https://gitlab.com/ymgan))
- documentation for Editors. [#1](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/1) ([ymgan](https://gitlab.com/ymgan))
- external url field for LinkedButton snippet. [#3](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/3) ([ymgan](https://gitlab.com/ymgan))
- this Changelog ([ymgan](https://gitlab.com/ymgan))

### Removed
- [custom.css](biodiversity/static/css/custom.css) file where styles in used are moved to 
[main.css](biodiversity/static/css/main.css) in previous release. ([ymgan](https://gitlab.com/ymgan))

### Fixed
- Hyperlink footer logo to its url. [#2](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/2) ([ymgan](https://gitlab.com/ymgan))
- Fix link of child page's cover image in OverviewPage. ([ymgan](https://gitlab.com/ymgan))
- Fix huge padding-bottom for embedded video. [#4](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/4) ([ymgan](https://gitlab.com/ymgan))

## [0.1](https://gitlab.com/ymgan/biodiversity-aq-dev/-/releases/v0.1) - 2020-03-12

Initial release.
