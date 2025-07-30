"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest


if __name__ == '__main__':
    kytest.WebConfig.host = 'https://www-test.qizhidao.com/'
    kytest.WebConfig.browser = 'firefox'

    kytest.main(path="tests/test_web.py")


