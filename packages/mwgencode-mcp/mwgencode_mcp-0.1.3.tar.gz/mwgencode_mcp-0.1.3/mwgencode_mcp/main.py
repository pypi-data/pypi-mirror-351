from mcp.server.fastmcp import FastMCP
from typing import TextIO
import logging
from gencode.gen_code import GenCode,GenProject_Sample,GenProject_Flask,GenProject_Aiohttp,GenSwagger
from gencode.importmdj.import_swagger2_class import  ImportSwagger
import argparse
import os
import sys
from gencode.gencode.export_class2swgclass import ExportClass2SWGClass
import yaml
import gencode.upgrade as upgrade
# from typing import Annotated
from pydantic import Field


os.environ["FASTMCP_PORT"] = "8300"

mcp = FastMCP("mwgencode 🚀", 
              init_timeout=30, 
              init_retry=3,
              instructions="""
        这个服务主要是调用mwgencode工具, 产生python代码, 生成flask或fastapi的web框架专案
        调用以下命令来完成专案的功能:
        1. 调用 init_project(project_name, project_type, root_path) 来初始化一个web框架专案, 产生一个包含 专案名.mdj文件和gen_code.yaml单元的专案;
        2. 调用 build(root_path) 来产生项目相关的文件,包括run.py,config.py,models.py等,当UMLmodel或gen_code.yaml有变更时,需要重新build,以生成代码;
        3. 调用 add(swagger_package, umlclass_operation, http_method_type, root_path) 来添加一个操作(umlclass_operation)到swagger相关类(swagger_package),并产生代码;
        4. 调用 export(umlclass, root_path) 来将逻辑视图中的指定UML类生成Swagger类，包含GET、POST、PUT、DELETE等操作。
        5. 调用 upgrade(project_dir, upgrade_type, root_path) 来对指定的项目进行升级操作，支持不同的升级类型。
       """)

class Gen_Code():
    def __init__(self,args):
        self.args = args
        self.prj_conf = None

    def _get_config(self) -> dict:
        def load_config():
            cnfgfile = os.path.join(os.path.abspath(self.args.get('root_path','.')), 'gen_code.yaml')
            if not os.path.exists(cnfgfile):
                raise Exception('gen_code.yaml文件不存在，请先执行 gencode init 初始化项目！')
            yml = open(cnfgfile)
            try:
                self.prj_conf = yaml.full_load(yml)
            except Exception as e:
                raise Exception('载入 gen_code.yaml 出错，error:%s' % e)
            return self.prj_conf
        if self.prj_conf is None:
            self.prj_conf  = load_config()
        return self.prj_conf

    def _get_apptype(self):
        try:
            return self._get_config().get('project', {}).get('type', 'flask')
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s' % e)

    def _get_rootpath(self):
        try:
            # cmd有指定rootpath 时，以指定的rootpath
            return self.args.get('root_path') if self.args.get('root_path','.')!='.' else self._get_config().get('project',{}).get('rootpath','.')
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s'%e)

    def _get_umlfile(self):
        try:
            return os.path.join(self._get_rootpath(),
                                   self._get_config()['project']['doc_dir'],
                                   self._get_config()['project']['models']['main']['file'])
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s'%e)
        
    def _get_no_main_umlfile(self):
        '''
        获取gen_code.yaml中指定的非主UML文件
        :return:
        '''
        try:
            models = self._get_config()['project']['models']
            # models 是一个字典，包含多个UML模型文件,如: {'main':{'file':'sample.mdj'},'sec':{'file':'sample1.mdj'},'thr':{'file':'sample2.mdj'}}
            #需要找出不是main的UML文件列表
            if not isinstance(models, dict):
                raise Exception('gen_code.yaml中models不是字典类型')
            result = []
            for key, value in models.items():
                if key != 'main' and 'file' in value:
                    uml_file = value['file']
                    if uml_file:
                        result.append(os.path.join(self._get_rootpath(),
                                                   self._get_config()['project']['doc_dir'],
                                                   uml_file))
            return result
        except Exception as e:
            raise Exception('gen_code.yaml 文件内容出错，%s'%e)

    def init_project(self):
        '''
        产生一个包含 sample.mdj文件和gen_code_run.py单元的专案
        :return:
        '''
        gp = GenProject_Sample(r'%s' % self.args.get('umlfile'),
                        r'%s' % self.args.get('root_path') )
        gp.gen_code(self.args.get('python_code',False),self.args.get('project_name'))


    def gen_export(self):
        umlfile = self._get_umlfile()
        swg = GenSwagger(umlfile)
        swg.export_one_swgclass(self.args.get('umlclass'),umlfile)

    def gen_add(self):
        umlfile = self._get_umlfile()
        swg = GenSwagger(umlfile)
        swg.add_operation(self.args.get('swagger_package'), 
                          self.args.get('umlclass_operation'), 
                          self.args.get('http_method_type','get'))
 
    def gen_build(self):
        prj_type = self._get_apptype()
        umlfile = self._get_umlfile()
        prj_rootpath = self._get_rootpath()
        if prj_type =='flask':
            gp = GenProject_Flask(r'%s' % umlfile,
                                  r'%s' % prj_rootpath)
        elif prj_type =='aiohttp':
            gp = GenProject_Aiohttp(r'%s' % umlfile,
                                    r'%s' % prj_rootpath)
        else:
            raise Exception('不支持该project type(%s)'%prj_type)
        gp.gen_code()
        g = GenCode(umlfile, prj_rootpath)
        # 产生model
        g.model()
        no_main_umlfiles = self._get_no_main_umlfile()
        # 产生非主UML文件的model
        if no_main_umlfiles:
            for file in no_main_umlfiles:
                if prj_type =='flask':
                    gp = GenProject_Flask(r'%s' % file,
                                        r'%s' % prj_rootpath)
                    gp.gen_code()

    def gen_upgrade(self):
        # logging.info(self.args)
        dir = self.args.get('dir','.')
        umlfile = self._get_umlfile()
        swg = ImportSwagger().impUMLModels(umlfile)
        if self.args.get('type','k8s')=='k8s':
            k8s = upgrade.Upgrade_k8s(dir,swg)
            k8s.merge_code()


