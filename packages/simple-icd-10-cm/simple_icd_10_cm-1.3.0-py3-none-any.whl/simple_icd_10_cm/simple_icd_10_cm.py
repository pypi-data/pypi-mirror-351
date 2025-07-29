# simple_icd_10_cm is released under the MIT License
# Copyright (c) 2021-2025 Stefano Travasci
# Read the full LICENCES at https://github.com/StefanoTrv/simple_icd_10_cm/blob/master/LICENSE

from typing import Optional
import xml.etree.ElementTree as ET

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources

from . import data  # relative-import the "package" containing the data

_chapter_list: list["_CodeTree"] = []

_code_to_node: dict[str, "_CodeTree"] = {}

_all_codes_list: list[str] = []

_all_codes_list_no_dots: list[str] = []

_code_to_index_dictionary: dict[str, int] = {}

_all_codes_package_file_name:str = 'code-list-April-2025.txt'
_classification_data_package_file_name:str = 'icd10cm-tabular-April-2025.xml'

class _CodeTree:
    def __init__(self, tree, parent = None, seven_chr_def_ancestor = None, seven_chr_note_ancestor = None, use_additional_code_ancestor = None, code_first_ancestor = None):
        #initialize all the values
        self.name = ""
        self.description = ""
        self.type = ""
        self.parent = parent
        self.children = []
        self.excludes1 = []
        self.excludes2 = []
        self.includes = []
        self.inclusion_term = []
        self.seven_chr_def = {}
        self.seven_chr_def_ancestor = seven_chr_def_ancestor
        self.seven_chr_note = ""
        self.seven_chr_note_ancestor = seven_chr_note_ancestor
        self.use_additional_code = ""
        self.use_additional_code_ancestor = use_additional_code_ancestor
        self.code_first = ""
        self.code_first_ancestor = code_first_ancestor
        
        #reads the data from the subtrees
        new_seven_chr_def_ancestor=seven_chr_def_ancestor
        new_seven_chr_note_ancestor=seven_chr_note_ancestor
        new_use_additional_code_ancestor=use_additional_code_ancestor
        new_code_first_ancestor=code_first_ancestor
        if "id" in tree.attrib: #the name of sections is an attribute instead of text inside an XML element
            self.name=tree.attrib["id"]
        for subtree in tree:
            if subtree.tag=="section" or subtree.tag=="diag": #creates a new child for this node
                self.children.append(_CodeTree(subtree,parent=self,seven_chr_def_ancestor=new_seven_chr_def_ancestor,seven_chr_note_ancestor=new_seven_chr_note_ancestor,use_additional_code_ancestor=new_use_additional_code_ancestor,code_first_ancestor=new_code_first_ancestor))
            elif subtree.tag=="name":
                self.name=subtree.text
            elif subtree.tag=="desc":
                self.description=subtree.text
            elif subtree.tag=="excludes1":
                for note in subtree:
                    self.excludes1.append(note.text)
            elif subtree.tag=="excludes2":
                for note in subtree:
                    self.excludes2.append(note.text)
            elif subtree.tag=="includes":
                for note in subtree:
                    self.includes.append(note.text)
            elif subtree.tag=="inclusionTerm":
                for note in subtree:
                    self.inclusion_term.append(note.text)
            elif subtree.tag=="sevenChrDef":
                last_char = None
                for extension in subtree:
                    if extension.tag=="extension":
                        self.seven_chr_def[extension.attrib["char"]]=extension.text
                        last_char = extension.attrib["char"]
                    elif extension.tag=="note":
                        self.seven_chr_def[last_char]=self.seven_chr_def[last_char]+"/"+extension.text
                new_seven_chr_def_ancestor=self
            elif subtree.tag=="sevenChrNote":
                self.seven_chr_note=subtree[0].text
                new_seven_chr_note_ancestor=self
            elif subtree.tag=="useAdditionalCode":
                for i in range(0,len(subtree)):#in case there are multiple lines
                    self.use_additional_code=self.use_additional_code+"\n"+subtree[i].text
                new_use_additional_code_ancestor=self
            elif subtree.tag=="codeFirst":
                for i in range(0,len(subtree)):#in case there are multiple lines
                    self.code_first=self.code_first+"\n"+subtree[i].text
                new_code_first_ancestor=self
        
        #cleans the use_additional_code and code_first fields from extra new lines
        if self.use_additional_code!="" and self.use_additional_code[0]=="\n":
            self.use_additional_code=self.use_additional_code[1:]
        if self.code_first!="" and self.code_first[0]=="\n":
            self.code_first=self.code_first[1:]
        
        #sets the type
        if tree.tag=="chapter":
            self.type="chapter"
        elif tree.tag=="section":
            self.type="section"
        elif tree.tag=="diag_ext":
            self.type="extended subcategory"
        elif tree.tag=="diag" and len(self.name)==3:
            self.type="category"
        else:
            self.type="subcategory"
        
        #adds the new node to the dictionary
        if self.name not in _code_to_node:#in case a section has the same name of a code (ex B99)
            _code_to_node[self.name]=self
        
        #if this code is a leaf, it adds to its children the codes created by adding the seventh character
        if len(self.children)==0 and (self.seven_chr_def!={} or self.seven_chr_def_ancestor!=None) and self.type!="extended subcategory":
            if self.seven_chr_def!={}:
                dictionary = self.seven_chr_def
            else:
                dictionary = self.seven_chr_def_ancestor.seven_chr_def # type: ignore[reportOptionalMemberAccess]
            extended_name=self.name
            if len(extended_name)==3:
                extended_name=extended_name+"."
            while len(extended_name)<7:#adds the placeholder X if needed
                extended_name = extended_name+"X"
            for extension in dictionary:
                if((extended_name[:3]+extended_name[4:]+extension) in all_confirmed_codes):#checks if there's a special rule that excludes this new code
                    new_XML = "<diag_ext><name>"+extended_name+extension+"</name><desc>"+self.description+", "+dictionary[extension]+"</desc></diag_ext>"
                    self.children.append(_CodeTree(ET.fromstring(new_XML),parent=self,seven_chr_def_ancestor=new_seven_chr_def_ancestor,seven_chr_note_ancestor=new_seven_chr_note_ancestor,use_additional_code_ancestor=new_use_additional_code_ancestor,code_first_ancestor=new_code_first_ancestor))

