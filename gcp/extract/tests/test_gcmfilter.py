import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from lib import configs, weights

def test_included_models():
    config = {
        "drop-models": 'access1-0'
    }
    assert configs.included_models(config) == (None, ['access1-0'])

    config = {
        "only-models": ['ccsm4', 'access1-0']
    }
    assert configs.included_models(config) == (['ccsm4', 'access1-0'], [])

    config = {
        "only-models": ['ccsm4', 'access1-0'],
        "drop-models": 'access1-0'
    }
    assert configs.included_models(config) == (['ccsm4'], [])

def test_march2018_filepath():
    config = {
        "drop-models": 'access1-0'
    }
    assert weights.march2018_filepath('rcp85', config, True) == '/shares/gcp/climate/BCSD/SMME/SMME-weights/rcp85_SMME_weights_no_access1-0.tsv'

    config = {
        "only-models": ['ccsm4', 'access1-0']
    }
    assert weights.march2018_filepath('rcp85', config, True) == '/shares/gcp/climate/BCSD/SMME/SMME-weights/rcp85_SMME_weights_of_access1-0_ccsm4.tsv'

    config = {
        "only-models": ['ccsm4', 'access1-0'],
        "drop-models": 'access1-0'
    }
    assert weights.march2018_filepath('rcp85', config, True) == '/shares/gcp/climate/BCSD/SMME/SMME-weights/rcp85_SMME_weights_of_ccsm4.tsv'

if __name__ == '__main__':
    test_included_models()
    test_march2018_filepath()