@mcp.resource("resource://help")
def get_greeting() -> str:
    """提供mwgencode_mcp帮助信息."""
    return "欢迎使用mwgencode_mcp！\n" \
           "这个服务主要是调用mwgencode工具, 产生python代码, 生成flask或fastapi的web框架专案\n" \
           "调用以下命令来完成专案的功能:\n" \
            "1. 初始化一个专案, 调用 init_project来初始化一个web框架专案\n" \
            "2. 生成专案代码, 调用 build来产生项目相关的文件;\n" \
            "3. 给swagger包增加一个操作, 调用 add来添加一个操作(umlclass_operation)到swagger相关类(swagger_package),并产生代码;\n" \
            "4. uml类生成swagger类,调用 export 来将逻辑视图中的指定UML类生成Swagger类\n" \
            "5. 调用 upgrade 来对指定的项目进行升级操作，支持不同的升级类型。\n" \
            "6. 调用 help() 来获取帮助信息。\n" 
@mcp.tool()
def init_project(project_name:str,project_type:str='flask',root_path:str='.') -> str:
    '''
    此函数用于初始化一个Web框架专案。它会根据传入的参数创建专案的初始文件，
    包括UML模型文件、配置文件等，还可以选择生成gen_code_run.py单元。

    :param project_name: 专案的名称，用于指定专案的标识。
    :param project_type: 专案的类型，支持的类型有 'flask'、'aiohttp' 和 'fastapi'，默认为 'flask'。
    :param python_code: 一个布尔值，若为True，则会生成gen_code_run.py单元，默认为False。
    :param root_path: 项目的根目录路径，默认为当前目录 '.'。
    :return: 
    '''
    try:
        python_code = False
        # print("init_project",project_name,project_type,python_code,root_path)
        params = {"project_name": project_name, 
                "project_type": project_type, 
                "python_code": python_code,
                "root_path": root_path}
        gen_code = Gen_Code(params)
        gen_code.init_project()
        return f"初始化专案完成，专案名称为：{project_name}，专案类型为：{project_type}，是否生成gen_code_run.py单元：{python_code}"
    except Exception as e:
        logging.error(f"初始化专案失败: {e}")
        return f"初始化专案失败: {e}"

@mcp.prompt(
    name="init_project",          
    description="初始化或创建一个专案(项目),生成mdj文件和gen_code.yaml文件"  
)
def init_project_prompt(
    project_name: str = Field(description="专案名称"),
    project_type: str = Field(default="flask", description="专案类型,支持flask、aiohttp和fastapi"),
    root_path: str = Field(default=".", description="项目的根目录路径")
) -> str:
    """This docstring is ignored when description is provided."""
    return f"请执行init_project命令, 在{root_path}目录,产生名为{project_name} 的{project_type}专案 ."

@mcp.tool()
def build(root_path:str='.') -> str:
    '''
    产生项目相关的文件,包括run.py,config.py,models.py等,当UMLmodel或gen_code.yaml有变更时,需要重新执行,以生成代码
    :param root_path: 项目的根目录路径，默认为当前目录 '.'。
    :return:
    '''
    try:
        # 以下代码用于解析命令行参数，构建一个解析器对象，描述为初始化web框架的代码
        # 此函数的主要作用是在UML模型文件或配置文件发生变更时，重新生成项目相关文件
        # 调用Gen_Code类的gen_build方法来完成项目文件的生成操作
        gen_code = Gen_Code({"root_path": root_path})
        gen_code.gen_build()
        return "项目相关文件生成完成"
    except Exception as e:
        logging.error(f"生成项目相关文件失败: {e}")
        return f"生成项目相关文件失败: {e}"

@mcp.prompt(
    name="build",          
    description="产生项目相关的文件,包含run.py,config.py,models.py等"
)
def build_prompt(
    root_path: str = Field(default=".", description="项目的根目录路径")
) -> str:
    """This docstring is ignored when description is provided."""
    return f"请执行build命令, 在{root_path}目录生成项目文件 ."


