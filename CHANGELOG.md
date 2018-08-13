# CHANGELOG

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