def _load_codes(all_codes_file_path:Optional[str] = None, classification_data_file_path:Optional[str] = None) -> None: # either both or none of the strings must be None
    #loads the list of all codes, to remove later from the tree the ones that do not exist for very specific rules not easily extracted from the XML file
    if all_codes_file_path is None:
        assert classification_data_file_path is None
        text = pkg_resources.read_text(data, _all_codes_package_file_name)
    else:
        assert classification_data_file_path is not None
        with open(all_codes_file_path, encoding="utf-8") as f:
            text = f.read()
    global all_confirmed_codes
    all_confirmed_codes = set()
    lines=text.split("\n")
    for line in lines:
        all_confirmed_codes.add(line.split(" ")[0].replace(".",""))
    
    #creates the tree
    if classification_data_file_path is None:
        root = ET.fromstring(pkg_resources.read_text(data, _classification_data_package_file_name))
    else:
        with open(classification_data_file_path, encoding="utf-8") as f:
            text = f.read()
            root = ET.fromstring(text)
    root.remove(root[0])
    root.remove(root[0])
    if len(_chapter_list)>0: #empties data structures only if needed and if the files have been read with no error
        _chapter_list.clear()
        _code_to_node.clear()
        _all_codes_list.clear()
        _all_codes_list_no_dots.clear()
        _code_to_index_dictionary.clear()
    for child in root:
        _chapter_list.append(_CodeTree(child))
    
    del all_confirmed_codes #deletes this list since it won't be needed anymore


_load_codes()

def change_version(all_codes_file_path:Optional[str] = None, classification_data_file_path:Optional[str] = None) -> None:
    if (all_codes_file_path is None and classification_data_file_path is None) or (all_codes_file_path is not None and classification_data_file_path is not None):
        _load_codes(all_codes_file_path=all_codes_file_path,classification_data_file_path=classification_data_file_path)
    else:
        ac_error = "None" if all_codes_file_path is None else "\"" + all_codes_file_path + "\""
        cd_error = "None" if classification_data_file_path is None else "\"" + classification_data_file_path + "\""
        raise ValueError("Either both paths must be provided, or none.\nProvided values were:\n\t-all_codes_file_path is "+ac_error+"\n\t-classification_data_file_path is "+cd_error+"\n")

def _add_dot_to_code(code:str) -> str:
    if len(code)<4 or code[3]==".":
        return code
    elif code[:3]+"."+code[3:] in _code_to_node:
        return code[:3]+"."+code[3:]
    else:
        return code

def is_valid_item(code:str) -> bool:
    return code in _code_to_node or len(code)>=4 and code[:3]+"."+code[3:] in _code_to_node

