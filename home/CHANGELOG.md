# Changelog for `home` app

## [Unreleased]

### Fixed

- Recent live pages not showing up in `AppLandingPage`. 
[#17](https://git.bebif.be/antabif/biodiversityaq/issues/17) ([ymgan](https://git.bebif.be/ymgan))

### Added 

- Different size and alignment options when inserting image in StreamField. 
[#12](https://git.bebif.be/antabif/biodiversityaq/issues/12) ([ymgan](https://git.bebif.be/ymgan))
- TableBlock for BaseMenuPage body. 
[#14](https://git.bebif.be/antabif/biodiversityaq/issues/14) ([ymgan](https://git.bebif.be/ymgan))
- Colour theme choices in all page models and footer. [#15](https://git.bebif.be/antabif/biodiversityaq/issues/15) 
([ymgan](https://git.bebif.be/ymgan))
- Styles for colour theme choices in all page templates and footer template. [#15](https://git.bebif.be/antabif/biodiversityaq/issues/15) 
([ymgan](https://git.bebif.be/ymgan))

### Removed

- Unregister right-aligned image in StreamField.
[#12](https://git.bebif.be/antabif/biodiversityaq/issues/12) ([ymgan](https://git.bebif.be/ymgan))
- pdf-icon feature from Draftail editor. [#8](https://git.bebif.be/antabif/biodiversityaq/issues/8), 
[#14](https://git.bebif.be/antabif/biodiversityaq/issues/14) ([ymgan](https://git.bebif.be/ymgan))
- old hard coded footer template that is no longer in used. ([ymgan](https://git.bebif.be/ymgan))


## [0.2.0](https://gitlab.com/ymgan/biodiversity-aq-dev/-/releases/v0.2.0) - 2020-04-23

### Added

- `LinkPage` (a subclass of [AbstractLinkPage](https://wagtailmenus.readthedocs.io/en/stable/abstractlinkpage.html)) 
will be used to link to a page in the page tree. 
[#9](https://git.bebif.be/antabif/biodiversityaq/issues/9) ([ymgan](https://git.bebif.be/ymgan))
- CC BY 3.0 license for images. 
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Add `pdf-icon` feature to Draftail editor. 
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))

### Fixed

- Only load `scrolling-navbar` in AppLandingPage and DetailPage. 
[#4](https://git.bebif.be/antabif/biodiversityaq/issues/4), [#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) 
([ymgan](https://git.bebif.be/ymgan))
- Load dropdown options to wagtail cms and django admin interface when user is superuser. 
[#6](https://git.bebif.be/antabif/biodiversityaq/issues/6) ([ymgan](https://git.bebif.be/ymgan))
- URLs not redirecting properly to root page. All hard coded urls are replaced using `{% url %}` or `{% pageurl %}` 
tag in base template. [#6](https://git.bebif.be/antabif/biodiversityaq/issues/6) ([ymgan](https://git.bebif.be/ymgan))
- Fix card cover images shrink/max out when screen resize. 
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Image attribution generation when caption is not provided. 
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Always show menus in home page. 
[#10](https://git.bebif.be/antabif/biodiversityaq/issues/10) ([ymgan](https://git.bebif.be/ymgan))
- OverviewPage is now left-aligned.
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Pin pages in OverviewPage and AppLandingPage are now centered and max 3 cards per row.
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Use specific submenu templates. 
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))

### Changed

- Show page title in `app_landing_page.html`. 
[#5](https://git.bebif.be/antabif/biodiversityaq/issues/5) ([ymgan](https://git.bebif.be/ymgan))
- Rename menu templates in `biodiversity/templates/menus/`. ([ymgan](https://git.bebif.be/ymgan))
- Change block name for menus in `biodiversity/templates/base.html` ([ymgan](https://git.bebif.be/ymgan))
- Upgrade packages: `Django==2.2.12`, `wagtail==2.7.2`
- Recent pages only shown in AppLandingPage, no longer shown in OverviewPage.
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Rename `show_in_parent` to `show_in_recent` for BaseMenuPage.
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Remove word `pinned pages` from AppLandingPage
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))
- Full width cover image for DetailPage.
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))

### Removed

- old README.md from home app. 
[#8](https://git.bebif.be/antabif/biodiversityaq/issues/8) ([ymgan](https://git.bebif.be/ymgan))


## [0.1.3](https://gitlab.com/ymgan/biodiversity-aq-dev/-/releases/v0.1.3) - 2020-03-23

### Added
- Flat menu handle choices in `settings/base.py`. [#9](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/9) 
([ymgan](https://gitlab.com/ymgan))
- Flat menu template under `biodiversity/templates/menus/flat/level_1.html`. 
[#9](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/9) 
([ymgan](https://gitlab.com/ymgan))
- Flat menu block in project base template `biodiversity/templates/base.html` and `home` app base template. 
[#9](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/9) 
([ymgan](https://gitlab.com/ymgan))
- `django-filter` in `requirements.txt`.

### Changed
- Project css `biodiversity/static/css/main.css`. Smaller navbar brand, smaller header menu and hence smaller top 
padding for `body`. ([ymgan](https://gitlab.com/ymgan))

### Removed 
- Previous `header.html` which is no longer used.

### Fixed
- Site matching query does not exist for login link after user logged out. 
[#12](https://gitlab.com/ymgan/biodiversity-aq-dev/-/issues/12) 
([ymgan](https://gitlab.com/ymgan))

## [0.1.2](https://gitlab.com/ymgan/biodiversity-aq-dev/-/releases/v0.1.2) - 2020-03-18

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
