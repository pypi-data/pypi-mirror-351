from .DWDContent import getDWDContent


def retrieve_nwp(service="DWD", model="ICON", eps=None, grid_type=None, variable=None, level_type=None,
                 levels=0, init_time=None, forecast_hour=None, merge_files=False, dest=None, validate_urls=True):
    """
    Downloads numerical weather prediction (NWP) datasets from opendata server.
    
    Parameters
    ----------
    service : str
            name of weather service. Default="DWD".
    model : str
            name of the model. Default="ICON".

    eps : bool
            if True, download ensemble forecast, otherwise download deterministic forecast.

    grid_type: str
        The type of the geo grid.

    variable : list or str
            list of variables to download. Multiple values are allowed.

    level_type : str
            one of "model", "pressure", or "single"

    levels : list or int
            levels to download. Unit depends on `level_type`.

    init_time : int or str

    forecast_hour : list or int
            hours since the initialization of forecast. Multiple values are allowed.

    merge_files : bool
            if true, GRIB files are concatenated to create one file.

    dest : str
            Destination folder for downloaded data. If the files are already available,
            they are not downloaded again.
            
    validate_urls : bool
            Whether to ping all download URLs first to validate state of the cache. Might slow
            down the process significantly for bigger data requests.

    Returns
    -------
    list :
            names of downloaded files.
    """
    content = getDWDContent()
    download_files = content.retrieve(service=service, model=model, eps=eps, grid_type=grid_type,
                                               variable=variable, level_type=level_type, levels=levels,
                                               init_time=init_time, forecast_hour=forecast_hour,
                                               merge_files=merge_files, dest=dest, validate_urls=validate_urls)
    return download_files
