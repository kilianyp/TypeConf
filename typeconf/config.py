PATH = "/data1/pfeiffky/gog/dataset/gog_v2.17/"
SPLIT_DIR = "/data1/pfeiffky/gog/dataset/splits/SPLIT_2020-11-04"

cfg = {
    "model": {
        "name": "unet",
        "num_classes": 1,
        "weights": "/data1/pfeiffky/gog/experiments/GoG/pretrain_202007101435/training_checkpoint_36760.pt",
    },
    "training": {
        "dataset": {
            "transform": {
                "name": "trainv2",
                "size": 320
            },
            "name": "gog-segmentation",
            "splits": ["train_post"],
            "path": PATH,
            "split_dir": SPLIT_DIR,
        },
        "optimizer": {
            "name": "adam"
        },
        "scheduler": {
            "name": "PiecewiseLinear",
            "parameter": "lr",
            "milestones": [(8, 0.003), (15, 0.001), (20, 0.0001)]
        },
        "loss": {
            "name": "soft_dice",
            "do_bg": True,
            "batch_dice": True
        },
        "batch_size": 16,
        "max_epochs": 30,
        "validation_interval": 2,
    },
    "validation": {
        "dataset": {
            "transform": {
                "name": "testv2",
                "size": 320
            },
            "name": "gog-segmentation",
            "splits": ["validation_post"],
            "path": PATH,
            "split_dir": SPLIT_DIR,
        },
        "batch_size": 32
    },
    "test": {
        "dataset": {
            "transform": {
                "name": "testv2",
                "size": 480
            },
            "name": "gog-segmentation",
            "splits": ["test_post"],
            "path": PATH,
            "split_dir": SPLIT_DIR
        },
        "batch_size": 32
    },
}
