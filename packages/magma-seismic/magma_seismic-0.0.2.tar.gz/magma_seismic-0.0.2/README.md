# magma-seismic
Some tools for MAGMA to handle seismic

## Install
```python
pip install magma-seismic
```
## Import module
```python
from magma_seismic.download import Download
import magma_seismic
```
## Check version
```python
magma_seismic.__version__
```
## Download from Winston
```python
download = Download(
    station='LEKR',
    channel='EHZ',
    start_date='2025-05-26',
    end_date='2025-05-26',
    
    # (int, optional) - download per how many minutes. Default to 60 minutes
    period=60,
    
    # (str, optional) - change the output directory. Default to current directory
    output_directory=r'D:\Projects\magma-seismic', #change the output directory. Default to current directory
    
    # (bool, optional) - change to False to skip download when file already exists. Default False
    overwrite=True,
    
    # (bool, optional) - to show detailed process. Default to False
    verbose=True,
)

download.to_idds(
    # (bool, optional) - merging or filling empty data. Default to False
    use_merge=True, 
)
```
### (Optional) - Change winston server
```python
download.set_client(
    host='winston address',
    port=123456, #winston port
    timeout=30
)
```
## Check download result
```python
# will show list of failed download
download.failed

# will show list of successfully download
download.success 
```