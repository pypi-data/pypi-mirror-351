Compute the [strongly connected components](https://en.wikipedia.org/wiki/Strongly_connected_component) of a graph.

```python
type Graph[L] = Mapping[L, Collection[L]]

def strongly_connected_components[L](graph: Graph[L]) -> Iterator[frozenset[L]]
```
