"""Tests for plugin.py."""
import pytest
import ckan.tests.helpers as helpers
import ckan.tests.factories as factories
import ckanext.or_facet.plugin as plugin


def _prepare_ors(field, fqs):
    return "{{!bool tag=orFq{} {}}}".format(
        field,
        " ".join(f"should='{fq}'" for fq in fqs),
    )


class TestConfig:
    def test_missing_config_parsed(self):
        assert plugin._get_default_ors() == []

    @pytest.mark.ckan_config("or_facet.or_facets", None)
    def test_empty_config_parsed(self):
        assert plugin._get_default_ors() == []

    @pytest.mark.ckan_config("or_facet.or_facets", "tags")
    def test_single_config_parsed(self):
        assert plugin._get_default_ors() == ["tags"]

    @pytest.mark.ckan_config("or_facet.or_facets", "tags res_format")
    def test_multiple_config_parsed(self):
        assert plugin._get_default_ors() == ["tags", "res_format"]


class TestExtraOrs:
    def test_base_case(self):
        extras = {
            "ext_a": 1,
            plugin._extra_or_prefix + "tags": "on",
            plugin._extra_or_prefix + "groups": "off",
        }
        assert plugin._get_extra_ors_state(extras) == {"tags": True, "groups": False}


class TestSplit:
    @pytest.mark.parametrize(
        ("fq", "field", "expected"),
        [
            (
                'tags:"Structural Framework"',
                "tags",
                ("{!bool tag=orFqtags should='tags:\"Structural Framework\"'}", ""),
            ),
            ("organization:123", "tags", (None, "organization:123")),
            ("", "tags", (None, "")),
            ("x:1", "x", (_prepare_ors("x", ["x:1"]), "")),
            ("x:hello x:world", "x", (_prepare_ors("x", ["x:hello", "x:world"]), "")),
            ("x:a y:b", "y", (_prepare_ors("y", ["y:b"]), "x:a")),
            ('x:"a" y:"b"', "y", (_prepare_ors("y", ['y:"b"']), 'x:"a"')),
            (
                "z:1 x:a z:2 x:\"b\" z:3 x:'c'",
                "x",
                (_prepare_ors("x", ["x:a", 'x:"b"', r"x:\'c\'"]), "z:1  z:2  z:3"),
            ),
            (
                "x-x:a-a y-y:b-b z-z:c-c",
                "x-x",
                (_prepare_ors("x-x", ["x-x:a-a"]), "y-y:b-b z-z:c-c"),
            ),
            (
                "x-x:a-a y-y:b-b z-z:c-c",
                "y-y",
                (_prepare_ors("y-y", ["y-y:b-b"]), "x-x:a-a  z-z:c-c"),
            ),
            (
                "x-x:a-a y-y:b-b z-z:c-c",
                "z-z",
                (_prepare_ors("z-z", ["z-z:c-c"]), "x-x:a-a y-y:b-b"),
            ),
        ],
    )
    def test_split(self, fq, field, expected):
        assert plugin._split_fq(fq, field) == expected


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
@pytest.mark.ckan_config("ckan.search.solr_allowed_query_parsers", "edismax bool")
class TestPlugin:
    @pytest.mark.ckan_config("or_facet.or_facets", "tags res_format")
    def test_search_with_two_ors(self, organization):
        expected_tags = {"bye": 1, "hello": 1, "world": 2}
        expected_formats = {"JSON": 1, "HTML": 1, "CSV": 2}

        d1 = factories.Dataset(tags=[{"name": "hello"}, {"name": "world"}])
        d2 = factories.Dataset(tags=[{"name": "bye"}, {"name": "world"}])

        factories.Resource(package_id=d1["id"], format="CSV")
        factories.Resource(package_id=d1["id"], format="JSON")
        factories.Resource(package_id=d2["id"], format="CSV")
        factories.Resource(package_id=d2["id"], format="HTML")

        for tag, count in expected_tags.items():
            result = helpers.call_action(
                "package_search",
                fl="id,tags",
                fq=f"tags:{tag}",
                **{"facet.field": '["tags"]'},
            )
            assert result["count"] == count
            assert result["facets"]["tags"] == expected_tags

        for fmt, count in expected_formats.items():
            result = helpers.call_action(
                "package_search",
                fq=f"res_format:{fmt}",
                **{"facet.field": '["res_format"]'},
            )
            assert result["count"] == count
            assert result["facets"]["res_format"] == expected_formats

    @pytest.mark.ckan_config("or_facet.or_facets", "tags")
    def test_search_with_one_or_and_one_extra_or(self):
        expected_tags = {"bye": 1, "hello": 1, "world": 2}
        expected_formats = {"JSON": 1, "HTML": 1, "CSV": 2}

        d1 = factories.Dataset(tags=[{"name": "hello"}, {"name": "world"}])
        d2 = factories.Dataset(tags=[{"name": "bye"}, {"name": "world"}])

        factories.Resource(package_id=d1["id"], format="CSV")
        factories.Resource(package_id=d1["id"], format="JSON")
        factories.Resource(package_id=d2["id"], format="CSV")
        factories.Resource(package_id=d2["id"], format="HTML")

        for tag, count in expected_tags.items():
            result = helpers.call_action(
                "package_search",
                fl="id,tags",
                fq=f"tags:{tag}",
                **{
                    "facet.field": '["tags"]',
                    plugin._extra_or_prefix + "res_format": "on",
                },
            )
            assert result["count"] == count
            assert result["facets"]["tags"] == expected_tags

        for fmt, count in expected_formats.items():
            result = helpers.call_action(
                "package_search",
                fq=f"res_format:{fmt}",
                **{
                    "facet.field": '["res_format"]',
                    plugin._extra_or_prefix + "res_format": "on",
                },
            )
            assert result["count"] == count
            assert result["facets"]["res_format"] == expected_formats

    @pytest.mark.ckan_config("or_facet.or_facets", "tags")
    def test_search_with_one_or(self):
        expected_tags = {"bye": 1, "hello": 1, "world": 2}
        factories.Dataset(tags=[{"name": "hello"}, {"name": "world"}])
        factories.Dataset(tags=[{"name": "bye"}, {"name": "world"}])

        for tag, count in expected_tags.items():
            result = helpers.call_action(
                "package_search",
                fl="id,tags",
                fq=f"tags:{tag}",
                **{"facet.field": '["tags"]'},
            )
            assert result["count"] == count
            assert result["facets"]["tags"] == expected_tags

    def test_search_without_ors(self):
        factories.Dataset(tags=[{"name": "hello"}, {"name": "world"}])
        factories.Dataset(tags=[{"name": "bye"}, {"name": "world"}])

        result = helpers.call_action(
            "package_search",
            fl="id,tags",
            fq="tags:hello",
            **{"facet.field": '["tags"]'},
        )
        assert result["count"] == 1
        assert result["facets"]["tags"] == {"hello": 1, "world": 1}

        result = helpers.call_action(
            "package_search",
            fl="id,tags",
            fq="tags:bye",
            **{"facet.field": '["tags"]'},
        )
        assert result["count"] == 1
        assert result["facets"]["tags"] == {"bye": 1, "world": 1}

        result = helpers.call_action(
            "package_search",
            fl="id,tags",
            fq="tags:world",
            **{"facet.field": '["tags"]'},
        )
        assert result["count"] == 2
        assert result["facets"]["tags"] == {"bye": 1, "hello": 1, "world": 2}
