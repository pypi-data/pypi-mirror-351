"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest


if __name__ == '__main__':
    kytest.AppConfig.did = ['417ff34c']
    kytest.AppConfig.pkg = 'com.qizhidao.clientapp'
    kytest.AppConfig.run_mode = 'polling'

    kytest.main(path="tests/test_adr.py")



