import pytest

from pandasai.query_builders.view_query_builder import ViewQueryBuilder


class TestViewQueryBuilder:
    @pytest.fixture
    def view_query_builder(self, mysql_view_schema, mysql_view_dependencies_dict):
        return ViewQueryBuilder(mysql_view_schema, mysql_view_dependencies_dict)

    def test__init__(self, mysql_view_schema, mysql_view_dependencies_dict):
        query_builder = ViewQueryBuilder(
            mysql_view_schema, mysql_view_dependencies_dict
        )
        assert isinstance(query_builder, ViewQueryBuilder)
        assert query_builder.schema == mysql_view_schema

    def test_build_query(self, view_query_builder):
        assert (
            view_query_builder.build_query()
            == """SELECT
  parents_id,
  parents_name,
  children_name
FROM (
  SELECT
    "parents.id" AS parents_id,
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )

    def test_get_columns(self, view_query_builder):
        assert view_query_builder._get_columns() == [
            "parents_id",
            "parents_name",
            "children_name",
        ]

    def test_get_columns_empty(self, view_query_builder):
        view_query_builder.schema.columns = None
        assert view_query_builder._get_columns() == ["*"]

    def test_get_table_expression(self, view_query_builder):
        assert (
            view_query_builder._get_table_expression()
            == """(
  SELECT
    "parents.id" AS parents_id,
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )

    def test_table_name_injection(self, view_query_builder):
        view_query_builder.schema.name = "users; DROP TABLE users;"
        query = view_query_builder.build_query()
        assert (
            query
            == '''SELECT
  parents_id,
  parents_name,
  children_name
FROM (
  SELECT
    "parents.id" AS parents_id,
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS "users; DROP TABLE users;"'''
        )

    def test_column_name_injection(self, view_query_builder):
        view_query_builder.schema.columns[0].name = "column; DROP TABLE users;"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  "column; DROP TABLE users;",
  parents_name,
  children_name
FROM (
  SELECT
    "column; DROP TABLE users;" AS "column; DROP TABLE users;",
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )

    def test_table_name_union_injection(self, view_query_builder):
        view_query_builder.schema.name = "users UNION SELECT 1,2,3;"
        query = view_query_builder.build_query()
        assert (
            query
            == '''SELECT
  parents_id,
  parents_name,
  children_name
FROM (
  SELECT
    "parents.id" AS parents_id,
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS "users UNION SELECT 1,2,3;"'''
        )

    def test_column_name_union_injection(self, view_query_builder):
        view_query_builder.schema.columns[
            0
        ].name = "column UNION SELECT username, password FROM users;"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  "column UNION SELECT username, password FROM users;",
  parents_name,
  children_name
FROM (
  SELECT
    "column UNION SELECT username, password FROM users;" AS "column UNION SELECT username, password FROM users;",
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )

    def test_table_name_comment_injection(self, view_query_builder):
        view_query_builder.schema.name = "users --"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  parents_id,
  parents_name,
  children_name
FROM (
  SELECT
    "parents.id" AS parents_id,
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS users"""
        )

    def test_column_name_comment_injection(self, view_query_builder):
        view_query_builder.schema.columns[0].name = "column --"
        query = view_query_builder.build_query()
        assert (
            query
            == """SELECT
  column,
  parents_name,
  children_name
FROM (
  SELECT
    column AS column,
    "parents.name" AS parents_name,
    "children.name" AS children_name
  FROM (
    SELECT
      *
    FROM parents
  ) AS parents
  JOIN (
    SELECT
      *
    FROM children
  ) AS children
    ON parents.id = children.id
) AS parent_children"""
        )
