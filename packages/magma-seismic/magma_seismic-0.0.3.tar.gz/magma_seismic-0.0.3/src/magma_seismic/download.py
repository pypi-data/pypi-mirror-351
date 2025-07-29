from .magma_seismic import MagmaSeismic
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from obspy.clients.earthworm import Client
from obspy import UTCDateTime
from typing import Self


class Download(MagmaSeismic):
    host = '172.16.1.220'
    port = 16032
    timeout = 5

    def __init__(self, station: str, channel: str, start_date: str, end_date: str, channel_type: str = 'D',
                 network: str = 'VG', location: str = '00', verbose: bool = False,
                 output_directory: str = None, period: int = 60, overwrite: bool = False):
        super().__init__(station, channel, channel_type, network, location, verbose)

        assert 0 < period < 24 * 60, ValueError(f'❌ Period must be between 1 and 1440 minutes. '
                                                f'Your value is {period} minutes')

        self.period = period
        self.start_date_str = start_date
        self.end_date_str = end_date
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if output_directory is None:
            output_directory = os.getcwd()
        self.output_directory = os.path.join(output_directory, 'output')
        os.makedirs(self.output_directory, exist_ok=True)

        self.download_directory = os.path.join(self.output_directory, 'download')
        os.makedirs(self.download_directory, exist_ok=True)

        self.overwrite = overwrite

        self.client = Client(
            host='172.16.1.220',
            port=16032,
            timeout=5
        )

        self.failed = []
        self.success = []

        if verbose:
            print('='*50)
            print('Station: ' + self.station)
            print('Channel: ' + self.channel)
            print('Network: ' + self.network)
            print('Location: ' + self.location)
            print('='*50)
            print('Start date: ' + self.start_date_str)
            print('End date: ' + self.end_date_str)
            print('Download per period: ' + str(self.period) + ' minutes')
            print('Output directory: ' + self.output_directory)
            print('Download directory: ' + self.download_directory)
            print('Overwrite file: ' + str(self.overwrite))
            print('='*50)
            print('Client host: ' + self.host)
            print('Client port: ' + str(self.port))
            print('Timeout: ' + str(self.timeout))
            print('='*50)

    def hours(self, hour_ranges: pd.DatetimeIndex) -> list[dict]:
        hours = []
        len_hours: int = len(str(len(hour_ranges)))
        for index, start_hour in enumerate(list(hour_ranges)):
            end_hour = start_hour + timedelta(minutes=self.period) - timedelta(milliseconds=1)
            hours.append({
                'index': str(index).zfill(len_hours),
                'start_hour': UTCDateTime(start_hour),
                'end_hour': UTCDateTime(end_hour),
            })
        return hours

    def set_client(self, host: str = '172.16.1.220', port: int = 16032, timeout: int = 5) -> Self:
        self.client = Client(
            host=host,
            port=port,
            timeout=timeout
        )

        if self.verbose:
            print(f'ℹ️ Client using {host}:{port} with timeout {timeout}')

        return self

    def _idds(self, date: datetime, use_merge: bool = False):
        network = self.network
        station = self.station
        channel = self.channel
        location = self.location
        channel_type = self.channel_type
        end_date = date + timedelta(days=1) - timedelta(milliseconds=1)

        year = date.year
        julian_day = date.strftime('%j')

        directory: str = os.path.join(self.download_directory, 'idds')
        os.makedirs(directory, exist_ok=True)

        idds_directory: str = os.path.join(directory, str(year), network, station, f'{channel}.{channel_type}', julian_day)
        os.makedirs(idds_directory, exist_ok=True)

        start_date_str = date.strftime('%Y-%m-%d')

        hour_ranges = pd.date_range(start=date, end=end_date, freq=f'{str(self.period)}min')
        for hour in self.hours(hour_ranges):
            hour_index = hour['index']
            start_hour = hour['start_hour']
            end_hour = hour['end_hour']
            start_hour_str = hour['start_hour'].strftime('%H:%M:%S')
            end_hour_str = hour['end_hour'].strftime('%H:%M:%S')
            nslc: str = f'{network}.{station}.{location}.{channel}.{channel_type}.{year}.{julian_day}.{hour_index}'
            mseed_path: str = os.path.join(idds_directory, nslc)

            if os.path.isfile(mseed_path) and self.overwrite is False:
                print(f'ℹ️ {start_date_str} {start_hour_str} to {end_hour_str} exists. Skipping')
                print(f'➡️🗃️ {mseed_path}')
                continue

            info = {
                'nslc': self.nslc,
                'filename': nslc,
                'start_date': start_date_str,
                'start_time': start_hour_str,
                'end_time': end_hour_str,
                'error': None
            }

            # Downloading miniseed
            try:
                if self.verbose:
                    print(f'⌛ {start_date_str} {start_hour_str} to {end_hour_str} :: Starting download')
                stream = self.client.get_waveforms(
                    network=network, station=station, location=location,
                    channel=channel, starttime=start_hour, endtime=end_hour)

                if len(stream) == 0:
                    info['error'] = 'Data not found in server'
                    self.failed.append(info)
                    print(f'⚠️ {start_date_str} {start_hour_str} to {end_hour_str} :: Data not found in server')
                    continue

                if self.verbose:
                    print(f'✅ {start_date_str} {start_hour_str} to {end_hour_str} :: Download completed')
            except Exception as e:
                info['error'] = f'Error downloading. {e}'
                self.failed.append(info)
                print(f'❌ {start_date_str} {start_hour_str} to {end_hour_str} :: Error downloading {nslc}\n{e}')
                continue

            # Writing mini seed
            try:
                for trace in stream:
                    trace.data = np.where(trace.data == -2 ** 31, 0, trace.data)
                    trace.data = trace.data.astype(np.int32)

                if use_merge:
                    try:
                        stream.merge(fill_value=0)
                        if self.verbose:
                            print(
                                f'🧲 {start_date_str} {start_hour_str} to {end_hour_str} :: Merged {len(stream)} traces.')
                    except Exception as e:
                        info['error'] = f'Merging error. {e}'
                        self.failed.append(info)
                        if self.verbose:
                            print(f'❌ {start_date_str} {start_hour_str} to {end_hour_str} :: Merging error. {e}')
                        continue

                stream.write(mseed_path, format='MSEED')
                self.success.append(info)
                print(f'🗃️ {start_date_str} {start_hour_str} to {end_hour_str} saved to :: {mseed_path}')
            except Exception as e:
                info['error'] = f'Error writing trace. {e}'
                self.failed.append(info)
                print(f'❌ Error writing {mseed_path} :: {start_hour_str} to {end_hour_str}\n{e}')
                continue

    def to_idds(self, use_merge: bool = False):
        date_range = pd.date_range(start=self.start_date, end=self.end_date, freq='d')
        for _date in date_range:
            self._idds(_date, use_merge=use_merge)
        print(f'='*75)
        if len(self.failed) > 0:
            print(f'⚠️ Failed to download {len(self.failed)} traces')
        print(f'✅ Download completed for {self.nslc} :: {self.start_date_str} to {self.end_date_str}')
        print(f'='*75)
