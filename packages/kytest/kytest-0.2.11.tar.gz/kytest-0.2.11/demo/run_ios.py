"""
@Author: kang.yang
@Date: 2024/7/12 17:10
"""
import kytest


if __name__ == '__main__':
    kytest.AppConfig.did = ['00008110-0018386236A2801E', '00008110-00126192228A801E']
    kytest.AppConfig.pkg = 'com.tencent.QQMusic'
    kytest.AppConfig.wda_project_path = '/Users/UI/Downloads/WebDriverAgent-master/WebDriverAgent.xcodeproj'
    kytest.AppConfig.run_mode = 'full'

    kytest.main(path="tests/test_ios.py")



