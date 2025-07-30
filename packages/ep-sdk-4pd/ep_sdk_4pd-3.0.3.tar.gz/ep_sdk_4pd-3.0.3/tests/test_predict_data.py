from ep_sdk_4pd.ep_data import EpData


def test_predict_data():
    print('-------------test_predict_data-------------')

    data = EpData.get_predict_data(scope="plant,weather")
    print(data)
    if data is None or len(data['plant']) == 0:
        return print("空空")
    print('-------------------------------------')


if __name__ == '__main__':
    test_predict_data()
