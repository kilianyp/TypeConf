
def test_preset(tmp_path):
    from typeconf.irconfig import IRConfig
    import json
    import os
    # create a simple preset there

    preset = {
        "testa": 1,
        "testb": 2
    }

    with open(os.path.join(tmp_path, 'test.json'), 'w') as f:
        json.dump(preset, f)

    IRConfig.register_preset_dir(tmp_path)
    cfg = {
        "preset": "${preset:test.json}"
    }
    cfg = IRConfig.create(cfg)
    cfg = IRConfig.to_container(cfg, resolve=True)
    assert cfg['preset'] == preset


