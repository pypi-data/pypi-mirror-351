import numpy as np
import pandas as pd

class Drillhole:
    def __init__(self, collar: pd.DataFrame, survey: pd.DataFrame):
        self.collar = collar.copy()
        self.survey = survey.copy()
        self.drillhole = None

    def desurvey(self):
        """
        Realiza o desurvey da trajetória do furo com base em collar e survey.
        """
        self.drillhole = self.survey.copy()
        self.drillhole['DIP'] = (
            90 - self.drillhole['DIP']
            if self.drillhole['DIP'].mean() > 45
            else self.drillhole['DIP']
        )

        self.drillhole[['X', 'Y', 'Z']] = np.nan
        self.drillhole.sort_values(by=['BHID', 'AT'], inplace=True)

        for bhid, group in self.drillhole.groupby('BHID'):
            collar_row = self.collar[self.collar['BHID'] == bhid]
            if collar_row.empty or group[['AT', 'DIP', 'AZ']].isna().any().any():
                print(f"Skipping BHID {bhid}: Missing data.")
                continue

            x0, y0, z0 = collar_row[['XCOLLAR', 'YCOLLAR', 'ZCOLLAR']].iloc[0].values
            AT, DIP, AZ = group['AT'].values, group['DIP'].values, group['AZ'].values

            if not ((0 <= DIP).all() and (DIP <= 90).all()):
                print(f"Skipping BHID {bhid}: Invalid dip angles.")
                continue

            x, y, z = np.zeros_like(AT, dtype=float), np.zeros_like(AT, dtype=float), np.zeros_like(AT, dtype=float)
            x[0], y[0], z[0] = x0, y0, z0

            for i in range(1, len(AT)):
                dx, dy, dz = self.minimum_curvature(AT[i-1], AT[i], DIP[i-1], DIP[i], AZ[i-1], AZ[i])
                x[i] = x[i-1] + dx
                y[i] = y[i-1] + dy
                z[i] = z[i-1] - dz

            self.drillhole.loc[group.index, 'X'] = x
            self.drillhole.loc[group.index, 'Y'] = y
            self.drillhole.loc[group.index, 'Z'] = z

        self.drillhole = self.drillhole.merge(self.collar, on='BHID', how='inner')

    def minimum_curvature(self, md1, md2, inc1, inc2, az1, az2):
        """
        Implementa o método da curvatura mínima para interpolar coordenadas 3D.
        """
        inc1_rad, inc2_rad = np.radians(inc1), np.radians(inc2)
        az1_rad, az2_rad = np.radians(az1), np.radians(az2)

        beta = np.arccos(
            np.cos(inc2_rad - inc1_rad) -
            np.sin(inc1_rad) * np.sin(inc2_rad) * (1 - np.cos(az2_rad - az1_rad))
        )

        rf = 1 if beta == 0 else 2 / beta * np.tan(beta / 2)
        delta_md = md2 - md1

        north = delta_md / 2 * (np.sin(inc1_rad) * np.cos(az1_rad) + np.sin(inc2_rad) * np.cos(az2_rad)) * rf
        east  = delta_md / 2 * (np.sin(inc1_rad) * np.sin(az1_rad) + np.sin(inc2_rad) * np.sin(az2_rad)) * rf
        tvd   = delta_md / 2 * (np.cos(inc1_rad) + np.cos(inc2_rad)) * rf

        return east, north, tvd
