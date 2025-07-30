"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest


if __name__ == '__main__':
    kytest.AppConfig.did = 'xxx'
    kytest.AppConfig.pkg = 'com.qzd.hm'
    kytest.AppConfig.ability = 'EntryAbility'

    kytest.main(path="tests/test_hm.py")

