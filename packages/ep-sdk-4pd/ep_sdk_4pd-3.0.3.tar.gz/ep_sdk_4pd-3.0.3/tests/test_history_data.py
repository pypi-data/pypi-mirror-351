import datetime
from turtle import pd

from ep_sdk_4pd.ep_data import EpData
from ep_sdk_4pd.ep_system import EpSystem


def test_history_data():
    print('-------------test_history_data-------------')

    system_data = EpSystem.get_system_date()
    dt1 = datetime.datetime.strptime("2024-01-01", "%Y-%m-%d")
    dt2 = datetime.datetime.strptime(system_data, "%Y-%m-%d")
    gaps = dt2 - dt1
    gap_days = gaps.days
    print("gap_days:", gap_days)

    data = EpData.get_history_data(scope="market",days=gap_days)
    print(data)
    print('-------------------------------------')


if __name__ == '__main__':
    test_history_data()
