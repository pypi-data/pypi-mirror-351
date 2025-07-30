=====================
django-rijkshuisstijl
=====================

Rijkshuisstijl boilerplate for Django.

:Version: 0.2.0
:Source: https://github.com/maykinmedia/django-rijkshuisstijl
:Keywords: ``Django, rijkshuisstijl``
:PythonVersion: 3.11


.. contents::

.. section-numbering::

Features
========

* Basic rijkshuisstijl (Dutch government branding) layout including headers, footer, buttons, forms and more.
* Modular setup using inclusion tags.
* Responsive

Installation
============

Requirements
------------

* Python 3.6 or above
* setuptools 30.3.0 or above
* Django 1.11 or above


Install
-------

Install from PyPI with pip:

.. code-block:: bash

    pip install django-rijkshuisstijl


Then add "rijkshuisstijl" and "sitetree" to INSTALLED_APPS.

Usage
=====

Add CSS/JS/icons to your main template:

.. code-block:: html

    {% load rijkshuisstijl %}
    <!DOCTYPE html>
    <html lang="nl" class="views">
    <head>
        {% meta_css %}
        {% meta_icons %}
    </head>
    <body class="view__body">
        {% meta_js %}
    </body>

Then add the basic structure, supply the current urls for various urls (depending on your project):

.. code-block:: html

    {% load rijkshuisstijl %}
    <!DOCTYPE html>
    <html lang="nl" class="views">
    <head>
        {% meta_css %}
        {% meta_icons %}
    </head>
    <body class="view__body">
        {% skiplink %}
        {% login_bar details_url='#' logout_url='#' login_url='#' registration_url='#' %}
        {% header %}
        {% navigation_bar details_url='#' logout_url='#' login_url='#' registration_url='#' %}

        <main class="view__content">
            {% skiplink_target %}
        </main>

        {% footer %}
        {% meta_js %}
    </body>

See the documentation for further information about logos, navigation, forms and datagrids.
