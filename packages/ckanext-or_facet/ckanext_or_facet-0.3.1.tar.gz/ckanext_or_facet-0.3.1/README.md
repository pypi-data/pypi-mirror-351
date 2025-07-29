[![Tests](https://github.com/DataShades/ckanext-or_facet/actions/workflows/test.yml/badge.svg?branch=master)](https://github.com/DataShades/ckanext-or_facet/actions)


# ckanext-or_facet


Change logic of applying facets. With a bit of extra configuration, search for
datasets, including **any** of applied facets, not necessary **all** of them


## Installation


To install ckanext-or-facet:

1. Install the ckanext-or_facet Python package:
   ```sh
   pip install ckanext-or-facet
   ```


1. Add ``or_facet`` to the ``ckan.plugins`` setting in CKAN config file

1. **Starting from CKAN v2.10.4**: Add ``ckan.search.solr_allowed_query_parsers =
   edismax bool`` to CKAN config file




## Config Settings
```ini
# List of facets that are using OR when applied.
# (optional, default: empty list).
ckanext.or_facet.optional = tags res_format
```
