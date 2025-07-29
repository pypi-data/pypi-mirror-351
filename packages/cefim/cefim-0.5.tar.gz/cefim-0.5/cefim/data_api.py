import requests
import pandas as pd

class CefimData:

    # AWS's elastic IP for the EC2 instance that is running the API
    _eip = "54.232.94.108"

    def __init__(self):
        self._url_bcb_focus = f"http://{self._eip}/api/bcbfocus"
        self._url_ntnb = f"http://{self._eip}/api/ntnb"
        self._url_titulos_publicos = f"http://{self._eip}/api/titulospublicos"

    def bcb_focus(
            self,
            indicator=None,
            frequency=None,
            metric=None,
            survey_type=None,
    ):
        """
        Returns the filtered data from the BCB's focus survey

        Returns
        -------
        df: pandas.DataFrame
        """
        response = requests.post(
            self._url_bcb_focus,
            params={
                'indicator': indicator,
                'frequency': frequency,
                'metric': metric,
                'survey_type': survey_type,
            },
        )
        if not response.ok:
            msg = "Unable to get data from database"
            raise ConnectionError(msg)

        df = pd.DataFrame(response.json())
        df['date'] = pd.to_datetime(df['date'], unit="ms")
        df = df.pivot(
            columns='prediction_scope',
            index='date',
            values='value',
        )
        return df

    def titulos_publicos(self):
        """
        Returns the full database of secondary market data for
        brazilian public bonds

        Returns
        -------
        df: pandas.DataFrame
        """
        response = requests.get(self._url_titulos_publicos)

        if not response.ok:
            msg = "Unable to get data from database"
            raise ConnectionError(msg)

        df = pd.DataFrame(response.json())
        df['reference_date'] = pd.to_datetime(df['reference_date'], unit="ms")
        df['emission_date'] = pd.to_datetime(df['emission_date'], unit="ms")
        df['maturity_date'] = pd.to_datetime(df['maturity_date'], unit="ms")
        return df

    def ntnb(self):
        """
        Returns the secondary market data for NTN-Bs

        Returns
        -------
        df: pandas.DataFrame
        """
        response = requests.get(self._url_ntnb)

        if not response.ok:
            msg = "Unable to get data from database"
            raise ConnectionError(msg)

        df = pd.DataFrame(response.json())
        df['reference_date'] = pd.to_datetime(df['reference_date'], unit="ms")
        df['emission_date'] = pd.to_datetime(df['emission_date'], unit="ms")
        df['maturity_date'] = pd.to_datetime(df['maturity_date'], unit="ms")
        return df