@mcp.tool()
def add(swagger_package:str,umlclass_operation:str,http_method_type:str='get',root_path:str='.') -> str:
    '''
    添加一个操作(umlclass_operation)到swagger相关类(swagger_package)

    此函数的主要作用是将指定的操作添加到Swagger相关类中。通过传入Swagger包类名、UML类操作名以及可选的HTTP方法类型，
    调用命令行参数解析和Gen_Code类的gen_add方法来完成操作的添加。

    :param swagger_package: Swagger包类的名称，例如 'employeemng'，用于指定要添加操作的Swagger类。
    :param umlclass_operation: UML类的操作名称，例如 'get_employee'，表示要添加的具体操作。
    :param http_method_type: 操作的HTTP方法类型，可选值有 'get'、'post'、'put'、'delete' 等，默认为 'get'。
    :param root_path: 项目的根目录路径，默认为当前目录 '.'。
    :return: 
    '''
    try:
        args = {'swagger_package': swagger_package,
                'umlclass_operation': umlclass_operation,
                'http_method_type': http_method_type,
                'root_path': root_path
                }
            
        gen_code = Gen_Code(args)
        gen_code.gen_add()
        return f"操作添加完成，Swagger包类为：{swagger_package}，UML类操作为：{umlclass_operation}，HTTP方法类型为：{http_method_type}"
    except Exception as e:
        logging.error(f"添加操作失败: {e}")
        return f"添加操作失败: {e}"

@mcp.prompt(
    name="add",          
    description="添加一个操作(umlclass_operation)到swagger相关类(swagger_package)"
)
def add_prompt(
    swagger_package: str = Field(description=" Swagger包类的名称，例如 'employeemng'，用于指定要添加操作的Swagger类"),
    umlclass_operation: str = Field(description="UML类的操作名称，例如 'get_employee'，表示要添加的具体操作。"),
    http_method_type: str = Field(default="get", description="操作的HTTP方法类型，可选值有 'get'、'post'、'put'、'delete' 等，默认为 'get'"),
    root_path: str = Field(default=".", description="项目的根目录路径")
) -> str:
    """This docstring is ignored when description is provided."""
    return f"请执行add命令, 给{swagger_package}swagger包,添加一个名为{umlclass_operation} 类型为{http_method_type}的操作."

@mcp.tool()
def export(umlclass:str,root_path:str='.') -> str:
    '''
    此函数的主要作用是将逻辑视图中的指定UML类生成Swagger类，包含GET、POST、PUT、DELETE等操作。
    当UML模型文件（UMLmodel）或项目配置文件（gen_code.yaml）有变更时，需要重新执行此函数，以确保生成最新的代码。
    :param root_path: 项目的根目录路径，默认为当前目录 '.'。
    :param umlclass: 逻辑视图中的UML类名称，例如 'employee'，用于指定要生成Swagger类的目标UML类。
    :return: 
    '''
    try:
        args = {'umlclass': umlclass,"root_path": root_path}
        gen_code = Gen_Code(args)
        gen_code.gen_export()
        return f"Swagger类生成完成，目标UML类为：{umlclass}"
    except Exception as e:  
        logging.error(f"生成Swagger类失败: {e}")
        return f"生成Swagger类失败: {e}"

@mcp.prompt(
    name="export",          
    description="将逻辑视图中的指定UML类生成Swagger类，包含GET、POST、PUT、DELETE等操作"
)
def export_prompt(
    umlclass: str = Field(description=" 逻辑视图中的UML类名称，例如 'employee'，用于指定要生成Swagger类的目标UML类"),
    root_path: str = Field(default=".", description="项目的根目录路径")
) -> str:
    """This docstring is ignored when description is provided."""
    return f"请执行export命令, 把{umlclass}类生成swagger类."


@mcp.tool()
def upgrade(project_dir:str,upgrade_type:str='k8s',root_path:str='.') -> str:
    '''
    此函数的主要作用是对指定的项目进行升级操作，支持不同的升级类型。
    当UML模型文件（UMLmodel）或项目配置文件（gen_code.yaml）有变更时，需要重新执行此函数，以确保生成最新的代码。

    :param project_dir: 项目的目录路径，用于指定要升级的项目。
    :param upgrade_type: 升级的类型，可选值有 'k8s' 等，默认为 'k8s'。
    :param root_path: 项目的根目录路径，默认为当前目录 '.'。
    :return: 
    '''
    try:
        args = {'dir': project_dir, 'type': upgrade_type, 'root_path': root_path}
        gen_code = Gen_Code(args)
        gen_code.gen_upgrade()
        return f"项目升级完成，项目目录为：{project_dir}，升级类型为：{upgrade_type}"
    except Exception as e:
        logging.error(f"项目升级失败: {e}")
        return f"项目升级失败: {e}"


if __name__ == "__main__":
    # mcp.run(transport='sse')
    mcp.run(transport='stdio')

 