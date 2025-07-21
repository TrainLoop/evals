# Python SDK How-To

Use these snippets to control collection.

## Flush data immediately
Set `flush_immediately=True` when calling `collect()`:
```python
collect(flush_immediately=True)
```

## Label requests
Add tags to headers:
```python
headers |= trainloop_tag("checkout")
```

## Custom config path
Specify a config file:
```python
collect("./trainloop/trainloop.config.yaml")
```
