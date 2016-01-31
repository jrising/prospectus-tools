## Installing the required packages

This code relies on yaml and statsmodels.  If you don't have them,
install them with:
```
pip install pyyaml
pip install statsmodels
```

## Using `quantiles.py`

Start by setting up a configuration file.  A few configuration files are included in the `quantile-configs` folder.  Then run the quantiles script as follows:

```
python quantiles.py <your configuration file.yml>
```

Short comments are in the `quantile-configs` configurations; more details are in the [configuration documentation](config-docs.md).