def is_chapter(code:str) -> bool:
    code = _add_dot_to_code(code)
    if code in _code_to_node:
        return _code_to_node[code].type=="chapter"
    else:
        return False

def is_block(code:str) -> bool:
    code = _add_dot_to_code(code)
    if code in _code_to_node:
        #second half of the or is for sections containing a single category
        return _code_to_node[code].type=="section" or _code_to_node[code].parent!=None and _code_to_node[code].parent.name==code # type: ignore[reportOptionalMemberAccess]
    else:
        return False

def is_category(code:str) -> bool:
    code = _add_dot_to_code(code)
    if code in _code_to_node:
        return _code_to_node[code].type=="category"
    else:
        return False

def is_subcategory(code:str, include_extended_subcategories:bool=True) -> bool:
    code = _add_dot_to_code(code)
    if code in _code_to_node:
        return _code_to_node[code].type=="subcategory" or _code_to_node[code].type=="extended subcategory" and include_extended_subcategories
    else:
        return False

def is_extended_subcategory(code:str) -> bool:
    code = _add_dot_to_code(code)
    if code in _code_to_node:
        return _code_to_node[code].type=="extended subcategory"
    else:
        return False
    
def is_category_or_subcategory(code:str) -> bool:
    return is_subcategory(code) or is_category(code)

def is_chapter_or_block(code:str) -> bool:
    return is_block(code) or is_chapter(code)

