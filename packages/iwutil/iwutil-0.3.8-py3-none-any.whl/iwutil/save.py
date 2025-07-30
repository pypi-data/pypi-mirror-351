from pathlib import Path
from json import dump


def create_folder(filename):
    """
    Create a folder if it does not exist

    Parameters
    ----------
    filename : str
        File name in the folder to create
    """
    Path(filename).parent.mkdir(parents=True, exist_ok=True)


def json(params, filename):
    """
    Save params to a json file

    Parameters
    ----------
    params : dict
        Dictionary of parameters
    filename : str
        Full path and name of the file to save
    """
    create_folder(filename)
    with open(filename, "w") as f:
        dump(params, f, indent=2)


def csv(df, filename):
    """
    Save df to a csv file

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to save
    filename : str
        Full path and name of the file to save
    """
    create_folder(filename)
    df.to_csv(filename, index=False)


def parquet(df, filename):
    """
    Save df to a parquet file

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to save
    filename : str
        Full path and name of the file to save
    """
    create_folder(filename)
    df.to_parquet(filename)


def txt(df, filename):
    """
    Save df to a txt file

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to save
    filename : str
        Full path and name of the file to save
    """
    create_folder(filename)
    df.to_csv(filename, index=False, sep="\t")


def fig(fig_to_save, filename):
    """
    Save fig to a file

    Parameters
    ----------
    fig_to_save : matplotlib.figure.Figure
        Figure to save
    filename : str
        Full path and name of the file to save
    """
    create_folder(filename)
    fig_to_save.savefig(filename)
