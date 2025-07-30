from ctapointing.imagesolver import SpotExtractorSky


def test_simulator_from_config():
    simulator = SpotExtractorSky.from_config(input_url="SpotExtractor_default.yaml")
    assert simulator.name == "Extractor-thresh5.0-no-mask"
