#java版本切换
import os
import sys
import winreg
import ctypes
import time
import re
if __name__ == '__main__':

    #通过参数传输要做的操作
    if len(sys.argv) > 1:
        #获取第一个参数
        action = sys.argv[1]
        #如果第一个参数是“add“，则执行添加操作，获取第二个参数，作为要添加的jdk别名，获取第三个参数，作为jdk的安装路径
        if action == "add":
            alias = sys.argv[2]
            jdk_path = sys.argv[3]
            #把alias和jdk_path合并成一个字符串，用“\\”分隔
            jdk_path_alias = jdk_path + r"\\" + alias
            #获得管理员权限
            if os.name == 'nt':
                ctypes.windll.shell32.ShellExecuteW(None, "runas",
                                                    sys.executable, __file__,
                                                    None, 1)
            #从注册表中获得环境变量JAVA_LIST，如果环境变量JAVA_LIST不存在，创建一个环境变量JAVA_LIST
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0, winreg.KEY_ALL_ACCESS)
            java_list, type = winreg.QueryValueEx(key, "JAVA_LIST")
            if not java_list:
                print("JAVA_LIST is not exist, create it.")
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                    0, winreg.KEY_ALL_ACCESS)
                #将JAVA_LIST的值设置为jdk_path_alias
                winreg.SetValueEx(key, "JAVA_LIST", 0, winreg.REG_EXPAND_SZ,
                                  jdk_path_alias)
                winreg.CloseKey(key)
                time.sleep(5)
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\JavaSoft\Java Runtime Environment", 0,
                    winreg.KEY_ALL_ACCESS)
                #将alias变为数字版本
                alias_num = alias.replace("jdk", "")
                winreg.CreateKey(key, alias_num)
                alias = winreg.OpenKey(key, alias_num, 0,
                                       winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(alias, "MicroVersion", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(alias, "JavaHome", 0, winreg.REG_SZ,
                                  jdk_path)
                winreg.SetValueEx(alias, "RuntimeLib", 0, winreg.REG_SZ,
                                  jdk_path + "\\bin\\server\\jvm.dll")
                winreg.CloseKey(key)
                winreg.CloseKey(alias)
                print("Add jdk " + alias + " success.")
            #查看是否已经存在该jdk别名，如果存在，则提示已经存在，并退出
            elif alias in java_list:
                print("The alias is already exist.")
                sys.exit(0)
            #如果不存在，则添加到JAVA_LIST中
            else:
                #将alias变为数字版本
                alias_num = alias.replace("jdk", "")
                print("JAVA_LIST is exist, add it.")
                print(java_list)
                #修改注册表，将jdk_path_alias添加到JAVA_LIST的值中
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                    0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "JAVA_LIST", 0, winreg.REG_EXPAND_SZ,
                                  str(java_list) + ";" + jdk_path_alias)
                winreg.CloseKey(key)
                #在Java Runtime Environment下新建一个值为JavaHome,RuntimeLib的子项，名为alias_num，值为jdk_path
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\JavaSoft\Java Runtime Environment", 0,
                    winreg.KEY_ALL_ACCESS)
                winreg.CreateKey(key, alias_num)
                alias = winreg.OpenKey(key, alias_num, 0,
                                       winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(alias, "MicroVersion", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(alias, "JavaHome", 0, winreg.REG_SZ,
                                  jdk_path)
                winreg.SetValueEx(alias, "RuntimeLib", 0, winreg.REG_SZ,
                                  jdk_path + "\\bin\\server\\jvm.dll")
                #在Java Development Kittment下新建一个值为JavaHome，MicroVersion的子项，名为alias_num，值为jdk_path
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\JavaSoft\Java Development Kit", 0,
                    winreg.KEY_ALL_ACCESS)
                winreg.CreateKey(key, alias_num)
                alias = winreg.OpenKey(key, alias_num, 0,
                                       winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(alias, "JavaHome", 0, winreg.REG_SZ,
                                  jdk_path)
                winreg.SetValueEx(alias, "MicroVersion", 0, winreg.REG_SZ, "0")
                winreg.CloseKey(key)
                winreg.CloseKey(alias)
                print("Add jdk " + alias + " success.")
        elif action == "remove":
            alias = sys.argv[2]
            #查看环境变量JAVA_LIST中是否存在要删除的jdk别名
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0, winreg.KEY_ALL_ACCESS)
            java_list, type = winreg.QueryValueEx(key, "JAVA_LIST")
            #遍历java_list，查看是否存在要删除的jdk别名
            if alias in java_list:
                #用;分隔java_list，获得java_list的列表
                java_list = java_list.split(";")
                for i in java_list:
                    if i.endswith(sys.argv[2]):
                        #如果存在，则删除
                        java_list.remove(i)
                        break
                #将java_list的列表转换为字符串，用“;”分隔
                java_list = ";".join(java_list)
                #将环境变量java_list的值设置为java_list
                winreg.SetValueEx(key, "JAVA_LIST", 0, winreg.REG_EXPAND_SZ,
                                  java_list)
                winreg.CloseKey(key)

                #删除Java Runtime Environment下的alias子项
                #将alias变为数字版本
                alias = alias.replace("jdk", "")
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\\JavaSoft\\Java Runtime Environment", 0,
                    winreg.KEY_ALL_ACCESS)
                winreg.DeleteKey(key, alias)
                winreg.CloseKey(key)
                #删除Java Development Kit下的alias子项
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    "SOFTWARE\\JavaSoft\\Java Development Kit", 0,
                    winreg.KEY_ALL_ACCESS)
                winreg.DeleteKey(key, alias)
                winreg.CloseKey(key)
                #删除jdk_path_alias
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                    0, winreg.KEY_ALL_ACCESS)
                java_list, type = winreg.QueryValueEx(key, "JAVA_LIST")
                #删除系统环境变量java_home
                winreg.DeleteValue(key, "JAVA_HOME")
                winreg.CloseKey(key)
                print("Remove jdk " + alias + " success.")
            else:
                print("The alias is not exist.")

        elif action == "list":
            #如果第一个参数是“list“，则执行列出操作，列出JAVA_LIST中的jdk别名
            #取出JAVA_LIST的值
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0, winreg.KEY_ALL_ACCESS)
            java_list, type = winreg.QueryValueEx(key, "JAVA_LIST")
            print(java_list)
            winreg.CloseKey(key)
        elif action == "set":
            #如果第一个参数是“set“，则执行设置操作，获取第二个参数，作为要设置的jdk别名
            alias = sys.argv[2]
            #从JAVA_LIST中获取alias对应的jdk路径
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0, winreg.KEY_ALL_ACCESS)
            java_list, type = winreg.QueryValueEx(key, "JAVA_LIST")
            if alias in java_list:
                #用;分隔java_list，获得java_list的列表
                java_list = java_list.split(";")
                for i in java_list:
                    if i.endswith(sys.argv[2]):
                        #提取出alias对应的jdk路径
                        jdk_path = i.replace("\\\\" + alias, "")
                        break
                #在注册表中设置系统环境变量JAVA_HOME为alias对应的jdk路径
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                    0, winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "JAVA_HOME", 0, winreg.REG_EXPAND_SZ,
                                  jdk_path)
                winreg.CloseKey(key)
                #修改注册表，将jdk的jre作为java运行时的默认路径
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"SOFTWARE\JavaSoft\Java Runtime Environment", 0,
                    winreg.KEY_ALL_ACCESS)
                winreg.SetValueEx(key, "CurrentVersion",
                                  0, winreg.REG_EXPAND_SZ,
                                  alias.replace("jdk", ""))
                winreg.CloseKey(key)
            else:
                print("JAVA_LIST is not exist, please check it.")
            #修改注册表，将java_home设置为jdk_path
    #如果参数个数不符合要求，则打印帮助信息
    else:
        print("Usage:")
        print("  java_env.py add <alias> <jdk_path>")
        print("  java_env.py remove <alias>")
        print("  java_env.py list")
        print("  java_env.py set <alias>")
        print("  java_env.py help")
        print("  java_env.py -h")
