import codecs
import os
import logging  # 引入logging模块
from datetime import datetime
import socket
from pathlib import Path

logging.basicConfig(level= int(os.environ.get('LOG_LEVEL', logging.INFO)),
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

def hostname():
    return socket.gethostname()
def write_gen_info(f):
    f.write('#' * 40+'\n')
    f.write('# create by :%s'%hostname()+'\n')
    f.write('# create time :%s'%datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')+'\n')
    f.write('#' * 40+'\n')

class Upgrade_base:
    def __init__(self,dir,swagger):
        self.root_path =dir
        self.swagger = swagger

    def load_file(self,filename):
        assert os.path.exists(filename), '该文件(%s)不存在' % filename
        codes = []
        with codecs.open(filename, "r", "utf-8") as file:
            for code in file.readlines():
                codes.append(code.rstrip())
        return codes

    def saveUTF8File(self,filename, codes, writegeninfo=False, exist_ok=True):
        '''
        把list 中的数据存UTF8格式
        :param filename:
        :param codes: 存放代码的 list
        :return:
        '''
        if not codes:
            return
        if not exist_ok and os.path.exists(filename):
            logging.info('the file(%s) is exist' % filename)
            return
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with codecs.open(filename, "w", "utf-8") as file:
            if writegeninfo:
                write_gen_info(file)
            for line in codes:
                if not line:
                    continue
                file.write(line + '\n')

    def merge_code(self):
        pass
class Upgrade_k8s(Upgrade_base):
    def merge_config(self):
        filename = os.path.join(os.path.realpath(self.root_path),'app','config.py')
        scodes = self.load_file(filename)
        code_ins = f'''
            # 支持k8s
            SUPPORT_K8S = os.environ.get('SUPPORT_K8S', 'false').lower() == 'true'
            @classmethod
            def get_host_addr(cls):
                from mwsdk import AgentConf
                if cls.SUPPORT_K8S:
                    return '{self.swagger.name}-server'
                return AgentConf().bind_ip
                '''
        try:
            scodes.index('    def get_host_addr(cls):')
        except Exception as e:
            code_ins_indx = scodes.index('    def init_app(app):') + 2
            scodes.insert(code_ins_indx, code_ins)
            self.saveUTF8File(filename, scodes, exist_ok=True)

    def merge_run(self):
        filename = os.path.join(os.path.realpath(self.root_path),'run.py')
        scodes = self.load_file(filename)
        for indx,code in enumerate(scodes):
            if code.startswith('    service_host') :
                scodes[indx] = '''    service_host = f"{config.get_host_addr()}:{ web_port}"'''
            scodes[indx]=scodes[indx].replace('service_host(),','service_host,')
        self.saveUTF8File(filename, scodes, exist_ok=True)

    def merge_uwsigrun(self):
        filename = os.path.join(os.path.realpath(self.root_path),'uwsgi_run.py')
        scodes = self.load_file(filename)
        for indx,code in enumerate(scodes) :
            if code.startswith('    service_host'):
                scodes[indx] = '''    service_host = f"{config.get_host_addr()}:{ web_port}"'''
            # scodes[indx]= code.replace('service_host(),', 'service_host,')
            # 不能用code替换,避免覆盖上次修改了的值
            scodes[indx] = scodes[indx].replace('service_host(),', 'service_host,')
        self.saveUTF8File(filename, scodes, exist_ok=True)
    #
    # def gen_k8s_yml(self):
    #     tmp_path = os.path.join(os.path.realpath(self.root_path), 'gencode', 'template')
    #     # 创建其他专案文件
    #     from jinja2 import FileSystemLoader, Environment
    #     load = FileSystemLoader(tmp_path)
    #     env = Environment(loader=load)
    #     self.saveUTF8File(os.path.join(os.path.realpath(self.root_path), f'{self.swager.name}-k8s.yml'),
    #                  [env.get_template('k8s-tmp.yml').render(root_path=os.path.split(self.root_path)[-1],
    #                                                               swagger=self.swager, plugins=None)],
    #                  exist_ok=False)

    def merge_code(self):
        self.merge_uwsigrun()
        self.merge_run()
        self.merge_config()



