# CHANGELOG

## 0.4.0

* **BREAK**: Output is no longer sent to stdout. Instead, a path to a destination file is now specified after the connection name when invoking `pycopyql`.

## 0.3.0

* `query` now uses a queue instead of recursion.
* `query` should now correctly handle duplicate query detection.
* `dependencies_inflector` and `dependents_inflector` now handle inflection failures by using the original uninflected value.
* `dependencies_inflector` and `dependents_inflector` now use database metadata to determine primary key column names.
* `dependencies_inflector` and `dependents_inflector` now take an optional fourth parameter, `inflector`, to support custom inflection.

## 0.2.1

* Fixed issue that prevented `pycopyql.resolver` and its contents from being included in the release.

## 0.2.0

* **BREAK**: `dependencies_inflector` and `dependents_inflector` have been relocated from `pycopyql.query` into `pycopyql.resolver.inflector`.
* **BREAK**: `dependencies_foreign_key` and `dependents_foreign_key` have been relocated from `pycopyql.query` into `pycopyql.resolver.foreign_key`.
* The `inflector` resolver, which composes the `dependencies_inflector` and `dependents_inflector` resolvers, has been added to `pycopyql.resolver.inflector`.
* The `foreign_key` resolver, which composes the `dependencies_foreign_key` and `dependents_foreign_key` resolvers, has been added to `pycopyql.resolver.foreign_key`.
* The `static_map` convenience function, which dynamically creates a resolver based on a static mapping of keys, has been added to `pycopyql.resolver.static`.

## 0.1.0

Initial release
