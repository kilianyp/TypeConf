

class Transform(BaseConfig):
    name: str
    size: int


class Dataset(BaseConfig):
    transform : Transform
    path : str
    split_dir : str