def get_description(code:str, prioritize_blocks:bool=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.description
    else:
        return node.description

def get_excludes1(code:str, prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.excludes1.copy()
    else:
        return node.excludes1.copy()

def get_excludes2(code:str, prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.excludes2.copy()
    else:
        return node.excludes2.copy()

def get_includes(code:str, prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.includes.copy()
    else:
        return node.includes.copy()

def get_inclusion_term(code:str, prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        return node.parent.inclusion_term.copy()
    else:
        return node.inclusion_term.copy()

def get_seven_chr_def(code:str, search_in_ancestors:bool=False, prioritize_blocks:bool=False) -> dict[str,str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.seven_chr_def.copy()
    if search_in_ancestors and len(res)==0 and node.seven_chr_def_ancestor!=None:
        return node.seven_chr_def_ancestor.seven_chr_def.copy()
    else:
        return res

def get_seven_chr_note(code:str, search_in_ancestors:bool=False, prioritize_blocks:bool=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.seven_chr_note
    if search_in_ancestors and res=="" and node.seven_chr_note_ancestor!=None:
        return node.seven_chr_note_ancestor.seven_chr_note
    else:
        return res

def get_use_additional_code(code:str, search_in_ancestors:bool=False, prioritize_blocks:bool=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.use_additional_code
    if search_in_ancestors and res=="" and node.use_additional_code_ancestor!=None:
        return node.use_additional_code_ancestor.use_additional_code
    else:
        return res

def get_code_first(code:str, search_in_ancestors:bool=False, prioritize_blocks:bool=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = node.code_first
    if search_in_ancestors and res=="" and node.code_first_ancestor!=None:
        return node.code_first_ancestor.code_first
    else:
        return res

def get_parent(code:str, prioritize_blocks:bool=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    if node.parent!=None:
        return node.parent.name
    else:
        return ""

def get_children(code:str, prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    res = []
    for child in node.children:
        res.append(child.name)
    return res

def is_leaf(code:str, prioritize_blocks:bool=False) -> bool:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    return len(node.children)==0

def get_full_data(code:str, search_in_ancestors:bool=False, prioritize_blocks:bool=False) -> str:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    str = "Name:\n"+node.name+"\nDescription:\n"+node.description
    if node.parent!=None:
        str = str + "\nParent:\n" + node.parent.name
    if node.excludes1!=[]:
        str = str + "\nexcludes1:"
        for item in node.excludes1:
            str = str + "\n" + item
    if node.excludes2!=[]:
        str = str + "\nexcludes2:"
        for item in node.excludes2:
            str = str + "\n" + item
    if node.includes!=[]:
        str = str + "\nincludes:"
        for item in node.includes:
            str = str + "\n" + item
    if node.inclusion_term!=[]:
        str = str + "\ninclusion term:"
        for item in node.inclusion_term:
            str = str + "\n" + item
    seven_chr_note=get_seven_chr_note(code,search_in_ancestors=search_in_ancestors,prioritize_blocks=prioritize_blocks)
    if seven_chr_note!="":
        str = str + "\nseven chr note:\n" + seven_chr_note
    seven_chr_def=get_seven_chr_def(code,search_in_ancestors=search_in_ancestors,prioritize_blocks=prioritize_blocks)
    if seven_chr_def!={}:
        str = str + "\nseven chr def:"
        for item in seven_chr_def:
            str = str + "\n" + item + ":\t" + seven_chr_def[item]
    use_additional=get_use_additional_code(code,search_in_ancestors=search_in_ancestors,prioritize_blocks=prioritize_blocks)
    if use_additional!="":
        str = str + "\nuse additional code:\n" + use_additional
    code_first=get_code_first(code,search_in_ancestors=search_in_ancestors,prioritize_blocks=prioritize_blocks)
    if code_first!="":
        str = str + "\ncode first:\n" + code_first
    if node.children==[]:
        str = str + "\nChildren:\nNone--"
    else:
        str = str + "\nChildren:\n"
        for child in node.children:
            str = str + child.name + ", "
    return str[:-2]

def get_ancestors(code:str,prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    result = []
    while node.parent != None:
        result.append(node.parent.name)
        node=node.parent
    return result

def get_descendants(code:str,prioritize_blocks:bool=False) -> list[str]:
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(code)]
    if prioritize_blocks and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    result = []
    _add_children_to_list(node, result)
    return result

def _add_children_to_list(node:_CodeTree, list:list[str]) -> None:
    for child in node.children:
        list.append(child.name)
        _add_children_to_list(child,list)

def is_ancestor(a:str,b:str,prioritize_blocks_a:bool=False,prioritize_blocks_b:bool=False) -> bool:
    if not is_valid_item(a):
        raise ValueError("The code \""+a+"\" does not exist.")
    node = _code_to_node[_add_dot_to_code(a)]
    if prioritize_blocks_a and node.parent!=None and node.parent.name==node.name:
        node = node.parent
    return a in get_ancestors(b, prioritize_blocks=prioritize_blocks_b) and (a!=b or prioritize_blocks_a)

def is_descendant(a:str,b:str,prioritize_blocks_a:bool=False,prioritize_blocks_b:bool=False) -> bool:
    return is_ancestor(b,a,prioritize_blocks_a=prioritize_blocks_b,prioritize_blocks_b=prioritize_blocks_a)

def get_nearest_common_ancestor(a:str,b:str,prioritize_blocks_a:bool=False,prioritize_blocks_b:bool=False) -> str:
    anc_a = [_add_dot_to_code(a)] + get_ancestors(a, prioritize_blocks=prioritize_blocks_a)
    anc_b = [_add_dot_to_code(b)] + get_ancestors(b, prioritize_blocks=prioritize_blocks_b)
    if len(anc_b) > len(anc_a):
        temp = anc_a
        anc_a = anc_b
        anc_b = temp
    for anc in anc_a:
        if anc in anc_b:
            return anc
    return ""

def get_all_codes(with_dots:bool=True) -> list[str]:
    if _all_codes_list==[]:
        _fill_all_codes_list()
    if with_dots:
        return _all_codes_list.copy()
    else:
        return _all_codes_list_no_dots.copy()

def _fill_all_codes_list() -> None:
    for chapter in _chapter_list:
        _add_tree_to_list(chapter)

def _add_tree_to_list(tree:_CodeTree) -> None:
    _all_codes_list.append(tree.name)
    if(len(tree.name)>4 and tree.name[3]=="."):
        _all_codes_list_no_dots.append(tree.name[:3]+tree.name[4:])
    else:
        _all_codes_list_no_dots.append(tree.name)
    for child in tree.children:
        _add_tree_to_list(child)

def get_index(code:str) -> int: # type: ignore[reportReturnType]
    if not is_valid_item(code):
        raise ValueError("The code \""+code+"\" does not exist.")
    code = _add_dot_to_code(code)
    if _all_codes_list==[]:
        _fill_all_codes_list()
    if code in _code_to_index_dictionary:
        return _code_to_index_dictionary[code]
    else:
        i=0
        for c in _all_codes_list:
            if c==code:
                _code_to_index_dictionary[code]=i
                return i
            else:
                i=i+1

def remove_dot(code:str) -> str:
    if _all_codes_list==[]:
        _fill_all_codes_list()
    return _all_codes_list_no_dots[get_index(code)]

def add_dot(code:str) -> str:
    if _all_codes_list==[]:
        _fill_all_codes_list()
    return _all_codes_list[get_index(code)]