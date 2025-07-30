from ffquant.indicators.BaseIndicator import BaseIndicator
from datetime import datetime, timedelta
import pytz
from ffquant.utils.Logger import stdout_log

__ALL__ = ['StopOpenPos']

class StopOpenPos(BaseIndicator):
    (STOP_OPEN_SHORT, NA, STOP_OPEN_LONG) = (-1, 0, 1)

    lines = ('stop_open_pos', 'delay')

    def __init__(self):
        super(StopOpenPos, self).__init__()
        self.addminperiod(1)

    def handle_api_resp(self, item):
        internal_key = self.get_internal_key()
        result_time_str = datetime.fromtimestamp(item['closeTime']/ 1000.0).strftime('%Y-%m-%d %H:%M:%S')
        root_create_time = item['createTime']
        leaf = item.get(internal_key, {})

        if leaf.get('value', None) is not None:
            self.cache[result_time_str]['create_time'] = root_create_time
            self.cache[result_time_str]['raw_material_time'] = leaf['closeTime']
            if leaf['value'] == 'STOP_OPEN_SHORT':
                self.cache[result_time_str]['value'] = self.STOP_OPEN_SHORT
            elif leaf['value'] == 'STOP_OPEN_LONG':
                self.cache[result_time_str]['value'] = self.STOP_OPEN_LONG
            elif leaf['value'] == 'NA':
                self.cache[result_time_str]['value'] = self.NA

        if self.p.debug:
            stdout_log(f"{self.__class__.__name__}, result_time_str: {result_time_str}, {internal_key}: {item.get(internal_key, None)}")

    # 它的返回值表示这个信号的生成时间戳 目的是让BaseIndicator打印信号的生成延迟
    def determine_final_result(self):
        current_bar_time = self.data.datetime.datetime(0).replace(tzinfo=pytz.utc).astimezone()
        current_bar_time_str = current_bar_time.strftime('%Y-%m-%d %H:%M:%S')
        self.lines.stop_open_pos[0] = self.cache[current_bar_time_str]['value']

        root_create_time = self.cache[current_bar_time_str]['create_time']
        line = getattr(self.lines, 'delay', None)
        if line is not None:
            leaf_close_time = self.cache[current_bar_time_str]['raw_material_time']
            self.lines.delay[0] = (root_create_time - leaf_close_time) / 1000.0

        return root_create_time

    def get_internal_key(self):
        return 'TYPE_STOP_OPEN_POSITION' if self.p.version is None else f'TYPE_STOP_OPEN_POSITION_{str(self.p.version).upper()}'