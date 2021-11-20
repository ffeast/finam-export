import unittest
from finam.export import fetch_url, Exporter
from finam.exception import FinamTooLongTimeframeError

class FinamTooLongTimeframeErrorTestCase(unittest.TestCase):
    def test_tooDeep(self):
        url = "https://export.finam.ru/export9.out?market=5&em=83&token=03AGdBq24TszZ-dPqHt33nEErdKlymyopEkaclaoED4Nm5NP078LpwSMcZApE1B-iL18KsheOiMdb3sVACEi7Ou91RxlZn7yQmfLoS3FgoCx7rSfIHjf-2ab4Ye5xASsdLFzND7PiF7Fuuv3qx0NswSb9V_dL3Q8sH304ZT8CjCg5XZFrVKwIVIErqi63hFli_xsOgUXFHiukCDeG6KtPG9znQzRMDxgDaApBsjGApFh4CAX5RFi40HqXSdNEJ92uMQHXaIrZT75--AzX-PBXFDtM4DFpHGzZKvMGAGc5IlM2WBZZiIIlHvFzCRwRxG2d5CtfWQpfYKN6g3GnH5w2NGf9ApwGqvmwN2AZrjsMYLKyuJwEmI-7O2HS7xj4MuJkvlcdPxhvgH9Om2mhJ-OR-_7CWSuY3H8xvWGwFlf-wDepX7TpxmKHvwucx_yoydfTy61DTwCf_P0Mf&code=EURUSD&apply=0&df=15&mf=7&yf=2019&from=15.08.2019&dt=15&mt=7&yt=2021&to=15.08.2021&p=7&f=EURUSD_190815_210815&e=.txt&cn=EURUSD&dtf=1&tmf=1&MSOR=1&mstime=on&mstimever=1&sep=1&sep2=1&datf=1&at=1"
        data = fetch_url(url)
        
        export = Exporter()
        with self.assertRaises(FinamTooLongTimeframeError):
            export._sanity_check(data)