.. This README is meant for consumption by humans and PyPI. PyPI can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on PyPI or github. It is a comment.

.. image:: https://github.com/collective/iosanita.policy/actions/workflows/plone-package.yml/badge.svg
    :target: https://github.com/collective/iosanita.policy/actions/workflows/plone-package.yml

.. image:: https://coveralls.io/repos/github/collective/iosanita.policy/badge.svg?branch=main
    :target: https://coveralls.io/github/collective/iosanita.policy?branch=main
    :alt: Coveralls

.. image:: https://codecov.io/gh/collective/iosanita.policy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/collective/iosanita.policy

.. image:: https://img.shields.io/pypi/v/iosanita.policy.svg
    :target: https://pypi.python.org/pypi/iosanita.policy/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/status/iosanita.policy.svg
    :target: https://pypi.python.org/pypi/iosanita.policy
    :alt: Egg Status

.. image:: https://img.shields.io/pypi/pyversions/iosanita.policy.svg?style=plastic   :alt: Supported - Python Versions

.. image:: https://img.shields.io/pypi/l/iosanita.policy.svg
    :target: https://pypi.python.org/pypi/iosanita.policy/
    :alt: License


================
IO-Sanita policy
================

Policy per il backend dei portali Io-Sanita.

Questo pacchetto si occupa di installare tutte le dipendenze necessarie per il progetto.


Rotte API
=========

@search-tassonomie
------------------

Endpoint che serve a ricercare i contenuti marcati da una determinata tassonomia.

Parametri:

- **type** (obbligatorio): il nome dell'indice in catalogo della tassonomia
- **value**: un eventuale valore per filtrare l'indice
- **portal_type**: un filtro su uno specifico portal_type
- **sort_on**: permette di ordinare i risultati in base ad un determinato indice
- **sort_order**: permette di scegliere l'ordinamento da usare

Le tassonomie (*type*) utilizzabili sono limitate:

- parliamo_di
- a_chi_si_rivolge_tassonomia

Esempio di chiamata::

    > http://localhost:8080/Plone/++api++/@search-tassonomie?type=a_chi_si_rivolge_tassonomia


Risposta::

    {
        "@id": "http://localhost:8080/Plone/++api++/@search-tassonomie?type=a_chi_si_rivolge_tassonomia",
        "facets": {
            "portal_types": [
                {
                    "title": "Struttura",
                    "token": "Struttura"
                }
            ]
        },
        "items": [
            {
            "@id": "http://localhost:8080/Plone/struttura",
            "@type": "Struttura",
            "description": "",
            "enhanced_links_enabled": null,
            "getObjSize": "0 KB",
            "image_field": "",
            "image_scales": null,
            "mime_type": "text/plain",
            "review_state": "private",
            "title": "struttura",
            "type_title": "Struttura"
            }
        ],
        "items_total": 1
    }

Installazione
=============

Per installare iosanita.policy bisogna per prima cosa aggiungerlo al buildout::

    [buildout]

    ...

    eggs =
        iosanita.policy


e poi lanciare il buildout con ``bin/buildout``.

Successivamente va installato dal pannello di controllo di Plone.


Contribuisci
============

- Issue Tracker: https://github.com/redturtle/iosanita.policy/issues
- Codice sorgente: https://github.com/redturtle/iosanita.policy


Licenza
=======

Questo progetto è rilasciato con licenza GPLv2.

Autori
======

Questo progetto è stato sviluppato da **RedTurtle Technology**.

.. image:: https://avatars1.githubusercontent.com/u/1087171?s=100&v=4
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
