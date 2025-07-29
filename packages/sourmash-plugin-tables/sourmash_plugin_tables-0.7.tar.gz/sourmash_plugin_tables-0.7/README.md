# tables

Tables! We all love them and couldn't function without them in our daily lives. Now sourmash has tables too!

## Installation

```
pip install sourmash_plugin_tables
```

## Usage




## Support

We suggest filing issues in [the main sourmash issue tracker](https://github.com/dib-lab/sourmash/issues) as that receives more attention!

## Dev docs

`tables` was developed from https://github.com/sourmash-bio/sourmash_plugin_template.

### Testing

Run:
```
pytest tests
```

Example/test data located in `tests/test-data` (shocking, I know)

### Generating a release

Bump version number in `pyproject.toml` and push.

Make a new release on github.

Then pull, and:

```
make dist
```

followed by `twine upload dist/...`.
