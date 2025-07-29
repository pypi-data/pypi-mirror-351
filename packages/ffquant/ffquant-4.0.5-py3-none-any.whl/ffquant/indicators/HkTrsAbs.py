from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['HkTrsAbs']

class HkTrsAbs(BaseIndicator):
    (OVER_MKT_HK_SELL_CN_BUY,
     HK_ACT_SELL,
     HK_TRS_DN,
     NA,
     HK_TRS_UP,
     HK_ACT_BUY,
     OVER_MKT_HK_BUY_CN_SELL) = (-3, -2, -1, 0, 1, 2, 3)

    lines = ('hk_trs_abs', 'delay')

    def __init__(self):
        super(HkTrsAbs, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime']/ 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        root_create_time = item['createTime']
        leaf = item.get(internal_key, {})

        if leaf.get('value', None) is not None:
            self.cache[result_time_str]['create_time'] = root_create_time
            self.cache[result_time_str]['raw_material_time'] = leaf['closeTime']
            if leaf['value'] == 'OVER_MKT_HK_SELL_CN_BUY':
                self.cache[result_time_str]['value'] = self.OVER_MKT_HK_SELL_CN_BUY
            elif leaf['value'] == 'HK_ACT_SELL':
                self.cache[result_time_str]['value'] = self.HK_ACT_SELL
            elif leaf['value'] == 'HK_TRS_DN':
                self.cache[result_time_str]['value'] = self.HK_TRS_DN
            elif leaf['value'] == 'HK_TRS_UP':
                self.cache[result_time_str]['value'] = self.HK_TRS_UP
            elif leaf['value'] == 'HK_ACT_BUY':
                self.cache[result_time_str]['value'] = self.HK_ACT_BUY
            elif leaf['value'] == 'OVER_MKT_HK_BUY_CN_SELL':
                self.cache[result_time_str]['value'] = self.OVER_MKT_HK_BUY_CN_SELL
            elif leaf['value'] == 'NA':
                self.cache[result_time_str]['value'] = self.NA

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    # 它的返回值表示这个信号的生成时间戳 目的是让BaseIndicator打印信号的生成延迟
    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.hk_trs_abs[0] = self.cache[current_bar_time_str]['value']

        root_create_time = self.cache[current_bar_time_str]['create_time']
        line = getattr(self.lines, 'delay', None)
        if line is not None:
            leaf_close_time = self.cache[current_bar_time_str]['raw_material_time']
            self.lines.delay[0] = (root_create_time - leaf_close_time) / 1000.0

        return root_create_time

    def get_internal_key(self):
        return 'TYPE_HK_TRS_ABS' if self.p.version is None else f'TYPE_HK_TRS_ABS_{str(self.p.version).upper()}'