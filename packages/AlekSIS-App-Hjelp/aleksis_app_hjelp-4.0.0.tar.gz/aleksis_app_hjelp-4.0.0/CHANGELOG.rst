Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

`4.0.0`_ - 2025-03-30
---------------------

This version requires AlekSIS-Core 4.0. It is incompatible with any previous
version.

Added
~~~~~

* Menu icon changes when entry is selected.

Fixed
~~~~~

* Menu item was shown although the user had no permission to use support functions.

`3.0`_ - 2023-05-14
-------------------

Fixed
~~~~~

* Icons in the FAQ were not rendered

`3.0b0`_ - 2023-02-22
---------------------

This version requires AlekSIS-Core 3.0. It is incompatible with any previous
version.

Removed
~~~~~~~

* Legacy menu integration for AlekSIS-Core pre-3.0


Added
~~~~~

* Support for SPA in AlekSIS-Core 3.0

`2.1`_ - 2022-06-25
-------------------

Added
~~~~~

* Add Ukrainian locale (contributed by Sergiy Gorichenko from Fre(i)e Software GmbH).

Changed
~~~~~~~

* Update icon choices for user-selectable icons with new Iconify iicon font.

`2.0.2`_ - 2022-01-16
-------------------

Fixed
~~~~~

* Add documentation.

`2.0.1`_ - 2022-01-04
---------------------

Fixed
~~~~~

* get_next_properties() is erroneously called when an issue report dropdown gets cleared

`2.0`_ - 2021-10-30
-------------------

Changed
~~~~~~~

* German translations were updated.

`2.0rc3`_ - 2021-08-17
----------------------

Fixed
~~~~~

* Get next properties in issue form not by the non-unique category name but
  by the unique id.

`2.0rc2`_ - 2021-06-26
----------------------

Fixed
~~~~~

* Migration for uniqueness per site was broken due to wrong syntax.

`2.0rc1`_ - 2021-06-23
----------------------

Fixed
~~~~~

* Include parents in unique key of FAQ sections for site and category.


`2.0b1`_ - 2021-06-02
---------------------

Changed
~~~~~~~~

* Ensure uniqueness per site of FAQ sections and categories with parents.


`2.0b0`_ - 2021-05-21
---------------------

Added
~~~~~

* FAQ sections and questions can now be edited in the frontend.
* FAQ sections and questions can now be sorted.

Changed
~~~~~~~

* Hjelp's menu items are now filtered with permissions.
* Ratings don't default to one star anymore.
* Forms aren't cached by the PWA anymore.

Fixed
~~~~~

* Issue categories weren't saved correctly.
* Mail templates weren't translated and formatted correctly.
* The Hjelp icon inside the menu changed it's name and was therefore displayed incorrectly.

`2.0a2`_ - 2020-05-04
---------------------

Added
~~~~~

* Ask questions
* Feedback
* Frequently asked questions
* Report issues


.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. _2.0a2: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0a2
.. _2.0b0: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0b0
.. _2.0b1: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0b1
.. _2.0rc1: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0rc1
.. _2.0rc2: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0rc2
.. _2.0rc3: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0rc3
.. _2.0: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0
.. _2.0.1: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0.1
.. _2.0.2: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.0.2
.. _2.1: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/2.1
.. _3.0b0: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/3.0b0
.. _3.0: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/3.0
.. _4.0.0: https://edugit.org/AlekSIS/Official/AlekSIS-App-Hjelp/-/tags/4.0.0
