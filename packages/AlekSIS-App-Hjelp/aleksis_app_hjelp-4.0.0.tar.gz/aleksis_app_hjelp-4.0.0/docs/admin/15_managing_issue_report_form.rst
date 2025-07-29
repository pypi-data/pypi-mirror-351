Managing issue report form
==========================

The Hjelp issue reporting system lets the operator categorize issues in a three-level model,
whereby the used categories become more concrete from the first to the third level.
Every category except the first-level ones that is created therefore has to refer to a so-called parent,
of which it is a subcategory.

Creating and managing categories is done in the backend admin
interface under *AlekSIS — Hjelp (Support) → Issue categories*.

.. image:: ../_static/issue_categories.png
  :width: 100%
  :alt: View for managing issue categories

Upon using the *Add issue category* button, a form is displayed which contains
all alterable attributes of the to-be category.

The *Name* textbox contains the text displayed when the given category is shown;
and by means of the *Parent category* dropdown select list,
a parent category can be selected. In case no parent category is specified,
the created category is on first level.

If the *Free text input allowed* checkbox is selected,
all possible children of the newly created category are ignored and instead,
a free text input is displayed upon selection on the next level.
One possible use case may be that the location of the selected issue has to be specified.

Special attention has to be paid to the *Icon* and *Placeholder* options as they refer
to the category select dropdown/free text input of the next level.
All icons that can be selected are again located on `Material Icons`_.

.. image:: ../_static/issue_category.png
  :width: 100%
  :alt: Issue category form

.. _Material Icons: https://material.io/resources/icons/
