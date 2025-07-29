from matplotlib.colors import LinearSegmentedColormap as _LinearSegmentedColormap
bwr_alpha = _LinearSegmentedColormap(
    'bwr_alpha', 
    dict(
        red=[
            (0, 0, 0), 
            (0.5, 1, 1), 
            (1, 1, 1)
        ],
        green=[
            (0, 0.5, 0),
            (0.5, 1, 1),
            (1, 0, 0)
        ],
        blue=[
            (0, 1, 1),
            (0.5, 1, 1),
            (1, 0, 0)
        ],
        alpha = [
            (0, 1, 1),
            (0.5, 0, 0),
            (1, 1, 1)
        ],
    ), 
)
gold_alpha = _LinearSegmentedColormap(
    'gold_alpha', 
    dict(
        red=[
            (0, 1, 1), 
            (1, 1, 1), 
        ],
        green=[
            (0, 1, 1),
            (1, 0.9, 1),
        ],
        blue=[
            (0, 1, 1),
            (1, 0, 1),
        ],
        alpha = [
            (0, 0, 0),
            (1, 1, 1)
        ],
    )
)
grey_alpha = _LinearSegmentedColormap(
    'grey_alpha', 
    dict(
        red=[
            (0, 0, 1), 
            (1, 0, 1), 
        ],
        green=[
            (0, 0, 1),
            (1, 0, 1),
        ],
        blue=[
            (0, 0, 1),
            (1, 0, 1),
        ],
        alpha = [
            (0, 0, 0),
            (1, 1, 1)
        ],
    )
)
red_alpha = _LinearSegmentedColormap(
    'red_alpha', 
    dict(
        red=[
            (0, 0, 1), 
            (1, 1, 1)
        ],
        green=[
            (0, 0, 1),
            (1, 0, 0)
        ],
        blue=[
            (0, 0, 1),
            (1, 0, 0)
        ],
        alpha = [
            (0, 0, 0),
            (1, 1, 1)
        ],
    ), 
)
blue_alpha = _LinearSegmentedColormap(
    'blue_alpha', 
    dict(
        red=[
            (0, 0, 1), 
            (1, 0, 1)
        ],
        green=[
            (0, 0, 1),
            (1, 0, 0)
        ],
        blue=[
            (0, 0, 1),
            (1, 1, 0)
        ],
        alpha = [
            (0, 0, 0),
            (1, 1, 1)
        ],
    ), 
)

gwb_alpha = _LinearSegmentedColormap(
    'gwb_alpha', 
    dict(
        red=[
            (0,   0, 0.36), 
            (0.5, 1, 1), 
            (1,   0.96, 1)
        ],
        green=[
            (0, 0, 0.75),
            (0.5, 1, 1),
            (1, 0.79, 0)
        ],
        blue=[
            (0, 0, 0.75),
            (0.5, 1, 1),
            (1, 0.29, 0)
        ],
        alpha = [
            (0, 1, 1),
            (0.5, 0, 0),
            (1, 1, 1)
        ],
    ), 
)