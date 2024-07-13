#1.check if only one module in file,if not abort scr
#2.check module name consistent with file name,if not abort scr
#3.string fliter,keep only module ();contents
#4.delete comment context//
#5.check if exits parameter options
#6.check if exits ifdef options,delete contents
#7.in out inout /width/name
import os
import re
def list_files_in_directory(directory_path):
    file_paths = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths
def count_module_blocks(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Initialize counters
        module_count = 0
        endmodule_count = 0
        in_module_block = False

        lines = content.split('\n')
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('module'):
                if not in_module_block:
                    in_module_block = True
                    module_count += 1
            elif stripped_line.startswith('endmodule'):
                if in_module_block:
                    in_module_block = False
                    endmodule_count += 1

        # Ensure each module has a corresponding endmodule
        if module_count != endmodule_count:
            raise ValueError("Mismatch between 'module' and 'endmodule' count.")

        return module_count

    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
def extract_module_declarations(file_path):
    # Check if the file extension is .v or .sv
    if not (file_path.endswith('.v') or file_path.endswith('.sv')):
        print(f"The file {file_path} is not a .v or .sv file. Ignoring...")
        return 0

    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Use regular expressions to find the module declaration
        module_declarations = re.findall(r'\bmodule\s+(\w+)\s*(?:\(|#\()', content)
        if not module_declarations:
            print("No module declarations found.")
            return 0

        # Remove all spaces from the module name
        module_name_no_spaces = re.sub(r'\s+', '', module_declarations[0])

        # Extract the file name without the extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]

        # Compare module name with the file name
        if module_name_no_spaces == file_name:
            return 1
        else:
            return 0

    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0
def file_input_filter(dir_path):
    all_files = list_files_in_directory(dir_path)
    for l in all_files:
        print(f"File {l} into py.scr ...")
    # step2 waive multi module file
    lst_filter_multi_module = []
    for file in all_files:
        if (file.endswith('.v') or file.endswith('.sv')):
            # print(f"The file {file} is not a .v or .sv file. Ignoring...")
            module_block_count = count_module_blocks(file)
            if module_block_count != 1:
                print(f"Waive {file} for this file 'module' number is: {module_block_count}")
            else:
                lst_filter_multi_module.append(file)
    # step3 waive module name inconsistent with file
    lst_filter_unequal_name_module = []
    for file in lst_filter_multi_module:
        if extract_module_declarations(file):
            lst_filter_unequal_name_module.append(file)
        else:
            print(f"Waive {file} for this file 'module name' != 'file name'")
    return lst_filter_unequal_name_module
def remove_comments(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Remove // comments
        content_no_comments = re.sub(r'//.*?\n', '\n', content, flags=re.DOTALL)

        return content_no_comments.strip()

    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return ""
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""
def extract_parameters(verilog_code, module_name):
    pattern = rf'module\s+{module_name}\s*#\s*\((.*?)\)\s*\(.*?\);'
    match = re.search(pattern, verilog_code, re.DOTALL)
    if match:
        parameter_str = match.group(1).strip()
        parameters = re.findall(r'parameter\s+(.*?)\s*=\s*([^,\s]+)', parameter_str)
        return parameters
    return []
def get_filename_without_extension(file_path):
    # Get the base name of the file without extension
    filename_without_extension = os.path.splitext(os.path.basename(file_path))[0]
    return filename_without_extension
def remove_ifdefs(verilog_code):
    # 定义正则表达式模式，匹配 `ifdef` 到 `endif` 之间的内容（包括 `ifdef` 和 `endif`）
    pattern = r'`ifdef\s+\w+\s*(.*?)`endif'
    # 使用 re.DOTALL 标志，使 . 匹配包括换行符在内的任意字符
    result = re.sub(pattern, '', verilog_code, flags=re.DOTALL)
    return result
def extract_ports(verilog_code):
    # 正则表达式模式，用于匹配模块端口声明
    pattern = r'\b(input|output|inout)\s+(\bwire\b|\breg\b)?(\s+\[.*?\])?\s*(\w+)\s*(,|\);)?'

    # 匹配所有端口声明
    matches = re.findall(pattern, verilog_code)

    ports = []
    for match in matches:
        direction = match[0]  # 输入、输出、双向
        datatype = match[1]  # 寄存器或线网
        width = match[2]  # 位宽
        port_name = match[3]  # 端口名

        # 处理位宽信息，如果没有提供则为None
        if width:
            width = width.strip()

        # 将信息添加到端口列表中
        ports.append({
            'direction': direction,
            'datatype': datatype,
            'width': width,
            'name': port_name
        })

    return ports

# #os operatons:
directory_path = './input_file'
file_lst = file_input_filter(directory_path)
print('--------------Files Pass check rules--------------')
for l in file_lst:
    print(l)

#1.get module -- );info
for file in file_lst:
    module_name=get_filename_without_extension(file)
    print(f"Processing {module_name}.....")
    verilog_code = remove_comments(file)
    verilog_code = remove_ifdefs(verilog_code)
    parameters = extract_parameters(verilog_code,module_name)
    # print(parameters)
    ports_info=extract_ports(verilog_code)
    # for port in ports_info:
    #     print(f"Port Name: {port['name']}")
    #     print(f"Direction: {port['direction']}")
    #     print(f"Data Type: {port['datatype']}")
    #     print(f"Width: {port['width']}")
    #     print()
    out_str=''
    for port in ports_info:
        if port['width']:
            # print(f"yes--{port['name']}")
            out_str = out_str + 'wire ' +port['width']+' '+ port['name'] + ';\n'
        else:
            out_str=out_str+'wire '+port['name']+';\n'
    out_str = out_str + '\n' + module_name + ' '
    if parameters:
        # print(parameters)
        out_str = out_str + ' # (\n'
        print("    This module defined parameters...")
        for index,para in enumerate(parameters):
            # print(f'Setting Default value {para[0]} to {para[1]}')
            print(index,para)
            out_str = out_str.replace(para[0],para[1])
            out_str = out_str +'.'+para[0]+' ('+para[1]+')'
            if index != len(parameters)-1:
                out_str = out_str +',\n'
            else:
                out_str = out_str + '\n) '
    out_str = out_str + module_name + '_u (\n'
######################## The same structure ends here ################################
    #1.MODE-1 only generate instance without connect
    for index,port in enumerate(ports_info):
        out_str = out_str +'.'+port['name']+'( )'
        if index != len(ports_info)-1:
            out_str=out_str+',\n'
        else:
            out_str = out_str + '\n);'
    with open('./tmp/'+module_name+'.v','w') as file:
        file.write(out_str)
